"""
SOZO Generator CLI — clinical document generation platform.

Usage:
    python -m sozo_generator.cli.main [COMMAND] [OPTIONS]
"""
import typer

# --- Import subcommand apps with graceful error handling ---

try:
    from .build_condition import build_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'build condition' command: {e}", fg=typer.colors.YELLOW))
    build_app = typer.Typer(name="build", help="(unavailable — import error)")

try:
    from .build_all import build_all_app
    _build_all_available = True
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'build all' command: {e}", fg=typer.colors.YELLOW))
    _build_all_available = False

try:
    from .ingest_evidence import evidence_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'ingest-evidence' command: {e}", fg=typer.colors.YELLOW))
    evidence_app = typer.Typer(name="ingest-evidence", help="(unavailable — import error)")

try:
    from .extract_template import extract_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'extract-template' command: {e}", fg=typer.colors.YELLOW))
    extract_app = typer.Typer(name="extract-template", help="(unavailable — import error)")

try:
    from .qa_report import qa_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'qa' command: {e}", fg=typer.colors.YELLOW))
    qa_app = typer.Typer(name="qa", help="(unavailable — import error)")

try:
    from .render_visuals import visuals_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'visuals' command: {e}", fg=typer.colors.YELLOW))
    visuals_app = typer.Typer(name="visuals", help="(unavailable — import error)")

try:
    from .qa_engine_cli import qa_engine_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'qa2' command: {e}", fg=typer.colors.YELLOW))
    qa_engine_app = typer.Typer(name="qa2", help="(unavailable — import error)")

try:
    from .review_cli import review_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'review' command: {e}", fg=typer.colors.YELLOW))
    review_app = typer.Typer(name="review", help="(unavailable — import error)")

try:
    from .evidence_cli import evidence_cli_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'evidence' command: {e}", fg=typer.colors.YELLOW))
    evidence_cli_app = typer.Typer(name="evidence", help="(unavailable — import error)")

try:
    from .manifest_cli import manifest_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'manifests' command: {e}", fg=typer.colors.YELLOW))
    manifest_app = typer.Typer(name="manifests", help="(unavailable — import error)")

try:
    from autoagent_clinical.cli import app as autoagent_clinical_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'autoagent-clinical' command: {e}", fg=typer.colors.YELLOW))
    autoagent_clinical_app = typer.Typer(name="autoagent-clinical", help="(unavailable — import error)")

# ---------------------------------------------------------------------------
# Top-level Typer app
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="sozo-generator",
    help="SOZO Brain Center clinical document generation platform.",
    add_completion=False,
)

# Register subcommand groups
app.add_typer(extract_app, name="extract-template")
app.add_typer(evidence_app, name="ingest-evidence")
app.add_typer(build_app, name="build")
app.add_typer(qa_app, name="qa")
app.add_typer(visuals_app, name="visuals")
app.add_typer(qa_engine_app, name="qa2")
app.add_typer(review_app, name="review")
app.add_typer(evidence_cli_app, name="evidence")
app.add_typer(manifest_app, name="manifests")
app.add_typer(autoagent_clinical_app, name="autoagent-clinical")

# Merge build-all commands into the build group
if _build_all_available:
    from .build_all import build_all_app  # noqa: F811 re-import to be explicit
    # Register the 'all' command from build_all_app directly on build_app
    # so it is accessible as `build all`
    try:
        from .build_all import build_all as _build_all_cmd
        build_app.command("all")(_build_all_cmd)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Top-level commands
# ---------------------------------------------------------------------------

VERSION = "1.1.0"  # Post-refactor: canonical pipeline, PMID validation, shared helpers

VALID_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "autism", "long_covid", "tinnitus", "insomnia",
    "trd_vns",
]

CONDITION_NAMES = {
    "parkinsons": "Parkinson's Disease",
    "depression": "Major Depressive Disorder",
    "anxiety": "Anxiety Disorders",
    "adhd": "ADHD",
    "alzheimers": "Alzheimer's Disease",
    "post_stroke": "Post-Stroke Rehabilitation",
    "tbi": "Traumatic Brain Injury",
    "chronic_pain": "Chronic Pain",
    "ptsd": "PTSD",
    "ocd": "Obsessive-Compulsive Disorder",
    "ms": "Multiple Sclerosis",
    "autism": "Autism Spectrum Disorder",
    "long_covid": "Long COVID (Post-COVID Syndrome)",
    "tinnitus": "Tinnitus",
    "insomnia": "Insomnia",
    "trd_vns": "Treatment-Resistant Depression — Implantable VNS",
}


