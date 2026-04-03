# Software Requirements Specification

**Document ID:** SOZO-REG-SRS-001
**Version:** 1.0
**Date:** 2026-04-03
**Classification:** Regulatory
**Status:** Draft
**Applicable Standard:** IEC 62304:2006+AMD1:2015 -- Medical device software -- Software life cycle processes
**Software Safety Classification:** Class B

---

## 1. Scope

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for the Sozo Protocol Generator, a clinical decision support software tool for neuromodulation protocol generation. Requirements are traceable to the risk management file (SOZO-REG-RMF-001) and the intended use statement (SOZO-REG-IUS-001).

---

## 2. Requirement Format

Each requirement follows this structure:

> **REQ-XXX-NNN:** Requirement statement
> - **Priority:** Must | Should | May
> - **Phase:** MVP | V2 | V3
> - **Verification:** Test | Inspection | Analysis
> - **Trace:** HAZ-NNN (where applicable)

---

## 3. Functional Requirements

### 3.1 Protocol Generation (REQ-FUN-001 through REQ-FUN-020)

**REQ-FUN-001:** The system shall accept a condition selection from the set of 15 supported conditions (Parkinson's G20, Depression F32, Anxiety F41.1, ADHD F90, Alzheimer's G30, Stroke I69, TBI S09.90, Chronic Pain M79.7, PTSD F43.1, OCD F42, MS G35, ASD F84.0, Long COVID U09.9, Tinnitus H93.1, Insomnia G47.0).
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-018

**REQ-FUN-002:** The system shall accept a modality selection from the set of 4 supported modalities (tDCS, TPS, taVNS, CES).
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-018

**REQ-FUN-003:** The system shall reject protocol generation requests for condition-modality combinations not present in the supported configuration and return a clear error message to the user.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-018

**REQ-FUN-004:** The system shall generate a complete protocol containing: target brain region(s), stimulation parameters (intensity, duration, frequency where applicable), electrode montage or stimulation site, number of sessions, and session frequency.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-001, HAZ-002, HAZ-017

**REQ-FUN-005:** The system shall map each supported condition-modality pair to one or more evidence-backed stimulation targets from a curated target database.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-001

**REQ-FUN-006:** The system shall enforce hard parameter bounds per modality: tDCS intensity 0.5--2.0 mA, tDCS duration 10--30 minutes; TPS per manufacturer specification; taVNS intensity 0.1--5.0 mA, taVNS frequency 1--30 Hz; CES intensity 0.1--4.0 mA, CES frequency 0.5--100 Hz.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-002

**REQ-FUN-007:** The system shall block (not merely warn) any generated protocol with parameters outside the defined bounds.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-002

**REQ-FUN-008:** The system shall include a rationale section in each generated protocol explaining the evidence basis for each parameter choice.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-009

**REQ-FUN-009:** The system shall attach at least one validated citation (PMID or DOI) to each primary parameter recommendation in the protocol.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-008

**REQ-FUN-010:** The system shall generate a visual electrode montage diagram (or stimulation site specification) for each protocol.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-017

**REQ-FUN-011:** The system shall accept optional clinician-provided notes or context as input to the protocol generation process.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

**REQ-FUN-012:** The system shall sanitize all clinician-provided free-text input before processing to prevent prompt injection or system manipulation.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-020

**REQ-FUN-013:** The system shall accept optional file uploads (clinical notes, prior protocols) as supplementary input to protocol generation.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-020

**REQ-FUN-014:** The system shall validate uploaded file types and reject unsupported or potentially malicious file formats.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-020

**REQ-FUN-015:** The system shall generate protocols using structured prompts that constrain LLM output to the defined parameter schema.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Inspection
- **Trace:** HAZ-001, HAZ-002, HAZ-020

**REQ-FUN-016:** The system shall validate LLM-generated output against the protocol schema before presenting to the clinician.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-001, HAZ-002

**REQ-FUN-017:** The system shall assign a unique identifier to each generated protocol.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-014

**REQ-FUN-018:** The system shall record the software version, model version, and evidence database version used for each protocol generation.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-014

**REQ-FUN-019:** The system shall support batch generation of protocols across multiple conditions for the same modality.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

**REQ-FUN-020:** The system shall generate protocol output in both structured data format (JSON) and human-readable document format (DOCX/PDF).
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

