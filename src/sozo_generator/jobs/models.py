"""Job models — core data structures for job orchestration."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any
from enum import Enum

class JobStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    PLANNING = "planning"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    BLOCKED = "blocked"

@dataclass
class AgentTask:
    """A single task assigned to an agent within a job."""
    task_id: str = ""
    agent_name: str = ""
    status: str = "pending"  # pending, running, completed, failed, skipped
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)  # paths to artifacts
    error: str = ""
    started_at: str = ""
    completed_at: str = ""
    attempts: int = 0
    max_attempts: int = 2
    depends_on: list[str] = field(default_factory=list)  # task_ids this depends on

@dataclass
class JobPlan:
    """Execution plan for a job — ordered list of agent tasks."""
    tasks: list[AgentTask] = field(default_factory=list)
    parallel_groups: list[list[str]] = field(default_factory=list)  # task_ids that can run in parallel

@dataclass
class Job:
    """A document generation/revision job."""
    job_id: str = ""
    status: JobStatus = JobStatus.CREATED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = ""
    created_by: str = ""
    # Request
    source_prompt: str = ""
    uploaded_files: list[str] = field(default_factory=list)
    template_ref: str = ""
    target_conditions: list[str] = field(default_factory=list)
    target_doc_types: list[str] = field(default_factory=list)
    target_tiers: list[str] = field(default_factory=list)
    doctor_comments: list[str] = field(default_factory=list)
    # Execution
    plan: Optional[JobPlan] = None
    active_agents: list[str] = field(default_factory=list)
    workspace_path: str = ""
    # Results
    artifacts: list[dict] = field(default_factory=list)  # [{type, path, agent, timestamp}]
    evidence_bundle_refs: list[str] = field(default_factory=list)
    qa_results: list[dict] = field(default_factory=list)
    review_state_summary: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # Completion
    completion_summary: dict = field(default_factory=dict)
    total_documents: int = 0
    total_passed_qa: int = 0

    def to_dict(self) -> dict:
        import dataclasses
        d = dataclasses.asdict(self)
        d['status'] = self.status.value
        if self.plan:
            d['plan'] = dataclasses.asdict(self.plan)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Job:
        data = dict(data)
        data['status'] = JobStatus(data.get('status', 'created'))
        plan_data = data.pop('plan', None)
        if plan_data and isinstance(plan_data, dict):
            tasks = [AgentTask(**t) for t in plan_data.get('tasks', [])]
            data['plan'] = JobPlan(tasks=tasks, parallel_groups=plan_data.get('parallel_groups', []))
        else:
            data['plan'] = None
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
