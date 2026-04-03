# Risk Management File

**Document ID:** SOZO-REG-RMF-001
**Version:** 1.0
**Date:** 2026-04-03
**Classification:** Regulatory
**Status:** Draft
**Applicable Standard:** ISO 14971:2019 -- Application of risk management to medical devices

---

## 1. Scope

This risk management file documents the systematic identification, analysis, evaluation, control, and monitoring of risks associated with the Sozo Protocol Generator clinical decision support software. Although the software is designed to qualify for regulatory exclusion as a CDS tool (see SOZO-REG-IUS-001), this risk management process is maintained as a quality and safety measure consistent with ISO 14971:2019.

---

## 2. Risk Management Plan

### 2.1 Risk Acceptability Criteria

#### Severity Scale

| Level | Description | Definition |
|---|---|---|
| S1 | Negligible | No patient impact. Minor inconvenience to clinician workflow. |
| S2 | Minor | Clinician receives suboptimal recommendation but identifies the issue during review. No patient harm. |
| S3 | Moderate | Clinician may not immediately identify an issue. Potential for suboptimal treatment selection. Reversible patient discomfort possible if the issue propagates to treatment. |
| S4 | Major | Incorrect protocol parameters could cause significant patient harm (burns, seizure, symptom exacerbation) if not caught during review. |
| S5 | Critical | Incorrect protocol parameters could cause serious injury or irreversible harm if applied without adequate review. |

#### Probability Scale

| Level | Description | Definition |
|---|---|---|
| P1 | Improbable | Less than 1 in 100,000 uses |
| P2 | Remote | 1 in 10,000 to 1 in 100,000 uses |
| P3 | Occasional | 1 in 1,000 to 1 in 10,000 uses |
| P4 | Probable | 1 in 100 to 1 in 1,000 uses |
| P5 | Frequent | Greater than 1 in 100 uses |

#### Risk Level Matrix

| | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| **S5** | Medium | High | High | Unacceptable | Unacceptable |
| **S4** | Low | Medium | High | High | Unacceptable |
| **S3** | Low | Low | Medium | Medium | High |
| **S2** | Negligible | Low | Low | Low | Medium |
| **S1** | Negligible | Negligible | Negligible | Low | Low |

- **Unacceptable:** Risk must be reduced. Software release not permitted at this level.
- **High:** Risk reduction required. Residual risk must be justified with documented benefit-risk analysis.
- **Medium:** Risk reduction should be implemented where practicable.
- **Low / Negligible:** Acceptable. Monitor through post-market surveillance.

---

## 3. Hazard Identification

### 3.1 Hazard Register

| Hazard ID | Hazard Description | Category |
|---|---|---|
| HAZ-001 | Incorrect stimulation target (brain region) recommended for a given condition | Protocol Generation |
| HAZ-002 | Incorrect stimulation parameters (intensity, duration, frequency) outside safe or therapeutic range | Protocol Generation |
| HAZ-003 | Missed contraindication for a specific patient or condition-modality combination | Safety |
| HAZ-004 | Missed medication interaction that alters seizure threshold or stimulation response | Safety |
| HAZ-005 | Off-label use not flagged to the reviewing clinician | Safety |
| HAZ-006 | Protocol generated for wrong patient population (e.g., pediatric parameters applied to adult, or vice versa) | Protocol Generation |
| HAZ-007 | Outdated evidence used as basis for protocol without staleness indication | Evidence |
| HAZ-008 | Hallucinated or fabricated citation presented as valid evidence | Evidence |
| HAZ-009 | Contradicting evidence suppressed or hidden from clinician view | Evidence |
| HAZ-010 | Clinician bypasses mandatory review step | Review Process |
| HAZ-011 | Audit trail gaps -- clinical decisions not recorded | Audit |
| HAZ-012 | Data loss -- generated protocol or review records lost | Data Integrity |
| HAZ-013 | Unauthorized access to patient data or protocol records | Security |
| HAZ-014 | Version confusion -- clinician uses outdated protocol version | Data Integrity |
| HAZ-015 | EEG data misinterpretation leading to incorrect phenotype-based personalization (V2) | Personalization |
| HAZ-016 | Low-confidence evidence presented as high-confidence to the clinician | Evidence |
| HAZ-017 | Incorrect electrode montage or placement specification | Protocol Generation |
| HAZ-018 | System generates protocol for unsupported condition without clear indication | Protocol Generation |
| HAZ-019 | Multiple concurrent protocols for same patient create interaction risk not flagged | Safety |
| HAZ-020 | LLM prompt injection or adversarial input corrupts protocol output | Security |

