# SOZO Generator — Example CLI Commands

All examples assume you are in the project root directory
and have set `PYTHONPATH=src`.

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH="src"
```

**Windows (cmd):**
```cmd
set PYTHONPATH=src
```

**Linux / macOS:**
```bash
export PYTHONPATH=src
```

---

## Example 1: List All Supported Conditions

```bash
PYTHONPATH=src python -m sozo_generator.cli.main list-conditions
```

Expected output:

```
Slug                  Name
--------------------------------------------------
  parkinsons            Parkinson's Disease
  depression            Major Depressive Disorder
  anxiety               Generalized Anxiety Disorder
  adhd                  Attention Deficit Hyperactivity Disorder
  alzheimers            Alzheimer's Disease / Mild Cognitive Impairment
  stroke_rehab          Post-Stroke Rehabilitation
  tbi                   Traumatic Brain Injury
  chronic_pain          Chronic Pain / Fibromyalgia
  ptsd                  Post-Traumatic Stress Disorder
  ocd                   Obsessive-Compulsive Disorder
  ms                    Multiple Sclerosis
  asd                   Autism Spectrum Disorder
  long_covid            Long COVID / Brain Fog
  tinnitus              Tinnitus
  insomnia              Insomnia / Sleep Disorder

Total: 15 conditions
```

---

## Example 2: Build All Parkinson's Documents (Both Tiers)

```bash
PYTHONPATH=src python -m sozo_generator.cli.main build condition \
    --condition parkinsons \
    --tier both \
    --doc-type all
```

Expected output:

```
Building documents for: parkinsons
  Tiers:     ['fellow', 'partners']
  Doc types: ['clinical_exam', 'phenotype_classification', 'responder_tracking',
               'psych_intake', 'network_assessment', 'handbook',
               'all_in_one_protocol', 'evidence_based_protocol']
  Visuals:   True
  Output:    outputs/documents

  [OK] outputs/documents/parkinsons/fellow/Clinical_Examination_Checklist_Fellow.docx
  [OK] outputs/documents/parkinsons/fellow/Phenotype_Classification_Fellow.docx
  [OK] outputs/documents/parkinsons/fellow/Responder_Tracking_Fellow.docx
  [OK] outputs/documents/parkinsons/fellow/Psychological_Intake_PRS_Baseline_Fellow.docx
  [OK] outputs/documents/parkinsons/fellow/SOZO_Clinical_Handbook_Fellow.docx
  [OK] outputs/documents/parkinsons/fellow/All_In_One_Protocol_Fellow.docx
  [OK] outputs/documents/parkinsons/fellow/Evidence_Based_Protocol_Fellow.docx
  [OK] outputs/documents/parkinsons/partners/Clinical_Examination_Checklist_Partners.docx
  [OK] outputs/documents/parkinsons/partners/Phenotype_Classification_Partners.docx
  [OK] outputs/documents/parkinsons/partners/Responder_Tracking_Partners.docx
  [OK] outputs/documents/parkinsons/partners/Psychological_Intake_PRS_Baseline_Partners.docx
  [OK] outputs/documents/parkinsons/partners/6Network_Bedside_Assessment_Partners.docx
  [OK] outputs/documents/parkinsons/partners/SOZO_Clinical_Handbook_Partners.docx
  [OK] outputs/documents/parkinsons/partners/All_In_One_Protocol_Partners.docx
  [OK] outputs/documents/parkinsons/partners/Evidence_Based_Protocol_Partners.docx

Successfully built 15 document(s) for 'parkinsons'.
```

---

## Example 3: Build Only the Fellow Evidence-Based Protocol for Depression

```bash
PYTHONPATH=src python -m sozo_generator.cli.main build condition \
    --condition depression \
    --tier fellow \
    --doc-type evidence_based_protocol
```

Expected output:

```
Building documents for: depression
  Tiers:     ['fellow']
  Doc types: ['evidence_based_protocol']
  Visuals:   True
  Output:    outputs/documents

  [OK] outputs/documents/depression/fellow/Evidence_Based_Protocol_Fellow.docx

Successfully built 1 document(s) for 'depression'.
```

---

## Example 4: Build the Partners Handbook for Anxiety (Without Visuals)

```bash
PYTHONPATH=src python -m sozo_generator.cli.main build condition \
    --condition anxiety \
    --tier partners \
    --doc-type handbook \
    --no-visuals