@app.command("version")
def version():
    """Print the current version of sozo-generator."""
    _version = VERSION
    try:
        # Try to read from pyproject.toml if importlib.metadata is available
        from importlib.metadata import version as pkg_version
        _version = pkg_version("sozo_generator")
    except Exception:
        pass
    typer.echo(f"sozo-generator {_version}")


@app.command("list-conditions")
def list_conditions():
    """List all 15 supported condition slugs with their display names."""
    # Try to pull live data from registry; fall back to built-in list
    try:
        from ..conditions.registry import get_registry  # type: ignore
        registry = get_registry()
        conditions = registry.list_all()
        if conditions:
            typer.echo(
                typer.style(
                    f"{'Slug':<20}  {'Name'}",
                    fg=typer.colors.CYAN,
                )
            )
            typer.echo("-" * 50)
            for c in conditions:
                if isinstance(c, dict):
                    slug = c.get("slug", "?")
                    name = c.get("display_name") or c.get("name", slug)
                else:
                    slug = getattr(c, "slug", "?")
                    name = getattr(c, "display_name", slug)
                typer.echo(f"  {slug:<20}  {name}")
            typer.echo("")
            typer.echo(
                typer.style(f"Total: {len(conditions)} conditions", fg=typer.colors.GREEN)
            )
            return
    except Exception:
        pass

    # Fallback: print built-in list
    typer.echo(
        typer.style(
            f"{'Slug':<20}  {'Name'}",
            fg=typer.colors.CYAN,
        )
    )
    typer.echo("-" * 50)
    for slug in VALID_SLUGS:
        name = CONDITION_NAMES.get(slug, slug)
        typer.echo(f"  {slug:<20}  {name}")
    typer.echo("")
    typer.echo(typer.style(f"Total: {len(VALID_SLUGS)} conditions", fg=typer.colors.GREEN))


@app.command("generate")
def generate(
    condition: str = typer.Argument(..., help="Condition slug (e.g. 'parkinsons') or 'all'"),
    tier: str = typer.Option("both", help="Tier: fellow, partners, or both"),
    doc_type: str = typer.Option("all", "--doc-type", "-d", help="Document type or 'all'"),
    output_dir: str = typer.Option(None, "--output-dir", "-o", help="Output directory override"),
    no_visuals: bool = typer.Option(False, "--no-visuals", help="Skip visual generation"),
    no_qa: bool = typer.Option(False, "--no-qa", help="Skip QA checks"),
    with_images: bool = typer.Option(False, "--with-images", help="Search and insert web images from PMC/Wikimedia"),
    with_pdf: bool = typer.Option(False, "--with-pdf", help="Also generate PDF alongside DOCX"),
):
    """Generate documents using the canonical GenerationService.

    This is the recommended generation command. It routes through the unified
    pipeline with QA, evidence traceability, and visual generation support.

    Use --with-images to automatically search PubMed Central and Wikimedia Commons
    for relevant clinical/scientific images and insert them into documents.

    Examples:
        sozo generate parkinsons
        sozo generate parkinsons --tier partners --doc-type handbook
        sozo generate all --tier both
    """
    from ..generation.service import GenerationService

    svc = GenerationService(
        output_dir=output_dir,
        with_visuals=not no_visuals,
        with_qa=not no_qa,
        with_images=with_images,
        with_pdf=with_pdf,
    )

    if condition == "all":
        results = svc.generate_batch(tier=tier, doc_type=doc_type)
    else:
        results = svc.generate(
            condition=condition,
            tier=tier,
            doc_type=doc_type,
            output_dir=output_dir,
        )

    # Print results
    success_count = sum(1 for r in results if r.success)
    fail_count = sum(1 for r in results if not r.success)

    for r in results:
        if r.success:
            qa_tag = ""
            if r.qa_passed is not None:
                qa_tag = f" [QA: {'PASS' if r.qa_passed else 'ISSUES'}]"
            typer.echo(f"  {typer.style('OK', fg=typer.colors.GREEN)}  {r.tier}/{r.doc_type}{qa_tag}")
        else:
            typer.echo(f"  {typer.style('FAIL', fg=typer.colors.RED)}  {r.tier}/{r.doc_type}: {r.error}")

    typer.echo("")
    color = typer.colors.GREEN if fail_count == 0 else typer.colors.YELLOW
    typer.echo(typer.style(
        f"Done: {success_count} generated, {fail_count} failed",
        fg=color,
    ))