### 3.2 Evidence Management (REQ-FUN-021 through REQ-FUN-035)

**REQ-FUN-021:** The system shall search PubMed via the NCBI E-utilities API for relevant publications when generating protocols.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-007

**REQ-FUN-022:** The system shall search CrossRef for DOI metadata and citation data.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-008

**REQ-FUN-023:** The system shall search Semantic Scholar for citation graph data and paper metadata.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-009

**REQ-FUN-024:** The system shall deduplicate retrieved publications based on PMID, DOI, and title similarity before evidence synthesis.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

**REQ-FUN-025:** The system shall score each retrieved publication based on study design hierarchy (systematic review > RCT > cohort > case series > case report > expert opinion).
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-016

**REQ-FUN-026:** The system shall validate every cited PMID against the PubMed API and confirm the publication exists and matches the attributed title and authors.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-008

**REQ-FUN-027:** The system shall validate every cited DOI against the CrossRef API.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-008

**REQ-FUN-028:** The system shall exclude from protocol evidence chains any citation that fails PMID or DOI validation and log the exclusion.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-008

**REQ-FUN-029:** The system shall flag publications older than 5 years (configurable threshold) with a staleness indicator visible in the protocol output.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-007

**REQ-FUN-030:** The system shall prioritize recent systematic reviews and meta-analyses in evidence ranking when available.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-007

**REQ-FUN-031:** The system shall present both supporting and contradicting evidence for each protocol parameter to the reviewing clinician.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-009

**REQ-FUN-032:** The system shall quantify the balance of evidence (e.g., "5 of 8 studies support this parameter; 3 report no significant effect").
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-009

**REQ-FUN-033:** The system shall assign a confidence score (High, Moderate, Low, Very Low) to each protocol recommendation based on evidence quantity, quality, consistency, and recency.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-016

**REQ-FUN-034:** The system shall cap the confidence score at "Low" for any recommendation supported by a single study regardless of study quality.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-016

**REQ-FUN-035:** The system shall display the confidence scoring methodology to the clinician upon request.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-016

### 3.3 Safety (REQ-FUN-036 through REQ-FUN-050)

**REQ-FUN-036:** The system shall maintain a contraindication database covering absolute and relative contraindications for each supported modality.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Inspection
- **Trace:** HAZ-003

**REQ-FUN-037:** The system shall check every generated protocol against the contraindication database for the selected condition-modality pair.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-003

**REQ-FUN-038:** The system shall block protocol generation when an absolute contraindication is identified and display the contraindication to the clinician.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-003

**REQ-FUN-039:** The system shall generate a mandatory warning when a relative contraindication is identified, requiring clinician acknowledgment before proceeding.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-003

**REQ-FUN-040:** The system shall maintain a medication interaction database covering drugs known to alter seizure threshold, stimulation response, or neuromodulation safety.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Inspection
- **Trace:** HAZ-004

**REQ-FUN-041:** The system shall accept a patient medication list as input and cross-reference it against the medication interaction database during protocol generation.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-004

**REQ-FUN-042:** The system shall flag identified medication interactions with severity level (major, moderate, minor) and the supporting citation.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-004

**REQ-FUN-043:** The system shall automatically determine off-label status for each condition-modality pair based on regulatory clearance data.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-005

**REQ-FUN-044:** The system shall flag off-label protocols with a visible indicator and route them to four-eyes review.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-005

**REQ-FUN-045:** The system shall validate patient age at protocol generation and reject requests for patients under 18 years of age.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-006

**REQ-FUN-046:** The system shall filter evidence to adult populations (18+) and exclude pediatric-only studies from protocol generation.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-006

**REQ-FUN-047:** The system shall detect when a patient has concurrent active protocols for different modalities and generate an interaction warning.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-019

**REQ-FUN-048:** The system shall include a safety summary section in each generated protocol listing all identified contraindications, medication interactions, off-label status, and safety flags.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-003, HAZ-004, HAZ-005

**REQ-FUN-049:** The system shall log all safety engine decisions (checks performed, results, flags generated) in the audit trail.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-011

**REQ-FUN-050:** The system shall support clinician override of relative contraindication warnings with mandatory rationale documentation.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-003

