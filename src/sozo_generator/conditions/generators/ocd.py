"""
Obsessive-Compulsive Disorder (OCD) — Complete condition generator.

Key references:
- Mondino M et al. (2015) Effects of cathodal tDCS over right DLPFC on OCD — Brain Stimulation. PMID: 25612915
- Bation R et al. (2016) tDCS in OCD: a pilot study — Progress in Neuro-Psychopharmacology. PMID: 26773527
- Grassi G et al. (2018) tDCS augments SMA inhibition in OCD — CNS Spectrums. PMID: 28338325
- Goodman WK et al. (1989) Yale-Brown Obsessive Compulsive Scale — Archives of General Psychiatry. PMID: 2684084
- Rotge JY et al. (2008) Provocation of OCD symptoms with neuroimaging — Molecular Psychiatry. PMID: 17955036
"""
import logging
from ...schemas.condition import (
    ConditionSchema, PhenotypeSubtype, NetworkProfile,
    StimulationTarget, AssessmentTool, SafetyNote, ProtocolEntry
)
from ...core.enums import (
    NetworkKey, NetworkDysfunction, Modality, EvidenceLevel
)
from ...core.utils import current_date_str
from ..shared_condition_schema import (
    make_network, make_tdcs_target, make_tps_target, make_safety,
    SHARED_ABSOLUTE_CONTRAINDICATIONS, SHARED_SAFETY_NOTES, SHARED_GOVERNANCE_RULES
)

logger = logging.getLogger(__name__)


