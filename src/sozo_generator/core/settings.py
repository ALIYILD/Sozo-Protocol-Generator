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

    # Logging
    log_level: str = Field(default="INFO")


def get_settings() -> SozoSettings:
    return SozoSettings()