### 3.4 Review Workflow (REQ-FUN-051 through REQ-FUN-060)

**REQ-FUN-051:** The system shall enforce a mandatory clinician review step before any protocol can transition to "approved" or "exportable" status.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-010

**REQ-FUN-052:** The system shall require clinician authentication (username and password or equivalent) at the review approval step.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-010

**REQ-FUN-053:** The system shall enforce four-eyes approval (two independent clinician reviews) for protocols flagged as off-label, high-risk, or low-confidence.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-005, HAZ-010, HAZ-015

**REQ-FUN-054:** The system shall prevent the same clinician from serving as both first and second reviewer in the four-eyes process.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-010

**REQ-FUN-055:** The system shall display all source citations, confidence scores, evidence quality assessments, safety flags, and contradicting evidence to the reviewer at the point of review.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-009, HAZ-016

**REQ-FUN-056:** The system shall allow the reviewing clinician to modify any protocol parameter, with the modification logged in the audit trail including the original value, new value, and clinician-provided rationale.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-011

**REQ-FUN-057:** The system shall allow the reviewing clinician to reject a protocol entirely, with a mandatory rejection rationale recorded in the audit trail.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-011

**REQ-FUN-058:** The system shall support a QA override process where a designated QA reviewer can request regeneration of a protocol with specific guidance.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-009

**REQ-FUN-059:** The system shall track protocol status through defined lifecycle states: Draft, Under Review, Approved, Rejected, Superseded, Archived.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-014

**REQ-FUN-060:** The system shall provide no mechanism (UI or API) to export or apply a protocol that has not completed the required review process.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-010

### 3.5 Patient Management (REQ-FUN-061 through REQ-FUN-075)

**REQ-FUN-061:** The system shall support creation and storage of patient records with demographics (name, date of birth, sex, medical record number).
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-006

**REQ-FUN-062:** The system shall calculate patient age from date of birth and validate against the 18+ age requirement at protocol generation.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-006

**REQ-FUN-063:** The system shall support recording of patient diagnoses with ICD-10 codes.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-018

**REQ-FUN-064:** The system shall support recording of patient medication lists with drug name, dosage, and indication.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-004

**REQ-FUN-065:** The system shall automatically cross-reference the patient medication list against the medication interaction database when generating a protocol for that patient.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-004

**REQ-FUN-066:** The system shall support recording of patient contraindications (e.g., metallic implants, epilepsy history, pregnancy).
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-003

**REQ-FUN-067:** The system shall automatically cross-reference patient contraindications against the contraindication database when generating a protocol for that patient.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-003

**REQ-FUN-068:** The system shall support recording of clinical assessments (standardized scales, clinician notes) associated with a patient.
- **Priority:** Should
- **Phase:** V2
- **Verification:** Test
- **Trace:** --

**REQ-FUN-069:** The system shall maintain a treatment history for each patient showing all protocols generated, reviewed, approved, rejected, and applied.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-014, HAZ-019

**REQ-FUN-070:** The system shall display the patient's treatment history to the clinician during protocol generation and review.
- **Priority:** Should
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-019

**REQ-FUN-071:** The system shall support recording of adverse events associated with a patient and protocol.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** --

**REQ-FUN-072:** The system shall flag patients with recorded adverse events during subsequent protocol generation for the same modality.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-003

**REQ-FUN-073:** The system shall support patient search by name, medical record number, or ICD-10 diagnosis code.
- **Priority:** Should
- **Phase:** V2
- **Verification:** Test
- **Trace:** --

**REQ-FUN-074:** The system shall encrypt all patient data at rest using AES-256 or equivalent.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Inspection
- **Trace:** HAZ-013

**REQ-FUN-075:** The system shall enforce access control on patient records such that only authorized clinicians can view or modify patient data.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-013

### 3.6 EEG and Personalization (REQ-FUN-076 through REQ-FUN-090)