@app.command("generate-from-template")
def generate_from_template(
    template: str = typer.Argument(..., help="Path to DOCX template or stored template profile ID"),
    condition: str = typer.Option("parkinsons", help="Target condition slug"),
    tier: str = typer.Option("partners", help="Tier: fellow or partners"),
    with_ai: bool = typer.Option(False, "--with-ai", help="Use AI (Claude/OpenAI) for section drafting"),
    with_research: bool = typer.Option(True, "--with-research/--no-research", help="Search PubMed for evidence"),
    with_visuals: bool = typer.Option(True, "--with-visuals/--no-visuals", help="Generate visual assets"),
):
    """Generate a document from an uploaded template for a different condition.

    The system parses the template structure, researches evidence, and generates
    content matching the template's layout and style for the target condition.

    Examples:
        sozo generate-from-template templates/gold_standard/Clinical_Handbook.docx --condition depression
        sozo generate-from-template tp-abc123 --condition adhd --with-ai
    """
    from pathlib import Path
    from ..generation.service import GenerationService

    svc = GenerationService(with_visuals=with_visuals, with_qa=True)

    # Determine if template is a file path or profile ID
    template_path = None
    template_id = None
    if Path(template).exists():
        template_path = template
        typer.echo(f"Ingesting template: {template}")
    else:
        template_id = template
        typer.echo(f"Using stored profile: {template}")

    typer.echo(f"Generating for: {condition} ({tier})")

    result = svc.generate_from_template(
        template_path=template_path,
        template_id=template_id,
        condition=condition,
        tier=tier,
        with_ai=with_ai,
        with_research=with_research,
    )

    if result.success:
        typer.echo(typer.style(f"\nOK: {result.output_path}", fg=typer.colors.GREEN))
        if result.qa_issues:
            typer.echo(f"\nReview issues ({len(result.qa_issues)}):")
            for issue in result.qa_issues[:10]:
                typer.echo(f"  {issue}")
        if result.visuals_generated:
            typer.echo(f"\nVisuals: {len(result.visuals_generated)} generated")
    else:
        typer.echo(typer.style(f"\nFAILED: {result.error}", fg=typer.colors.RED))


@app.command("template-ingest")
def template_ingest(
    path: str = typer.Argument(..., help="Path to DOCX template file"),
    name: str = typer.Option("", help="Profile name (auto-generated if empty)"),
):
    """Ingest a DOCX template and store its learned profile."""
    from ..template_profiles.builder import build_template_profile
    from ..template_profiles.store import TemplateProfileStore

    typer.echo(f"Ingesting: {path}")
    profile = build_template_profile(path, name=name)
    store = TemplateProfileStore()
    store.save(profile)

    typer.echo(typer.style(f"\nProfile created: {profile.profile_id}", fg=typer.colors.GREEN))
    typer.echo(f"  Name: {profile.name}")
    typer.echo(f"  Type: {profile.template_type}")
    typer.echo(f"  Doc type: {profile.inferred_doc_type}")
    typer.echo(f"  Sections: {profile.total_sections}")
    typer.echo(f"  Tables: {profile.total_tables}")
    typer.echo(f"  Figures: {profile.total_figures}")
    typer.echo(f"  Source condition: {profile.source_condition}")


@app.command("template-list")
def template_list():
    """List all stored template profiles."""
    from ..template_profiles.store import TemplateProfileStore
    store = TemplateProfileStore()
    profiles = store.list_profiles()

    if not profiles:
        typer.echo("No template profiles stored.")
        return

    typer.echo(typer.style(f"{'ID':<20} {'Name':<30} {'Type':<15} {'Sections'}", fg=typer.colors.CYAN))
    typer.echo("-" * 80)
    for p in profiles:
        typer.echo(f"  {p['profile_id']:<20} {p['name'][:28]:<30} {p['template_type']:<15} {p['total_sections']}")


