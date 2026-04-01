"""Tests for job orchestration and agent system."""
from __future__ import annotations
import pytest
from pathlib import Path


class TestJobModels:
    def test_job_creation(self):
        from sozo_generator.jobs.models import Job, JobStatus
        job = Job(job_id="test-1", source_prompt="Generate parkinsons docs")
        assert job.status == JobStatus.CREATED
        assert job.job_id == "test-1"

    def test_job_serialization_roundtrip(self):
        from sozo_generator.jobs.models import Job, JobStatus, JobPlan, AgentTask
        job = Job(
            job_id="test-2", status=JobStatus.RUNNING,
            target_conditions=["parkinsons"], target_doc_types=["handbook"],
            plan=JobPlan(tasks=[
                AgentTask(task_id="t1", agent_name="template_agent"),
                AgentTask(task_id="t2", agent_name="draft_agent", depends_on=["t1"]),
            ]),
        )
        data = job.to_dict()
        restored = Job.from_dict(data)
        assert restored.job_id == "test-2"
        assert restored.status == JobStatus.RUNNING
        assert len(restored.plan.tasks) == 2
        assert restored.plan.tasks[1].depends_on == ["t1"]

    def test_job_status_enum(self):
        from sozo_generator.jobs.models import JobStatus
        assert JobStatus.CREATED.value == "created"
        assert JobStatus.AWAITING_REVIEW.value == "awaiting_review"


class TestJobManager:
    def test_create_and_retrieve(self, tmp_path):
        from sozo_generator.jobs.manager import JobManager
        mgr = JobManager(tmp_path / "jobs")
        job = mgr.create_job(source_prompt="test", target_conditions=["parkinsons"])
        assert job.job_id.startswith("job-")
        retrieved = mgr.get_job(job.job_id)
        assert retrieved is not None
        assert retrieved.target_conditions == ["parkinsons"]

    def test_update_status(self, tmp_path):
        from sozo_generator.jobs.manager import JobManager
        from sozo_generator.jobs.models import JobStatus
        mgr = JobManager(tmp_path / "jobs")
        job = mgr.create_job(source_prompt="test")
        mgr.update_status(job.job_id, JobStatus.RUNNING)
        updated = mgr.get_job(job.job_id)
        assert updated.status == JobStatus.RUNNING

    def test_list_jobs(self, tmp_path):
        from sozo_generator.jobs.manager import JobManager
        import time
        mgr = JobManager(tmp_path / "jobs")
        mgr.create_job(source_prompt="j1")
        time.sleep(1.1)  # ensure different timestamps for job IDs
        mgr.create_job(source_prompt="j2")
        jobs = mgr.list_jobs()
        assert len(jobs) >= 2


class TestJobWorkspace:
    def test_create_workspace(self, tmp_path):
        from sozo_generator.jobs.workspace import JobWorkspace, WORKSPACE_FOLDERS
        ws = JobWorkspace(tmp_path, "job-test")
        ws.create()
        for folder in WORKSPACE_FOLDERS:
            assert (ws.root / folder).exists()

    def test_artifact_registration(self, tmp_path):
        from sozo_generator.jobs.workspace import JobWorkspace
        ws = JobWorkspace(tmp_path, "job-test")
        ws.create()
        art = ws.register_artifact("draft", "drafts/test.docx", "draft_agent")
        assert art.artifact_id == "art-001"
        assert len(ws.list_artifacts()) == 1
        assert len(ws.list_artifacts("draft")) == 1
        assert len(ws.list_artifacts("qa_report")) == 0

    def test_file_io(self, tmp_path):
        from sozo_generator.jobs.workspace import JobWorkspace
        ws = JobWorkspace(tmp_path, "job-test")
        ws.create()
        ws.write_file("logs", "test.log", "hello")
        content = ws.read_file("logs", "test.log")
        assert content == "hello"


