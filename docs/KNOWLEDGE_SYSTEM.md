# SOZO Clinical Knowledge System — Architecture

**Date**: 2026-04-03
**Status**: Phase 1-6 implementation

---

## 1. What This Is

The SOZO Knowledge System is a structured clinical knowledge compiler that stores
and maintains all clinical information needed to generate SOZO Brain Center documents.

Instead of embedding clinical data inside Python builder functions, the knowledge
system stores it in validated, cross-referenced YAML objects that any generation
pathway can consume.

---

## 2. Folder Structure

```
sozo_knowledge/
├── knowledge/                    # Canonical knowledge objects (YAML)
│   ├── conditions/               # One YAML per condition
│   │   ├── parkinsons.yaml
│   │   ├── depression.yaml
│   │   ├── adhd.yaml
│   │   ├── asd.yaml
│   │   └── migraine.yaml
│   ├── modalities/               # One YAML per modality
│   │   ├── tdcs.yaml
│   │   ├── tps.yaml
│   │   ├── tavns.yaml
│   │   └── ces.yaml
│   ├── assessments/              # Assessment scale definitions
│   ├── targets/                  # Brain target / montage definitions
│   ├── contraindications/        # Contraindication profiles
│   ├── evidence_maps/            # Condition × modality evidence linkage
│   ├── glossary/                 # Clinical terminology
│   └── shared/                   # Cross-condition rules, boilerplate
│       ├── governance_rules.yaml
│       ├── safety_principles.yaml
│       └── sozo_sequence.yaml
└── raw/                          # Unprocessed source material

src/sozo_generator/knowledge/     # Python code for knowledge system
├── __init__.py
├── schemas.py                    # Pydantic models for all knowledge types
├── loader.py                     # YAML loading + validation
├── linker.py                     # Cross-reference validation + graph
└── base.py                       # KnowledgeBase: unified query interface
```

---

## 3. Core Principle: Knowledge Objects Drive Generation

```
Knowledge Objects (YAML)
        │
        ▼
KnowledgeBase (Python)  ← validates, links, resolves
        │
        ▼
GenerationService       ← consumes knowledge for any document type
        │
        ├── Handbooks (Fellow / Partners)
        ├── Assessments (Fellow / Partners)
        ├── Protocols (Fellow / Partners)
        ├── Evidence summaries
        ├── Quick guides
        ├── Training slides
        └── Comparison tables
```

Any new document type can be added by writing a new generation template
that queries the KnowledgeBase — no need to create new Python builders.

---

## 4. Knowledge Object Schemas

### Condition
The central knowledge object. Contains:
- Identity (slug, name, ICD-10, aliases)
- Clinical overview + pathophysiology
- Brain regions and network profiles (FNON)
- Clinical phenotypes with network signatures
- Assessment tools and scales
- Stimulation targets and protocols
- Safety/contraindication rules
- Evidence summary and references

### Modality
Defines a neuromodulation technique:
- Parameters (intensity, duration, frequency)
- Devices (with regulatory status)
- Safety principles
- Applicable conditions (linked)
- Evidence level per condition

### Assessment
Defines a clinical assessment scale:
- Scale name, abbreviation
- Domains measured
- Applicable conditions
- Scoring ranges and thresholds
- Evidence PMID
- Timing (baseline, weekly, endpoint)

### BrainTarget
Defines a stimulation target:
- Anatomical region
- EEG 10-20 coordinates
- Associated networks
- Modalities that can reach it
- Conditions where it's relevant

### EvidenceMap
Links condition + modality + target to evidence:
- Evidence level
- Key PMIDs
- Trial summaries
- Gaps and flags

### ContraindicationProfile
Shared safety rules:
- Absolute vs relative
- Per-modality applicability
- Regulatory basis

### SharedClinicalRule
Cross-condition rules like:
- SOZO S-O-Z-O session sequence
- Off-label disclosure requirements
- Governance rules
- Session monitoring checklist

---

## 5. Linkage Graph

```
Condition ──── references ──── Modality
    │                              │
    ├── has ── NetworkProfile       ├── uses ── Device
    ├── has ── Phenotype            ├── has ── Contraindication
    ├── uses ── Assessment          └── targets ── BrainTarget
    ├── uses ── BrainTarget
    └── linked via ── EvidenceMap
```

The KnowledgeBase validates that all cross-references resolve.
Missing links are flagged as validation warnings, not silently ignored.

---

## 6. How Generation Consumes Knowledge

```python
from sozo_generator.knowledge.base import KnowledgeBase

kb = KnowledgeBase()
kb.load_all()

# Get a condition with all linked objects resolved
condition = kb.get_condition("depression")
modalities = kb.get_modalities_for_condition("depression")
assessments = kb.get_assessments_for_condition("depression")
targets = kb.get_targets_for_condition("depression")
evidence = kb.get_evidence_map("depression", "tdcs")

# Use in generation
service = GenerationService(knowledge_base=kb)
result = service.generate(condition="depression", tier="partners", doc_type="handbook")
```

---

## 7. Migration Path

The knowledge system runs alongside the existing condition generators.
Migration is incremental:

1. Knowledge objects are the source of truth for NEW generation paths
2. Existing ConditionSchema builders continue to work (backward compatible)
3. As knowledge objects mature, generators migrate to consume them
4. Eventually, Python condition builders are replaced by YAML knowledge + generation templates
