"""Job manager — creates, tracks, and persists jobs."""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from .models import Job, JobStatus, JobPlan
from .workspace import JobWorkspace

logger = logging.getLogger(__name__)

class JobManager:
    def __init__(self, jobs_dir: Path, workspaces_dir: Path = None):
        self.jobs_dir = Path(jobs_dir)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.workspaces_dir = Path(workspaces_dir or self.jobs_dir / "workspaces")
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)

    def create_job(self, source_prompt: str = "", created_by: str = "",
                   target_conditions: list[str] = None, target_doc_types: list[str] = None,
                   target_tiers: list[str] = None, uploaded_files: list[str] = None,
                   template_ref: str = "", doctor_comments: list[str] = None) -> Job:
        job_id = f"job-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        job = Job(
            job_id=job_id, created_by=created_by, source_prompt=source_prompt,
            target_conditions=target_conditions or [], target_doc_types=target_doc_types or [],
            target_tiers=target_tiers or ["fellow", "partners"],
            uploaded_files=uploaded_files or [], template_ref=template_ref,
            doctor_comments=doctor_comments or [],
        )
        # Create workspace
        ws = JobWorkspace(self.workspaces_dir, job_id)
        ws.create()
        job.workspace_path = str(ws.root)
        self._save_job(job)
        logger.info("Created job %s", job_id)
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        path = self.jobs_dir / f"{job_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Job.from_dict(data)

    def update_status(self, job_id: str, status: JobStatus, **kwargs) -> Job:
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        job.status = status
        job.updated_at = datetime.now(timezone.utc).isoformat()
        for k, v in kwargs.items():
            if hasattr(job, k):
                setattr(job, k, v)
        self._save_job(job)
        return job

    def add_artifact(self, job_id: str, artifact: dict) -> Job:
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        job.artifacts.append(artifact)
        self._save_job(job)
        return job

    def add_error(self, job_id: str, error: str) -> None:
        job = self.get_job(job_id)
        if job:
            job.errors.append(error)
            self._save_job(job)

    def list_jobs(self, status: str = None) -> list[Job]:
        jobs = []
        for p in sorted(self.jobs_dir.glob("job-*.json"), reverse=True):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                job = Job.from_dict(data)
                if status and job.status.value != status:
                    continue
                jobs.append(job)
            except Exception:
                pass
        return jobs

    def get_workspace(self, job_id: str) -> JobWorkspace:
        return JobWorkspace(self.workspaces_dir, job_id)

    def _save_job(self, job: Job) -> None:
        path = self.jobs_dir / f"{job.job_id}.json"
        path.write_text(json.dumps(job.to_dict(), indent=2, default=str), encoding="utf-8")
