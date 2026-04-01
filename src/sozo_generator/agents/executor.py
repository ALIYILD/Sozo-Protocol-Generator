"""Agent executor — runs agent tasks from a job plan in dependency order."""
from __future__ import annotations
import logging
from pathlib import Path
from ..jobs.models import Job, JobPlan, AgentTask, JobStatus
from ..jobs.manager import JobManager
from .registry import get_agent
from .base import AgentResult

logger = logging.getLogger(__name__)

class AgentExecutor:
    """Executes a job's agent tasks in dependency order."""

    def __init__(self, job_manager: JobManager):
        self.job_manager = job_manager

    def execute_job(self, job: Job, progress_callback=None) -> Job:
        """Execute all tasks in the job's plan."""
        if not job.plan:
            job.errors.append("No plan set")
            self.job_manager.update_status(job.job_id, JobStatus.FAILED, errors=job.errors)
            return job

        self.job_manager.update_status(job.job_id, JobStatus.RUNNING)
        workspace_path = job.workspace_path
        completed_tasks = set()
        task_outputs = {}

        for task in job.plan.tasks:
            # Check dependencies
            unmet = [d for d in task.depends_on if d not in completed_tasks]
            if unmet:
                # Check if deps failed
                failed_deps = [d for d in unmet if any(t.task_id == d and t.status == "failed" for t in job.plan.tasks)]
                if failed_deps:
                    task.status = "skipped"
                    task.error = f"Skipped due to failed dependencies: {failed_deps}"
                    continue

            agent = get_agent(task.agent_name)
            if not agent:
                task.status = "failed"
                task.error = f"Agent '{task.agent_name}' not found"
                job.warnings.append(task.error)
                continue

            if progress_callback:
                progress_callback(f"Running {agent.name}...")

            # Merge upstream outputs into input
            merged_input = dict(task.input_data)
            for dep_id in task.depends_on:
                if dep_id in task_outputs:
                    merged_input[f"upstream_{dep_id}"] = task_outputs[dep_id]

            # Execute with retry
            result = None
            for attempt in range(task.max_attempts):
                task.attempts = attempt + 1
                try:
                    from datetime import datetime, timezone
                    task.started_at = datetime.now(timezone.utc).isoformat()
                    result = agent.execute(merged_input, workspace_path, job=job)
                    task.completed_at = datetime.now(timezone.utc).isoformat()
                    break
                except Exception as e:
                    logger.warning("Agent %s attempt %d failed: %s", agent.name, attempt+1, e)
                    if attempt + 1 >= task.max_attempts:
                        result = AgentResult(success=False, error=str(e))

            if result and result.success:
                task.status = "completed"
                task.output_data = result.output_data
                task.artifacts = [str(a.get("path", "")) for a in result.artifacts]
                task_outputs[task.task_id] = result.output_data
                completed_tasks.add(task.task_id)
                # Register artifacts to job
                for art in result.artifacts:
                    job.artifacts.append({**art, "agent": agent.name, "task_id": task.task_id})
                job.warnings.extend(result.warnings)
            else:
                task.status = "failed"
                task.error = result.error if result else "Unknown error"
                job.errors.append(f"{agent.name}: {task.error}")

        # Determine final status
        all_completed = all(t.status in ("completed", "skipped") for t in job.plan.tasks)
        any_failed = any(t.status == "failed" for t in job.plan.tasks)

        if all_completed and not any_failed:
            final_status = JobStatus.AWAITING_REVIEW
        elif any_failed:
            # Check if we got partial results
            if any(t.status == "completed" for t in job.plan.tasks):
                final_status = JobStatus.AWAITING_REVIEW
                job.warnings.append("Partial completion — some agents failed")
            else:
                final_status = JobStatus.FAILED
        else:
            final_status = JobStatus.COMPLETED

        # Count documents
        job.total_documents = sum(1 for a in job.artifacts if a.get("type") == "document")

        self.job_manager.update_status(
            job.job_id, final_status,
            artifacts=job.artifacts, errors=job.errors, warnings=job.warnings,
            total_documents=job.total_documents, plan=job.plan,
        )
        return self.job_manager.get_job(job.job_id)