---

## 4. Risk Analysis

| Hazard ID | Hazardous Situation | Potential Harm | Severity | Probability (Pre-Control) | Risk Level (Pre-Control) |
|---|---|---|---|---|---|
| HAZ-001 | Software recommends wrong brain region (e.g., M1 instead of DLPFC for depression). Clinician does not catch error during review. | Ineffective treatment; potential adverse stimulation effects on non-target region. | S4 | P3 | High |
| HAZ-002 | Generated protocol specifies current intensity above safe limits (e.g., 4 mA tDCS). Clinician applies without verification. | Skin burns, phosphenes, seizure risk, patient distress. | S5 | P3 | High |
| HAZ-003 | Patient has metallic cranial implant. System does not flag contraindication. Clinician proceeds with TPS. | Implant heating, tissue damage, device malfunction. | S5 | P2 | High |
| HAZ-004 | Patient on bupropion (seizure threshold lowering). System does not flag interaction risk. Clinician applies tDCS at standard parameters. | Increased seizure risk. | S4 | P3 | High |
| HAZ-005 | Protocol involves off-label modality-condition pairing. System does not flag off-label status. Clinician proceeds without informed consent disclosure. | Regulatory non-compliance, inadequate informed consent, potential for untested treatment effects. | S3 | P3 | Medium |
| HAZ-006 | System applies pediatric dosing literature to adult patient or generates protocol for a 16-year-old using adult parameters. | Subtherapeutic or excessive stimulation. | S3 | P2 | Low |
| HAZ-007 | Protocol based on a 2008 study that has been superseded by a 2024 meta-analysis with different parameter recommendations. | Suboptimal treatment; potential use of parameters now known to be ineffective or harmful. | S3 | P4 | Medium |
| HAZ-008 | LLM generates a plausible-looking PMID that does not exist. Clinician trusts the citation without checking. | Treatment based on non-existent evidence. Potential patient harm from unsupported parameters. | S4 | P4 | High |
| HAZ-009 | Evidence search returns studies both supporting and contradicting a parameter choice. System presents only supporting studies. | Clinician makes decision without full evidence picture. Potential for harm from unbalanced evidence review. | S4 | P3 | High |
| HAZ-010 | Software defect or workflow error allows protocol to be exported or applied without clinician review. | Patient receives protocol that was never reviewed by a qualified professional. | S5 | P2 | High |
| HAZ-011 | Protocol modification or approval not recorded in audit log due to system error. | Unable to trace clinical decisions for adverse event investigation or regulatory audit. | S3 | P2 | Low |
| HAZ-012 | Database failure causes loss of generated protocol or review records. | Clinical continuity disrupted. Historical treatment data unavailable. | S3 | P2 | Low |
| HAZ-013 | Unauthorized user accesses patient records or modifies protocol parameters. | HIPAA/GDPR violation. Potential for unauthorized treatment modifications. | S4 | P2 | Medium |
| HAZ-014 | Clinician references an older version of a protocol that has been superseded. Applies outdated parameters. | Treatment based on parameters that were subsequently corrected or updated. | S3 | P3 | Medium |
| HAZ-015 | EEG analysis algorithm misclassifies patient phenotype, leading to inappropriate protocol personalization. (V2 feature) | Suboptimal or contraindicated stimulation parameters for the patient's actual neurophysiological state. | S4 | P3 | High |
| HAZ-016 | System assigns high confidence score to a recommendation based on a single small pilot study. Clinician relies on the confidence rating. | Over-reliance on weak evidence. Potential for harm from insufficiently supported parameters. | S3 | P4 | Medium |
| HAZ-017 | Generated protocol specifies incorrect electrode montage (e.g., reversed anode/cathode placement). | Opposite stimulation polarity. Inhibition where excitation intended, or vice versa. | S4 | P3 | High |
| HAZ-018 | Clinician requests protocol for a condition not in the supported list. System generates output without clear indication that the condition is unsupported. | Protocol based on insufficient or absent condition-specific evidence. | S3 | P3 | Medium |
| HAZ-019 | Patient is receiving concurrent tDCS and taVNS protocols. System does not flag combined treatment interaction risks. | Cumulative stimulation effects, increased adverse event risk. | S4 | P2 | Medium |
| HAZ-020 | Malicious or malformed input in a clinical note field causes the LLM to generate a protocol with unsafe parameters. | Patient harm from adversarially corrupted protocol. | S5 | P1 | Medium |