@app.command("knowledge-status")
def knowledge_status():
    """Show the status of the SOZO knowledge system."""
    from ..knowledge.base import KnowledgeBase

    kb = KnowledgeBase()
    kb.load_all()

    typer.echo(typer.style("SOZO Knowledge System", fg=typer.colors.CYAN, bold=True))
    typer.echo("-" * 50)

    s = kb.summary()
    for key, val in s.items():
        if key != "loaded":
            typer.echo(f"  {key:<20} {val}")

    typer.echo("")
    report = kb.validate()
    color = typer.colors.GREEN if report.valid else typer.colors.YELLOW
    typer.echo(typer.style(
        f"Validation: {report.resolved}/{report.total_checks} links resolved, "
        f"{report.broken_count} issues",
        fg=color,
    ))

    if report.issues:
        typer.echo("")
        for issue in report.issues[:10]:
            typer.echo(f"  [{issue.severity}] {issue.message}")
        if len(report.issues) > 10:
            typer.echo(f"  ... and {len(report.issues) - 10} more")


@app.command("knowledge-inspect")
def knowledge_inspect(
    condition: str = typer.Argument(..., help="Condition slug to inspect"),
):
    """Inspect knowledge for a specific condition."""
    from ..knowledge.base import KnowledgeBase

    kb = KnowledgeBase()
    kb.load_all()

    cond = kb.get_condition(condition)
    if not cond:
        typer.echo(typer.style(f"Condition not found: {condition}", fg=typer.colors.RED))
        available = kb.list_conditions()
        if available:
            typer.echo(f"Available: {', '.join(available)}")
        return

    typer.echo(typer.style(f"{cond.display_name} ({cond.icd10})", fg=typer.colors.CYAN, bold=True))
    typer.echo(f"  Category: {cond.category}")
    typer.echo(f"  Evidence quality: {cond.evidence_quality}")
    typer.echo(f"  Modalities: {', '.join(cond.applicable_modalities)}")
    typer.echo(f"  Protocols: {len(cond.protocols)}")
    typer.echo(f"  Phenotypes: {len(cond.phenotypes)}")
    typer.echo(f"  References: {len(cond.references)}")
    typer.echo(f"  Safety rules: {len(cond.safety_rules)}")

    if cond.network_profiles:
        typer.echo(f"\n  Networks:")
        for np in cond.network_profiles:
            marker = " *" if np.primary else ""
            typer.echo(f"    {np.network.upper()}: {np.dysfunction} ({np.severity}){marker}")

    if cond.phenotypes:
        typer.echo(f"\n  Phenotypes:")
        for p in cond.phenotypes:
            typer.echo(f"    {p.label}: {', '.join(p.key_features[:3])}")

    if cond.protocols:
        typer.echo(f"\n  Protocols:")
        for p in cond.protocols:
            ol = " [OFF-LABEL]" if p.off_label else ""
            typer.echo(f"    {p.protocol_id}: {p.label} ({p.modality}){ol}")


@app.command("generate-canonical")
def generate_canonical_cmd(
    condition: str = typer.Argument(..., help="Condition slug from knowledge base"),
    doc_type: str = typer.Option("evidence_based_protocol", "--doc-type", "-d", help="Blueprint slug"),
    tier: str = typer.Option("fellow", help="fellow or partners"),
    no_visuals: bool = typer.Option(False, "--no-visuals"),
):
    """Generate a document using the canonical blueprint-driven path.

    This uses the KnowledgeBase + DocumentBlueprint instead of legacy builders.
    Supports conditions that exist only in the knowledge system (e.g., migraine).

    Examples:
        sozo generate-canonical parkinsons
        sozo generate-canonical migraine --tier partners
        sozo generate-canonical depression --doc-type evidence_based_protocol
    """
    from ..generation.service import GenerationService

    svc = GenerationService(with_visuals=not no_visuals, with_qa=False)
    result = svc.generate_canonical(condition, doc_type, tier)

    if result.success:
        typer.echo(typer.style(f"OK: {result.output_path}", fg=typer.colors.GREEN))
    else:
        typer.echo(typer.style(f"FAILED: {result.error}", fg=typer.colors.RED))


