from __future__ import annotations

import pytest


def test_content_block_table_shape_validation_blocks():
    from sozo_generator.knowledge.schemas import KnowledgeCondition, ConditionContentBlock, ContentTable
    from sozo_generator.knowledge.validators.document_content_validator import (
        validate_condition_content_blocks,
    )
    from sozo_generator.core.enums import QASeverity

    cond = KnowledgeCondition(
        slug="x",
        display_name="X",
        icd10="X00",
        content_blocks=[
            ConditionContentBlock(
                block_id="b1",
                doc_types=["handbook"],
                section_slugs=["patient_handouts"],
                tier="both",
                clinician_only=False,
                kind="table",
                table=ContentTable(headers=["a", "b"], rows=[["only-one-col"]]),
            )
        ],
    )

    issues = validate_condition_content_blocks(cond)
    assert any(i.severity == QASeverity.BLOCK for i in issues)


def test_patient_handouts_must_not_be_clinician_only():
    from sozo_generator.knowledge.schemas import KnowledgeCondition, ConditionContentBlock
    from sozo_generator.knowledge.validators.document_content_validator import (
        validate_condition_content_blocks,
    )
    from sozo_generator.core.enums import QASeverity

    cond = KnowledgeCondition(
        slug="x",
        display_name="X",
        icd10="X00",
        content_blocks=[
            ConditionContentBlock(
                block_id="b1",
                doc_types=["handbook"],
                section_slugs=["patient_handouts"],
                clinician_only=True,
                kind="prose",
                text="hello",
            )
        ],
    )

    issues = validate_condition_content_blocks(cond)
    assert any(i.severity == QASeverity.BLOCK for i in issues)