---

## 5. Risk Control Measures

### 5.1 Risk Control Summary

| Hazard ID | Control Type | Control Measure | Implementation Location | Verification Method |
|---|---|---|---|---|
| HAZ-001 | Design | Condition-to-target mapping validated against curated evidence database. LLM output constrained to approved target list per condition-modality pair. | Protocol generation engine, target validation module | Unit test: verify all 15 conditions map to evidence-backed targets. Integration test: confirm out-of-range targets are rejected. |
| HAZ-002 | Design | Parameter bounds engine enforces hard limits per modality (e.g., tDCS: 0.5--2.0 mA, 10--30 min; TPS: per manufacturer specification). Any parameter outside bounds is blocked, not merely flagged. | Safety engine, parameter validation layer | Unit test: verify all boundary conditions. Penetration test: attempt to generate protocol exceeding bounds. |
| HAZ-003 | Design | Contraindication database checked for every condition-modality-patient combination. Absolute contraindications block protocol generation. Relative contraindications generate mandatory warnings. | Safety engine, contraindication module | Test against known contraindication list. Verify blocking behavior for absolute contraindications. |
| HAZ-004 | Design | Medication interaction database cross-referenced during protocol generation. Known interactions flagged with severity level and citation. | Safety engine, medication interaction module | Test against pharmacological interaction database. Verify flag generation for known interactions. |
| HAZ-005 | Design | Off-label status automatically determined by comparing condition-modality pair against regulatory clearance database. Off-label protocols flagged and routed to four-eyes review. | Safety engine, regulatory status module | Test each condition-modality pair for correct label/off-label classification. |
| HAZ-006 | Design | Patient age validated at protocol generation. System rejects requests for patients under 18. Population-specific parameters tagged in evidence database. | Protocol generation engine, patient validation | Test: attempt generation for age 16, verify rejection. Test: verify adult-only literature used. |
| HAZ-007 | Design | Evidence staleness detection: publications older than configurable threshold (default: 5 years) flagged. System prioritizes recent systematic reviews and meta-analyses. Staleness indicator visible in protocol output. | Evidence pipeline, staleness detection module | Test: verify staleness flag on publications older than threshold. Verify sort order prioritizes recent evidence. |
| HAZ-008 | Design | PMID validation against PubMed API for every cited reference. DOI validation against CrossRef. Citations that fail validation are excluded from protocol evidence chain and logged. | Evidence pipeline, PMID/DOI validation service | Test: inject fabricated PMIDs, verify exclusion. Test: verify all citations in generated protocols resolve to real publications. |
| HAZ-009 | Design | QA engine presents all retrieved evidence, including contradicting studies. Contradicting evidence explicitly labeled and quantified (e.g., "3 of 7 studies report no significant effect"). Clinician review screen displays evidence for and against. | QA engine, evidence presentation layer | Test: inject contradicting evidence, verify it appears in output. Review UI test: confirm contradicting evidence visible. |
| HAZ-010 | Design | Mandatory review gate: protocol cannot transition to "approved" or "exportable" state without authenticated clinician review action. Four-eyes approval required for high-risk protocols. No API endpoint permits bypassing review. | Workflow engine, state machine, API authorization | Test: attempt to export protocol without review, verify rejection. Security test: attempt direct API call to bypass review state. |
| HAZ-011 | Design | Immutable append-only audit log for all protocol lifecycle events (generation, review, modification, approval, rejection, export). Log entries include timestamp, user identity, action, and changed values. | Audit service, database layer | Test: perform all lifecycle actions, verify audit log completeness. Test: attempt to modify existing log entry, verify rejection. |
| HAZ-012 | Design | Database replication with automated failover. Daily backups with point-in-time recovery. Backup restoration tested quarterly. | Infrastructure, database configuration | Quarterly backup restoration test. Verify replication lag monitoring. |
| HAZ-013 | Design | Authentication required for all access. Role-based access control (RBAC) with principle of least privilege. Session timeout after 30 minutes of inactivity. Encryption at rest and in transit. | Authentication service, RBAC module, infrastructure | Penetration test: attempt unauthorized access. Test: verify session timeout. Verify encryption configuration. |
| HAZ-014 | Design | Protocol versioning with clear version identifiers. Active version prominently displayed. Superseded versions marked as such. Export always uses current approved version. | Protocol management, version control module | Test: create multiple versions, verify only current version is exportable. Verify superseded versions display warning. |
| HAZ-015 | Design | EEG analysis confidence scoring. Low-confidence phenotype classifications flagged to clinician with recommendation to verify with clinical assessment. Phenotype override capability for clinician. (V2) | EEG analysis module, confidence scoring | Test: inject ambiguous EEG data, verify low-confidence flag. Verify clinician override functionality. |
| HAZ-016 | Design | Evidence confidence scoring based on study design hierarchy, sample size, replication status, and recency. Single-study recommendations capped at "Low" confidence regardless of study quality. Confidence methodology visible to clinician. | Evidence pipeline, confidence scoring engine | Test: verify single-study evidence scores "Low". Test: verify meta-analysis scores higher than individual RCT. Verify scoring methodology displayed. |
| HAZ-017 | Design | Electrode montage validated against condition-specific montage library. Anode/cathode positions cross-referenced with target region. Visual montage diagram included in protocol output for clinician verification. | Protocol generation engine, montage validation | Test: verify montage correctness for all condition-modality pairs. Test: attempt to generate reversed montage, verify correction or flag. |
| HAZ-018 | Design | Condition validation against supported condition list. Unsupported conditions rejected with clear error message. No fallback generation for unsupported conditions. | Protocol generation engine, condition validation | Test: request protocol for unsupported condition, verify rejection and error message. |
| HAZ-019 | Design | Concurrent protocol detection: system queries active protocols for the patient before generation. Concurrent stimulation protocols flagged with interaction warning. (V2 -- requires patient management module) | Safety engine, patient protocol registry | Test: create two concurrent protocols for same patient, verify interaction flag. |
| HAZ-020 | Design | Input sanitization on all user-facing fields. LLM system prompt hardened against injection. Output validation against parameter bounds (same as HAZ-002). Anomaly detection on generated parameters. | Input validation layer, LLM prompt engineering, output validation | Penetration test: attempt prompt injection via clinical note fields. Verify output validation catches anomalous parameters. |