@app.command("review-summary")
def review_summary_cmd(
    condition: str = typer.Argument(..., help="Condition slug"),
    doc_type: str = typer.Option("evidence_based_protocol", "--doc-type", "-d"),
    tier: str = typer.Option("fellow"),
):
    """Show a review summary for a canonical document."""
    from ..knowledge.base import KnowledgeBase
    from ..knowledge.assembler import CanonicalDocumentAssembler
    from ..knowledge.review import build_review_summary

    kb = KnowledgeBase()
    kb.load_all()
    assembler = CanonicalDocumentAssembler(kb)
    try:
        _, prov = assembler.assemble(condition, doc_type, tier)
        summary = build_review_summary(prov)
        typer.echo(summary.to_text())
    except Exception as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED))


@app.command("regression-compare")
def regression_compare_cmd(
    condition: str = typer.Argument(..., help="Condition slug"),
    doc_type: str = typer.Option("evidence_based_protocol", "--doc-type", "-d"),
    tier: str = typer.Option("fellow"),
):
    """Compare legacy vs canonical generation for a condition."""
    from ..knowledge.regression import compare_outputs

    result = compare_outputs(condition, doc_type, tier)
    if result:
        typer.echo(result.to_text())
    else:
        typer.echo(typer.style("Comparison not available", fg=typer.colors.YELLOW))


@app.command("validate-knowledge")
def validate_knowledge_cmd():
    """Validate all knowledge and blueprint YAML files."""
    from ..knowledge.validate import validate_all

    report = validate_all()
    typer.echo(report.to_text())
    color = typer.colors.GREEN if report.passed else typer.colors.RED
    typer.echo(typer.style(
        f"\n{'PASSED' if report.passed else 'FAILED'}", fg=color, bold=True
    ))


@app.command("batch-readiness")
def batch_readiness_cmd(
    tier: str = typer.Option("fellow"),
):
    """Report readiness status for all canonical combinations."""
    from ..knowledge.batch import BatchRunner

    runner = BatchRunner()
    report = runner.readiness_report(tier)
    typer.echo(report.to_text())


@app.command("batch-generate")
def batch_generate_cmd(
    condition: str = typer.Option("", help="Single condition (empty = all)"),
    blueprint: str = typer.Option("", help="Single blueprint (empty = all)"),
    tier: str = typer.Option("fellow"),
):
    """Batch generate canonical documents."""
    from ..knowledge.batch import BatchRunner

    runner = BatchRunner()
    conds = [condition] if condition else None
    bps = [blueprint] if blueprint else None
    report = runner.generate_all_canonical(conditions=conds, blueprints=bps, tier=tier)
    typer.echo(report.to_text())

    # Save report
    from pathlib import Path
    report_path = Path("outputs") / "batch_report.json"
    report.save(report_path)
    typer.echo(f"\nReport saved: {report_path}")


@app.command("review-plan")
def review_plan_cmd(
    condition: str = typer.Argument(..., help="Condition slug"),
    comments_file: str = typer.Argument(..., help="Path to comments file (text or JSON)"),
    doc_type: str = typer.Option("evidence_based_protocol", "--doc-type", "-d"),
    tier: str = typer.Option("fellow"),
):
    """Create a change plan from reviewer comments (dry run — no regeneration)."""
    from ..knowledge.revision.parser import ingest_from_text, ingest_from_json
    from ..knowledge.revision.engine import RevisionEngine

    path = Path(comments_file)
    if path.suffix == ".json":
        comments = ingest_from_json(path)
    else:
        text = path.read_text()
        comments = ingest_from_text(text, f"review-{condition}", condition, doc_type, tier)

    engine = RevisionEngine()
    plan = engine.create_change_plan(comments)
    typer.echo(plan.to_text())


