"""Ingest PubMed evidence for a condition."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

try:
    from ..core.enums import ClaimCategory
    from ..core.settings import SozoSettings
    from ..conditions.registry import get_registry
    from ..evidence.pubmed_client import PubMedClient
    from ..evidence.cache import EvidenceCache
except ImportError as e:
    typer.echo(
        typer.style(
            f"Import error: {e}\n"
            "Ensure sozo_generator is installed and all dependencies are available.",
            fg=typer.colors.RED,
        )
    )
    raise SystemExit(1)

evidence_app = typer.Typer(
    name="ingest-evidence",
    help="Ingest PubMed evidence for conditions.",
    add_completion=False,
)


_PROFILES_DIR = Path(__file__).parent.parent.parent.parent.parent / "data/reference/evidence_profiles"


def _load_profile(condition_slug: str) -> Optional[dict]:
    """Load condition-specific evidence search profile from YAML if available."""
    profile_path = _PROFILES_DIR / f"{condition_slug}.yaml"
    if not profile_path.exists():
        # Try relative to CWD
        alt = Path("data/reference/evidence_profiles") / f"{condition_slug}.yaml"
        if alt.exists():
            profile_path = alt
        else:
            return None
    try:
        import yaml
        with open(profile_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _build_query(condition_name: str, category: ClaimCategory) -> str:
    """Build a PubMed search query for a condition + claim category."""
    category_terms = {
        ClaimCategory.PATHOPHYSIOLOGY: "pathophysiology mechanism",
        ClaimCategory.BRAIN_REGIONS: "brain region neuroscience imaging",
        ClaimCategory.NETWORK_INVOLVEMENT: "brain network connectivity",
        ClaimCategory.CLINICAL_PHENOTYPES: "clinical phenotype subtype",
        ClaimCategory.ASSESSMENT_TOOLS: "assessment scale measurement clinical",
        ClaimCategory.STIMULATION_TARGETS: "transcranial stimulation target neuromodulation",
        ClaimCategory.STIMULATION_PARAMETERS: "stimulation parameters protocol dosing",
        ClaimCategory.MODALITY_RATIONALE: "neuromodulation therapy rationale",
        ClaimCategory.SAFETY: "safety adverse effects",
        ClaimCategory.CONTRAINDICATIONS: "contraindications precautions",
        ClaimCategory.RESPONDER_CRITERIA: "treatment response outcome predictor",
        ClaimCategory.INCLUSION_CRITERIA: "inclusion exclusion clinical trial criteria",
        ClaimCategory.EXCLUSION_CRITERIA: "exclusion contraindication clinical criteria",
    }
    term = category_terms.get(category, category.value.replace("_", " "))
    return f"{condition_name}[Title/Abstract] AND {term}"


@evidence_app.command("ingest")
def ingest_evidence(
    condition: str = typer.Option(..., "--condition", help="Condition slug (e.g. parkinsons)"),
    max_results: int = typer.Option(30, "--max-results", help="Maximum PubMed results per query"),
    force_refresh: bool = typer.Option(
        False,
        "--force-refresh/--no-force-refresh",
        help="Bypass cache and re-fetch from PubMed",
    ),
    categories: Optional[str] = typer.Option(
        None,
        "--categories",
        help="Comma-separated claim categories to search (default: all)",
    ),
):
    """Ingest PubMed evidence for a condition and store in local cache."""
    try:
        settings = SozoSettings()
    except Exception as e:
        typer.echo(typer.style(f"Failed to load settings: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    # Load condition from registry
    try:
        registry = get_registry()
        condition_obj = registry.get(condition)
    except Exception as e:
        typer.echo(typer.style(f"Condition '{condition}' not found: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    condition_name = condition_obj.get("display_name", condition) if isinstance(condition_obj, dict) else getattr(condition_obj, "display_name", condition)

    # Resolve which categories to search
    if categories:
        requested_cats = [c.strip() for c in categories.split(",") if c.strip()]
        search_categories: list[ClaimCategory] = []
        for cat_str in requested_cats:
            try:
                search_categories.append(ClaimCategory(cat_str))
            except ValueError:
                valid = ", ".join(c.value for c in ClaimCategory)
                typer.echo(
                    typer.style(
                        f"Unknown category '{cat_str}'. Valid values: {valid}",
                        fg=typer.colors.YELLOW,
                    )
                )
    else:
        search_categories = list(ClaimCategory)

    if not search_categories:
        typer.echo(typer.style("No valid categories to search.", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    # Load condition-specific evidence profile if available
    profile = _load_profile(condition)
    profile_queries = {}
    if profile and "search_profiles" in profile:
        profile_queries = profile["search_profiles"]
        typer.echo(
            typer.style(f"  [PROFILE] ", fg=typer.colors.CYAN)
            + f"Loaded evidence profile with {len(profile_queries)} targeted queries"
        )

    typer.echo(
        typer.style(
            f"Ingesting PubMed evidence for: {condition_name}",
            fg=typer.colors.CYAN,
        )
    )
    typer.echo(f"  Categories:    {len(search_categories)}")
    typer.echo(f"  Max results:   {max_results} per category")
    typer.echo(f"  Force refresh: {force_refresh}")
    typer.echo(f"  Cache dir:     {settings.cache_dir}")
    typer.echo("")

    # Instantiate PubMedClient and EvidenceCache
    try:
        pubmed_client = PubMedClient(
            email=settings.ncbi_email,
            api_key=settings.ncbi_api_key or None,
            cache_dir=settings.cache_dir,
            force_refresh=force_refresh,
        )
        cache = EvidenceCache(cache_dir=settings.cache_dir)
    except Exception as e:
        typer.echo(typer.style(f"Failed to initialize PubMed client: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    total_articles = 0
    categories_done = 0

    # If profile has targeted queries, run those in addition to (or instead of) generic categories
    if profile_queries and not categories:
        for profile_key, profile_cfg in profile_queries.items():
            raw_query = str(profile_cfg.get("query", "")).replace("\n", " ").strip()
            profile_max = profile_cfg.get("max_results", max_results)
            cache_key = f"profile|{condition}|{profile_key}|{profile_max}"
            if not force_refresh:
                cached = cache.get(cache_key)
                if cached is not None:
                    count = len(cached) if isinstance(cached, list) else 0
                    typer.echo(
                        typer.style("  [CACHE] ", fg=typer.colors.YELLOW)
                        + f"{profile_key}: {count} articles (cached)"
                    )
                    total_articles += count
                    categories_done += 1
                    continue
            try:
                articles = pubmed_client.search(query=raw_query, max_results=profile_max)
                article_dicts = [
                    a.model_dump() if hasattr(a, "model_dump") else dict(a)
                    for a in articles
                ]
                cache.set(cache_key, article_dicts)
                count = len(articles)
                typer.echo(
                    typer.style("  [OK]    ", fg=typer.colors.GREEN)
                    + f"{profile_key}: {count} articles found"
                )
                total_articles += count
                categories_done += 1
            except Exception as e:
                typer.echo(
                    typer.style("  [FAIL]  ", fg=typer.colors.RED)
                    + f"{profile_key}: {e}"
                )
        typer.echo("")
        typer.echo(
            typer.style(
                f"Cached evidence for {condition_name}: {total_articles} articles "
                f"across {categories_done} profile queries.",
                fg=typer.colors.GREEN,
            )
        )
        return

    for cat in search_categories:
        query = _build_query(condition_name, cat)
        cache_key = f"ingest|{condition}|{cat.value}|{max_results}"

        # Check cache unless force-refresh
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached is not None:
                count = len(cached) if isinstance(cached, list) else 0
                typer.echo(
                    typer.style(f"  [CACHE] ", fg=typer.colors.YELLOW)
                    + f"{cat.value}: {count} articles (cached)"
                )
                total_articles += count
                categories_done += 1
                continue

        try:
            articles = pubmed_client.search(query=query, max_results=max_results)
            article_dicts = [
                a.model_dump() if hasattr(a, "model_dump") else dict(a)
                for a in articles
            ]
            cache.set(cache_key, article_dicts)
            count = len(articles)
            typer.echo(
                typer.style(f"  [OK]    ", fg=typer.colors.GREEN)
                + f"{cat.value}: {count} articles found"
            )
            total_articles += count
            categories_done += 1
        except Exception as e:
            typer.echo(
                typer.style(f"  [FAIL]  ", fg=typer.colors.RED)
                + f"{cat.value}: {e}"
            )

    typer.echo("")
    typer.echo(
        typer.style(
            f"Cached evidence for {condition_name}: {total_articles} articles "
            f"across {categories_done} categories.",
            fg=typer.colors.GREEN,
        )
    )