**REQ-FUN-076:** The system shall accept EEG data uploads in standard formats (EDF, EDF+, BDF).
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-077:** The system shall validate uploaded EEG file format and reject corrupted or unsupported files with a clear error message.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-078:** The system shall perform automated EEG analysis to extract relevant features (power spectral density, connectivity metrics, event-related potentials where applicable).
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-079:** The system shall classify EEG phenotypes based on extracted features using validated classification algorithms.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-080:** The system shall assign a confidence score to each EEG phenotype classification and display it to the clinician.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-081:** The system shall flag low-confidence EEG classifications with a recommendation to verify with clinical assessment.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-082:** The system shall allow clinician override of EEG-derived phenotype classification with rationale documentation.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-083:** The system shall match EEG phenotypes to condition-specific protocol modifications based on published phenotype-response evidence.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-084:** The system shall present phenotype-matched protocol modifications as recommendations, not automatic changes, requiring clinician approval.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015

**REQ-FUN-085:** The system shall display the evidence basis for phenotype-to-protocol matching decisions.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-015, HAZ-016

**REQ-FUN-086:** The system shall support longitudinal EEG comparison to track changes in phenotype across treatment sessions.
- **Priority:** Should
- **Phase:** V3
- **Verification:** Test
- **Trace:** --

**REQ-FUN-087:** The system shall support integration of questionnaire-based phenotyping (e.g., symptom profiles) as a complement to EEG data.
- **Priority:** Should
- **Phase:** V2
- **Verification:** Test
- **Trace:** --

**REQ-FUN-088:** The system shall maintain a phenotype-response evidence database linking EEG phenotypes to treatment outcomes from published studies.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Inspection
- **Trace:** HAZ-015

**REQ-FUN-089:** The system shall record all EEG analysis parameters, phenotype classifications, and personalization decisions in the audit trail.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-011

**REQ-FUN-090:** The system shall validate that EEG-derived protocol modifications remain within the defined parameter bounds.
- **Priority:** Must
- **Phase:** V2
- **Verification:** Test
- **Trace:** HAZ-002

---

## 4. Non-Functional Requirements

### 4.1 Performance (REQ-NFR-001 through REQ-NFR-005)

**REQ-NFR-001:** The system shall complete protocol generation (from request to output ready for review) within 60 seconds under normal operating conditions.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

**REQ-NFR-002:** The system shall complete evidence search and retrieval within 30 seconds per query.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

**REQ-NFR-003:** The system shall render all UI pages within 2 seconds of request under normal operating conditions.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

**REQ-NFR-004:** The system shall support at least 50 concurrent users without performance degradation below the specified thresholds.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

**REQ-NFR-005:** The system shall process batch protocol generation (up to 15 conditions for one modality) within 15 minutes.
- **Priority:** Should
- **Phase:** MVP
- **Verification:** Test
- **Trace:** --

### 4.2 Security (REQ-NFR-006 through REQ-NFR-012)

**REQ-NFR-006:** The system shall require authentication for all user access. Anonymous access shall not be permitted for any functionality.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-013

**REQ-NFR-007:** The system shall implement role-based access control (RBAC) with at minimum the following roles: Administrator, Clinician, Reviewer, Read-Only.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-013

**REQ-NFR-008:** The system shall encrypt all data in transit using TLS 1.2 or higher.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Inspection
- **Trace:** HAZ-013

**REQ-NFR-009:** The system shall encrypt all data at rest using AES-256 or equivalent.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Inspection
- **Trace:** HAZ-013

**REQ-NFR-010:** The system shall terminate user sessions after 30 minutes of inactivity.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-013

**REQ-NFR-011:** The system shall log all authentication events (login, logout, failed attempts) in the audit trail.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-011, HAZ-013

**REQ-NFR-012:** The system shall enforce password complexity requirements: minimum 12 characters, including uppercase, lowercase, numeric, and special characters.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-013

### 4.3 Reliability (REQ-NFR-013 through REQ-NFR-016)

**REQ-NFR-013:** The system shall maintain 99.5% uptime measured on a monthly basis, excluding scheduled maintenance windows.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Analysis
- **Trace:** --

**REQ-NFR-014:** The system shall implement graceful degradation when external services (PubMed, CrossRef, Semantic Scholar) are unavailable, using cached evidence and notifying the clinician of reduced evidence coverage.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-007

**REQ-NFR-015:** The system shall perform automated daily database backups with point-in-time recovery capability.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Inspection
- **Trace:** HAZ-012

**REQ-NFR-016:** The system shall test backup restoration on a quarterly basis with documented results.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Inspection
- **Trace:** HAZ-012

### 4.4 Traceability and Audit (REQ-NFR-017 through REQ-NFR-020)

