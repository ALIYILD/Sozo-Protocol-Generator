# Intended Use Statement

**Document ID:** SOZO-REG-IUS-001
**Version:** 1.0
**Date:** 2026-04-03
**Classification:** Regulatory
**Status:** Draft

---

## 1. Product Identification

| Field | Value |
|---|---|
| Product Name | Sozo Protocol Generator |
| Product Type | Clinical Decision Support Software (CDS) |
| Software Version | 1.0 (MVP) |
| Manufacturer | PerfFlux Ltd |
| UDI-DI | To be assigned |

---

## 2. Intended Use

The Sozo Protocol Generator is a clinical decision support software tool intended to assist qualified healthcare professionals in generating evidence-based neuromodulation treatment protocols for adult patients (18 years and older) with supported neurological and psychiatric conditions.

The software retrieves, synthesizes, and presents published clinical evidence to support clinicians in configuring neuromodulation treatment parameters. All generated protocols require mandatory clinician review and approval before any clinical application.

**The Sozo Protocol Generator does not autonomously prescribe, administer, or modify treatment. It does not diagnose conditions. It does not replace clinical judgment.**

---

## 3. Intended Users

The software is intended for use by:

- Licensed physicians specializing in neurology, psychiatry, rehabilitation medicine, or pain management
- Licensed neuromodulation clinicians with documented training in the applicable modality
- Clinical researchers operating under institutional review board (IRB) or ethics committee oversight

All users must hold valid clinical licensure in their jurisdiction of practice and possess demonstrated competency in at least one supported neuromodulation modality.

---

## 4. Intended Patient Population

| Parameter | Specification |
|---|---|
| Age | Adults 18 years and older |
| Sex | All |
| Conditions | See Section 4.1 |

### 4.1 Supported Conditions

| # | Condition | ICD-10 Code |
|---|---|---|
| 1 | Parkinson's Disease | G20 |
| 2 | Major Depressive Disorder | F32 |
| 3 | Generalized Anxiety Disorder | F41.1 |
| 4 | Attention-Deficit/Hyperactivity Disorder | F90 |
| 5 | Alzheimer's Disease | G30 |
| 6 | Stroke (Sequelae) | I69 |
| 7 | Traumatic Brain Injury | S09.90 |
| 8 | Chronic Pain | M79.7 |
| 9 | Post-Traumatic Stress Disorder | F43.1 |
| 10 | Obsessive-Compulsive Disorder | F42 |
| 11 | Multiple Sclerosis | G35 |
| 12 | Autism Spectrum Disorder | F84.0 |
| 13 | Long COVID | U09.9 |
| 14 | Tinnitus | H93.1 |
| 15 | Insomnia | G47.0 |

### 4.2 Supported Modalities

| # | Modality | Abbreviation |
|---|---|---|
| 1 | Transcranial Direct Current Stimulation | tDCS |
| 2 | Transcranial Pulse Stimulation | TPS |
| 3 | Transcranial Auricular Vagus Nerve Stimulation | taVNS |
| 4 | Cranial Electrotherapy Stimulation | CES |

---

## 5. Intended Use Environment

The software is intended for use in the following clinical settings:

- Outpatient neuromodulation clinics
- Hospital outpatient departments with neuromodulation services
- Academic and clinical research settings
- Telehealth environments where the clinician remotely configures protocols for on-site administration

The software is not intended for use in emergency departments, inpatient acute care, surgical settings, or by patients directly.

---

## 6. Clinical Benefits

The Sozo Protocol Generator provides the following clinical decision support benefits:

1. **Protocol standardization** -- Generates protocols aligned with published evidence and established parameter ranges, reducing unwarranted variation in clinical practice.
2. **Evidence traceability** -- Each protocol parameter is linked to specific published sources identified by PMID, DOI, or equivalent identifier, enabling clinicians to verify the evidence basis independently.
3. **Safety checking** -- Automated screening against known contraindications, medication interactions, and parameter safety bounds prior to clinician review.
4. **Efficiency** -- Reduces time required for manual literature review and protocol configuration while maintaining clinician oversight.
5. **Audit trail** -- Complete record of protocol generation, review decisions, and modifications for quality assurance and regulatory compliance.

---

## 7. Limitations and Contraindications

### 7.1 Limitations

- The software does not diagnose medical conditions.
- The software does not autonomously prescribe or administer treatment.
- The software does not replace clinical judgment, training, or experience.
- Generated protocols are recommendations only and must be reviewed, modified as necessary, and approved by a qualified clinician before use.
- Evidence retrieval depends on the availability and completeness of indexed publications in the source databases at the time of query.
- The software does not guarantee that all relevant published evidence has been identified or included.
- The software does not account for all possible patient-specific factors that may influence treatment decisions.