@app.command("review-regenerate")
def review_regenerate_cmd(
    condition: str = typer.Argument(..., help="Condition slug"),
    comments_file: str = typer.Argument(..., help="Path to comments file"),
    doc_type: str = typer.Option("evidence_based_protocol", "--doc-type", "-d"),
    tier: str = typer.Option("fellow"),
    force: bool = typer.Option(False, "--force", help="Force past manual approval requirements"),
):
    """Apply reviewer comments and regenerate the document."""
    from ..knowledge.revision.parser import ingest_from_text, ingest_from_json
    from ..knowledge.revision.engine import RevisionEngine

    path = Path(comments_file)
    if path.suffix == ".json":
        comments = ingest_from_json(path)
    else:
        text = path.read_text()
        comments = ingest_from_text(text, f"review-{condition}", condition, doc_type, tier)

    engine = RevisionEngine()
    result = engine.review_and_regenerate(
        document_id=f"review-{condition}",
        condition=condition,
        blueprint=doc_type,
        tier=tier,
        comments=comments,
        force=force,
    )

    if result.success:
        typer.echo(typer.style(f"\nRegenerated: {result.output_path}", fg=typer.colors.GREEN))
        typer.echo(result.to_text())
    else:
        typer.echo(typer.style(f"\nFailed: {result.error}", fg=typer.colors.RED))


@app.command("promotion-detect")
def promotion_detect_cmd():
    """Detect reusable override patterns from revision history."""
    from ..knowledge.revision.promotion import PromotionEngine
    engine = PromotionEngine()
    candidates = engine.detect_candidates()
    if not candidates:
        typer.echo("No promotion candidates detected.")
        return
    typer.echo(f"Found {len(candidates)} candidates:")
    for c in candidates:
        ev = " [EVIDENCE]" if c.evidence_sensitive else ""
        typer.echo(f"  [{c.candidate_id}] {c.pattern_summary} (×{c.repeat_count}, conf={c.confidence:.0%}){ev}")


@app.command("promotion-propose")
def promotion_propose_cmd(
    candidate_id: str = typer.Argument(..., help="Candidate ID from detection"),
    change: str = typer.Option("", help="Proposed change description"),
):
    """Create a promotion proposal from a detected candidate."""
    from ..knowledge.revision.promotion import PromotionEngine
    engine = PromotionEngine()
    candidates = engine.detect_candidates()
    match = next((c for c in candidates if c.candidate_id == candidate_id), None)
    if not match:
        typer.echo(typer.style(f"Candidate not found: {candidate_id}", fg=typer.colors.RED))
        return
    proposal = engine.create_proposal(match, proposed_change=change)
    engine._save_proposal(proposal)
    typer.echo(proposal.to_text())


@app.command("promotion-list")
def promotion_list_cmd():
    """List all promotion proposals."""
    from ..knowledge.revision.promotion import PromotionEngine
    engine = PromotionEngine()
    proposals = engine.list_proposals()
    if not proposals:
        typer.echo("No promotion proposals.")
        return
    for p in proposals:
        typer.echo(f"  [{p.get('status', '?')}] {p.get('proposal_id', '?')}: {p.get('proposed_change_summary', '')[:60]}")


@app.command("docx-review-ingest")
def docx_review_ingest_cmd(
    docx_file: str = typer.Argument(..., help="Path to reviewed DOCX with Word comments"),
    condition: str = typer.Option("", help="Condition slug (auto-detect if empty)"),
    doc_type: str = typer.Option("evidence_based_protocol", "--doc-type", "-d"),
    tier: str = typer.Option("fellow"),
):
    """Extract and map reviewer comments from a Word DOCX file."""
    from ..knowledge.revision.docx_comments import (
        extract_docx_comments, map_comments_to_sections, docx_comments_to_review_set
    )

    # Extract
    result = extract_docx_comments(docx_file)
    if not result.comments:
        typer.echo("No comments found in DOCX.")
        return

    # Map to sections
    prov_path = Path(docx_file).with_suffix(".provenance.json")
    result = map_comments_to_sections(result, prov_path if prov_path.exists() else None)
    typer.echo(result.to_text())

    # Convert to review comments
    review_set = docx_comments_to_review_set(result, condition, doc_type, tier)
    typer.echo(f"\nConverted {len(review_set.comments)} comments to review pipeline format.")


