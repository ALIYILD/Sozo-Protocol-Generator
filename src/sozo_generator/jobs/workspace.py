"""Job workspace — controlled folder structure for agent artifacts."""
from __future__ import annotations
import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

WORKSPACE_FOLDERS = [
    "input", "parsed_template", "content_matches", "evidence",
    "drafts", "revisions", "qa", "reports", "exports", "logs",
]

@dataclass
class ArtifactEntry:
    """A registered artifact in the workspace."""
    artifact_id: str = ""
    artifact_type: str = ""  # template, draft, evidence, qa_report, export, log
    file_path: str = ""
    created_by: str = ""  # agent name
    created_at: str = ""
    metadata: dict = field(default_factory=dict)

class JobWorkspace:
    """Managed workspace for a single job."""

    def __init__(self, base_dir: Path, job_id: str):
        self.base_dir = Path(base_dir)
        self.job_id = job_id
        self.root = self.base_dir / job_id
        self._manifest_path = self.root / "manifest.json"
        self._artifacts: list[ArtifactEntry] = []

    def create(self) -> Path:
        """Create workspace with standard folder structure."""
        for folder in WORKSPACE_FOLDERS:
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        self._save_manifest()
        logger.info("Created workspace: %s", self.root)
        return self.root

    def get_folder(self, name: str) -> Path:
        """Get path to a workspace subfolder."""
        folder = self.root / name
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def register_artifact(self, artifact_type: str, file_path: str, created_by: str, metadata: dict = None) -> ArtifactEntry:
        """Register an artifact in the manifest."""
        entry = ArtifactEntry(
            artifact_id=f"art-{len(self._artifacts)+1:03d}",
            artifact_type=artifact_type,
            file_path=str(file_path),
            created_by=created_by,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self._artifacts.append(entry)
        self._save_manifest()
        return entry

    def list_artifacts(self, artifact_type: str = None) -> list[ArtifactEntry]:
        if artifact_type:
            return [a for a in self._artifacts if a.artifact_type == artifact_type]
        return list(self._artifacts)

    def write_file(self, subfolder: str, filename: str, content: str) -> Path:
        """Write a file to a workspace subfolder. Returns path."""
        folder = self.get_folder(subfolder)
        path = folder / filename
        path.write_text(content, encoding="utf-8")
        return path

    def read_file(self, subfolder: str, filename: str) -> Optional[str]:
        path = self.root / subfolder / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def write_log(self, agent_name: str, message: str) -> None:
        log_file = self.get_folder("logs") / f"{agent_name}.log"
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    def cleanup(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)

    def _save_manifest(self) -> None:
        import dataclasses
        data = {
            "job_id": self.job_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "artifacts": [dataclasses.asdict(a) for a in self._artifacts],
        }
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_manifest(self) -> None:
        if self._manifest_path.exists():
            data = json.loads(self._manifest_path.read_text(encoding="utf-8"))
            self._artifacts = [
                ArtifactEntry(**{k: v for k, v in a.items() if k in ArtifactEntry.__dataclass_fields__})
                for a in data.get("artifacts", [])
            ]