### 7.2 Contraindications

The software itself has no contraindications as it does not deliver treatment. Contraindications for specific neuromodulation modalities and conditions are surfaced within the generated protocol for clinician evaluation. The clinician is responsible for applying all contraindications relevant to the individual patient.

---

## 8. Regulatory Classification Rationale

### 8.1 United States -- FDA

The Sozo Protocol Generator is designed to meet the criteria for Clinical Decision Support (CDS) software excluded from device regulation under Section 3060(a) of the 21st Century Cures Act (Public Law 114-255), codified at 21 U.S.C. 360j(o)(1)(E).

The software satisfies all four criteria for CDS exclusion:

| Criterion | Compliance |
|---|---|
| (i) Not intended to acquire, process, or analyze a medical image, signal, or pattern from an in vitro diagnostic device | The software does not acquire or process medical device signals in its MVP configuration. EEG integration (V2) will be reassessed separately. |
| (ii) Intended for the purpose of displaying, analyzing, or printing medical information about a patient or other medical information | The software displays synthesized medical literature and protocol parameters for clinician review. |
| (iii) Intended for the purpose of supporting or providing recommendations to a health care professional about prevention, diagnosis, or treatment of a disease or condition | The software provides evidence-based protocol recommendations for neuromodulation treatment. |
| (iv) Intended for the purpose of enabling such health care professional to independently review the basis for such recommendations that such software presents so that it is not the intent that such health care professional rely primarily on any of such recommendations to make a clinical diagnosis or treatment decision regarding an individual patient without independently reviewing the basis for such recommendations | Full evidence chains with source citations are presented. The clinician must independently review all evidence and approve protocols before use. |

### 8.2 European Union -- MDR

Under Regulation (EU) 2017/745 (Medical Device Regulation), software that provides clinical decision support by aggregating and presenting published medical literature for clinician review, without directly controlling or influencing medical devices, may be excluded from the definition of a medical device under Article 2(1) where the clinician independently assesses all recommendations.

The manufacturer will maintain a regulatory monitoring process to reassess classification if the software's functionality, intended use, or risk profile changes, particularly upon introduction of EEG analysis (V2) or closed-loop device integration.

### 8.3 United Kingdom -- MHRA

Classification under UK MDR 2002 (as amended) will follow the same rationale as the EU MDR assessment above. The manufacturer will engage with MHRA guidance on software as a medical device (SaMD) to confirm the exclusion applies in the UK regulatory context.

---

## 9. Clinician-in-the-Loop Requirements

The following mandatory controls ensure that the Sozo Protocol Generator operates exclusively as a decision support tool and never as an autonomous treatment system:

| Control | Description |
|---|---|
| Mandatory Review | Every generated protocol must be reviewed by a qualified clinician before it can be exported, saved as final, or applied clinically. |
| Four-Eyes Approval | For protocols involving off-label use, high-risk parameters, or low-confidence evidence, a second independent clinician review is required before approval. |
| Full Evidence Visibility | All source citations, confidence scores, evidence quality assessments, and safety flags are visible to the reviewing clinician at the point of review. |
| Modification Authority | The reviewing clinician may modify any protocol parameter. All modifications are logged with rationale. |
| Rejection Authority | The reviewing clinician may reject a generated protocol entirely. Rejected protocols are retained in the audit log with rejection rationale. |
| No Autonomous Execution | The software has no capability to transmit parameters to or control any neuromodulation device. |

---

## 10. Data Sources

The software retrieves published clinical evidence from the following sources:

| Source | Type | Access Method |
|---|---|---|
| PubMed / MEDLINE | Peer-reviewed literature | NCBI E-utilities API |
| CrossRef | DOI metadata and citation data | CrossRef REST API |
| Semantic Scholar | Citation graphs and paper metadata | Semantic Scholar API |
| Clinical practice guidelines | Professional society guidelines | Manual curation, periodic review |

All retrieved citations are validated against their source database. Citations that cannot be validated (PMID not found, DOI not resolvable) are flagged and excluded from protocol generation or clearly marked as unvalidated.

---

## 11. Document Control

| Action | Name | Date |
|---|---|---|
| Prepared by | | 2026-04-03 |
| Reviewed by | | |
| Approved by | | |

---

*This document is controlled. Printed copies are for reference only. The current version is maintained in the document management system.*