@app.command("docx-review-regenerate")
def docx_review_regenerate_cmd(
    docx_file: str = typer.Argument(..., help="Path to reviewed DOCX"),
    condition: str = typer.Argument(..., help="Condition slug"),
    doc_type: str = typer.Option("evidence_based_protocol", "--doc-type", "-d"),
    tier: str = typer.Option("fellow"),
    force: bool = typer.Option(False, "--force"),
):
    """Extract DOCX comments and regenerate the document."""
    from ..knowledge.revision.docx_comments import (
        extract_docx_comments, map_comments_to_sections, docx_comments_to_review_set
    )
    from ..knowledge.revision.engine import RevisionEngine

    # Extract and map
    result = extract_docx_comments(docx_file)
    result = map_comments_to_sections(result)
    review_set = docx_comments_to_review_set(result, condition, doc_type, tier)

    if not review_set.comments:
        typer.echo("No comments to apply.")
        return

    # Regenerate
    engine = RevisionEngine()
    regen = engine.review_and_regenerate(
        document_id=f"docx-review-{condition}",
        condition=condition,
        blueprint=doc_type,
        tier=tier,
        comments=review_set,
        force=force,
    )

    if regen.success:
        typer.echo(typer.style(f"\nRegenerated: {regen.output_path}", fg=typer.colors.GREEN))
        typer.echo(regen.to_text())
    else:
        typer.echo(typer.style(f"\nFailed: {regen.error}", fg=typer.colors.RED))


@app.command("docx-review-unresolved")
def docx_review_unresolved_cmd(
    docx_file: str = typer.Argument(..., help="Path to reviewed DOCX"),
):
    """Show DOCX comments that need manual resolution."""
    from ..knowledge.revision.docx_comments import extract_docx_comments, map_comments_to_sections
    from ..knowledge.revision.resolution import ResolutionManager

    result = extract_docx_comments(docx_file)
    result = map_comments_to_sections(result)
    mgr = ResolutionManager()
    typer.echo(mgr.summary(result))


@app.command("docx-review-resolve")
def docx_review_resolve_cmd(
    docx_file: str = typer.Argument(..., help="Path to reviewed DOCX"),
    comment_id: str = typer.Option(..., "--comment", "-c", help="Comment ID to resolve"),
    section: str = typer.Option("", "--section", "-s", help="Target section slug"),
    target_kind: str = typer.Option("section", "--kind", help="section/document_general/visual/table/blocked"),
    by: str = typer.Option("operator", "--by", help="Resolver name"),
    notes: str = typer.Option("", "--notes"),
):
    """Manually resolve an ambiguous DOCX comment mapping."""
    from ..knowledge.revision.resolution import ResolutionManager

    mgr = ResolutionManager()
    decision = mgr.resolve(
        comment_id=comment_id,
        section_slug=section,
        target_kind=target_kind,
        decided_by=by,
        notes=notes,
    )
    typer.echo(typer.style(f"Resolved: {comment_id} → {target_kind}:{section}", fg=typer.colors.GREEN))


@app.command("docx-review-candidates")
def docx_review_candidates_cmd(
    docx_file: str = typer.Argument(..., help="Path to reviewed DOCX"),
):
    """Show ranked mapping candidates for each DOCX comment."""
    from ..knowledge.revision.docx_comments import extract_docx_comments, map_comments_to_sections
    from ..knowledge.revision.resolution import ResolutionManager

    result = extract_docx_comments(docx_file)
    result = map_comments_to_sections(result)
    mgr = ResolutionManager()

    for c in result.comments:
        candidates = mgr.get_candidates(c)
        state = c.mapping_state
        typer.echo(f"\n[{state}] {c.text[:60]}")
        typer.echo(f"  Comment ID: {c.comment_id}")
        for i, cand in enumerate(candidates[:5]):
            marker = " ← top" if i == 0 and cand.section_slug != "(document_general)" else ""
            typer.echo(f"  {i+1}. {cand.section_slug} (score: {cand.score:.1f}, conf: {cand.confidence:.0%}){marker}")
            if cand.explanation:
                typer.echo(f"     {cand.explanation[:80]}")


@app.command("cockpit")
def cockpit_cmd():
    """Show platform-wide operational overview."""
    from ..knowledge.cockpit import CockpitService
    svc = CockpitService()
    typer.echo(svc.overview().to_text())