### 5.2 Key Control Categories

| Control Category | Controls Applied | Hazards Mitigated |
|---|---|---|
| PMID / DOI Validation | Automated validation of every citation against source database | HAZ-008 |
| Safety Engine | Contraindication check, medication interaction check, parameter bounds enforcement | HAZ-002, HAZ-003, HAZ-004, HAZ-019 |
| Mandatory Clinician Review | Protocol cannot be finalized without authenticated clinician review | HAZ-001, HAZ-005, HAZ-006, HAZ-009, HAZ-010, HAZ-017 |
| Four-Eyes Approval | Second independent clinician review for high-risk protocols | HAZ-005, HAZ-010, HAZ-015 |
| QA Engine | Evidence balance presentation, contradicting evidence surfacing | HAZ-009, HAZ-016 |
| Parameter Bounds | Hard limits per modality, blocking (not warning) for out-of-range values | HAZ-002, HAZ-017, HAZ-020 |
| Audit Log | Immutable append-only record of all protocol lifecycle events | HAZ-011, HAZ-014 |
| Staleness Detection | Publication age flagging, recency prioritization | HAZ-007 |
| Confidence Scoring | Multi-factor evidence confidence with single-study ceiling | HAZ-016 |

---

## 6. Residual Risk Assessment

### 6.1 Residual Risk by Hazard

