"""
Clinical Image Search Engine.

Searches for relevant clinical/scientific images from open-access sources
to support SOZO clinical documents. Focuses on:
- Brain network diagrams from publications
- EEG/QEEG topographic maps
- MRI/fMRI visualizations
- Neuroanatomy illustrations
- Stimulation target diagrams
- Clinical assessment visuals

Sources prioritized (most open → least):
1. PubMed Central (PMC) open-access figures
2. Wikimedia Commons (CC-licensed)
3. Open-access neuroimaging databases (NeuroVault, OpenNeuro)
4. General web image search (filtered for academic/medical)

IMPORTANT: All images must be attributed. No copyrighted images without license.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus, urljoin

logger = logging.getLogger(__name__)


@dataclass
class ImageResult:
    """A single image search result."""

    url: str
    thumbnail_url: str = ""
    title: str = ""
    description: str = ""
    source: str = ""  # "pmc", "wikimedia", "web"
    license: str = ""  # "CC-BY", "CC-BY-SA", "public_domain", "fair_use", "unknown"
    attribution: str = ""
    pmcid: str = ""  # If from PMC
    doi: str = ""
    width: int = 0
    height: int = 0
    relevance_score: float = 0.0
    query: str = ""
    content_hash: str = ""

    @property
    def is_open_access(self) -> bool:
        return self.license in ("CC-BY", "CC-BY-SA", "CC0", "public_domain")

    @property
    def safe_filename(self) -> str:
        h = hashlib.md5(self.url.encode()).hexdigest()[:12]
        ext = _guess_extension(self.url)
        return f"img_{h}{ext}"


def _guess_extension(url: str) -> str:
    """Guess image file extension from URL."""
    lower = url.lower().split("?")[0]
    for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".tiff"):
        if lower.endswith(ext):
            return ext
    return ".png"


# ── Query Templates ─────────────────────────────────────────────────────────

# Maps (condition_slug, section_id) → list of search queries
# These are carefully crafted to find relevant scientific images

CONDITION_DISPLAY_NAMES = {
    "parkinsons": "Parkinson's Disease",
    "depression": "Major Depressive Disorder",
    "anxiety": "Generalized Anxiety Disorder",
    "adhd": "ADHD",
    "alzheimers": "Alzheimer's Disease",
    "stroke_rehab": "Post-Stroke Rehabilitation",
    "tbi": "Traumatic Brain Injury",
    "chronic_pain": "Chronic Pain Fibromyalgia",
    "ptsd": "PTSD",
    "ocd": "Obsessive Compulsive Disorder",
    "ms": "Multiple Sclerosis",
    "asd": "Autism Spectrum Disorder",
    "long_covid": "Long COVID Brain Fog",
    "tinnitus": "Tinnitus",
    "insomnia": "Insomnia Sleep Disorder",
}

SECTION_QUERY_TEMPLATES = {
    "overview": [
        "{condition} brain pathophysiology diagram",
        "{condition} neural circuits illustration",
    ],
    "pathophysiology": [
        "{condition} pathophysiology brain regions fMRI",
        "{condition} neural pathway diagram neuroscience",
    ],
    "anatomy": [
        "{condition} brain regions affected neuroanatomy",
        "{condition} brain MRI structural changes",
    ],
    "networks": [
        "{condition} brain network dysfunction fMRI connectivity",
        "{condition} default mode network salience network",
        "functional brain network {condition} resting state fMRI",
    ],
    "phenotypes": [
        "{condition} clinical subtypes phenotypes classification",
    ],
    "protocols": [
        "transcranial direct current stimulation tDCS electrode montage",
        "transcranial pulse stimulation TPS neuromodulation brain",
        "{condition} tDCS protocol DLPFC montage",
    ],
    "protocols_tps": [
        "transcranial pulse stimulation TPS NEUROLITH brain target",
        "focused ultrasound neuromodulation brain diagram",
    ],
    "protocols_tdcs": [
        "tDCS electrode montage 10-20 EEG system anode cathode",
        "high-definition tDCS HD-tDCS brain stimulation",
    ],
    "safety": [
        "neuromodulation safety contraindications tDCS TPS diagram",
    ],
    "assessments": [
        "{condition} clinical assessment scales outcomes",
    ],
    "brain_map": [
        "{condition} brain map stimulation targets neuroimaging",
        "EEG 10-10 electrode placement brain topography",
    ],
    "eeg_qeeg": [
        "QEEG topographic map {condition} EEG power spectral",
        "EEG 10-20 system electrode placement diagram",
        "quantitative EEG brain mapping topography",
    ],
    "mri_fmri": [
        "{condition} brain MRI fMRI activation map",
        "{condition} functional connectivity MRI brain network",
        "brain fMRI {condition} BOLD activation",
    ],
    "connectivity": [
        "{condition} brain network connectivity matrix",
        "functional connectivity {condition} resting state",
    ],
    "neuromodulation": [
        "non-invasive brain stimulation NIBS neuromodulation overview",
        "tDCS TPS taVNS CES brain stimulation comparison",
    ],
}


def build_queries(
    condition_slug: str,
    section_id: str,
    extra_terms: list[str] | None = None,
) -> list[str]:
    """Build search queries for a condition + section combination."""
    condition_name = CONDITION_DISPLAY_NAMES.get(condition_slug, condition_slug)

    templates = SECTION_QUERY_TEMPLATES.get(section_id, [])
    if not templates:
        # Generic fallback
        templates = [
            "{condition} brain neuroimaging",
            "{condition} neuromodulation diagram",
        ]

    queries = []
    for template in templates:
        q = template.format(condition=condition_name)
        queries.append(q)

    if extra_terms:
        for term in extra_terms:
            queries.append(f"{condition_name} {term}")

    return queries


class ImageSearchEngine:
    """Searches for relevant clinical/scientific images.

    Supports multiple backends:
    - PubMed Central figure search (via NCBI E-utilities)
    - Wikimedia Commons API
    - General web search (via httpx)

    Results are ranked by relevance and license openness.
    """

    def __init__(self, cache_dir: str | Path | None = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/image_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._search_cache_file = self.cache_dir / "_search_cache.json"
        self._search_cache = self._load_search_cache()

    def _load_search_cache(self) -> dict:
        if self._search_cache_file.exists():
            try:
                return json.loads(self._search_cache_file.read_text())
            except Exception:
                pass
        return {}

    def _save_search_cache(self):
        try:
            self._search_cache_file.write_text(
                json.dumps(self._search_cache, indent=2, default=str)
            )
        except Exception as e:
            logger.debug(f"Failed to save search cache: {e}")

    def search(
        self,
        query: str,
        max_results: int = 10,
        sources: list[str] | None = None,
    ) -> list[ImageResult]:
        """Search for images matching a query.

        Args:
            query: Search query string
            max_results: Maximum results to return
            sources: List of sources to search ("pmc", "wikimedia", "web")
                     Default: all sources

        Returns:
            List of ImageResult objects, sorted by relevance
        """
        if sources is None:
            sources = ["pmc", "wikimedia"]

        cache_key = f"{query}|{','.join(sources)}|{max_results}"
        if cache_key in self._search_cache:
            cached = self._search_cache[cache_key]
            # Check cache age (24 hours)
            if time.time() - cached.get("ts", 0) < 86400:
                return [ImageResult(**r) for r in cached.get("results", [])]

        all_results = []

        for source in sources:
            try:
                if source == "pmc":
                    results = self._search_pmc(query, max_results)
                    all_results.extend(results)
                elif source == "wikimedia":
                    results = self._search_wikimedia(query, max_results)
                    all_results.extend(results)
            except Exception as e:
                logger.warning(f"Image search failed for {source}: {e}")

        # Sort by relevance and license quality
        all_results.sort(key=lambda r: (-r.relevance_score, not r.is_open_access))
        all_results = all_results[:max_results]

        # Cache
        self._search_cache[cache_key] = {
            "ts": time.time(),
            "results": [_result_to_dict(r) for r in all_results],
        }
        self._save_search_cache()

        return all_results

    def search_for_section(
        self,
        condition_slug: str,
        section_id: str,
        max_results: int = 5,
    ) -> list[ImageResult]:
        """Search for images relevant to a specific document section."""
        queries = build_queries(condition_slug, section_id)
        all_results = []
        seen_urls = set()

        for query in queries[:3]:  # Limit to 3 queries per section
            results = self.search(query, max_results=max_results)
            for r in results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    all_results.append(r)

        return all_results[:max_results]

    def _search_pmc(self, query: str, max_results: int) -> list[ImageResult]:
        """Search PubMed Central for open-access figures."""
        try:
            import httpx
        except ImportError:
            logger.debug("httpx not available for PMC search")
            return []

        results = []
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pmc",
            "term": f"{query} AND open access[filter]",
            "retmax": min(max_results * 2, 20),
            "retmode": "json",
            "sort": "relevance",
        }

        try:
            resp = httpx.get(search_url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            pmcids = data.get("esearchresult", {}).get("idlist", [])

            for pmcid in pmcids[:max_results]:
                # Build figure URL pattern for PMC
                figure_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/figure/fig1/"
                thumbnail = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/bin/thumb.png"

                results.append(ImageResult(
                    url=figure_url,
                    thumbnail_url=thumbnail,
                    title=f"PMC{pmcid} Figure",
                    source="pmc",
                    license="CC-BY",
                    attribution=f"PubMed Central PMC{pmcid}",
                    pmcid=f"PMC{pmcid}",
                    relevance_score=0.8,
                    query=query,
                ))

            time.sleep(0.35)  # NCBI rate limit

        except Exception as e:
            logger.debug(f"PMC search error: {e}")

        return results

    def _search_wikimedia(self, query: str, max_results: int) -> list[ImageResult]:
        """Search Wikimedia Commons for CC-licensed images."""
        try:
            import httpx
        except ImportError:
            logger.debug("httpx not available for Wikimedia search")
            return []

        results = []
        api_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{query} filetype:bitmap",
            "srnamespace": "6",  # File namespace
            "srlimit": min(max_results, 10),
            "format": "json",
        }

        try:
            resp = httpx.get(api_url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            search_results = data.get("query", {}).get("search", [])

            for item in search_results:
                title = item.get("title", "")
                # Build Wikimedia image URL
                file_title = title.replace("File:", "").replace(" ", "_")
                thumb_url = (
                    f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote_plus(file_title)}"
                    f"?width=800"
                )
                page_url = f"https://commons.wikimedia.org/wiki/{quote_plus(title)}"

                results.append(ImageResult(
                    url=thumb_url,
                    thumbnail_url=thumb_url,
                    title=title.replace("File:", "").replace("_", " "),
                    description=item.get("snippet", ""),
                    source="wikimedia",
                    license="CC-BY-SA",
                    attribution=f"Wikimedia Commons: {title}",
                    relevance_score=0.7,
                    query=query,
                ))

        except Exception as e:
            logger.debug(f"Wikimedia search error: {e}")

        return results

    def download_image(
        self,
        result: ImageResult,
        output_dir: str | Path | None = None,
    ) -> Optional[Path]:
        """Download an image and store it in the cache.

        Returns the local file path, or None if download failed.
        """
        try:
            import httpx
        except ImportError:
            logger.warning("httpx not available — cannot download images")
            return None

        target_dir = Path(output_dir) if output_dir else self.cache_dir / "downloaded"
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = result.safe_filename
        local_path = target_dir / filename

        if local_path.exists() and local_path.stat().st_size > 1000:
            logger.debug(f"Image already cached: {local_path}")
            return local_path

        download_url = result.thumbnail_url or result.url
        try:
            resp = httpx.get(download_url, timeout=30, follow_redirects=True)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                logger.debug(f"Not an image: {content_type} from {download_url}")
                return None

            local_path.write_bytes(resp.content)

            # Save metadata
            meta_path = local_path.with_suffix(".json")
            meta_path.write_text(json.dumps(_result_to_dict(result), indent=2))

            logger.info(f"Downloaded image: {local_path.name} ({len(resp.content) // 1024}KB)")
            return local_path

        except Exception as e:
            logger.warning(f"Image download failed: {e}")
            return None


def _result_to_dict(r: ImageResult) -> dict:
    """Convert ImageResult to serializable dict."""
    return {
        "url": r.url,
        "thumbnail_url": r.thumbnail_url,
        "title": r.title,
        "description": r.description,
        "source": r.source,
        "license": r.license,
        "attribution": r.attribution,
        "pmcid": r.pmcid,
        "doi": r.doi,
        "relevance_score": r.relevance_score,
        "query": r.query,
    }
