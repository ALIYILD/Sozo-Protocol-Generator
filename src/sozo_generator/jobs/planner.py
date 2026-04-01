"""Job planner — converts user requests into executable agent task graphs."""
from __future__ import annotations
import logging
from .models import Job, JobPlan, AgentTask

logger = logging.getLogger(__name__)

class JobPlanner:
    """Creates execution plans based on job parameters."""

    def plan(self, job: Job) -> JobPlan:
        """Create an agent task graph for the job."""
        has_template = bool(job.template_ref or job.uploaded_files)
        has_comments = bool(job.doctor_comments)
        has_conditions = bool(job.target_conditions)

        tasks = []

        # Step 0: Condition matching — infer/validate conditions from prompt (always first)
        tasks.append(AgentTask(
            task_id="t0_condition_match", agent_name="condition_match_agent",
            input_data={"source_prompt": job.source_prompt, "target_conditions": job.target_conditions},
            depends_on=[],
        ))

        # Step 1: Template parsing (if template provided)
        if has_template:
            tasks.append(AgentTask(
                task_id="t1_template", agent_name="template_agent",
                input_data={"template_ref": job.template_ref, "uploaded_files": job.uploaded_files},
                depends_on=["t0_condition_match"],
            ))

        # Step 2: Content retrieval (always) — depends on condition match + template if present
        t2_deps = ["t0_condition_match"]
        if has_template:
            t2_deps.append("t1_template")
        tasks.append(AgentTask(
            task_id="t2_content", agent_name="content_agent",
            input_data={"conditions": job.target_conditions, "doc_types": job.target_doc_types},
            depends_on=t2_deps,
        ))

        # Step 3: Evidence retrieval (always) — depends on condition match
        tasks.append(AgentTask(
            task_id="t3_evidence", agent_name="evidence_agent",
            input_data={"conditions": job.target_conditions},
            depends_on=["t0_condition_match"],
        ))

        # Step 4: Draft assembly OR revision
        if has_comments:
            tasks.append(AgentTask(
                task_id="t4_revision", agent_name="revision_agent",
                input_data={"comments": job.doctor_comments},
                depends_on=["t2_content", "t3_evidence"],
            ))
        else:
            tasks.append(AgentTask(
                task_id="t4_draft", agent_name="draft_agent",
                input_data={"conditions": job.target_conditions, "doc_types": job.target_doc_types, "tiers": job.target_tiers},
                depends_on=["t2_content", "t3_evidence"],
            ))

        # Step 5: Visual — generate protocol diagrams (after draft, before QA)
        draft_task = "t4_revision" if has_comments else "t4_draft"
        tasks.append(AgentTask(
            task_id="t5_visual", agent_name="visual_agent",
            input_data={},
            depends_on=[draft_task],
        ))

        # Step 6: QA (always)
        tasks.append(AgentTask(
            task_id="t6_qa", agent_name="qa_agent",
            input_data={},
            depends_on=["t5_visual"],
        ))

        # Step 7: Review pack (always)
        tasks.append(AgentTask(
            task_id="t7_review_pack", agent_name="review_pack_agent",
            input_data={},
            depends_on=["t6_qa"],
        ))

        return JobPlan(tasks=tasks)
