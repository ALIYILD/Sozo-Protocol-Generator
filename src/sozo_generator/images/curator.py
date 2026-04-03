"""
Image Curator — selects and manages images for clinical documents.

The curator:
1. Determines which document sections need supporting images
2. Searches for relevant images via the search engine
3. Downloads and caches selected images
4. Builds an image manifest for each document build
5. Provides images to the DOCX renderer for insertion

Image selection priorities:
1. Pre-curated images in data/images/ (highest priority — manually vetted)
2. Previously cached images for this condition+section
3. Freshly searched images from PMC/Wikimedia (auto-fetched)
4. Platform-generated visuals as fallback

IMPORTANT: All external images include source attribution.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .search import ImageSearchEngine, ImageResult, build_queries

logger = logging.getLogger(__name__)

# ── Section → image need mapping ────────────────────────────────────────────
# Defines which sections benefit from supporting images and what to search for

SECTION_IMAGE_NEEDS = {
    "overview": {
        "description": "Condition overview illustration",
        "search_sections": ["overview"],
        "max_images": 1,
    },
    "pathophysiology": {
        "description": "Pathophysiology diagram or brain imaging",
        "search_sections": ["pathophysiology", "mri_fmri"],
        "max_images": 2,
    },
    "anatomy": {
        "description": "Brain region illustration or MRI",
        "search_sections": ["anatomy", "mri_fmri"],
        "max_images": 1,
    },
    "networks": {
        "description": "Brain network connectivity or fMRI",
        "search_sections": ["networks", "connectivity"],
        "max_images": 2,
    },
    "phenotypes": {
        "description": "Clinical phenotype classification",
        "search_sections": ["phenotypes"],
        "max_images": 1,
    },
    "protocols": {
        "description": "Stimulation protocol or montage diagram",
        "search_sections": ["protocols", "protocols_tdcs", "protocols_tps"],
        "max_images": 2,
    },
    "assessments": {
        "description": "Clinical assessment tools",
        "search_sections": ["assessments"],
        "max_images": 1,
    },
}


@dataclass
class CuratedImage:
    """An image selected for inclusion in a document."""

    local_path: Path
    caption: str
    attribution: str
    source: str  # "precurated", "cached", "searched", "generated"
    section_id: str
    condition_slug: str
    license: str = ""
    original_url: str = ""
    width_inches: float = 5.0


@dataclass
class DocumentImageManifest:
    """All images curated for one document build."""

    condition_slug: str
    document_type: str
    tier: str
    images: list[CuratedImage] = field(default_factory=list)

    def images_for_section(self, section_id: str) -> list[CuratedImage]:
        return [img for img in self.images if img.section_id == section_id]

    def to_dict(self) -> dict:
        return {
            "condition_slug": self.condition_slug,
            "document_type": self.document_type,
            "tier": self.tier,
            "images": [
                {
                    "local_path": str(img.local_path),
                    "caption": img.caption,
                    "attribution": img.attribution,
                    "source": img.source,
                    "section_id": img.section_id,
                    "license": img.license,
                    "original_url": img.original_url,
                }
                for img in self.images
            ],
        }


class ImageCurator:
    """Curates images for SOZO clinical documents.

    Usage:
        curator = ImageCurator()
        manifest = curator.curate_for_document(
            condition_slug="parkinsons",
            document_type="evidence_based_protocol",
            tier="partners",
        )
        for section_id in ["networks", "pathophysiology"]:
            images = manifest.images_for_section(section_id)
            for img in images:
                print(f"Insert {img.local_path} at section {section_id}")
    """

    def __init__(
        self,
        image_dir: str | Path | None = None,
        cache_dir: str | Path | None = None,
        enable_web_search: bool = True,
        max_images_per_section: int = 2,
    ):
        self.image_dir = Path(image_dir) if image_dir else Path("data/images")
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/image_cache")
        self.enable_web_search = enable_web_search
        self.max_per_section = max_images_per_section
        self._search_engine = None

    @property
    def search_engine(self) -> ImageSearchEngine:
        if self._search_engine is None:
            self._search_engine = ImageSearchEngine(cache_dir=self.cache_dir)
        return self._search_engine

    def curate_for_document(
        self,
        condition_slug: str,
        document_type: str,
        tier: str,
        sections: list[str] | None = None,
    ) -> DocumentImageManifest:
        """Curate images for all sections of a document.

        Args:
            condition_slug: Condition slug
            document_type: Document type value
            tier: "fellow" or "partners"
            sections: List of section IDs to curate for (None = all)

        Returns:
            DocumentImageManifest with all curated images
        """
        manifest = DocumentImageManifest(
            condition_slug=condition_slug,
            document_type=document_type,
            tier=tier,
        )

        target_sections = sections or list(SECTION_IMAGE_NEEDS.keys())

        for section_id in target_sections:
            need = SECTION_IMAGE_NEEDS.get(section_id)
            if not need:
                continue

            max_images = min(need["max_images"], self.max_per_section)
            images = self._curate_section(
                condition_slug=condition_slug,
                section_id=section_id,
                search_sections=need["search_sections"],
                description=need["description"],
                max_images=max_images,
            )
            manifest.images.extend(images)

        logger.info(
            f"Curated {len(manifest.images)} images for "
            f"{condition_slug}/{document_type}/{tier}"
        )
        return manifest

    def _curate_section(
        self,
        condition_slug: str,
        section_id: str,
        search_sections: list[str],
        description: str,
        max_images: int,
    ) -> list[CuratedImage]:
        """Curate images for a single section."""
        images = []

        # 1. Check pre-curated images
        precurated = self._find_precurated(condition_slug, section_id)
        images.extend(precurated[:max_images])
        if len(images) >= max_images:
            return images

        # 2. Check cached downloads
        cached = self._find_cached(condition_slug, section_id)
        for img in cached:
            if len(images) >= max_images:
                break
            if not any(i.local_path == img.local_path for i in images):
                images.append(img)
        if len(images) >= max_images:
            return images

        # 3. Web search (if enabled)
        if self.enable_web_search:
            remaining = max_images - len(images)
            searched = self._search_and_download(
                condition_slug, section_id, search_sections, remaining
            )
            images.extend(searched)

        return images[:max_images]

    def _find_precurated(
        self, condition_slug: str, section_id: str
    ) -> list[CuratedImage]:
        """Look for pre-curated images in data/images/<condition>/<section>/."""
        images = []
        search_dirs = [
            self.image_dir / condition_slug / section_id,
            self.image_dir / "shared" / section_id,
            self.image_dir / condition_slug,
        ]

        for d in search_dirs:
            if not d.exists():
                continue
            for f in sorted(d.iterdir()):
                if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".svg"):
                    # Look for companion .json metadata
                    meta = self._load_image_meta(f)
                    images.append(CuratedImage(
                        local_path=f,
                        caption=meta.get("caption", f"Figure: {f.stem}"),
                        attribution=meta.get("attribution", "SOZO Brain Center"),
                        source="precurated",
                        section_id=section_id,
                        condition_slug=condition_slug,
                        license=meta.get("license", "proprietary"),
                    ))

        return images

    def _find_cached(
        self, condition_slug: str, section_id: str
    ) -> list[CuratedImage]:
        """Look for previously downloaded images in cache."""
        images = []
        cache_section_dir = self.cache_dir / "downloaded" / condition_slug / section_id

        if not cache_section_dir.exists():
            return images

        for f in sorted(cache_section_dir.iterdir()):
            if f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                meta = self._load_image_meta(f)
                images.append(CuratedImage(
                    local_path=f,
                    caption=meta.get("caption", meta.get("title", f.stem)),
                    attribution=meta.get("attribution", ""),
                    source="cached",
                    section_id=section_id,
                    condition_slug=condition_slug,
                    license=meta.get("license", "unknown"),
                    original_url=meta.get("url", ""),
                ))

        return images

    def _search_and_download(
        self,
        condition_slug: str,
        section_id: str,
        search_sections: list[str],
        max_images: int,
    ) -> list[CuratedImage]:
        """Search web and download images for a section."""
        images = []
        download_dir = self.cache_dir / "downloaded" / condition_slug / section_id
        download_dir.mkdir(parents=True, exist_ok=True)

        for search_section in search_sections:
            if len(images) >= max_images:
                break

            try:
                results = self.search_engine.search_for_section(
                    condition_slug, search_section, max_results=3
                )

                for result in results:
                    if len(images) >= max_images:
                        break

                    # Prefer open-access
                    if not result.is_open_access:
                        continue

                    local_path = self.search_engine.download_image(
                        result, output_dir=download_dir
                    )
                    if local_path:
                        images.append(CuratedImage(
                            local_path=local_path,
                            caption=result.title or f"Figure: {section_id}",
                            attribution=result.attribution,
                            source="searched",
                            section_id=section_id,
                            condition_slug=condition_slug,
                            license=result.license,
                            original_url=result.url,
                        ))

            except Exception as e:
                logger.debug(f"Search failed for {search_section}: {e}")

        return images

    def _load_image_meta(self, image_path: Path) -> dict:
        """Load companion metadata JSON for an image."""
        meta_path = image_path.with_suffix(".json")
        if meta_path.exists():
            try:
                return json.loads(meta_path.read_text())
            except Exception:
                pass
        return {}

    def save_manifest(self, manifest: DocumentImageManifest, output_path: Path):
        """Save manifest to JSON for provenance tracking."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(manifest.to_dict(), indent=2))
        logger.debug(f"Image manifest saved: {output_path}")
