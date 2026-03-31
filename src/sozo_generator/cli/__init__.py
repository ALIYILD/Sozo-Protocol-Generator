"""SOZO Generator CLI package."""

try:
    from .build_condition import build_app
    from .build_all import build_all_app
    from .ingest_evidence import evidence_app
    from .extract_template import extract_app
    from .qa_report import qa_app
    from .render_visuals import visuals_app
    from .main import app

    __all__ = [
        "app",
        "build_app",
        "build_all_app",
        "evidence_app",
        "extract_app",
        "qa_app",
        "visuals_app",
    ]
except ImportError:
    # Allow partial imports during development
    pass