**REQ-NFR-017:** The system shall maintain an immutable, append-only audit log of all protocol lifecycle events including generation, review, modification, approval, rejection, and export.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-011

**REQ-NFR-018:** Each audit log entry shall contain: timestamp (UTC), user identity, action performed, affected resource identifier, and changed values (before and after) where applicable.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-011

**REQ-NFR-019:** The system shall prevent modification or deletion of existing audit log entries.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-011

**REQ-NFR-020:** The system shall support audit log export in a machine-readable format (JSON or CSV) for regulatory review purposes.
- **Priority:** Must
- **Phase:** MVP
- **Verification:** Test
- **Trace:** HAZ-011

---

## 5. SOUP (Software of Unknown Provenance) List

The following third-party software components are used in the Sozo Protocol Generator. Each component is assessed for its contribution to the software safety classification.

| # | Component | Version | Purpose | License | Safety Contribution | Risk Control |
|---|---|---|---|---|---|---|
| 1 | Python | 3.11.x | Runtime environment | PSF | Foundation for all processing | Version pinned, security patches monitored |
| 2 | FastAPI | 0.100+ | Web framework, API layer | MIT | Handles all HTTP requests including safety-critical endpoints | Input validation, dependency updates monitored |
| 3 | Pydantic | 2.x | Data validation and serialization | MIT | Schema enforcement for protocol parameters | Validates all input/output data structures |
| 4 | LangGraph | 0.x | LLM orchestration and workflow | MIT | Controls protocol generation workflow | Prompt engineering, output validation |
| 5 | Anthropic SDK | 0.x | Claude API client | MIT | LLM inference for protocol generation | Output validation, parameter bounds checking |
| 6 | python-docx | 0.8+ | DOCX document generation | MIT | Protocol export formatting | Output only, no safety-critical function |
| 7 | SQLAlchemy | 2.x | Database ORM | MIT | Data persistence for protocols, audit logs | Data integrity, transaction management |
| 8 | Alembic | 1.x | Database migration management | MIT | Schema versioning | Migration testing before deployment |
| 9 | PostgreSQL | 15+ | Relational database | PostgreSQL License | Persistent storage for all application data | Replication, backup, encryption at rest |
| 10 | httpx | 0.24+ | HTTP client for external API calls | BSD | PubMed, CrossRef, Semantic Scholar queries | Timeout configuration, error handling |
| 11 | uvicorn | 0.23+ | ASGI server | BSD | Application server | TLS configuration, security headers |
| 12 | React | 18.x | Frontend framework | MIT | Clinician user interface | Client-side only, all validation server-side |
| 13 | Next.js | 14.x | Frontend framework / SSR | MIT | Application routing, server-side rendering | Security headers, CSRF protection |
| 14 | Redis | 7.x | Caching and session management | BSD | Evidence caching, session storage | Cache invalidation, session timeout enforcement |
| 15 | Docker | 24.x | Containerization | Apache 2.0 | Deployment packaging | Image scanning, minimal base images |

### SOUP Monitoring Process

- All SOUP components are monitored for security vulnerabilities via automated dependency scanning (e.g., Dependabot, Snyk).
- Critical and high-severity vulnerabilities in SOUP components shall be assessed within 48 hours of disclosure and patched within 14 days.
- SOUP component updates are tested in a staging environment before production deployment.

---

## 6. Traceability Matrix

### 6.1 Requirements to Hazards