```

Expected output:

```
Building documents for: anxiety
  Tiers:     ['partners']
  Doc types: ['handbook']
  Visuals:   False
  Output:    outputs/documents

  [OK] outputs/documents/anxiety/partners/SOZO_Clinical_Handbook_Partners.docx

Successfully built 1 document(s) for 'anxiety'.
```

---

## Example 5: Build Everything — All 15 Conditions, Both Tiers, All Documents

```bash
PYTHONPATH=src python -m sozo_generator.cli.main build all \
    --tier both \
    --doc-type all \
    --with-visuals
```

Expected output:

```
Building documents for 15 condition(s)...
  Tiers:          ['fellow', 'partners']
  Doc types:      8 type(s)
  Visuals:        True
  Skip existing:  True
  Output:         outputs/documents

Building  [####################################]  15/15

Built 15/15 conditions successfully.
```

To force a full rebuild (overwrite existing documents):

```bash
PYTHONPATH=src python -m sozo_generator.cli.main build all \
    --tier both \
    --doc-type all \
    --no-skip-existing
```

To build a subset of conditions:

```bash
PYTHONPATH=src python -m sozo_generator.cli.main build all \
    --conditions "parkinsons,depression,anxiety" \
    --tier both \
    --doc-type all
```

---

## Example 6: Generate Visual Figures for a Specific Condition

```bash
PYTHONPATH=src python -m sozo_generator.cli.main visuals render \
    --condition parkinsons \
    --force
```

Expected output:

```
Rendering visuals for 1 condition(s)...
  Force:      True
  Output dir: outputs/visuals

  [OK] brain_map: outputs/visuals/parkinsons/parkinsons_brain_map.png
  [OK] network_diagram: outputs/visuals/parkinsons/parkinsons_network_diagram.png
  [OK] symptom_flow: outputs/visuals/parkinsons/parkinsons_symptom_flow.png
  [OK] patient_journey: outputs/visuals/parkinsons/parkinsons_patient_journey.png

Generated 4 visual file(s) for 1/1 condition(s).
```

---

## Example 7: Generate Visuals for All Conditions (Including Shared Legends)

```bash
PYTHONPATH=src python -m sozo_generator.cli.main visuals render \
    --condition all
```

Expected output (truncated):

```
Rendering visuals for 15 condition(s)...
  Force:      False
  Output dir: outputs/visuals

  [OK] brain_map: outputs/visuals/parkinsons/parkinsons_brain_map.png
  [OK] network_diagram: outputs/visuals/parkinsons/parkinsons_network_diagram.png
  ...
  [OK] brain_map: outputs/visuals/insomnia/insomnia_brain_map.png
  ...
  [LEGEND] evidence_legend: outputs/visuals/shared/evidence_legend.png
  [LEGEND] network_color_legend: outputs/visuals/shared/network_color_legend.png

Generated 62 visual file(s) for 15/15 condition(s).
```

---

## Example 8: QA Report for a Single Condition

```bash
PYTHONPATH=src python -m sozo_generator.cli.main qa report \
    --condition parkinsons \
    --format markdown
```

Expected output (passing condition):

```
Running QA checks for 1 condition(s)...
  Checking: parkinsons

# SOZO QA Report

## Parkinson's Disease (parkinsons) — PASS
- Generated: 2026-03-31T12:00:00.000000
- Documents: 15/15 passed
- Completeness: 100%
- Ready for clinical review: True

  [READY] parkinsons: 15/15 docs passed (100% complete)
```

Expected output (failing condition — some documents not yet built):

```
Running QA checks for 1 condition(s)...
  Checking: anxiety

# SOZO QA Report

## Generalized Anxiety Disorder (anxiety) — FAIL
- Generated: 2026-03-31T12:00:00.000000
- Documents: 7/15 passed
- Completeness: 47%
- Ready for clinical review: False
### Recommendations
- 8 document(s) missing or too small.
### Missing/Failed Documents
- [partners] clinical_exam: File not found: ...
- [partners] phenotype_classification: File not found: ...
...

  [NOT READY] anxiety: 7/15 docs passed (47% complete)
```

---

## Example 9: QA Report for All Conditions, Written to a File

```bash
PYTHONPATH=src python -m sozo_generator.cli.main qa report \
    --condition all \
    --format markdown \
    --output outputs/qa_report.md
```

Expected output:

```
Running QA checks for 15 condition(s)...
  Checking: parkinsons
  Checking: depression
  ...
  Checking: insomnia

Report written to: outputs/qa_report.md

  [READY]     parkinsons: 15/15 docs passed (100% complete)
  [READY]     depression: 15/15 docs passed (100% complete)
  [NOT READY] anxiety: 0/15 docs passed (0% complete)
  ...

3 condition(s) flagged: anxiety, adhd, long_covid
```

---

## Example 10: Ingest PubMed Evidence for a Condition

```bash
PYTHONPATH=src python -m sozo_generator.cli.main ingest-evidence ingest \
    --condition depression \
    --max-results 30
```

Expected output:

```
Ingesting PubMed evidence for: Major Depressive Disorder
  Categories:    13
  Max results:   30 per category
  Force refresh: False
  Cache dir:     data/raw/pubmed_cache

  [OK]    pathophysiology: 28 articles found
  [OK]    brain_regions: 30 articles found
  [CACHE] network_involvement: 22 articles (cached)
  [OK]    clinical_phenotypes: 15 articles found
  [OK]    assessment_tools: 30 articles found
  [OK]    stimulation_targets: 30 articles found
  [OK]    stimulation_parameters: 27 articles found
  [OK]    modality_rationale: 30 articles found
  [OK]    safety: 18 articles found
  [OK]    contraindications: 12 articles found
  [OK]    responder_criteria: 25 articles found
  [OK]    inclusion_criteria: 30 articles found
  [OK]    exclusion_criteria: 20 articles found

Cached evidence for Major Depressive Disorder: 317 articles across 13 categories.
```

To force re-fetch from PubMed (bypass cache):

```bash
PYTHONPATH=src python -m sozo_generator.cli.main ingest-evidence ingest \
    --condition depression \
    --max-results 50 \
    --force-refresh
```

To ingest evidence for specific claim categories only:

```bash
PYTHONPATH=src python -m sozo_generator.cli.main ingest-evidence ingest \
    --condition depression \
    --categories "stimulation_targets,stimulation_parameters,responder_criteria"
```

---

## Example 11: Analyze a Template Directory

```bash
PYTHONPATH=src python -m sozo_generator.cli.main extract-template extract \
    --input "path/to/template_folder" \
    --output outputs/template_analysis.json
```

Expected output:

```
Scanning template directory: path/to/template_folder
  Analyzing: fellow/Clinical_Examination_Checklist_Fellow.docx
  Analyzing: fellow/Phenotype_Classification_Fellow.docx
  ...
  Analyzing: partners/6Network_Bedside_Assessment_Partners.docx

Analysis written to: outputs/template_analysis.json

Found 15 documents, 7 Fellow / 8 Partners
```

---

## Example 12: Full Build From Scratch (Clean Run)

This sequence ingests evidence, builds all documents, generates visuals, and runs QA:

```bash
# Step 1: Ingest PubMed evidence for all conditions
for slug in parkinsons depression anxiety adhd alzheimers stroke_rehab tbi \
            chronic_pain ptsd ocd ms asd long_covid tinnitus insomnia; do
    PYTHONPATH=src python -m sozo_generator.cli.main ingest-evidence ingest \
        --condition "$slug" --max-results 30
done

# Step 2: Build all 225 documents
PYTHONPATH=src python -m sozo_generator.cli.main build all \
    --tier both \
    --doc-type all \
    --no-skip-existing

# Step 3: Generate all visuals including shared legends
PYTHONPATH=src python -m sozo_generator.cli.main visuals render \
    --condition all \
    --force

# Step 4: Run QA and write report
PYTHONPATH=src python -m sozo_generator.cli.main qa report \
    --condition all \
    --format markdown \
    --output outputs/qa_report.md
```

---

## Document Type Values Reference

Use these values with `--doc-type`:

| Value | Document |
|---|---|
| `clinical_exam` | Clinical Examination Checklist |
| `phenotype_classification` | Phenotype Classification |
| `responder_tracking` | Responder Tracking |
| `psych_intake` | Psychological Intake / PRS Baseline |
| `network_assessment` | 6-Network Bedside Assessment (Partners only) |
| `handbook` | SOZO Clinical Handbook |
| `all_in_one_protocol` | FNON All-in-One Protocol |
| `evidence_based_protocol` | Evidence-Based Protocol |
| `all` | All document types |
