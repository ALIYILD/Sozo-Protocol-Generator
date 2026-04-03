# Canonical Document Generation — Migration Architecture

**Date**: 2026-04-03
**Status**: Phase 2 implementation — spec-driven generation

---

## 1. Current State (What's Wrong)

The generation pipeline has a **disconnect between declarations and execution**:

- `DOCUMENT_DEFINITIONS` declares what each doc type should contain (sections, visuals)
- `DocumentExporter._get_content()` hardcodes what each doc type actually builds
- These two layers don't talk to each other

**Consequences:**
- Adding a section requires editing Python dispatcher code
- Tier differences are scattered across exporter conditionals
- No spec layer connects knowledge → document structure → rendering
- Visuals, evidence PMIDs, and claims are declared on SectionContent but never populated

## 2. Target State (What We're Building)

```
DocumentBlueprint (YAML)     ← declares what a doc type should contain
        │
        ▼
CanonicalDocumentAssembler   ← reads blueprint + knowledge, assembles sections
        │
        ├── KnowledgeBase    ← condition/modality/assessment/contraindication data
        ├── SectionBlueprint ← per-section requirements and rendering hints
        ├── VisualSpec       ← what visuals each section needs
        └── QA               ← validates assembled document
        │
        ▼
DocumentSpec + SectionContent ← existing rendering models (unchanged)
        │
        ▼
DocumentRenderer             ← existing DOCX rendering (unchanged)
```

**Key principle:** The blueprint is the spec. The assembler reads it. The renderer draws it.
No hardcoded dispatch. No tier conditionals in the exporter.

## 3. New Models

| Model | Purpose | Stored As |
|-------|---------|-----------|
| **DocumentBlueprint** | Declares a document type's full structure | YAML in sozo_knowledge/blueprints/ |
| **SectionBlueprint** | Declares one section's requirements | Inline in DocumentBlueprint |
| **ProtocolSpec** | Structured protocol metadata | Part of KnowledgeCondition.protocols |
| **AssessmentSpec** | Structured assessment metadata | Part of KnowledgeCondition.assessments |
| **VisualRequirement** | What visual a section needs | Inline in SectionBlueprint |

## 4. First Migration: Parkinson's Evidence-Based Protocol (Fellow)

Why this one:
- Most sections (12+), highest complexity
- Fellow tier = simpler (no FNON networks)
- Well-understood condition data
- Exercises most section builders

What changes:
- Blueprint YAML defines all sections, their order, requirements
- CanonicalDocumentAssembler reads blueprint + PD knowledge
- Each section is assembled from knowledge fields (not hardcoded builder dispatch)
- Output is standard DocumentSpec → rendered by existing DocumentRenderer

What stays:
- ConditionSchema builders still work (backward compatible)
- DocumentRenderer is unchanged
- Existing GenerationService.generate() path is unchanged
- New path is GenerationService.generate_canonical()

## 5. Risks

| Risk | Mitigation |
|------|-----------|
| Output differs from legacy | Compare output sections side-by-side |
| Missing data for some sections | Blueprint marks sections as optional with fallback |
| Builder logic has hidden complexity | Assembler can delegate to existing builders as fallback |
| Too much abstraction | Keep it concrete — YAML blueprints, not meta-frameworks |