class TestJobPlanner:
    def test_plan_generate(self):
        from sozo_generator.jobs.models import Job
        from sozo_generator.jobs.planner import JobPlanner
        job = Job(job_id="test", target_conditions=["parkinsons"])
        planner = JobPlanner()
        plan = planner.plan(job)
        assert len(plan.tasks) >= 4
        agent_names = [t.agent_name for t in plan.tasks]
        assert "content_agent" in agent_names
        assert "evidence_agent" in agent_names
        assert "draft_agent" in agent_names
        assert "qa_agent" in agent_names

    def test_plan_with_template(self):
        from sozo_generator.jobs.models import Job
        from sozo_generator.jobs.planner import JobPlanner
        job = Job(job_id="test", template_ref="template.docx", target_conditions=["parkinsons"])
        plan = planner = JobPlanner()
        plan = planner.plan(job)
        agent_names = [t.agent_name for t in plan.tasks]
        assert "template_agent" in agent_names

    def test_plan_with_comments(self):
        from sozo_generator.jobs.models import Job
        from sozo_generator.jobs.planner import JobPlanner
        job = Job(job_id="test", doctor_comments=["remove TPS"], target_conditions=["parkinsons"])
        planner = JobPlanner()
        plan = planner.plan(job)
        agent_names = [t.agent_name for t in plan.tasks]
        assert "revision_agent" in agent_names
        assert "draft_agent" not in agent_names


class TestAgentRegistry:
    def test_all_agents_registered(self):
        from sozo_generator.agents.registry import list_agents, get_agent
        # Import to trigger registration
        from sozo_generator.agents import (
            template_agent, content_agent, evidence_agent,
            draft_agent, revision_agent, qa_agent, review_pack_agent,
        )
        agents = list_agents()
        assert len(agents) == 7
        for name in agents:
            agent = get_agent(name)
            assert agent is not None
            assert agent.name == name

    def test_unknown_agent_returns_none(self):
        from sozo_generator.agents.registry import get_agent
        assert get_agent("nonexistent") is None


class TestAgentExecution:
    def test_content_agent_runs(self, tmp_path):
        """Content agent should execute and produce output."""
        from sozo_generator.agents.content_agent import ContentAgent
        agent = ContentAgent()
        result = agent.execute(
            {"conditions": ["parkinsons"], "doc_types": ["handbook"]},
            str(tmp_path),
        )
        assert result.success
        assert result.output_data  # has output data

    def test_evidence_agent_runs(self, tmp_path):
        from sozo_generator.agents.evidence_agent import EvidenceAgent
        agent = EvidenceAgent()
        result = agent.execute(
            {"conditions": ["parkinsons"]},
            str(tmp_path),
        )
        assert result.success
        assert result.output_data  # has output data

    def test_qa_agent_runs(self, tmp_path):
        from sozo_generator.agents.qa_agent import QAAgent
        agent = QAAgent()
        result = agent.execute(
            {"conditions": ["parkinsons"]},
            str(tmp_path),
            job=type("J", (), {"target_conditions": ["parkinsons"]})(),
        )
        assert result.success

    def test_draft_agent_runs(self, tmp_path):
        from sozo_generator.agents.draft_agent import DraftAgent
        agent = DraftAgent()
        result = agent.execute(
            {"conditions": ["parkinsons"], "doc_types": ["handbook"], "tiers": ["fellow"]},
            str(tmp_path),
        )
        assert result.success
        assert result.output_data.get("total_documents", 0) >= 1


class TestSafety:
    def test_agent_cannot_use_unapproved_tools(self):
        """Agents only access approved modules, not arbitrary system."""
        from sozo_generator.agents.base import BaseAgent
        # BaseAgent has no shell, no file traversal outside workspace
        assert not hasattr(BaseAgent, "run_shell")
        assert not hasattr(BaseAgent, "browse_web")

    def test_draft_agent_requires_review(self):
        from sozo_generator.agents.draft_agent import DraftAgent
        agent = DraftAgent()
        assert agent.requires_human_review is True

    def test_revision_agent_requires_review(self):
        from sozo_generator.agents.revision_agent import RevisionAgent
        agent = RevisionAgent()
        assert agent.requires_human_review is True

    def test_qa_agent_no_review_required(self):
        from sozo_generator.agents.qa_agent import QAAgent
        agent = QAAgent()
        assert agent.requires_human_review is False