| Requirement | Hazard(s) |
|---|---|
| REQ-FUN-001, REQ-FUN-002, REQ-FUN-003 | HAZ-018 |
| REQ-FUN-004, REQ-FUN-005 | HAZ-001 |
| REQ-FUN-006, REQ-FUN-007 | HAZ-002 |
| REQ-FUN-008, REQ-FUN-031, REQ-FUN-032 | HAZ-009 |
| REQ-FUN-009, REQ-FUN-026, REQ-FUN-027, REQ-FUN-028 | HAZ-008 |
| REQ-FUN-010, REQ-FUN-004 (montage) | HAZ-017 |
| REQ-FUN-012, REQ-FUN-014, REQ-FUN-015 | HAZ-020 |
| REQ-FUN-016, REQ-FUN-015 | HAZ-001, HAZ-002 |
| REQ-FUN-017, REQ-FUN-018, REQ-FUN-059 | HAZ-014 |
| REQ-FUN-021, REQ-FUN-029, REQ-FUN-030 | HAZ-007 |
| REQ-FUN-025, REQ-FUN-033, REQ-FUN-034, REQ-FUN-035 | HAZ-016 |
| REQ-FUN-036 through REQ-FUN-039, REQ-FUN-050 | HAZ-003 |
| REQ-FUN-040 through REQ-FUN-042 | HAZ-004 |
| REQ-FUN-043, REQ-FUN-044 | HAZ-005 |
| REQ-FUN-045, REQ-FUN-046 | HAZ-006 |
| REQ-FUN-047 | HAZ-019 |
| REQ-FUN-051 through REQ-FUN-054, REQ-FUN-060 | HAZ-010 |
| REQ-FUN-055 | HAZ-009, HAZ-016 |
| REQ-FUN-056, REQ-FUN-057, REQ-FUN-049 | HAZ-011 |
| REQ-FUN-061, REQ-FUN-062, REQ-FUN-046 | HAZ-006 |
| REQ-FUN-064, REQ-FUN-065 | HAZ-004 |
| REQ-FUN-066, REQ-FUN-067, REQ-FUN-072 | HAZ-003 |
| REQ-FUN-069, REQ-FUN-070 | HAZ-014, HAZ-019 |
| REQ-FUN-074, REQ-FUN-075 | HAZ-013 |
| REQ-FUN-076 through REQ-FUN-085, REQ-FUN-088, REQ-FUN-090 | HAZ-015 |
| REQ-FUN-089 | HAZ-011 |
| REQ-FUN-090 | HAZ-002 |
| REQ-NFR-006 through REQ-NFR-012 | HAZ-013 |
| REQ-NFR-014 | HAZ-007 |
| REQ-NFR-015, REQ-NFR-016 | HAZ-012 |
| REQ-NFR-017 through REQ-NFR-020 | HAZ-011 |

### 6.2 Requirements to Design Components

| Design Component | Requirements |
|---|---|
| Protocol Generation Engine | REQ-FUN-001 through REQ-FUN-020 |
| Evidence Pipeline | REQ-FUN-021 through REQ-FUN-035 |
| Safety Engine | REQ-FUN-036 through REQ-FUN-050 |
| Review Workflow Engine | REQ-FUN-051 through REQ-FUN-060 |
| Patient Management Module (V2) | REQ-FUN-061 through REQ-FUN-075 |
| EEG Analysis Module (V2) | REQ-FUN-076 through REQ-FUN-090 |
| Authentication / RBAC Service | REQ-NFR-006 through REQ-NFR-012 |
| Audit Service | REQ-NFR-017 through REQ-NFR-020 |
| Infrastructure / DevOps | REQ-NFR-001 through REQ-NFR-005, REQ-NFR-013 through REQ-NFR-016 |

### 6.3 Requirements to Verification

| Verification Type | Requirements |
|---|---|
| Unit Test | REQ-FUN-001 through REQ-FUN-007, REQ-FUN-016, REQ-FUN-024 through REQ-FUN-028, REQ-FUN-033, REQ-FUN-034, REQ-FUN-037, REQ-FUN-038, REQ-FUN-045, REQ-FUN-046 |
| Integration Test | REQ-FUN-009, REQ-FUN-021 through REQ-FUN-023, REQ-FUN-041, REQ-FUN-065, REQ-FUN-067 |
| System Test | REQ-FUN-051 through REQ-FUN-060, REQ-NFR-001 through REQ-NFR-005 |
| Security Test | REQ-FUN-012, REQ-FUN-014, REQ-FUN-020 (HAZ-020), REQ-NFR-006 through REQ-NFR-012 |
| Inspection | REQ-FUN-015, REQ-FUN-036, REQ-FUN-040, REQ-NFR-008, REQ-NFR-009, REQ-NFR-015, REQ-NFR-016 |
| Analysis | REQ-NFR-013 |

---

## 7. Document Control

| Action | Name | Date |
|---|---|---|
| Prepared by | | 2026-04-03 |
| Reviewed by | | |
| Approved by | | |

---

*This document is controlled. Printed copies are for reference only. The current version is maintained in the document management system.*