| Hazard ID | Residual Severity | Residual Probability | Residual Risk Level | Justification |
|---|---|---|---|---|
| HAZ-001 | S4 | P1 | Low | Curated target mapping plus mandatory clinician review. Clinicians are trained to verify stimulation targets. |
| HAZ-002 | S5 | P1 | Medium | Hard parameter bounds prevent out-of-range values. Clinician review provides second check. Residual risk from parameters within bounds but suboptimal for individual patient accepted given clinician oversight. |
| HAZ-003 | S5 | P1 | Medium | Contraindication database coverage may be incomplete for rare conditions. Clinician remains responsible for patient-specific contraindication assessment. |
| HAZ-004 | S4 | P2 | Medium | Medication interaction database may not cover all substances. Clinician pharmacological knowledge provides additional safety layer. |
| HAZ-005 | S3 | P2 | Low | Automated off-label detection plus four-eyes review for flagged protocols. |
| HAZ-006 | S3 | P1 | Low | Age validation at input. Adult-only evidence filtering. |
| HAZ-007 | S3 | P2 | Low | Staleness flagging plus clinician awareness of evidence currency. |
| HAZ-008 | S4 | P1 | Low | PMID/DOI validation eliminates fabricated citations. Residual risk limited to valid PMIDs cited out of context, mitigated by clinician evidence review. |
| HAZ-009 | S4 | P1 | Low | QA engine requires presentation of contradicting evidence. Residual risk from evidence not retrieved by search, mitigated by multi-source search strategy. |
| HAZ-010 | S5 | P1 | Medium | Mandatory review gate enforced at API level. No bypass mechanism exists by design. Residual risk from implementation defect, mitigated by security testing. |
| HAZ-011 | S3 | P1 | Low | Immutable audit log with integrity verification. |
| HAZ-012 | S3 | P1 | Low | Replication, automated backup, tested restoration. |
| HAZ-013 | S4 | P1 | Low | Authentication, RBAC, encryption, session management, penetration testing. |
| HAZ-014 | S3 | P1 | Low | Version control with superseded version marking. |
| HAZ-015 | S4 | P2 | Medium | Confidence scoring and clinician override. (V2 -- risk assessment to be updated upon implementation.) |
| HAZ-016 | S3 | P2 | Low | Confidence scoring methodology with single-study ceiling. Scoring visible to clinician. |
| HAZ-017 | S4 | P1 | Low | Montage validation against curated library plus visual diagram for clinician verification. |
| HAZ-018 | S3 | P1 | Low | Condition validation rejects unsupported conditions at input. |
| HAZ-019 | S4 | P1 | Low | Concurrent protocol detection with interaction flagging. (V2) |
| HAZ-020 | S5 | P1 | Medium | Input sanitization, prompt hardening, output validation. Residual risk from novel attack vectors, mitigated by ongoing security testing. |

### 6.2 Overall Residual Risk Assessment

After implementation of all identified risk controls, no individual hazard carries an unacceptable residual risk level. Five hazards (HAZ-002, HAZ-003, HAZ-004, HAZ-010, HAZ-020) retain a "Medium" residual risk level. For each, the benefit-risk analysis is favorable:

- The residual risk is primarily theoretical, requiring simultaneous failure of multiple independent controls (automated safety checks AND clinician review).
- The clinical benefit of standardized, evidence-based protocol generation with safety checking outweighs the residual risk when clinician-in-the-loop controls are functioning as designed.
- HAZ-015 (EEG misinterpretation) is a V2 feature and will undergo separate risk assessment before implementation.

The overall residual risk of the Sozo Protocol Generator is **acceptable** given the implemented controls and the mandatory clinician-in-the-loop architecture.

---

## 7. Risk Management Review

### 7.1 Review Schedule

- Pre-release review: Before each major version release
- Periodic review: Annually, or upon any of the following triggers:
  - Reported adverse event or near-miss
  - Significant software architecture change
  - Addition of new conditions, modalities, or features (e.g., V2 EEG integration)
  - Change in regulatory requirements or guidance
  - Post-market surveillance findings

### 7.2 Post-Market Surveillance Inputs

- Clinician feedback and reported issues
- Protocol rejection rates and rejection reasons
- Safety flag override rates
- Adverse event reports
- Literature monitoring for new contraindications or safety signals

---

## 8. Document Control

| Action | Name | Date |
|---|---|---|
| Prepared by | | 2026-04-03 |
| Reviewed by | | |
| Approved by | | |

---

*This document is controlled. Printed copies are for reference only. The current version is maintained in the document management system.*