@app.command("cockpit-conditions")
def cockpit_conditions_cmd():
    """Show per-condition operational summary."""
    from ..knowledge.cockpit import CockpitService
    svc = CockpitService()

    typer.echo(typer.style(
        f"{'Condition':<18} {'Ready':>6} {'Review':>7} {'Incomplete':>10} {'PMIDs':>6}",
        fg=typer.colors.CYAN,
    ))
    typer.echo("-" * 55)
    for cs in svc.conditions_summary():
        typer.echo(f"  {cs.condition:<18} {cs.ready:>4}   {cs.review_required:>5}   {cs.incomplete:>8}   {cs.total_pmids:>5}")


@app.command("cockpit-blockers")
def cockpit_blockers_cmd():
    """Show all release blockers across the platform."""
    from ..knowledge.cockpit import CockpitService
    svc = CockpitService()
    blockers = svc.blockers()
    if not blockers:
        typer.echo(typer.style("No blockers — all documents are release-ready!", fg=typer.colors.GREEN))
        return
    typer.echo(f"Total blockers: {len(blockers)}")
    for b in blockers[:20]:
        typer.echo(f"  [{b.blocker_type}] {b.condition}/{b.doc_type}/{b.tier}: {b.summary}")
    if len(blockers) > 20:
        typer.echo(f"  ... and {len(blockers) - 20} more")


@app.command("cockpit-pack")
def cockpit_pack_cmd(
    condition: str = typer.Argument(...),
    tier: str = typer.Option("fellow"),
):
    """Show release pack summary for a condition/tier."""
    from ..knowledge.cockpit import CockpitService
    svc = CockpitService()
    pack = svc.pack_summary(condition, tier)

    status = typer.style("RELEASE READY", fg=typer.colors.GREEN) if pack["release_ready"] else typer.style("NOT READY", fg=typer.colors.YELLOW)
    typer.echo(f"\n{condition.upper()} ({tier}) — {status}")
    typer.echo(f"  Total docs: {pack['total']}")
    typer.echo(f"  Ready: {pack['ready']}")
    if pack["ready_docs"]:
        typer.echo(f"  Ready docs: {', '.join(pack['ready_docs'])}")
    if pack["blocked_docs"]:
        typer.echo(f"  Blocked:")
        for bd in pack["blocked_docs"]:
            typer.echo(f"    {bd['doc_type']}: {bd['reason']} ({bd['placeholders']} placeholders)")


@app.command("release-create")
def release_create_cmd(
    condition: str = typer.Argument(...),
    tier: str = typer.Option("fellow"),
    by: str = typer.Option("operator", "--by"),
):
    """Create a draft release for a condition/tier pack."""
    from ..knowledge.publish import ReleaseService
    svc = ReleaseService()
    release = svc.create_release(condition, tier, created_by=by)
    typer.echo(release.to_text())


@app.command("release-approve")
def release_approve_cmd(
    release_id: str = typer.Argument(...),
    by: str = typer.Option(..., "--by"),
    notes: str = typer.Option("", "--notes"),
):
    """Approve a release for publication."""
    from ..knowledge.publish import ReleaseService
    svc = ReleaseService()
    release = svc.approve(release_id, by, notes)
    typer.echo(typer.style(f"Approved: {release_id}", fg=typer.colors.GREEN))


@app.command("release-publish")
def release_publish_cmd(
    release_id: str = typer.Argument(...),
):
    """Publish an approved release (generate bundle)."""
    from ..knowledge.publish import ReleaseService
    svc = ReleaseService()
    release = svc.publish(release_id)
    typer.echo(typer.style(f"Published: {release.bundle_path}", fg=typer.colors.GREEN))
    typer.echo(release.to_text())


@app.command("release-list")
def release_list_cmd():
    """List all releases."""
    from ..knowledge.publish import ReleaseService
    svc = ReleaseService()
    releases = svc.list_releases()
    if not releases:
        typer.echo("No releases.")
        return
    for r in releases:
        typer.echo(f"  [{r.get('state', '?')}] {r.get('release_id', '?')}: {r.get('scope', '?')} ({r.get('included', 0)} docs)")


if __name__ == "__main__":
    app()
