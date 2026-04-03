# Template-Driven AI-Assisted Document Generation — Architecture Note

**Date**: 2026-04-03
**Status**: Implementation in progress

---

## 1. Overview

This capability extends the Sozo Protocol Generator into a template-driven, AI-assisted,
evidence-grounded clinical document generation platform. Users can:

1. Upload a gold-standard DOCX template (e.g., a Parkinson's handbook)
2. The system parses and learns its structure, tone, tables, figures, and section patterns
3. Choose a different condition (e.g., Depression, ADHD, Stroke)
4. The system uses AI + literature + internal data to generate a new document
5. The output preserves the same style, depth, and layout as the uploaded template
6. All clinical claims are evidence-grounded and reviewable

---

## 2. Existing Infrastructure (What We Build On)

The codebase already has substantial template learning infrastructure:

| Module | What It Does | Reuse |
|--------|-------------|-------|
| `template/parser.py` | Parses DOCX heading structure, placeholders | Extend |
| `template/learning/document_ingester.py` | Creates structural fingerprints | Reuse |
| `template/learning/pattern_extractor.py` | Builds MasterTemplateProfile | Reuse |
| `template/learning/content_harvester.py` | Extracts reusable section content | Reuse |
| `template/learning/consistency_scorer.py` | Validates output against profile | Reuse |
| `template/learning/profile_guided_generator.py` | Reorders sections to match profile | Extend |
| `template/learning/template_matcher.py` | Identifies doc type of uploaded template | Reuse |
| `template/template_driven_generator.py` | Maps template sections to condition data | Extend heavily |
| `generation/service.py` | Canonical generation orchestrator | Extend |
| `evidence/query_planner.py` | PubMed query planning | Reuse |
| `evidence/pubmed_client.py` | PubMed API client | Reuse |
| `content/assembler.py` | Section content assembly | Reuse |
| `ai/chat_engine.py` | LLM interface (Claude/OpenAI) | Reuse |
| `docx/renderer.py` | DOCX rendering | Reuse |
| `data/learned/` | 225+ document fingerprints, 905 harvested sections | Reuse |

**Key insight**: We do NOT need to build template parsing from scratch. The existing
`TemplateParser`, `DocumentIngester`, `PatternExtractor`, and `ContentHarvester` provide
the foundation. We need to:
1. Enhance the parsed output into a richer `TemplateProfile`
2. Add a research orchestration layer
3. Add an AI section writer with grounding
4. Wire it all into `GenerationService`

---

## 3. New Modules

### A. `src/sozo_generator/template_profiles/` — Profile Storage & Models
- `models.py` — TemplateProfile, TemplateSectionSpec, FormattingProfile, ToneProfile
- `store.py` — Save/load/list template profiles (JSON-backed)
- `builder.py` — Build TemplateProfile from parsed DOCX (uses existing parsers)

### B. `src/sozo_generator/research/` — Research Orchestration
- `orchestrator.py` — ResearchOrchestrator: section-level evidence gathering
- `adapters.py` — Pluggable search adapters (PubMed, guidelines, web)
- `models.py` — ResearchBundle, ResearchQuery, SourceResult

### C. `src/sozo_generator/writers/` — AI Section Writing
- `brief_builder.py` — Builds SectionBrief from template spec + condition data + evidence
- `section_writer.py` — AI-powered section drafting with LLM adapter
- `editor.py` — Consistency editing, tone normalization, placeholder cleanup
- `models.py` — SectionBrief, DraftedSection

### D. `src/sozo_generator/grounding/` — Evidence Grounding & Validation
- `validator.py` — Maps claims to evidence, flags unsupported content
- `models.py` — GroundingResult, ClaimEvidence

---

## 4. Data Flow

```
User uploads DOCX
       │
       ▼
┌──────────────────┐
│ Template Ingestion│  ← TemplateParser + DocumentIngester + new ProfileBuilder
│ → TemplateProfile │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ User selects:    │
│ - condition      │
│ - tier           │
│ - doc type       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ Research          │────►│ Evidence from:   │
│ Orchestrator      │     │ - Internal data  │
│ (per section)     │     │ - PubMed         │
│                   │     │ - Content library │
└────────┬─────────┘     └──────────────────┘
         │
         ▼
┌──────────────────┐
│ Brief Builder     │  ← template spec + condition data + evidence + style rules
│ → SectionBrief[]  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Section Writer    │  ← AI drafts section-by-section, grounded by brief
│ → DraftedSection[]│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Grounding Check   │  ← Maps claims to evidence, flags gaps
│ + QA Validation   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DOCX/PDF Render   │  ← Template-style layout + visuals
│ + Build Manifest  │
└──────────────────┘
```

---

## 5. Integration with GenerationService

The existing `GenerationService.generate()` path stays unchanged.
A new method `GenerationService.generate_from_template()` is added:

```python
service = GenerationService()

# Existing path (unchanged)
results = service.generate(condition="parkinsons", tier="partners", doc_type="handbook")

# New template-driven path
results = service.generate_from_template(
    template_id="tp-abc123",         # or template_path="path/to/template.docx"
    condition="depression",
    tier="partners",
    with_ai=True,                    # Use AI for section drafting
    with_research=True,              # Search PubMed for fresh evidence
    with_visuals=True,
    with_qa=True,
)
```

---

## 6. Template Profile Schema

```python
class TemplateProfile(BaseModel):
    profile_id: str
    name: str
    source_filename: str
    template_type: str              # e.g., "handbook", "protocol"
    inferred_doc_type: DocumentType
    tier: Tier
    created_at: str
    version: str = "1.0"

    # Structure
    section_map: list[TemplateSectionSpec]
    heading_hierarchy: dict[int, int]  # level → count
    total_sections: int
    total_tables: int
    total_figures: int

    # Content
    table_specs: list[TableSpec]
    figure_specs: list[FigureSpec]
    formatting_profile: FormattingProfile
    tone_profile: ToneProfile
    placeholder_map: dict[str, list[str]]

    # Identity
    source_condition: Optional[str]  # Condition detected in template
    template_fingerprint: str        # Content hash
```

---

## 7. Implementation Order

1. **Phase 2**: Schema models (TemplateProfile, SectionBrief, DraftedSection, ResearchBundle)
2. **Phase 3**: Template ingestion (enhance existing parsers → TemplateProfile)
3. **Phase 4**: Research orchestration (section-level evidence gathering)
4. **Phase 5**: Section writing (AI-powered, grounded, reviewable)
5. **Phase 6**: Integration (GenerationService + CLI + Streamlit)
6. **Phase 7**: Tests

Each phase produces working, testable code before moving to the next.
