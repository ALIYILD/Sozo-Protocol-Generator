from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SozoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # NCBI / PubMed
    ncbi_email: str = Field(default="sozo@sozobraincenter.com", description="Email for NCBI Entrez")
    ncbi_api_key: str = Field(default="", description="NCBI API key for higher rate limits")

    # Output paths
    output_dir: Path = Field(default=Path("outputs/"), description="Base output directory")
    cache_dir: Path = Field(default=Path("data/raw/pubmed_cache/"), description="PubMed cache directory")
    conditions_dir: Path = Field(default=Path("data/processed/conditions/"), description="Processed condition data")
    evidence_dir: Path = Field(default=Path("data/processed/evidence/"), description="Evidence records")
    templates_dir: Path = Field(default=Path("templates/"), description="Document templates")
    visuals_dir: Path = Field(default=Path("outputs/visuals/"), description="Generated visuals")
    qa_dir: Path = Field(default=Path("outputs/qa/"), description="QA reports")

    # Generation flags
    with_visuals: bool = Field(default=True, description="Include visual diagrams in output")
    with_appendix: bool = Field(default=True, description="Include evidence appendix")
    strict_evidence: bool = Field(default=False, description="Fail generation if evidence is insufficient")
    review_mode: bool = Field(default=False, description="Add extra review flags and markers")
    force_refresh_evidence: bool = Field(default=False, description="Bypass cache and re-fetch PubMed data")

    # LLM adapter (optional, off by default)
    llm_adapter_enabled: bool = Field(default=False, alias="SOZO_LLM_ADAPTER_ENABLED")
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="", description="Anthropic API key for Claude-powered chat")

    # Multi-source search
    use_crossref: bool = Field(default=True, description="Enable Crossref search")
    use_semantic_scholar: bool = Field(default=True, description="Enable Semantic Scholar search")
    semantic_scholar_api_key: str = Field(default="", description="S2 API key for higher rate limits")

    # Research pipeline
    enable_research_pipeline: bool = Field(
        default=True,
        description="Use full PRISMA-style research pipeline for evidence",
    )
    pipeline_logs_dir: Path = Field(
        default=Path("data/evidence_pipeline_logs/"),
        description="Directory for PRISMA pipeline audit logs",
    )

    # Logging
    log_level: str = Field(default="INFO")

    # ── Phase 2 feature flags ────────────────────────────────────────
    enable_qa_blocking: bool = Field(
        default=False,
        description="When True, BLOCK-severity QA issues prevent document export",
    )
    enable_claim_tracing: bool = Field(
        default=True,
        description="Attach structured claim objects to generated sections",
    )
    enable_evidence_snapshots: bool = Field(
        default=True,
        description="Write versioned evidence snapshots alongside builds",
    )
    enable_build_manifests: bool = Field(
        default=True,
        description="Write build manifests for every export",
    )
    enable_reviewer_workflow: bool = Field(
        default=False,
        description="Track review state for generated documents",
    )
    snapshots_dir: Path = Field(
        default=Path("data/evidence_snapshots/"),
        description="Directory for versioned evidence snapshots",
    )
    manifests_dir: Path = Field(
        default=Path("outputs/manifests/"),
        description="Directory for build manifests",
    )
    reviews_dir: Path = Field(
        default=Path("outputs/reviews/"),
        description="Directory for review state files",
    )


def get_settings() -> SozoSettings:
    return SozoSettings()