def build_ocd_condition() -> ConditionSchema:
    """Build the complete OCD condition schema."""
    return ConditionSchema(
        slug="ocd",
        display_name="Obsessive-Compulsive Disorder",
        icd10="F42",
        aliases=["OCD", "obsessive-compulsive", "obsessions and compulsions", "OC spectrum"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Obsessive-Compulsive Disorder (OCD) is a psychiatric disorder characterized by recurrent, "
            "intrusive obsessions (unwanted thoughts, urges, or images causing marked distress) and/or "
            "compulsions (repetitive behaviors or mental acts performed to reduce obsession-related "
            "anxiety). Lifetime prevalence is approximately 2-3%. OCD is classified among the most "
            "disabling psychiatric conditions (WHO top 10 disabling conditions).\n\n"
            "OCD neurobiological model: a hyperactive cortico-striato-thalamo-cortical (CSTC) loop "
            "drives compulsive behavior. The orbitofrontal cortex (OFC), anterior cingulate cortex (ACC), "
            "and caudate nucleus are hyperactive, producing excessive error signaling and 'not done' "
            "feelings that drive repetitive checking and rituals. 40-60% of OCD patients fail to "
            "adequately respond to first-line treatments (SSRIs + CBT with ERP).\n\n"
            "Neuromodulation targets: (1) right DLPFC cathodal tDCS to inhibit the hyperactive "
            "cortico-striatal loop; (2) supplementary motor area (SMA) cathodal tDCS to reduce "
            "motor compulsion generation; (3) taVNS as adjunct for OCD with anxiety/mood comorbidity."
        ),

        pathophysiology=(
            "OCD pathophysiology centers on hyperactivity of the cortico-striato-thalamo-cortical "
            "(CSTC) loop. Key nodes: orbitofrontal cortex (OFC, responsible for error signaling and "
            "excessive 'checking' drive), anterior cingulate cortex (ACC, conflict monitoring and "
            "'not done' signal generation), caudate nucleus (habit formation and compulsive behavior "
            "entrenchment), and mediodorsal thalamus (gating and loop amplification).\n\n"
            "Three parallel CSTC circuit types are implicated: (1) the 'direct pathway' is "
            "hyperactive, driving excessive thalamocortical activation; (2) the 'indirect pathway' "
            "is hypofunctional in OCD, failing to provide normal brake mechanisms; (3) both produce "
            "net excessive loop activity. Serotonin modulates CSTC tone — explaining SSRI efficacy.\n\n"
            "Neuroimaging: hyperactivation of OFC-caudate during symptom provocation is the most "
            "replicated finding (Rotge et al. 2008 meta-analysis). SMA hyperactivation contributes "
            "to motor compulsions. Successful treatment (CBT or SSRI) normalizes OFC-caudate "
            "hyperactivation. tDCS mechanism: cathodal inhibition of DLPFC or SMA may modulate "
            "prefrontal-striatal circuit excitability and reduce OFC hyperactivity via top-down "
            "connectivity."
        ),

        core_symptoms=[
            "Obsessions — recurrent, persistent, intrusive thoughts, urges, or images",
            "Compulsions — repetitive behaviors (checking, washing, ordering, counting) or mental acts performed to neutralize obsessions",
            "Marked anxiety and distress from obsessions",
            "Significant time consumption (>1 hour/day) or marked functional impairment",
            "Insight variability — good, fair, poor, or absent insight",
        ],

        non_motor_symptoms=[
            "Comorbid depression (50-60% lifetime)",
            "Comorbid anxiety disorders (generalized anxiety, panic, social anxiety)",
            "Tic disorders (Tourette's co-occurrence ~30% of childhood OCD)",
            "Body dysmorphic disorder (OCD spectrum)",
            "Hoarding disorder (OCD spectrum)",
            "Sleep disturbance",
        ],

        key_brain_regions=[
            "Orbitofrontal Cortex (OFC) — lateral and medial",
            "Anterior Cingulate Cortex (ACC) / Subgenual ACC",
            "Caudate Nucleus (bilateral)",
            "Supplementary Motor Area (SMA) / pre-SMA",
            "Mediodorsal Thalamus",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
        ],

        brain_region_descriptions={
            "Orbitofrontal Cortex (OFC) — lateral and medial": "Hyperactive in OCD — generates excessive 'not done' error signals and drives repetitive checking compulsions. OFC-caudate hyperactivation is the most replicated neuroimaging finding.",
            "Anterior Cingulate Cortex (ACC) / Subgenual ACC": "Conflict monitoring and error amplification. Hyperactive dACC drives excessive awareness of potential harm, fueling obsession-compulsion cycle.",
            "Caudate Nucleus (bilateral)": "Habit formation and compulsive behavior entrenchment in OCD. Caudate hyperactivation in OFC-striatal loop. Normalizes with successful treatment.",
            "Supplementary Motor Area (SMA) / pre-SMA": "Motor compulsion generation. SMA hyperactivation in OCD with predominant motor compulsions (washing, checking, ordering). Cathodal tDCS target for SMA inhibition.",
            "Mediodorsal Thalamus": "Gating node in CSTC loop. Hyperactivity amplifies OFC-ACC-caudate circuit activity in OCD.",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Top-down regulatory control over OFC-caudate loop. Right DLPFC cathodal tDCS may modulate DLPFC-OFC balance to reduce compulsive drive.",
        },

        network_profiles=[
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN OCD. The CEN is abnormally hyperactive in OCD — specifically the "
                "orbitofrontal-striatal loop produces excessive error signaling and compulsive behavior. "
                "Unlike most conditions where CEN is hypoactive, OCD shows an overactive but "
                "dysfunctional prefrontal-striatal circuit generating excessive top-down compulsive "
                "drive. tDCS targets cathodal inhibition to reduce CSTC hyperactivity.",
                primary=True, severity="severe",
                evidence_note="OFC-caudate hyperactivation meta-analysis; Rotge et al. 2008; CSTC loop model",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "SN hyperactivation (ACC, anterior insula) drives the excessive 'harm threat' salience "
                "that underlies OCD obsessions. Aberrant salience attribution to neutral stimuli "
                "triggers obsessive cycles. Insula hyperreactivity contributes to contamination "
                "obsessions and disgust response.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Limbic hyperactivity — amygdala and hippocampus — amplifies the anxiety and distress "
                "associated with obsessions. High comorbidity of depression (50-60%) and anxiety "
                "reflects limbic network involvement in OCD.",
                severity="moderate",
                evidence_note="OCD-anxiety-depression comorbidity; shared limbic mechanisms",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation in OCD contributes to excessive self-referential intrusive thoughts, "
                "ego-dystonic obsessions, and ruminative cognitive patterns. DMN-CEN connectivity "
                "abnormalities are documented in OCD resting-state fMRI.",
                severity="mild-moderate",
            ),
        ],

        primary_network=NetworkKey.CEN,

        fnon_rationale=(
            "In OCD, the CSTC loop is hyperactive — unlike most conditions where the target network "
            "is hypoactive, OCD requires INHIBITORY modulation of key nodes. The FNON framework "
            "deploys: (1) cathodal right DLPFC tDCS to suppress hyperactive prefrontal-striatal drive; "
            "(2) cathodal SMA tDCS to directly inhibit motor compulsion generation; (3) taVNS as "
            "adjunct for OCD with significant anxiety and mood comorbidity via vagal-limbic modulation."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="cont",
                label="CONT — Contamination/Washing",
                description="Contamination obsessions (germs, dirt, disease) driving excessive washing, cleaning, or avoidance. Most prevalent OCD symptom dimension.",
                key_features=["Contamination obsessions", "Excessive washing/cleaning", "Avoidance of 'contaminated' objects", "Disgust sensitivity"],
                primary_networks=[NetworkKey.CEN, NetworkKey.SN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Right DLPFC cathodal (F4) + left DLPFC anodal",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="check",
                label="CHECK — Checking",
                description="Doubt-based obsessions (harm, incompleteness) driving repetitive checking behaviors. Incompleteness/'not-done' feeling prominent.",
                key_features=["Harm obsessions", "Excessive checking", "'Not done' feelings", "Doubt"],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.SN],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Right DLPFC cathodal OR SMA cathodal",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="symm",
                label="SYMM — Symmetry/Ordering",
                description="Need for symmetry, exactness, and 'just right' feelings driving ordering, arranging, and counting rituals. Strong motor compulsion component.",
                key_features=["Symmetry obsessions", "Ordering/arranging rituals", "'Just right' compulsions", "Counting"],
                primary_networks=[NetworkKey.CEN, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="SMA cathodal — motor compulsion inhibition",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="intru",
                label="INTRU — Intrusive Thoughts",
                description="Ego-dystonic intrusive thoughts (taboo, aggressive, sexual, or religious) without prominent behavioral compulsions. Mental neutralization prominent.",
                key_features=["Ego-dystonic intrusive thoughts", "Mental compulsions (neutralization)", "Taboo/aggressive/sexual content", "Guilt and shame"],
                primary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS],
                tdcs_target="Right DLPFC cathodal + taVNS for anxiety",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="hoard",
                label="HOARD — Hoarding",
                description="Difficulty discarding possessions and excessive acquisition. OCD spectrum condition with distinct circuitry from classic OCD.",
                key_features=["Excessive acquisition", "Difficulty discarding", "Cluttered living spaces", "Significant distress at discarding"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.CEN],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Left DLPFC anodal for decision-making enhancement",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="ybocs",
                name="Yale-Brown Obsessive Compulsive Scale",
                abbreviation="Y-BOCS",
                domains=["obsession_severity", "compulsion_severity", "total_ocd_severity"],
                timing="baseline",
                evidence_pmid="2684084",
                notes="Gold standard OCD severity scale. Clinician-administered. Score /40. Score 0-7=subclinical; 8-15=mild; 16-23=moderate; 24-31=severe. MCID = 35% reduction.",
            ),
            AssessmentTool(
                scale_key="ocir",
                name="Obsessive-Compulsive Inventory — Revised",
                abbreviation="OCI-R",
                domains=["washing", "checking", "ordering", "obsessing", "hoarding", "neutralizing"],
                timing="baseline",
                evidence_pmid="12014669",
                notes="Self-report OCD measure. 18 items, 0-4 scale. Score >=21 = probable OCD. Useful for symptom dimension profiling across the five OCD dimensions.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Depression comorbidity monitoring. Mandatory — 50-60% OCD-depression comorbidity.",
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Anxiety comorbidity monitoring. OCD with prominent anxiety features may benefit from taVNS adjunct.",
            ),
        ],

        baseline_measures=[
            "Y-BOCS (clinician-administered — primary OCD severity measure)",
            "OCI-R (self-report — symptom dimension profiling)",
            "PHQ-9 (depression comorbidity)",
            "GAD-7 (anxiety comorbidity)",
            "SOZO PRS (OCD symptoms, anxiety, mood, functioning — 0-10)",
        ],

        followup_measures=[
            "Y-BOCS at Week 4 and Week 8-10",
            "OCI-R at Week 4 and Week 8-10",
            "PHQ-9 at every session",
            "SOZO PRS at each session and end of block",
        ],

        inclusion_criteria=[
            "DSM-5 diagnosis of OCD",
            "Y-BOCS score >=16 (moderate severity)",
            "Age 18-65 years",
            "Capacity to provide informed consent",
            "Stable SSRI/medication regimen for >=8 weeks (or medication-naive)",
        ],

        exclusion_criteria=[
            "Active psychosis or psychotic features",
            "Bipolar disorder Type I",
            "Current active suicidal ideation with plan",
            "Severe personality disorder as primary diagnosis",
            "Active severe substance use disorder",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "Monitor for paradoxical OCD symptom exacerbation in early sessions — cathodal DLPFC tDCS may initially increase awareness of obsessional content before habituating. Brief psychoeducation and reassurance may be required.",
                "moderate",
                "Clinical experience in OCD neuromodulation; cortical excitability change dynamics",
            ),
            make_safety(
                "monitoring",
                "Document OCI-R and PHQ-9 at every session. OCD patients with treatment-resistant presentations have elevated suicide risk. Monitor for emerging suicidality.",
                "moderate",
                "OCD suicidality epidemiology; clinical monitoring requirement",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Right Dorsolateral Prefrontal Cortex (Cathodal)", "R-DLPFC", "right",
                "Cathodal tDCS over right DLPFC inhibits hyperactive CSTC loop by reducing prefrontal "
                "drive to OFC-striatal circuit. Mondino et al. (2015) demonstrated right DLPFC cathodal "
                "tDCS significantly reduced OCD symptoms (Y-BOCS). Bation et al. (2016) confirmed "
                "pilot RCT evidence. NOTE: cathode is placed at F4 for inhibitory effect. OFF-LABEL.",
                "C-OCD-R — Right DLPFC Cathodal Inhibition",
                EvidenceLevel.MEDIUM, off_label=True,
                eeg_canonical=["F4"],
            ),
            make_tdcs_target(
                "Supplementary Motor Area (Cathodal)", "SMA", "bilateral",
                "SMA cathodal tDCS directly inhibits motor compulsion generation in OCD with predominant "
                "motor compulsions (washing, checking, ordering). Grassi et al. (2018) demonstrated "
                "SMA tDCS augmentation effect in OCD. OFF-LABEL.",
                "C-OCD-SMA — SMA Cathodal Motor Inhibition",
                EvidenceLevel.LOW, off_label=True,
                eeg_canonical=["Fz", "FCz"],
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS modulates limbic anxiety and noradrenergic tone via NTS-LC pathways. "
                          "Adjunct for OCD with prominent anxiety and mood comorbidity. Investigational "
                          "in OCD — no dedicated RCT published.",
                protocol_label="TAVNS-OCD — Anxiety & Limbic Adjunct",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                eeg_canonical=["Ear"],
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-OCD-R", label="Right DLPFC Cathodal — OCD Inhibition Protocol", modality=Modality.TDCS,
                target_region="Right Dorsolateral Prefrontal Cortex", target_abbreviation="R-DLPFC",
                phenotype_slugs=["cont", "check", "intru"],
                network_targets=[NetworkKey.CEN, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "F4 (right DLPFC) — INHIBITORY PLACEMENT",
                    "anode": "F3 (left DLPFC) or Fp1 (left supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "20-30 min",
                    "sessions": "10-15 over 3 weeks",
                    "electrode_size": "35 cm2",
                    "note": "IMPORTANT: Cathodal electrode at F4 (inhibitory). This is REVERSED from standard depression montage.",
                },
                rationale="Cathodal right DLPFC tDCS inhibits hyperactive prefrontal drive to OFC-striatal "
                          "CSTC loop, reducing compulsion generation. Mondino et al. (2015, Brain Stimulation) "
                          "demonstrated significant Y-BOCS reduction with right DLPFC cathodal tDCS vs sham. "
                          "Bation et al. (2016) pilot RCT confirmed efficacy. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C-OCD-SMA", label="SMA Cathodal — Motor Compulsion Inhibition", modality=Modality.TDCS,
                target_region="Supplementary Motor Area", target_abbreviation="SMA",
                phenotype_slugs=["check", "symm"],
                network_targets=[NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "Cz (SMA / vertex approximation)",
                    "anode": "Iz (inion) or shoulder reference",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "SMA cathodal targeting — Cz electrode placement for motor compulsion inhibition",
                },
                rationale="SMA cathodal tDCS directly reduces motor compulsion generation for OCD with "
                          "prominent motor rituals. Grassi et al. (2018) demonstrated augmented SMA "
                          "inhibition with cathodal tDCS in OCD. Adjunct or alternative to DLPFC protocol. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-OCD", label="taVNS — Anxiety & Mood Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["intru", "cont"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 us",
                    "intensity": "Below pain threshold",
                    "duration": "30 min",
                    "sessions": "Daily adjunct",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS modulates anxiety and noradrenergic limbic tone as adjunct for OCD with "
                          "prominent anxiety and depression comorbidity. Investigational in OCD.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational in OCD. Adjunct only.",
            ),
        ],

        symptom_network_mapping={
            "Obsessions (intrusive thoughts)": [NetworkKey.CEN, NetworkKey.DMN],
            "Compulsions (motor rituals)": [NetworkKey.CEN, NetworkKey.SN],
            "Anxiety associated with obsessions": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Depression comorbidity": [NetworkKey.LIMBIC, NetworkKey.CEN],
        },

        symptom_modality_mapping={
            "Obsessions (intrusive thoughts)": [Modality.TDCS],
            "Compulsions (motor rituals)": [Modality.TDCS],
            "Anxiety associated with obsessions": [Modality.TAVNS, Modality.CES, Modality.TDCS],
            "Depression comorbidity": [Modality.TDCS, Modality.CES],
        },

        responder_criteria=[
            ">=35% reduction in Y-BOCS total score from baseline (OCD treatment response criterion)",
            "Y-BOCS score <16 (mild range — partial remission)",
            "Clinically meaningful SOZO PRS improvement in OCD symptoms domain",
        ],

        non_responder_pathway=(
            "For non-responders at Week 4:\n"
            "1. Confirm SSRI adequacy — subtherapeutic SSRI dose limits neuromodulation response\n"
            "2. Ensure concurrent ERP/CBT is in place\n"
            "3. Switch from DLPFC cathodal to SMA cathodal if motor compulsions predominate\n"
            "4. Add taVNS for anxiety/mood comorbidity\n"
            "5. Doctor psychiatric review for SSRI dose escalation or augmentation"
        ),

        evidence_summary=(
            "OCD neuromodulation has emerging-to-moderate evidence. Mondino et al. (2015) Brain "
            "Stimulation: right DLPFC cathodal tDCS significantly reduced Y-BOCS vs sham (N=12). "
            "Bation et al. (2016) pilot RCT confirmed efficacy. Grassi et al. (2018) SMA cathodal "
            "augmentation study is positive. All studies are small — larger RCTs urgently needed. "
            "| Evidence counts (published papers): TMS=100, DBS=50, tDCS=10, taVNS=5, LIFU=3. "
            "Best modalities: TMS (Deep/H7), DBS (VC/VS)."
        ),

        evidence_gaps=[
            "Small sample sizes in all published tDCS OCD trials — no adequately powered multi-site RCT",
            "Head-to-head comparison of DLPFC cathodal vs SMA cathodal vs combined — no comparative study",
            "taVNS in OCD — no published RCT",
            "Long-term OCD symptom maintenance after tDCS — limited follow-up data",
        ],

        references=[
            {
                "authors": "Mondino M et al.",
                "year": 2015,
                "title": "Effects of transcranial direct current stimulation on obsessive-compulsive disorder: a pilot study",
                "journal": "Brain Stimulation",
                "pmid": "25612915",
                "evidence_type": "pilot_study",
            },
            {
                "authors": "Bation R et al.",
                "year": 2016,
                "title": "Transcranial direct current stimulation in treatment-refractory obsessive-compulsive disorder: an open-label pilot study",
                "journal": "Progress in Neuro-Psychopharmacology and Biological Psychiatry",
                "pmid": "26773527",
                "evidence_type": "pilot_study",
            },
            {
                "authors": "Grassi G et al.",
                "year": 2018,
                "title": "tDCS of supplementary motor area augments its inhibitory role in compulsive behavior",
                "journal": "CNS Spectrums",
                "pmid": "28338325",
                "evidence_type": "rct",
            },
            {
                "authors": "Goodman WK et al.",
                "year": 1989,
                "title": "The Yale-Brown Obsessive Compulsive Scale: I. Development, use, and reliability",
                "journal": "Archives of General Psychiatry",
                "pmid": "2684084",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "IMPORTANT: Right DLPFC cathodal montage — cathode is at F4 (inhibitory). This is the REVERSE of the standard depression montage where anode is at F3.",
            "Coordinate with treating psychiatrist regarding SSRI optimization — inadequate pharmacotherapy limits neuromodulation efficacy",
            "Brief psychoeducation about possible initial symptom fluctuation in early sessions before improvement",
            "Monitor PHQ-9 — OCD-depression comorbidity is high and undertreated depression impairs OCD treatment response",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES,
    )
