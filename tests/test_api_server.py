"""Tests for the FastAPI server module (import and structure tests)."""
import pytest


class TestAPIServerModule:
    def test_server_module_parses(self):
        """Server module should parse without FastAPI installed."""
        import ast
        from pathlib import Path
        code = Path("src/sozo_api/server.py").read_text()
        ast.parse(code)  # Must not raise

    def test_api_init_exists(self):
        from pathlib import Path
        assert Path("src/sozo_api/__init__.py").exists()

    def test_server_file_exists(self):
        from pathlib import Path
        assert Path("src/sozo_api/server.py").exists()


class TestAPIImports:
    def test_can_import_visuals_service(self):
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        assert len(svc.list_types()) >= 9

    def test_can_import_generation_service(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        assert svc is not None

    def test_can_import_cockpit_service(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        assert svc is not None

    def test_can_import_knowledge_base(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        assert len(kb.conditions) >= 16
