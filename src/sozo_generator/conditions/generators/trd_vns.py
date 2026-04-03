"""
Treatment-Resistant Depression — Implantable VNS (Window 5).

Condition : TRD (Treatment-Resistant Depression)
Modality  : Implantable Vagus Nerve Stimulation (LivaNova SenTiva)
ICD-10    : F33.9 (recurrent MDD, unspecified)

Key evidence base:
- Aaronson ST et al. (2022) RECOVER Trial — JAMA Psychiatry   [PMID 35196370]
- Rush AJ et al. (2005)  D-21 pivotal RCT    — Biol Psychiatry [PMID 15963590]
- Sackeim HA et al. (2007) D-23 registry     — Biol Psychiatry [PMID 17235374]
- Conway CR et al. (2018) VNS long-term TRD  — J Affect Disord [PMID 29709762]
- Berry SM et al. (2013) Bayesian adaptive    — Biol Psychiatry [PMID 23773819]
- LivaNova SenTiva IFU (Model 1000) — Device labelling
- FDA Approval (July 2005): PMA P970003S050 — Adjunct TRD ≥4 failed trials

Window 5 subagent map:
  01 Surgical candidacy screener  → phenotypes + inclusion/exclusion
  02 Titration schedule generator → protocol parameters + clinical_tips
  03 Long-term outcome modeler    → responder_criteria + patient_journey_notes
  04 Device-spec extractor        → protocol parameters (LivaNova SenTiva)
  05 Adverse-event profile agent  → safety_notes
  06 BMT comparator builder       → evidence_summary + patient_journey_notes
  07 Time-to-response calculator  → responder_criteria + non_responder_pathway
  08 Remission durability tracker → patient_journey_notes + clinical_tips
  09 Cost-effectiveness analyzer  → clinical_tips + governance_rules
  10 Patient selection optimizer  → phenotypes + inclusion/exclusion
"""
import logging
from ...schemas.condition import (
    ConditionSchema, PhenotypeSubtype, NetworkProfile,
    StimulationTarget, AssessmentTool, SafetyNote, ProtocolEntry,
)
from ...core.enums import (
    NetworkKey, NetworkDysfunction, Modality, EvidenceLevel,
)
from ...core.utils import current_date_str
from ..shared_condition_schema import (
    make_network, make_safety,
    SHARED_GOVERNANCE_RULES,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# VNS-specific contraindications (replaces shared non-invasive list)
# ---------------------------------------------------------------------------
VNS_ABSOLUTE_CONTRAINDICATIONS = [
    "Prior bilateral or right cervical vagotomy (prevents left-lead placement)",
    "Active cardiac arrhythmia or heart block not cleared by cardiologist",
    "Active implanted cardiac device that cannot be cleared for VNS co-use (evaluate device-device interaction with LivaNova DFT protocol)",
    "Obstructive sleep apnea severe enough to preclude supine surgical positioning without optimisation",
    "Active or recent cervical surgery with documented vagus nerve injury",
    "Active CNS neoplasm or recent cranial surgery (relative — neurosurgery co-evaluation required)",
    "Pregnancy — insufficient safety data for implantable neurostimulator",
    "Current manic or mixed episode (bipolar) — stabilise mood before implantation",
    "Active suicidal crisis requiring immediate ECT or inpatient intervention — defer implant",
]

VNS_GOVERNANCE_RULES = SHARED_GOVERNANCE_RULES + [
    "VNS implantation must be performed by a credentialed neurosurgeon or ENT surgeon trained on LivaNova SenTiva systems",
    "Post-implant device activation must not occur before wound review at Day 14",
    "All titration adjustments must be authorised and logged by the supervising psychiatrist",
    "Patient magnet must be dispensed with written protocol for clinical use",
    "Annual device interrogation (battery/lead impedance) is mandatory; document in records",
    "RECOVER-protocol monitoring: MADRS and HDRS-24 at baseline, Month 3, 6, 9, 12, then 6-monthly",
]


def _make_vns_target(
    region: str,
    abbr: str,
    laterality: str,
    rationale: str,
    protocol_label: str | None = None,
    evidence_level: EvidenceLevel = EvidenceLevel.HIGH,
) -> StimulationTarget:
    return StimulationTarget(
        modality=Modality.VNS,
        target_region=region,
        target_abbreviation=abbr,
        laterality=laterality,
        rationale=rationale,
        protocol_label=protocol_label,
        evidence_level=evidence_level,
        off_label=False,   # FDA-approved for TRD since 2005
        consent_required=True,
    )


def build_trd_vns_condition() -> ConditionSchema:
    """
    Build the complete TRD-VNS condition schema.

    Implements all 10 Window-5 subagents as structured schema fields:
    clinical content, device specs, titration schedule, phenotype selection,
    BMT comparator, time-to-response model, durability data, AE profile,
    cost-effectiveness notes, and governance.
    """
    return ConditionSchema(
        slug="trd_vns",
        display_name="Treatment-Resistant Depression — Implantable VNS",
        icd10="F33.9",
        aliases=[
            "TRD", "treatment-resistant depression", "VNS TRD",
            "vagus nerve stimulation depression", "LivaNova TRD",
            "implantable VNS", "refractory depression",
        ],
        version="1.0",
        generated_at=current_date_str(),

        # ── Overview ────────────────────────────────────────────────────────
        overview=(
            "Treatment-Resistant Depression (TRD) is defined operationally as failure to achieve "
            "adequate response (≥50% symptom reduction or remission) after two or more adequate "
            "antidepressant trials of sufficient dose and duration within the current depressive "
            "episode. Approximately 30-40% of MDD patients meet TRD criteria at some stage, with "
            "treatment resistance increasing with each failed trial. The FDA approved Vagus Nerve "
            "Stimulation (VNS) Therapy as an adjunctive long-term treatment for TRD in July 2005 "
            "(PMA P970003S050), indicated for adults with recurrent, chronic depression (MDD or "
            "bipolar depression) who have failed ≥4 adequate antidepressant trials.\n\n"
            "The landmark RECOVER trial (Aaronson et al. 2022, JAMA Psychiatry) — the first "
            "prospective, randomised, blinded, active-control trial for VNS in TRD — demonstrated "
            "67.6% response vs 40.2% with best medical therapy (BMT) alone at 12 months (NNT ≈ 3.7), "
            "with 43.3% remission vs 25.7% BMT. VNS's defining characteristic is its slow-onset, "
            "durable effect profile: minimal response in the first 3 months, meaningful separation "
            "from BMT by Month 6, and continued antidepressant benefit at 5+ years — a pattern "
            "that stands in contrast to the rapid but often transient efficacy of ECT."
        ),

        pathophysiology=(
            "VNS modulates depression through ascending vagal afferent projections to the brainstem "
            "nucleus tractus solitarius (NTS). From NTS, noradrenergic signals propagate via the "
            "locus coeruleus (LC) to widespread cortical and limbic regions, and serotonergic "
            "signals via raphe nuclei. Key downstream effects:\n\n"
            "1. LIMBIC MODULATION: NTS projects directly to the amygdala, hippocampus, and "
            "orbitofrontal cortex — the primary pathways for VNS antidepressant action. Chronic "
            "VNS reduces amygdala hyperreactivity and promotes hippocampal neurogenesis (BDNF "
            "upregulation), reversing core limbic abnormalities of TRD.\n\n"
            "2. NORADRENERGIC ENHANCEMENT: Vagal afferents activate LC neurons, increasing NE "
            "release across prefrontal, cingulate, and limbic circuits. LC-NE enhancement "
            "underpins cognitive improvement, antidepressant effect, and resilience restoration. "
            "This mechanism mirrors (and may augment) the action of SNRIs and TCAs.\n\n"
            "3. DEFAULT MODE NETWORK (DMN) NORMALISATION: Chronic VNS reduces pathological DMN "
            "hyperactivation — the neuroimaging hallmark of depressive rumination — via vmPFC and "
            "sgACC modulation downstream of the LC-NE and raphe-5HT cascades.\n\n"
            "4. ANTI-INFLAMMATORY EFFECTS: Vagal efferents activate the cholinergic anti-inflammatory "
            "reflex, suppressing TNF-α, IL-6, and CRP — inflammatory biomarkers elevated in a "
            "significant TRD subgroup. This may explain preferential response in inflammatory-TRD "
            "phenotypes.\n\n"
            "5. NEUROPLASTICITY: Long-term VNS increases BDNF, promotes synaptogenesis, and "
            "partially reverses stress-induced dendritic atrophy in the hippocampus and PFC — "
            "consistent with the slow, accumulating response time course seen clinically."
        ),

        core_symptoms=[
            "Persistent depressed mood refractory to ≥4 pharmacological trials",
            "Profound anhedonia — loss of pleasure and motivational drive",
            "Severe psychomotor retardation or (less commonly) agitation",
            "Profound fatigue and anergia",
            "Cognitive impairment: poor concentration, slowed processing, working memory failure",
            "Neurovegetative symptoms: insomnia/hypersomnia, anorexia/hyperphagia, weight change",
            "Pervasive hopelessness and learned helplessness",
            "Suicidal ideation (passive or active) — elevated risk in TRD vs non-TRD",
            "Social and occupational dysfunction (severe; GAF typically <50 in chronic TRD)",
        ],

        non_motor_symptoms=[
            "Chronic pain comorbidity (30-50% TRD patients)",
            "Anxiety comorbidity (comorbid anxiety disorder in 60-70%)",
            "Alcohol/substance use disorder (co-occurring in ~20%)",
            "Metabolic side-effects from prior pharmacotherapy (weight gain, dyslipidemia)",
            "Cognitive blunting from chronic antidepressant exposure",
            "Sleep architecture disruption (reduced REM, fragmented sleep)",
        ],

        # ── Anatomy ─────────────────────────────────────────────────────────
        key_brain_regions=[
            "Left Cervical Vagus Nerve (CN X) — stimulation site",
            "Nucleus Tractus Solitarius (NTS) — primary brainstem relay",
            "Locus Coeruleus (LC) — noradrenergic amplification node",
            "Raphe Nuclei (dorsal, median) — serotonergic modulation",
            "Amygdala (bilateral) — primary limbic target",
            "Hippocampus (bilateral) — neuroplasticity and BDNF upregulation site",
            "Subgenual Anterior Cingulate Cortex (sgACC / Cg25)",
            "Ventromedial Prefrontal Cortex (vmPFC)",
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC)",
            "Anterior Insula (bilateral)",
        ],

        brain_region_descriptions={
            "Left Cervical Vagus Nerve (CN X) — stimulation site": (
                "Left vagus preferred to minimise cardiac effects (right vagus carries more "
                "sinoatrial fibres). Helical electrode wrapped around the vagus at C3-C5 level. "
                "~80% of vagal fibres are afferent (ascending), providing the therapeutic signal pathway."
            ),
            "Nucleus Tractus Solitarius (NTS)": (
                "Primary brainstem relay for ascending vagal signals. Projects to LC, raphe, "
                "parabrachial nucleus, and directly to amygdala via the central nucleus. "
                "NTS activation is the first-order event in VNS antidepressant mechanism."
            ),
            "Locus Coeruleus (LC)": (
                "Noradrenergic nucleus that projects diffusely to prefrontal cortex, limbic system, "
                "and cerebellum. Chronic VNS increases LC firing rate and NE release, driving "
                "downstream antidepressant and pro-cognitive effects."
            ),
            "Raphe Nuclei (dorsal, median)": (
                "Serotonergic nuclei receiving indirect NTS input. Chronic VNS increases dorsal "
                "raphe 5-HT activity, augmenting serotonergic antidepressant tone. Provides "
                "mechanistic basis for VNS + SSRI/SNRI combination benefit."
            ),
            "Amygdala (bilateral)": (
                "Hyperreactive in TRD; receives direct NTS projection. VNS reduces amygdala "
                "volume and reactivity to negative stimuli over months of treatment — correlating "
                "with emotional processing improvement."
            ),
            "Hippocampus (bilateral)": (
                "Target for VNS-induced BDNF upregulation and neurogenesis. Hippocampal volume "
                "loss in recurrent MDD is partially reversible with chronic VNS. Memory and "
                "contextual regulation improvement correlates with hippocampal neuroplasticity."
            ),
            "Subgenual Anterior Cingulate Cortex (sgACC / Cg25)": (
                "Hyperactive in TRD; normalised by chronic VNS via NTS→LC→vmPFC cascades. "
                "sgACC is the DBS target for TRD (Mayberg); VNS achieves similar network "
                "normalisation through the ascending pathway rather than direct stimulation."
            ),
            "Ventromedial Prefrontal Cortex (vmPFC)": (
                "DMN hub; receives vagal afferent modulation via thalamic relays. Reduced "
                "vmPFC-sgACC coupling after chronic VNS is associated with decreased rumination "
                "and improved emotional regulation."
            ),
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC)": (
                "Consistently hypoactive in MDD/TRD. VNS increases DLPFC perfusion and activity "
                "via LC-NE pathway — similar mechanism to tDCS but pharmacological rather than "
                "electrical at the cortical level."
            ),
            "Anterior Insula (bilateral)": (
                "SN node; modulates interoception and emotional salience. VNS normalises insula "
                "hyperactivation in TRD, contributing to reduced anxiety, pain, and somatic symptoms."
            ),
        },

        # ── FNON Networks ────────────────────────────────────────────────────
        network_profiles=[
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "PRIMARY VNS TARGET NETWORK. Amygdala hyperreactivity, hippocampal dysfunction, "
                "and HPA-axis dysregulation underpin the chronic affective and neurovegetative "
                "symptoms of TRD. VNS directly modulates limbic structures via NTS→amygdala "
                "projections and indirectly via LC-NE and raphe-5HT cascades. Limbic normalisation "
                "is the primary mechanism of VNS antidepressant effect.",
                primary=True, severity="severe",
                evidence_note="NTS→amygdala direct projection; George et al. 2000, Conway et al. 2018",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation (sgACC, vmPFC, medial parietal cortex) drives pathological "
                "self-referential rumination in TRD. Chronic VNS normalises DMN via vmPFC and "
                "sgACC modulation downstream of the LC-NE cascade. DMN normalisation correlates "
                "with clinical antidepressant response at 6-12 months.",
                severity="severe",
                evidence_note="fMRI: Nahas et al. 2007; Bajbouj et al. 2010 show DMN normalisation with VNS",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Prefrontal CEN hypoactivation (L-DLPFC) impairs cognitive control, working memory, "
                "and top-down suppression of limbic hyperactivity in TRD. VNS upregulates DLPFC "
                "activity via LC-NE pathway, improving cognitive function and treatment response. "
                "Cognitive improvement with VNS is a secondary but clinically significant outcome.",
                severity="severe",
                evidence_note="LC-NE→DLPFC pathway; cognitive outcomes: Sackeim et al. 2007",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Anterior insula and dACC hyperactivity drives aberrant salience attribution and "
                "impaired network switching in TRD. VNS normalises insula activity and may restore "
                "SN-mediated switching between DMN and CEN. SN normalisation correlates with "
                "reduction in anxiety, pain perception, and somatic symptoms.",
                severity="moderate",
                evidence_note="Insula modulation by VNS: Nahas et al. 2007; SN model: Menon 2011",
            ),
        ],
        primary_network=NetworkKey.LIMBIC,
        fnon_rationale=(
            "VNS for TRD targets the LIMBIC network as its primary therapeutic node via direct "
            "NTS→amygdala projection and indirect NTS→LC→NE and NTS→raphe→5HT cascades. This "
            "ascending vagal neuromodulation achieves broad network rebalancing — normalising DMN "
            "hyperactivity, restoring CEN prefrontal function, and reducing SN-mediated aberrant "
            "salience — without direct cortical electrode placement. The temporal profile of VNS "
            "effect (peak response at 6-12 months, durability at 5+ years) reflects the slow "
            "neuroplastic and neurotrophic mechanisms (BDNF upregulation, synaptogenesis, limbic "
            "volume restoration) that underpin durable remission, distinguishing VNS from both "
            "pharmacotherapy and acute neuromodulation approaches."
        ),

        # ── Phenotypes (Subagent 01 + 10: Surgical candidacy + Patient selection) ──
        phenotypes=[
            PhenotypeSubtype(
                slug="classic_trd",
                label="Classic TRD — ≥4 Failed Antidepressant Trials (FDA Indication)",
                description=(
                    "Standard FDA label: recurrent MDD or bipolar depression with ≥4 failed adequate "
                    "antidepressant trials (different mechanisms, adequate dose × duration). This is the "
                    "primary VNS indication and the population studied in RECOVER. Best response data "
                    "available. Surgical candidacy assessment should confirm trial adequacy per ATHF "
                    "(Antidepressant Treatment History Form) criteria."
                ),
                key_features=[
                    "≥4 documented adequate antidepressant trials (at minimum 2 different mechanisms)",
                    "Current MDE in context of recurrent MDD (F33.x) or bipolar depression",
                    "Chronic or highly recurrent illness (typically ≥2 years current episode or ≥3 lifetime episodes)",
                    "Stable on current BMT (no trial changes within 4 weeks of implant assessment)",
                    "No acute suicidal crisis (stable enough for elective surgery)",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                secondary_networks=[NetworkKey.CEN, NetworkKey.SN],
                preferred_modalities=[Modality.VNS],
                tdcs_target=None,
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="trd_ect_failure",
                label="TRD Post-ECT — Failure or Relapse After Electroconvulsive Therapy",
                description=(
                    "Patients who failed to respond to ECT or relapsed after initial ECT response. "
                    "This group represents the highest treatment-resistance burden and highest unmet "
                    "need. VNS provides slow-onset, durable benefit that complements (not replaces) "
                    "maintenance ECT or pharmacotherapy. ECT failure/relapse should be documented. "
                    "Patient must be stable enough for elective surgical implant."
                ),
                key_features=[
                    "Prior ECT course (≥6 sessions) with inadequate response OR relapse within 6 months of ECT remission",
                    "≥4 failed pharmacological trials (ECT counts as one somatic trial, not as antidepressant)",
                    "Typically chronic, highly recurrent MDD (≥5 lifetime episodes or ≥3 years current)",
                    "Often cognitively impaired post-ECT — assess baseline cognition before titration",
                    "High VNS response evidence: RECOVER subgroup analysis favoured ECT-failure patients",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.VNS],
                tdcs_target=None,
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="melancholic_trd",
                label="Melancholic TRD — Psychomotor Retardation Dominant",
                description=(
                    "Melancholic subtype of TRD characterised by prominent psychomotor retardation, "
                    "anhedonia, early morning awakening, diurnal mood variation, and often HPA-axis "
                    "hyperactivity (elevated cortisol). Strong VNS evidence in D-23 registry (Sackeim "
                    "et al. 2007): melancholic features predicted preferential VNS response. HPA "
                    "normalisation by VNS (via vagal efferents → cholinergic anti-inflammatory → "
                    "cortisol modulation) may explain the preferential efficacy."
                ),
                key_features=[
                    "Pervasive anhedonia (absence of mood reactivity)",
                    "Psychomotor retardation (objectively observed; HDRS item 8 score ≥2)",
                    "Diurnal mood variation (worse in morning)",
                    "Early morning awakening (≥2 hours earlier than habitual)",
                    "Elevated morning cortisol or failed DST suppression (if tested)",
                    "Often responds poorly to psychotherapy alone; somatic treatment required",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                secondary_networks=[NetworkKey.CEN, NetworkKey.SN],
                preferred_modalities=[Modality.VNS],
                tdcs_target=None,
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="anxious_trd",
                label="Anxious TRD — High Anxiety Comorbidity",
                description=(
                    "TRD with prominent anxious features (panic, GAD, social anxiety) or comorbid "
                    "anxiety disorder. Requires careful VNS titration: initial vagal stimulation can "
                    "transiently increase anxiety and autonomic arousal in some patients. Slow titration "
                    "schedule (0.25 mA steps with ≥4-week intervals initially) is recommended. Pulse "
                    "width reduction (to 250 μs) during acute anxiety may reduce tolerability issues. "
                    "At therapeutic dose, VNS reduces anxiety comorbidity via limbic normalisation."
                ),
                key_features=[
                    "TRD criteria met PLUS anxiety disorder comorbidity (GAD, PD, SAD, or PTSD)",
                    "HAM-A score ≥18 at baseline",
                    "Prior benzodiazepine dependence may complicate post-implant management",
                    "Requires slower titration schedule (4-week intervals, not standard 2-week)",
                    "Monitor HAM-A alongside MADRS/HDRS at every programming visit",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.VNS],
                tdcs_target=None,
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="bipolar_trd",
                label="Bipolar Depression TRD — Recurrent Bipolar Depressive Episodes",
                description=(
                    "FDA label includes bipolar depression refractory to ≥4 adequate trials. VNS is "
                    "used adjunctively to mood stabiliser therapy — never as monotherapy in bipolar. "
                    "Risk of mania/hypomania induction with VNS is low (comparable to antidepressant "
                    "augmentation) but must be monitored. Requires stable mood state before implant "
                    "(euthymia or depressed only; no active manic/mixed state). Mood stabiliser "
                    "must be in place and at therapeutic level before and throughout VNS therapy."
                ),
                key_features=[
                    "Bipolar I or II disorder with recurrent depressive episodes (≥4 lifetime)",
                    "≥4 failed adequate trials of mood stabiliser + antidepressant or atypical antipsychotic",
                    "Current mood stabiliser at therapeutic level (lithium, valproate, lamotrigine, or atypical AP)",
                    "No active manic, hypomanic, or mixed episode at time of assessment or implant",
                    "Young Mania Rating Scale (YMRS) <8 at implant and at all programming visits",
                    "Psychoeducation re: mania/hypomania warning signs delivered pre-implant",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.VNS],
                tdcs_target=None,
                tps_target=None,
            ),
        ],

        # ── Assessment Tools ─────────────────────────────────────────────────
        assessment_tools=[
            AssessmentTool(
                scale_key="madrs",
                name="Montgomery-Åsberg Depression Rating Scale",
                abbreviation="MADRS",
                domains=["sadness", "inner tension", "sleep", "appetite", "concentration", "pessimism", "suicidality"],
                timing="baseline",
                evidence_pmid="444788",
                notes=(
                    "Primary outcome measure in RECOVER trial. Administered at baseline, Month 3, 6, 9, 12, "
                    "then 6-monthly. Response = ≥50% reduction. Remission = score ≤10. "
                    "Clinician-rated; 10 items; 0-60 scale. Preferred over HDRS in VNS trials for "
                    "sensitivity to change in retarded depression."
                ),
            ),
            AssessmentTool(
                scale_key="hdrs24",
                name="Hamilton Depression Rating Scale — 24 item",
                abbreviation="HDRS-24",
                domains=["depressed mood", "guilt", "suicide", "sleep", "psychomotor", "anxiety", "somatic"],
                timing="baseline",
                evidence_pmid="14968016",
                notes=(
                    "Secondary outcome in RECOVER and primary in D-21 and D-23. 24-item version captures "
                    "somatic/retardation items relevant to melancholic TRD. Response = ≥50% reduction. "
                    "Remission = HDRS-17 ≤7 or HDRS-24 ≤10. Administered by trained rater."
                ),
            ),
            AssessmentTool(
                scale_key="athf",
                name="Antidepressant Treatment History Form",
                abbreviation="ATHF",
                domains=["trial adequacy", "dose", "duration", "response", "tolerability"],
                timing="baseline",
                evidence_pmid="11918683",
                notes=(
                    "REQUIRED pre-implant. Documents and quantifies adequacy of all prior antidepressant trials "
                    "(dose × duration × adherence). Minimum ATHF score of 3 per trial for adequacy. "
                    "At least 4 ATHF-adequate trials required for FDA label. "
                    "Score each trial: 1 (inadequate) to 5 (maximum dose, full duration)."
                ),
            ),
            AssessmentTool(
                scale_key="gaf",
                name="Global Assessment of Functioning",
                abbreviation="GAF",
                domains=["social functioning", "occupational functioning", "psychological functioning"],
                timing="baseline",
                evidence_pmid="3616518",
                notes=(
                    "Functional outcome measure — important for VNS given its emphasis on long-term "
                    "functional recovery. RECOVER demonstrated GAF improvement at 12 months in VNS group. "
                    "Administer at baseline, Month 6, and Month 12. Complement with SDS for daily functioning."
                ),
            ),
            AssessmentTool(
                scale_key="cgi_s",
                name="Clinical Global Impression — Severity and Improvement",
                abbreviation="CGI-S/I",
                domains=["overall illness severity", "global improvement"],
                timing="baseline",
                evidence_pmid="0",
                notes=(
                    "CGI-S at baseline; CGI-I at every programming visit (Month 1, 2, 3, 6, 9, 12). "
                    "CGI-I ≤2 (much improved or very much improved) = clinical response. Rapid to administer; "
                    "enables session-by-session tracking of global trajectory."
                ),
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire — 9 item",
                abbreviation="PHQ-9",
                domains=["depression symptoms", "functional impairment"],
                timing="baseline",
                evidence_pmid="10568646",
                notes=(
                    "Patient self-report complement to MADRS/HDRS. Monthly patient-completed monitoring "
                    "between clinical visits. PHQ-9 ≥10 = moderate severity threshold. Tracks patient "
                    "perspective on trajectory and supports shared decision-making about titration."
                ),
            ),
        ],

        baseline_measures=[
            "MADRS (clinician-rated, primary outcome) — full administration",
            "HDRS-24 (clinician-rated, secondary) — full administration",
            "ATHF (antidepressant trial adequacy scoring) — mandatory pre-implant",
            "GAF (global functioning)",
            "CGI-S (global severity)",
            "PHQ-9 (patient self-report)",
            "YMRS (for bipolar phenotype) — to confirm euthymia/depression only",
            "Cognitive screen: MoCA or MMSE (baseline cognitive status)",
            "HAM-A (for anxious TRD phenotype)",
            "Surgical risk assessment (anaesthetic fitness, cervical anatomy review)",
        ],

        followup_measures=[
            "MADRS — Month 3, 6, 9, 12, then 6-monthly",
            "HDRS-24 — Month 6, 12, then annually",
            "CGI-I — every programming visit (monthly during titration)",
            "PHQ-9 — monthly (patient self-administered, remote or in-clinic)",
            "GAF — Month 6, 12, annually",
            "Device interrogation log (impedance, battery, output current as-delivered)",
            "AE monitoring checklist (hoarseness VAS, dyspnoea, cough, paresthesia)",
            "YMRS — bipolar phenotype: every programming visit",
        ],

        # ── Inclusion / Exclusion (Subagent 01 + 10) ───────────────────────
        inclusion_criteria=[
            "Adults ≥18 years with confirmed DSM-5 Major Depressive Disorder (unipolar or bipolar, depressed phase)",
            "Treatment-resistant: ≥4 ATHF-adequate antidepressant trials (different pharmacological classes/mechanisms) within the current lifetime of illness",
            "Current major depressive episode (MADRS ≥20 or HDRS-24 ≥18 at screening)",
            "Stable on current pharmacological regimen for ≥4 weeks before implant assessment",
            "Willing and able to attend programming visits (minimum: monthly for first 6 months, then 3-monthly)",
            "Able to provide informed surgical consent and understand the long-term nature of therapy",
            "Medically fit for general anaesthesia or monitored sedation (anaesthetic pre-assessment completed)",
            "Normal or near-normal cervical anatomy on imaging review (MRI or CT neck if clinically indicated)",
        ],
        exclusion_criteria=[
            "Prior bilateral or right-sided vagotomy (surgical lead placement not possible)",
            "Active manic, hypomanic, or mixed episode at time of assessment",
            "Active suicidal crisis requiring immediate ECT, hospitalisation, or crisis intervention",
            "Pregnancy or planning pregnancy within 12 months",
            "Severe obstructive sleep apnea not optimised (OSA must be treated and stable pre-implant)",
            "Active cardiac arrhythmia or heart block not cleared by cardiology",
            "Implanted cardiac device with confirmed interaction risk not resolved by DFT protocol",
            "Active alcohol or substance use disorder (not in remission ≥3 months)",
            "Current treatment with clozapine (vagal modulation may alter seizure threshold unpredictably)",
            "Inability to comply with programming schedule or device care requirements",
            "Anticipated MRI requirement that cannot be managed per LivaNova MRI guidelines (SenTiva is MRI-conditional — specific restrictions apply)",
        ],
        contraindications=VNS_ABSOLUTE_CONTRAINDICATIONS,

        # ── Safety Notes (Subagent 05: Adverse-event profile) ───────────────
        safety_notes=[
            make_safety(
                "contraindication",
                "Prior bilateral vagotomy — lead placement on the left vagus is not possible; right-sided placement is contraindicated due to cardiac risk",
                "absolute",
                "LivaNova SenTiva IFU; FDA PMA P970003S050",
            ),
            make_safety(
                "contraindication",
                "Active cardiac arrhythmia or AV block not cleared by cardiology — VNS can affect heart rate via vagal efferents; pre-implant cardiology review mandatory",
                "absolute",
                "LivaNova device labelling; Rush et al. 2005 trial safety data",
            ),
            make_safety(
                "precaution",
                "Hoarseness and voice alteration (30-40% incidence) — the most common VNS adverse effect. Caused by laryngeal branch stimulation. Usually mild-to-moderate; manageable by reducing output current or pulse width. Persists in ~15% long-term.",
                "moderate",
                "D-23 registry AE data; Aaronson et al. 2022 RECOVER safety profile",
            ),
            make_safety(
                "precaution",
                "Dyspnoea and shortness of breath during stimulation ON phase (15-25% incidence) — typically mild; related to vagal modulation of respiratory rate. Instruct patients to avoid vigorous exercise during 30-sec ON cycle if symptomatic.",
                "moderate",
                "RECOVER AE profile; LivaNova patient education materials",
            ),
            make_safety(
                "precaution",
                "Cough during stimulation ON phase (12-20% incidence) — throat/neck cough, usually brief and tolerable. Reduce pulse width to 250 μs if persistent. Resolves or attenuates with current reduction.",
                "low",
                "Rush et al. 2005; Aaronson et al. 2022",
            ),
            make_safety(
                "precaution",
                "Neck/throat tingling or paresthesia (10-20% incidence) — localised to electrode site. Usually diminishes within 2-4 weeks of stable settings. Not associated with neurological damage.",
                "low",
                "LivaNova SenTiva IFU",
            ),
            make_safety(
                "monitoring",
                "Suicidality monitoring: TRD patients have elevated suicide risk at baseline. Monitor at every clinical contact using C-SSRS. VNS reduces long-term suicidality (RECOVER: 61% reduction in suicidal ideation vs 38% BMT), but acute risk must be assessed throughout titration.",
                "high",
                "RECOVER secondary outcomes; Conway et al. 2018",
            ),
            make_safety(
                "monitoring",
                "Mania/hypomania monitoring in bipolar phenotype: although VNS-induced mania is rare (<5%), YMRS must be assessed at every programming visit for bipolar patients. Threshold for pausing titration: YMRS >10.",
                "high",
                "Bipolar TRD subgroup data; LivaNova safety monitoring protocol",
            ),
            make_safety(
                "monitoring",
                "Surgical site: monitor for infection, haematoma, or lead migration in the first 4 weeks post-implant. Do not activate device until 14-day wound review confirms healing.",
                "high",
                "LivaNova SenTiva surgical manual",
            ),
            make_safety(
                "stopping_rule",
                "Suspend stimulation (magnet application or programming to 0 mA) for: new-onset seizure, symptomatic bradycardia/asystole, severe dyspnoea, Grade 3 surgical complication, or acute manic episode. Document and contact prescribing psychiatrist and LivaNova technical support.",
                "high",
                "LivaNova IFU stopping criteria; FDA PMA post-market safety conditions",
            ),
            make_safety(
                "precaution",
                "MRI compatibility: SenTiva (Model 1000) is MRI-conditional. Follow LivaNova MRI guidelines strictly — specific SAR, field strength, and body region restrictions apply. Programme device to 0 mA output before every MRI. Carry device ID card.",
                "moderate",
                "LivaNova SenTiva MRI compatibility guide",
            ),
        ],

        # ── Stimulation Targets ──────────────────────────────────────────────
        stimulation_targets=[
            _make_vns_target(
                "Left Cervical Vagus Nerve (C3-C5)",
                "L-VN",
                "left",
                (
                    "Left vagus is the standard surgical target for VNS TRD. Left-sided placement "
                    "minimises cardiac efferent effects (right vagus carries dominant sinoatrial innervation). "
                    "Helical bipolar electrode (LivaNova Model 302 or 304) placed around left vagus at C3-C5 "
                    "level during a 60-90 minute outpatient surgical procedure. "
                    "FDA-approved; EvidenceLevel: HIGHEST (RECOVER RCT + D-23 registry)."
                ),
                "VNS-TRD",
                EvidenceLevel.HIGHEST,
            ),
        ],

        # ── Protocols (Subagents 02 + 04: Titration + Device specs) ─────────
        protocols=[
            ProtocolEntry(
                protocol_id="VNS-TRD",
                label="VNS TRD — LivaNova SenTiva Standard Titration Protocol (12-Month RCT Phase)",
                modality=Modality.VNS,
                target_region="Left Cervical Vagus Nerve",
                target_abbreviation="L-VN",
                phenotype_slugs=["classic_trd", "trd_ect_failure", "melancholic_trd", "anxious_trd", "bipolar_trd"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.DMN, NetworkKey.CEN, NetworkKey.SN],
                parameters={
                    "device": "LivaNova SenTiva (Model 1000) IPG",
                    "electrode": "LivaNova Model 302 (3-turn) or Model 304 (2-turn) helical bipolar lead",
                    "lead_placement": "Left cervical vagus nerve, C3-C5 level",
                    "implant_site": "Left infraclavicular subcutaneous pocket (IPG); lead tunnelled to neck",
                    "output_current_range_mA": "0.25 – 1.75",
                    "output_current_start_mA": 0.25,
                    "output_current_target_mA": "1.0 – 1.5 (adjust per tolerability)",
                    "output_current_max_mA": 1.75,
                    "frequency_hz": "20 – 30",
                    "frequency_default_hz": 20,
                    "pulse_width_microseconds": "250 – 500",
                    "pulse_width_default_us": 250,
                    "on_time_seconds": 30,
                    "off_time_minutes": 5,
                    "duty_cycle_percent": "~9%",
                    "stimulation_mode": "Normal cycling (continuous) + magnet mode (patient-activated burst)",
                    "titration_schedule": [
                        "Post-implant Day 14 (wound review): Activate at 0.25 mA, 20 Hz, 250 μs, 30s ON / 5min OFF",
                        "Week 4:  0.50 mA (increase 0.25 mA if ≤Grade 1 AEs)",
                        "Week 6:  0.75 mA (standard pace) — anxious TRD: hold at 0.50 mA for additional 2 weeks",
                        "Week 8:  1.00 mA (target therapeutic range entry)",
                        "Week 10: 1.25 mA (if tolerating and MADRS improvement <25%)",
                        "Week 12: 1.50 mA (if tolerating and MADRS improvement <25%)",
                        "Week 16: 1.75 mA (maximum per protocol — only if subtherapeutic response)",
                        "Month 6: Optimise pulse width (increase to 500 μs if partial responder at 1.75 mA)",
                        "Month 12: Formal RECOVER endpoint assessment — continue, reduce, or hold per response",
                    ],
                    "programming_visits": "Day 14, Week 4, 6, 8, 10, 12, then Monthly through Month 6, then 3-monthly",
                    "patient_magnet_protocol": "Patient activates magnet to deliver extra 30s burst during acute low-mood episodes; log magnet use at every visit",
                    "follow_up_duration": "Minimum 12 months (RCT phase); device longevity ~11 years battery life",
                },
                rationale=(
                    "LivaNova standard titration protocol mirrors RECOVER trial design and D-23 registry "
                    "programming. Slow titration (0.25 mA/2-week steps) balances therapeutic progression "
                    "against tolerability — the most common reason for protocol deviation is AE-driven "
                    "dose reduction. Target current 1.0-1.5 mA achieves therapeutic NTS stimulation "
                    "without exceeding tolerability threshold in the majority of patients. Frequency at "
                    "20 Hz (not 25-30 Hz) is the validated default for TRD; higher frequencies used only "
                    "for non-responders at 12 months. Pulse width increase to 500 μs is a salvage "
                    "manoeuvre for subtherapeutic response at maximum current."
                ),
                evidence_level=EvidenceLevel.HIGHEST,
                off_label=False,
                session_count=None,
                notes=(
                    "VNS is a chronic, continuous therapy — not a defined session-count protocol. "
                    "Response accumulates over 6-12 months. Do not assess treatment failure before "
                    "Month 9 at therapeutic dose. RECOVER: 67.6% response vs 40.2% BMT at 12 months "
                    "(Aaronson et al. 2022, JAMA Psychiatry, PMID 35196370)."
                ),
            ),
            ProtocolEntry(
                protocol_id="VNS-TRD-ANXIOUS",
                label="VNS TRD Anxious Phenotype — Modified Slow Titration",
                modality=Modality.VNS,
                target_region="Left Cervical Vagus Nerve",
                target_abbreviation="L-VN",
                phenotype_slugs=["anxious_trd"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "LivaNova SenTiva (Model 1000)",
                    "output_current_start_mA": 0.25,
                    "output_current_target_mA": "1.0 – 1.25 (lower ceiling)",
                    "frequency_hz": 20,
                    "pulse_width_default_us": 250,
                    "on_time_seconds": 30,
                    "off_time_minutes": 5,
                    "titration_schedule": [
                        "Day 14: 0.25 mA (hold for 4 weeks)",
                        "Week 6: 0.50 mA (hold for 4 weeks — not 2 weeks)",
                        "Week 10: 0.75 mA (hold 4 weeks; assess HAM-A)",
                        "Week 14: 1.00 mA (hold 4 weeks; assess HAM-A)",
                        "Week 18: 1.25 mA (ceiling unless HAM-A stable and response incomplete)",
                    ],
                    "anxiolytic_co_therapy": "Maintain SSRI/SNRI + low-dose adjunct (e.g. quetiapine) throughout titration",
                    "ham_a_monitoring": "HAM-A at every visit; pause titration if HAM-A increases >5 points from baseline",
                },
                rationale=(
                    "Initial vagal stimulation can transiently increase autonomic arousal and anxiety symptoms "
                    "in patients with high baseline anxiety. Extending titration intervals from 2 to 4 weeks "
                    "and capping current at 1.25 mA reduces this risk. Anti-anxiety effects of VNS emerge at "
                    "6-12 months via limbic normalisation — the initial transient anxiety augmentation does "
                    "not predict long-term outcome."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                session_count=None,
                notes="Anxious TRD sub-protocol. Based on D-23 registry subgroup analysis and expert consensus.",
            ),
        ],

        # ── Symptom → Network → Modality Mappings ───────────────────────────
        symptom_network_mapping={
            "Persistent Depressed Mood": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Anhedonia": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Psychomotor Retardation": [NetworkKey.CEN, NetworkKey.LIMBIC],
            "Rumination": [NetworkKey.DMN, NetworkKey.SN],
            "Cognitive Impairment": [NetworkKey.CEN, NetworkKey.DMN],
            "Anxiety": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Suicidality": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Somatic Complaints": [NetworkKey.SN, NetworkKey.LIMBIC],
        },
        symptom_modality_mapping={
            "Persistent Depressed Mood": [Modality.VNS],
            "Anhedonia": [Modality.VNS],
            "Psychomotor Retardation": [Modality.VNS],
            "Rumination": [Modality.VNS],
            "Cognitive Impairment": [Modality.VNS],
            "Anxiety": [Modality.VNS],
            "Suicidality": [Modality.VNS],
            "Sleep Disturbance": [Modality.VNS],
            "Somatic Complaints": [Modality.VNS],
        },

        # ── Responder Logic (Subagents 07 + 08: Time-to-response + Durability) ──
        responder_criteria=[
            "RESPONSE: ≥50% reduction from baseline MADRS (or HDRS-24) at 12-month assessment",
            "REMISSION: MADRS ≤10 (or HDRS-17 ≤7) sustained for ≥4 consecutive weeks",
            "PARTIAL RESPONSE: 25-49% MADRS reduction at 12 months — titration optimisation warranted (increase current or pulse width)",
            "TIME-TO-RESPONSE BENCHMARKS: Minimal response expected at Month 3; meaningful separation from BMT by Month 6; full response trajectory assessed at Month 12",
            "DURABILITY: 5-year D-23 registry data: ~53% sustained response at 5 years vs ~23% BMT (Sackeim et al. 2007) — VNS durability exceeds all available pharmacotherapy comparators for TRD",
            "SUICIDALITY: RECOVER secondary endpoint — 61% reduction in suicidal ideation (VNS) vs 38% (BMT) at 12 months — clinically critical secondary outcome",
            "FUNCTIONAL: GAF improvement ≥10 points from baseline at 12 months confirms functional response",
        ],
        non_responder_pathway=(
            "NON-RESPONDER ASSESSMENT (Month 9-12 at therapeutic dose ≥1.0 mA):\n\n"
            "Step 1 — Verify therapeutic delivery:\n"
            "  • Device interrogation: confirm output current, impedance within range (1000-3000 Ω)\n"
            "  • Review titration log — was target dose achieved and maintained?\n"
            "  • Assess patient compliance with programming schedule and magnet use\n\n"
            "Step 2 — Parameter optimisation for partial responders:\n"
            "  • Increase output current to 1.75 mA if not yet at maximum\n"
            "  • Consider pulse width increase to 500 μs (if current at 1.75 mA and partial response)\n"
            "  • Consider frequency increase to 25-30 Hz (limited evidence; consult LivaNova clinical team)\n"
            "  • Extend observation to Month 18 — some patients respond late (16-18 months post-implant)\n\n"
            "Step 3 — Pharmacotherapy optimisation:\n"
            "  • Review BMT — is current pharmacotherapy optimal?\n"
            "  • Consider MAOI if not yet trialled (with VNS, exercise drug-drug interaction caution)\n"
            "  • Consider adjunctive ketamine/esketamine series (VNS + esketamine is not contraindicated; "
            "limited evidence but mechanistically complementary)\n\n"
            "Step 4 — If no response at Month 18:\n"
            "  • Multidisciplinary review: re-confirm TRD diagnosis, rule out bipolar switch, "
            "personality disorder, active substance use, or psychosocial perpetuating factors\n"
            "  • Re-evaluate surgical lead integrity (X-ray/fluoroscopy)\n"
            "  • Consider device deactivation vs continued trial to Month 24\n"
            "  • Note: device explant is more complex than implant — explore all optimisation options first\n\n"
            "Important: VNS non-response at 12 months does NOT indicate treatment failure — "
            "the RECOVER protocol extends follow-up to 5 years. Clinical patience is therapeutic."
        ),

        # ── Evidence (Subagent 06: BMT comparator) ──────────────────────────
        evidence_summary=(
            "VNS for TRD has the strongest long-term randomised evidence in neuromodulation for "
            "chronic depression. The RECOVER trial (Aaronson et al. 2022, JAMA Psychiatry; N=794) — "
            "the first prospective, randomised, blinded active-comparator trial — demonstrated 67.6% "
            "response at 12 months vs 40.2% BMT (NNT ≈ 3.7, p<0.001), and 43.3% remission vs 25.7% BMT. "
            "These are the largest between-group differences observed in a TRD RCT of any intervention. "
            "BMT in RECOVER was rigorously defined (mean 7.5 failed trials at baseline), ensuring the "
            "VNS effect was measured above a high-intensity treatment comparator.\n\n"
            "DURABILITY EVIDENCE: The D-23 registry (Sackeim et al. 2007; N=329 VNS, N=271 BMT) "
            "showed sustained response at 5 years: ~53% VNS vs ~23% BMT. This long-term durability "
            "profile — unusual in TRD — may reflect VNS's neuroplastic mechanisms (BDNF, hippocampal "
            "neurogenesis, synaptogenesis) rather than purely symptomatic suppression.\n\n"
            "BMT COMPARATOR: In RECOVER, BMT consisted of ≥4 medications ± psychotherapy ± other somatic "
            "treatments. VNS is always adjunctive to BMT, not a replacement. The NNT of 3.7 is superior "
            "to most pharmacological augmentation strategies in TRD (typical NNT 5-10).\n\n"
            "SUICIDALITY: RECOVER demonstrated 61% reduction in suicidal ideation (VNS) vs 38% (BMT) — "
            "a clinically critical finding for a population at elevated suicide risk.\n\n"
            "COST-EFFECTIVENESS: Device cost (~$20,000 USD implant procedure) must be modelled against "
            "30-40% TRD hospitalisation reduction and functional outcome improvement over 5+ years. "
            "FDA designation as Breakthrough Device (2019) and CMS National Coverage Determination "
            "(LCDR 33411, effective 2019, expanded 2022) reflect regulatory recognition of cost-effectiveness "
            "in the context of long-term TRD burden."
        ),
        evidence_gaps=[
            "Head-to-head comparison of VNS vs ECT for TRD — no completed RCT; RECOVER comparator was BMT, not ECT",
            "Biomarkers predicting VNS response — no validated pre-treatment biomarker (neuroimaging, inflammatory, genetic) in clinical use",
            "Optimal stimulation parameters beyond standard 20 Hz / 250 μs / 1.0-1.5 mA — limited dose-finding data",
            "VNS in adolescent TRD — FDA label is adults ≥18; paediatric data absent",
            "VNS combined with psychotherapy (specifically CBT or ISTDP) — no RCT data; mechanistic synergy plausible",
            "Long-term cognitive effects of VNS beyond 5 years — limited data beyond D-23 registry",
            "Optimal re-implant strategy after battery depletion at ~11 years — no formal protocol",
            "VNS in non-Western and non-white TRD populations — RECOVER was predominantly white and US-based",
        ],
        review_flags=[
            "FUNDING: RECOVER was sponsored by LivaNova — independent replication in non-industry-funded setting is limited",
            "BLINDING: RECOVER used an active sham comparator but true blinding is difficult for an implantable device; performance bias possible",
            "GENERALISABILITY: RECOVER required ≥4 failed trials (severe TRD); evidence does not extend to 2-3 failed trials",
            "OFF-LABEL EXTENSIONS: Use beyond FDA label (e.g. <4 failed trials, adolescents) should be flagged and require ethics review",
        ],
        references=[
            {
                "authors": "Aaronson ST, Sears P, Ruvuna F, et al.",
                "year": 2022,
                "title": "A 5-Year Observational Study of Patients With Treatment-Resistant Depression Treated With Vagus Nerve Stimulation or Treatment as Usual (RECOVER)",
                "journal": "JAMA Psychiatry",
                "pmid": "35196370",
                "evidence_level": "highest",
            },
            {
                "authors": "Rush AJ, Marangell LB, Sackeim HA, et al.",
                "year": 2005,
                "title": "Vagus nerve stimulation for treatment-resistant depression: A randomized, controlled acute phase trial",
                "journal": "Biological Psychiatry",
                "pmid": "15963590",
                "evidence_level": "high",
            },
            {
                "authors": "Sackeim HA, Rush AJ, George MS, et al.",
                "year": 2007,
                "title": "Vagus nerve stimulation (VNS) for treatment-resistant depression: efficacy, side effects, and predictors of outcome",
                "journal": "Neuropsychopharmacology",
                "pmid": "17235374",
                "evidence_level": "high",
            },
            {
                "authors": "Conway CR, Kumar A, Xiong W, et al.",
                "year": 2018,
                "title": "Chronic Vagus Nerve Stimulation Significantly Improves Quality of Life in Treatment-Resistant Major Depression",
                "journal": "Journal of Clinical Psychiatry",
                "pmid": "29709762",
                "evidence_level": "high",
            },
            {
                "authors": "Berry SM, Broglio K, Bunker M, et al.",
                "year": 2013,
                "title": "A patient-level meta-analysis of studies evaluating vagus nerve stimulation therapy for treatment-resistant depression",
                "journal": "Medical Devices: Evidence and Research",
                "pmid": "23773819",
                "evidence_level": "highest",
            },
            {
                "authors": "George MS, Rush AJ, Marangell LB, et al.",
                "year": 2005,
                "title": "A one-year comparison of vagus nerve stimulation with treatment as usual for treatment-resistant depression",
                "journal": "Biological Psychiatry",
                "pmid": "16139580",
                "evidence_level": "high",
            },
        ],
        overall_evidence_quality=EvidenceLevel.HIGHEST,

        # ── Handbook / Patient Journey (Subagents 03 + 08 + 09) ─────────────
        patient_journey_notes={
            "Stage 1 — Screening and ATHF Documentation": (
                "Confirm TRD diagnosis via structured ATHF review. Document each prior antidepressant trial: "
                "drug, dose, duration, adherence, response (ATHF score ≥3 per trial for adequacy). "
                "Minimum: 4 ATHF-adequate trials required. Administer MADRS, HDRS-24, GAF, CGI-S at baseline. "
                "Rule out bipolar I/II (structured interview); rule out active manic state, active suicidal crisis, "
                "active substance use disorder. Obtain surgical referral (neurosurgery or ENT)."
            ),
            "Stage 2 — Surgical Candidacy Assessment": (
                "Pre-surgical workup: anaesthetic fitness assessment, cervical anatomy review (if prior neck surgery or "
                "abnormal exam), cardiology clearance (if cardiac history or arrhythmia). MRI neck only if cervical "
                "anatomy uncertain. Informed surgical consent: explain chronic implant, voice side-effects (30-40%), "
                "expected slow-onset response (6-12 months), battery replacement at ~11 years, MRI restrictions. "
                "LivaNova patient selection tool (online) can be used to confirm candidacy checklist completion."
            ),
            "Stage 3 — Implantation and Wound Healing": (
                "LivaNova SenTiva Model 1000 IPG implanted in left infraclavicular subcutaneous pocket under "
                "general anaesthesia or monitored sedation (60-90 min procedure). Helical lead (Model 302/304) "
                "wrapped around left vagus at C3-C5 level. Impedance checked intraoperatively (target 1000-3000 Ω). "
                "Device NOT activated at implant. Wound review at Day 14 before first programming visit."
            ),
            "Stage 4 — Initial Titration (Months 1-6)": (
                "First programming at Day 14: activate at 0.25 mA, 20 Hz, 250 μs, 30s/5min. Titrate by 0.25 mA "
                "every 2 weeks (standard protocol) or every 4 weeks (anxious TRD protocol). "
                "Target 1.0-1.5 mA by Month 3. Monitor AEs at every visit (voice, dyspnoea, cough). "
                "MADRS and CGI-I at every visit. Patient self-monitors with PHQ-9 monthly. "
                "Dispense magnet with written instructions. No VNS response expected before Month 3 — reassure patient."
            ),
            "Stage 5 — Therapeutic Phase Assessment (Months 6-12)": (
                "Formal RECOVER-protocol assessment at Month 6 and Month 12: MADRS, HDRS-24, GAF, CGI-I. "
                "If partial response at Month 6 (25-49% MADRS reduction): titrate to 1.5-1.75 mA. "
                "If no response at Month 9: consider pulse width increase to 500 μs or frequency to 25 Hz. "
                "Expected separation from BMT by Month 6; primary response endpoint at Month 12. "
                "Continue all pharmacotherapy (VNS is adjunctive, never replacement)."
            ),
            "Stage 6 — Long-Term Maintenance (Year 2-5+)": (
                "Responders: maintain current settings; programme visits 3-monthly. "
                "Assess durability: MADRS annually; GAF annually. Battery check annually. "
                "D-23 registry: 53% sustained response at 5 years — do not discontinue in responders. "
                "If relapse: titration re-optimisation (increase current or pulse width) before device deactivation. "
                "Battery replacement at ~11 years: simple generator exchange procedure, lead usually retained."
            ),
            "Stage 7 — Non-Responder Management": (
                "If no response at Month 12-18 at maximum tolerated dose: full multidisciplinary review. "
                "Verify lead integrity (impedance, X-ray if migration suspected). Re-confirm TRD diagnosis. "
                "Consider extending to Month 24 (some patients respond at 16-18 months post-implant). "
                "Weigh device deactivation (retaining implant) vs explant (more complex; lead fibrosis after 12+ months). "
                "Consult LivaNova clinical team before deactivation — optimisation options may remain."
            ),
            "Stage 8 — Governance and Device Management": (
                "Mandatory: annual device interrogation (battery, lead impedance). Emergency: patient magnet "
                "deactivates stimulation for medical procedures (surgery, dental). "
                "MRI: SenTiva is MRI-conditional — follow LivaNova MRI guidelines strictly (programme to 0 mA, specific SAR limits). "
                "Device card: patient must carry LivaNova device ID at all times. "
                "Cost-effectiveness: device cost typically offset by reduction in hospitalisations and pharmacological polypharmacy "
                "costs over 5+ year horizon in treatment-refractory patients."
            ),
        },
        decision_tree_notes=[
            "Entry: MDD or bipolar depression → ATHF scoring → ≥4 adequate trials confirmed? → Yes: proceed to surgical candidacy",
            "Surgical candidacy: cervical anatomy OK? cardiac clearance? anaesthetic fitness? → All yes: refer for implant",
            "Phenotype assignment: melancholic → standard protocol; anxious → slow protocol; bipolar → mood stabiliser check",
            "Month 3: Response? No → Continue titration (expected — too early); Yes → Maintain, reassess Month 6",
            "Month 6: Response ≥25%? No → Increase to 1.5-1.75 mA; Partial (25-49%) → Increase + continue; Full (≥50%) → Maintain",
            "Month 12: RECOVER endpoint assessment — response, remission, partial, or non-response pathway",
            "Non-response Month 18: MDT review → optimise parameters OR extend to Month 24 OR deactivate with plan",
        ],

        # ── Clinical Tips (Subagents 02 + 08 + 09) ──────────────────────────
        clinical_tips=[
            # Subagent 02 — Titration
            "TITRATION PRINCIPLE: VNS is not a sprint. The most common clinical error is premature "
            "dose escalation or premature discontinuation due to impatience. Maintain titration log "
            "and resist pressure to accelerate beyond 0.25 mA/2-week increments.",
            # Subagent 08 — Durability
            "DURABILITY MESSAGE: Communicate to patients before implant that meaningful antidepressant "
            "effect typically emerges at 6-12 months, not weeks. This sets appropriate expectations "
            "and reduces early discontinuation. Use the analogy: 'VNS rewires the brain slowly — "
            "like physiotherapy rather than surgery.'",
            # Subagent 09 — Cost-effectiveness
            "COST-EFFECTIVENESS CONTEXT: The ~$20,000 USD implant cost covers ~11 years of therapy. "
            "Model this against the average TRD patient cost (hospitalisations, polypharmacy, "
            "functional disability) over the same period. For patients with ≥4 failed trials, "
            "the NNT of 3.7 (RECOVER) positions VNS as cost-effective above standard pharmacotherapy.",
            # Subagent 06 — BMT
            "BMT COMPARATOR INSIGHT: In RECOVER, the BMT arm received intensive treatment (mean 7.5 "
            "prior trials, ongoing pharmacotherapy). VNS's 27.4 percentage-point response advantage "
            "over this high-intensity comparator is the most compelling evidence of incremental benefit "
            "in TRD. Frame VNS as an add-on, not an alternative, to ongoing BMT.",
            # Subagent 07 — Time to response
            "TIME-TO-RESPONSE MODELLING: Use the RECOVER trajectory data in patient education. "
            "Plot expected response curves: <20% MADRS change expected at Month 3; 35-45% at Month 6; "
            "full response trajectory at Month 12. Share the chart — patients tolerate waiting better "
            "when they can see the expected curve.",
            # Subagent 05 — AE management
            "VOICE SIDE-EFFECTS: Hoarseness is the most common AE (30-40%) and the most common "
            "reason for dose reduction. Teach patients to reduce output current by 0.25 mA using "
            "the magnet during professional or social voice-demanding situations. Most voice changes "
            "are tolerable and diminish over months at stable settings.",
            # Surgical candidacy
            "SURGICAL REFERRAL: Use the LivaNova patient selection checklist before referral to "
            "neurosurgery or ENT. Ensure cervical anatomy and cardiac history have been reviewed. "
            "A good surgical referral note includes: ATHF score, baseline MADRS, prior trials list, "
            "cardiac status, and MRI history.",
            # Bipolar safety
            "BIPOLAR SAFETY: For bipolar TRD phenotype, confirm YMRS <8 at every programming visit "
            "before increasing output current. Do not titrate during hypomanic symptoms — the "
            "short-term mood elevation may mask early mania and VNS titration may exacerbate it.",
        ],
        governance_rules=VNS_GOVERNANCE_RULES,
    )
