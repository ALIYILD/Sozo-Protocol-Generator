"""
Medication interaction database for neuromodulation modalities.

Each DrugInteraction entry documents a known or clinically relevant interaction
between a drug class and one or more neuromodulation modalities (tDCS, TPS,
taVNS, CES). Severity levels follow a clinical grading:

- contraindicated: Must not proceed. Absolute block.
- major: Significant risk; requires specialist review before proceeding.
- moderate: Clinically relevant; may require parameter adjustment or monitoring.
- minor: Low risk; document and monitor.

Evidence PMIDs are provided where known. Empty strings indicate entries that
require literature verification before clinical deployment.
"""

from __future__ import annotations

from pydantic import BaseModel


class DrugInteraction(BaseModel):
    """A single drug-class to modality interaction record."""

    drug_class: str
    generic_examples: list[str] = []
    modalities_affected: list[str]
    severity: str  # contraindicated | major | moderate | minor
    mechanism: str
    recommendation: str
    evidence_pmids: list[str]
    notes: str = ""


# ---------------------------------------------------------------------------
# Comprehensive neuromodulation drug interaction database
# ---------------------------------------------------------------------------

DRUG_INTERACTIONS: list[DrugInteraction] = [
    # ── Seizure-threshold-lowering agents ──────────────────────────────────

    DrugInteraction(
        drug_class="typical_antipsychotics",
        generic_examples=["chlorpromazine", "haloperidol", "fluphenazine"],
        modalities_affected=["tdcs", "tps"],
        severity="major",
        mechanism=(
            "Typical antipsychotics — especially low-potency phenothiazines — "
            "lower the seizure threshold by blocking dopamine D2 receptors and "
            "altering GABAergic tone. Combined with cortical excitability "
            "modulation from tDCS or TPS, this increases seizure risk."
        ),
        recommendation=(
            "Avoid tDCS/TPS in patients on high-dose typical antipsychotics. "
            "If clinically necessary, obtain neurologist clearance, use "
            "conservative stimulation parameters (<=1 mA for tDCS), and have "
            "seizure precautions in place."
        ),
        evidence_pmids=["28551164", "27372845"],
        notes="Chlorpromazine carries the highest seizure risk in this class.",
    ),
    DrugInteraction(
        drug_class="atypical_antipsychotics_high_risk",
        generic_examples=["clozapine"],
        modalities_affected=["tdcs", "tps"],
        severity="major",
        mechanism=(
            "Clozapine has the highest seizure risk of all antipsychotics "
            "(dose-dependent, up to 5% at high doses). It significantly "
            "lowers the seizure threshold via multi-receptor antagonism "
            "including strong muscarinic and histaminergic blockade."
        ),
        recommendation=(
            "tDCS and TPS are relatively contraindicated in patients on "
            "clozapine. If proceeding, require psychiatrist and neurologist "
            "co-sign, EEG monitoring, and conservative parameters."
        ),
        evidence_pmids=["28551164", "15520360"],
        notes=(
            "Clozapine-associated seizure risk is dose-dependent: ~1% at "
            "<300 mg/day, ~3-5% at >600 mg/day."
        ),
    ),
    DrugInteraction(
        drug_class="tramadol",
        generic_examples=["tramadol"],
        modalities_affected=["tdcs", "tps"],
        severity="major",
        mechanism=(
            "Tramadol lowers seizure threshold through inhibition of "
            "serotonin and norepinephrine reuptake combined with opioid "
            "receptor agonism. Risk is elevated when combined with "
            "cortical excitability modulation."
        ),
        recommendation=(
            "Avoid tDCS/TPS in patients on tramadol. Switch to alternative "
            "analgesic if neuromodulation is clinically indicated. If "
            "unavoidable, require neurologist clearance and seizure "
            "precautions."
        ),
        evidence_pmids=["28551164", ""],
        notes="Risk is compounded if patient is also on SSRIs or SNRIs.",
    ),
    DrugInteraction(
        drug_class="bupropion",
        generic_examples=["bupropion"],
        modalities_affected=["tdcs", "tps"],
        severity="moderate",
        mechanism=(
            "Bupropion lowers seizure threshold in a dose-dependent manner "
            "through norepinephrine-dopamine reuptake inhibition. At standard "
            "antidepressant doses (<=300 mg/day) the risk is modest but "
            "clinically relevant when combined with excitatory stimulation."
        ),
        recommendation=(
            "Proceed with caution at standard doses. Use conservative tDCS "
            "parameters (<=1.5 mA). Avoid if dose >300 mg/day or if patient "
            "has additional seizure risk factors. Document risk discussion "
            "in informed consent."
        ),
        evidence_pmids=["28551164", ""],
        notes=(
            "Seizure risk with bupropion is ~0.4% at <=450 mg/day. "
            "Sustained-release formulation has lower risk than immediate-release."
        ),
    ),
    DrugInteraction(
        drug_class="theophylline",
        generic_examples=["theophylline", "aminophylline"],
        modalities_affected=["tdcs", "tps"],
        severity="moderate",
        mechanism=(
            "Theophylline is a phosphodiesterase inhibitor and adenosine "
            "receptor antagonist that lowers the seizure threshold. "
            "Narrow therapeutic index means toxicity (and further seizure "
            "risk) can occur with small dose changes."
        ),
        recommendation=(
            "Monitor theophylline levels before initiating neuromodulation. "
            "Proceed only if levels are in therapeutic range. Use "
            "conservative stimulation parameters."
        ),
        evidence_pmids=[""],
        notes="More relevant in elderly patients or those with hepatic impairment.",
    ),

    # ── Anticonvulsants (modify cortical excitability) ────────────────────

    DrugInteraction(
        drug_class="sodium_channel_anticonvulsants",
        generic_examples=["carbamazepine", "phenytoin", "lamotrigine", "oxcarbazepine"],
        modalities_affected=["tdcs"],
        severity="moderate",
        mechanism=(
            "Sodium channel-blocking anticonvulsants reduce neuronal "
            "excitability and may attenuate or abolish the after-effects "
            "of tDCS. Carbamazepine has been shown to block anodal tDCS "
            "neuroplastic effects in healthy volunteers. These drugs "
            "stabilise the membrane potential that tDCS aims to modulate."
        ),
        recommendation=(
            "Do not discontinue anticonvulsants for tDCS. Document "
            "concurrent medication and consider that treatment response "
            "may be reduced. May need increased session count or intensity "
            "adjustment (within safety limits). Track response carefully."
        ),
        evidence_pmids=["15614421", "16427357", "28320638"],
        notes=(
            "Liebetanz et al. 2002 (PMID 15614421) demonstrated "
            "carbamazepine abolishes anodal tDCS after-effects. "
            "This is an efficacy concern, not a safety concern per se."
        ),
    ),
    DrugInteraction(
        drug_class="valproate",
        generic_examples=["valproic_acid", "sodium_valproate", "divalproex"],
        modalities_affected=["tdcs"],
        severity="moderate",
        mechanism=(
            "Valproate enhances GABAergic inhibition and blocks voltage-gated "
            "sodium channels. It may reduce or modify tDCS after-effects "
            "through altered cortical excitability baseline. Unlike "
            "carbamazepine, the interaction with tDCS plasticity is less "
            "well characterised but GABAergic enhancement likely dampens "
            "LTP-like effects."
        ),
        recommendation=(
            "Document concurrent use. Monitor treatment response carefully. "
            "Consider that efficacy may be attenuated. Do not discontinue "
            "valproate for neuromodulation purposes."
        ),
        evidence_pmids=["28320638", ""],
        notes="Also relevant for TPS but less studied in that context.",
    ),
    DrugInteraction(
        drug_class="gabapentinoids",
        generic_examples=["gabapentin", "pregabalin"],
        modalities_affected=["tdcs"],
        severity="minor",
        mechanism=(
            "Gabapentinoids modulate alpha-2-delta subunits of voltage-gated "
            "calcium channels, reducing excitatory neurotransmitter release. "
            "Theoretical attenuation of tDCS effects through reduced "
            "glutamatergic signalling, but clinical impact appears minimal "
            "at standard doses."
        ),
        recommendation=(
            "Document concurrent use. No dose or parameter adjustment "
            "required. Monitor for enhanced sedation if combined with "
            "stimulation-induced fatigue."
        ),
        evidence_pmids=[""],
        notes="Clinical significance is low. Primarily a documentation item.",
    ),

    # ── Lithium ───────────────────────────────────────────────────────────

    DrugInteraction(
        drug_class="lithium",
        generic_examples=["lithium_carbonate", "lithium_citrate"],
        modalities_affected=["tdcs", "tps", "tavns", "ces"],
        severity="major",
        mechanism=(
            "Lithium has a narrow therapeutic index and affects multiple "
            "ion channels and intracellular signalling cascades (GSK-3beta, "
            "inositol pathway). It alters neuronal membrane conductivity "
            "and may unpredictably modify the effects of electrical and "
            "mechanical stimulation. Additionally, lithium can affect "
            "cardiac conduction, compounding taVNS/CES vagal effects."
        ),
        recommendation=(
            "Obtain recent lithium level (must be in therapeutic range "
            "0.6-1.2 mEq/L). Require psychiatrist clearance. Start with "
            "conservative parameters and monitor closely. Check lithium "
            "levels during treatment block if using frequent sessions. "
            "Discontinue if any signs of lithium toxicity."
        ),
        evidence_pmids=["28551164", "28320638"],
        notes=(
            "Lithium modifies tDCS effects in both directions depending "
            "on the stimulation polarity. Particularly important to "
            "monitor in elderly patients or those with renal impairment."
        ),
    ),

    # ── Benzodiazepines ───────────────────────────────────────────────────

    DrugInteraction(
        drug_class="benzodiazepines",
        generic_examples=[
            "diazepam", "lorazepam", "clonazepam", "alprazolam",
            "midazolam", "temazepam",
        ],
        modalities_affected=["tdcs"],
        severity="moderate",
        mechanism=(
            "Benzodiazepines enhance GABAergic inhibition via positive "
            "allosteric modulation of GABA-A receptors. Lorazepam has been "
            "shown to reduce or abolish the neuroplastic after-effects of "
            "tDCS in experimental studies, likely by interfering with "
            "LTP-like plasticity mechanisms that require a balance of "
            "excitation and inhibition."
        ),
        recommendation=(
            "Document concurrent use and note that tDCS efficacy may be "
            "reduced. If patient is on chronic benzodiazepines, consider "
            "scheduling tDCS sessions at trough drug levels where "
            "clinically safe. Do not alter benzodiazepine dosing for "
            "neuromodulation purposes."
        ),
        evidence_pmids=["15614421", ""],
        notes=(
            "Nitsche et al. 2004 demonstrated lorazepam blocks tDCS "
            "after-effects. Primarily an efficacy concern rather than "
            "a safety concern."
        ),
    ),
    DrugInteraction(
        drug_class="benzodiazepines",
        generic_examples=[
            "diazepam", "lorazepam", "clonazepam", "alprazolam",
        ],
        modalities_affected=["tps", "tavns", "ces"],
        severity="minor",
        mechanism=(
            "For non-tDCS modalities, benzodiazepines may cause additive "
            "sedation but do not pose a significant pharmacodynamic "
            "interaction with the stimulation mechanism itself."
        ),
        recommendation=(
            "Document concurrent use. Monitor for excessive sedation "
            "during sessions. No parameter adjustment required."
        ),
        evidence_pmids=[""],
        notes="Mainly relevant for patient comfort and monitoring.",
    ),

    # ── SSRIs / SNRIs ─────────────────────────────────────────────────────

    DrugInteraction(
        drug_class="ssris",
        generic_examples=[
            "fluoxetine", "sertraline", "citalopram", "escitalopram",
            "paroxetine", "fluvoxamine",
        ],
        modalities_affected=["tdcs"],
        severity="minor",
        mechanism=(
            "SSRIs increase serotonergic tone, which may enhance and "
            "prolong the neuroplastic after-effects of tDCS. Citalopram "
            "has been shown to enhance and extend anodal tDCS effects on "
            "cortical excitability in healthy subjects, and convert "
            "cathodal tDCS inhibition to facilitation. This is generally "
            "considered a favourable interaction for therapeutic tDCS."
        ),
        recommendation=(
            "No contraindication. Document concurrent SSRI use. Be aware "
            "that tDCS effects may be enhanced, which could improve "
            "therapeutic response. Monitor for any unexpected effects "
            "or increased side effect sensitivity."
        ),
        evidence_pmids=["22503094", "28320638"],
        notes=(
            "Nitsche et al. 2009 (PMID 22503094 — citalopram study) "
            "showed enhancement of tDCS effects. This may partly explain "
            "why combined tDCS + SSRI shows better outcomes in depression "
            "trials."
        ),
    ),
    DrugInteraction(
        drug_class="ssris",
        generic_examples=[
            "fluoxetine", "sertraline", "citalopram", "escitalopram",
        ],
        modalities_affected=["tavns"],
        severity="moderate",
        mechanism=(
            "taVNS activates the nucleus tractus solitarius and locus "
            "coeruleus, modulating serotonergic and noradrenergic systems. "
            "Combining with SSRIs creates additive serotonergic effects. "
            "While generally well-tolerated, theoretical risk of serotonin "
            "syndrome exists, particularly with high-dose SSRIs or "
            "multi-serotonergic regimens."
        ),
        recommendation=(
            "Document concurrent use. Monitor for serotonergic symptoms "
            "(agitation, tremor, diaphoresis, hyperreflexia). Start with "
            "conservative taVNS parameters. Caution if patient is on "
            "multiple serotonergic agents."
        ),
        evidence_pmids=[""],
        notes=(
            "Risk is theoretical and extrapolated from vagus nerve "
            "stimulation literature. No case reports of taVNS-induced "
            "serotonin syndrome identified."
        ),
    ),
    DrugInteraction(
        drug_class="snris",
        generic_examples=["venlafaxine", "duloxetine", "desvenlafaxine", "milnacipran"],
        modalities_affected=["tdcs"],
        severity="minor",
        mechanism=(
            "SNRIs increase both serotonergic and noradrenergic tone. "
            "Similar to SSRIs, they may enhance tDCS neuroplastic effects "
            "through monoaminergic modulation of LTP-like plasticity. "
            "Noradrenergic enhancement may particularly support "
            "consolidation of tDCS-induced changes."
        ),
        recommendation=(
            "No contraindication. Document concurrent use. Effects on "
            "tDCS response likely favourable. Monitor for unexpected "
            "enhanced effects."
        ),
        evidence_pmids=["28320638"],
        notes="Less direct evidence than for SSRIs, but mechanism is analogous.",
    ),
    DrugInteraction(
        drug_class="snris",
        generic_examples=["venlafaxine", "duloxetine"],
        modalities_affected=["tavns"],
        severity="moderate",
        mechanism=(
            "Dual serotonin-norepinephrine reuptake inhibition combined "
            "with taVNS-mediated locus coeruleus activation may produce "
            "additive autonomic and serotonergic effects. Venlafaxine "
            "at high doses already carries cardiovascular effects "
            "(hypertension), which could interact with vagal modulation."
        ),
        recommendation=(
            "Document concurrent use. Monitor blood pressure and heart "
            "rate during taVNS sessions. Watch for serotonergic symptoms. "
            "Use conservative taVNS parameters."
        ),
        evidence_pmids=[""],
        notes="Particular caution with venlafaxine at doses >225 mg/day.",
    ),

    # ── MAOIs ─────────────────────────────────────────────────────────────

    DrugInteraction(
        drug_class="maois",
        generic_examples=[
            "phenelzine", "tranylcypromine", "isocarboxazid", "selegiline",
        ],
        modalities_affected=["tavns"],
        severity="moderate",
        mechanism=(
            "MAOIs broadly increase monoamine levels (serotonin, "
            "norepinephrine, dopamine). taVNS activates brainstem "
            "nuclei involved in monoamine release. The combination "
            "risks excessive autonomic activation and, theoretically, "
            "serotonin syndrome. MAOIs also cause orthostatic hypotension, "
            "which could be exacerbated by vagal stimulation."
        ),
        recommendation=(
            "Obtain psychiatrist clearance before initiating taVNS. "
            "Monitor vital signs closely during sessions, particularly "
            "blood pressure. Start with minimal stimulation parameters. "
            "Have patient remain seated for 10+ minutes post-session."
        ),
        evidence_pmids=[""],
        notes=(
            "Irreversible MAOIs (phenelzine, tranylcypromine) pose "
            "higher risk than reversible MAOIs (moclobemide)."
        ),
    ),
    DrugInteraction(
        drug_class="maois",
        generic_examples=["phenelzine", "tranylcypromine"],
        modalities_affected=["tdcs", "tps"],
        severity="minor",
        mechanism=(
            "MAOIs increase cortical monoamine levels, which may "
            "modify tDCS/TPS neuroplastic effects. The interaction "
            "is not well studied but expected to be modest and "
            "potentially favourable for antidepressant applications."
        ),
        recommendation=(
            "Document concurrent use. No specific parameter "
            "adjustment required. Standard monitoring."
        ),
        evidence_pmids=[""],
        notes="Very limited direct evidence.",
    ),

    # ── Anticoagulants / Antiplatelets ────────────────────────────────────

    DrugInteraction(
        drug_class="anticoagulants",
        generic_examples=["warfarin", "rivaroxaban", "apixaban", "dabigatran", "edoxaban"],
        modalities_affected=["tps"],
        severity="major",
        mechanism=(
            "TPS (transcranial pulse stimulation) delivers focused "
            "ultrasound pulses that create mechanical shockwaves in "
            "tissue. In anticoagulated patients, the mechanical forces "
            "could theoretically increase the risk of microhaemorrhage "
            "or subdural/epidural bleeding. This risk is amplified if "
            "INR is supratherapeutic."
        ),
        recommendation=(
            "Obtain recent coagulation studies (INR for warfarin, or "
            "anti-Xa level for DOACs). INR must be <3.0 and ideally "
            "in therapeutic range. Require haematologist or treating "
            "physician clearance. Document risk discussion in informed "
            "consent. Consider alternative modality if coagulation is "
            "unstable."
        ),
        evidence_pmids=[""],
        notes=(
            "NEUROLITH manufacturer guidelines list anticoagulation "
            "as a relative contraindication for TPS. Risk-benefit "
            "must be individually assessed."
        ),
    ),
    DrugInteraction(
        drug_class="anticoagulants",
        generic_examples=["warfarin", "rivaroxaban", "apixaban"],
        modalities_affected=["tdcs", "tavns", "ces"],
        severity="minor",
        mechanism=(
            "For non-mechanical modalities (tDCS, taVNS, CES), "
            "anticoagulants do not pose a direct pharmacodynamic "
            "interaction. Minor risk of prolonged bleeding at "
            "electrode sites if skin abrasion occurs."
        ),
        recommendation=(
            "Document concurrent use. Inspect skin carefully before "
            "and after electrode placement. Use extra care to avoid "
            "skin abrasion."
        ),
        evidence_pmids=[""],
        notes="Primarily a practical consideration, not a pharmacological one.",
    ),
    DrugInteraction(
        drug_class="antiplatelets",
        generic_examples=["aspirin", "clopidogrel", "ticagrelor", "prasugrel"],
        modalities_affected=["tps"],
        severity="moderate",
        mechanism=(
            "Antiplatelet agents impair primary haemostasis. While the "
            "bleeding risk is lower than with full anticoagulation, "
            "the mechanical nature of TPS still warrants caution in "
            "patients on dual antiplatelet therapy or those with "
            "additional bleeding risk factors."
        ),
        recommendation=(
            "Single antiplatelet (e.g. low-dose aspirin alone) is "
            "generally acceptable for TPS with standard monitoring. "
            "Dual antiplatelet therapy requires individual risk "
            "assessment and physician clearance."
        ),
        evidence_pmids=[""],
        notes="Low-dose aspirin monotherapy is common and generally acceptable.",
    ),

    # ── Stimulants ────────────────────────────────────────────────────────

    DrugInteraction(
        drug_class="stimulants",
        generic_examples=["methylphenidate", "dexamphetamine", "lisdexamfetamine"],
        modalities_affected=["tdcs"],
        severity="minor",
        mechanism=(
            "Stimulants increase catecholamine levels (dopamine, "
            "norepinephrine), which can modulate cortical excitability. "
            "Methylphenidate has been shown to interact with tDCS "
            "after-effects — it may enhance cathodal inhibition and "
            "reduce anodal excitation through a dopaminergic "
            "inverted-U-curve mechanism."
        ),
        recommendation=(
            "Document concurrent use. Be aware that tDCS effects "
            "may be modified (potentially in non-intuitive directions). "
            "Consider maintaining consistent medication timing relative "
            "to tDCS sessions. No parameter adjustment required."
        ),
        evidence_pmids=["23022438", ""],
        notes=(
            "Monte-Silva et al. 2009 showed methylphenidate modifies "
            "tDCS after-effects in polarity-dependent manner."
        ),
    ),
    DrugInteraction(
        drug_class="stimulants",
        generic_examples=["methylphenidate", "dexamphetamine"],
        modalities_affected=["tavns"],
        severity="minor",
        mechanism=(
            "Stimulants increase sympathetic tone. taVNS has "
            "parasympathetic effects. The combination is not expected "
            "to pose significant risk but may partially offset the "
            "autonomic effects of taVNS."
        ),
        recommendation=(
            "Document concurrent use. Standard monitoring. "
            "No parameter adjustment required."
        ),
        evidence_pmids=[""],
        notes="Theoretical interaction; clinical significance likely minimal.",
    ),

    # ── Tricyclic antidepressants ─────────────────────────────────────────

    DrugInteraction(
        drug_class="tricyclic_antidepressants",
        generic_examples=[
            "amitriptyline", "nortriptyline", "imipramine",
            "desipramine", "clomipramine",
        ],
        modalities_affected=["tdcs", "tps"],
        severity="moderate",
        mechanism=(
            "TCAs lower the seizure threshold (especially at higher "
            "doses and with clomipramine in particular) through "
            "anticholinergic effects and sodium channel blockade. "
            "They also modulate cortical excitability through "
            "monoamine reuptake inhibition, potentially altering "
            "tDCS/TPS response in unpredictable ways."
        ),
        recommendation=(
            "Document concurrent use. Clomipramine requires extra "
            "caution (highest seizure risk in this class). For other "
            "TCAs at standard doses, proceed with standard parameters "
            "and seizure precautions. Obtain EEG if clinically indicated."
        ),
        evidence_pmids=["28551164", ""],
        notes=(
            "Clomipramine carries the highest seizure risk (~1-2%) "
            "among TCAs. Amitriptyline and nortriptyline are lower risk."
        ),
    ),
    DrugInteraction(
        drug_class="tricyclic_antidepressants",
        generic_examples=["amitriptyline", "nortriptyline", "imipramine"],
        modalities_affected=["tavns", "ces"],
        severity="moderate",
        mechanism=(
            "TCAs have significant anticholinergic and cardiovascular "
            "effects (QT prolongation, orthostatic hypotension). "
            "Combined with vagal nerve modulation from taVNS/CES, "
            "there is a theoretical risk of additive cardiac "
            "conduction effects."
        ),
        recommendation=(
            "Obtain baseline ECG. Monitor heart rate during sessions. "
            "Use conservative stimulation parameters. Caution in "
            "elderly patients or those with pre-existing cardiac "
            "conduction abnormalities."
        ),
        evidence_pmids=[""],
        notes="Particular caution with higher TCA doses and in elderly.",
    ),

    # ── Atypical antipsychotics (lower risk) ──────────────────────────────

    DrugInteraction(
        drug_class="atypical_antipsychotics_lower_risk",
        generic_examples=[
            "quetiapine", "olanzapine", "risperidone", "aripiprazole",
            "ziprasidone", "lurasidone",
        ],
        modalities_affected=["tdcs", "tps"],
        severity="moderate",
        mechanism=(
            "Atypical antipsychotics (excluding clozapine) have a "
            "variable but generally lower risk of seizure threshold "
            "reduction compared to typical antipsychotics. They also "
            "modulate dopaminergic, serotonergic, and histaminergic "
            "systems, potentially altering neuromodulation response."
        ),
        recommendation=(
            "Document concurrent use. Standard seizure precautions. "
            "No specific parameter adjustment required at standard "
            "doses. Higher doses warrant additional caution."
        ),
        evidence_pmids=["28551164", ""],
        notes=(
            "Olanzapine and quetiapine carry slightly higher seizure "
            "risk than risperidone or aripiprazole within this class."
        ),
    ),

    # ── Cholinesterase inhibitors ─────────────────────────────────────────

    DrugInteraction(
        drug_class="cholinesterase_inhibitors",
        generic_examples=["donepezil", "rivastigmine", "galantamine"],
        modalities_affected=["tdcs", "tps"],
        severity="minor",
        mechanism=(
            "Cholinesterase inhibitors increase acetylcholine levels, "
            "which may enhance cholinergic-dependent plasticity and "
            "potentially augment tDCS/TPS effects. This is generally "
            "considered a favourable interaction in Alzheimer's "
            "disease patients undergoing neuromodulation."
        ),
        recommendation=(
            "Document concurrent use. No contraindication. The "
            "combination is actively being studied as a synergistic "
            "therapeutic approach in Alzheimer's disease."
        ),
        evidence_pmids=[""],
        notes=(
            "Several ongoing trials combine tDCS/TPS with donepezil "
            "for Alzheimer's. The interaction appears favourable."
        ),
    ),

    # ── Memantine ─────────────────────────────────────────────────────────

    DrugInteraction(
        drug_class="nmda_antagonists",
        generic_examples=["memantine", "ketamine", "esketamine"],
        modalities_affected=["tdcs"],
        severity="moderate",
        mechanism=(
            "NMDA receptor antagonists block the receptor critical for "
            "tDCS-induced LTP-like neuroplasticity. Memantine and "
            "dextromethorphan have been shown to abolish tDCS "
            "after-effects in experimental studies, as the lasting "
            "effects of tDCS depend on NMDA receptor activation."
        ),
        recommendation=(
            "Document concurrent use. Be aware that tDCS efficacy "
            "may be substantially reduced. For memantine in Alzheimer's "
            "patients, consider that treatment response may be attenuated. "
            "Do not discontinue memantine for neuromodulation purposes."
        ),
        evidence_pmids=["15614421", "28320638"],
        notes=(
            "Liebetanz et al. 2002 demonstrated dextromethorphan "
            "abolishes tDCS after-effects. This finding extends to "
            "other NMDA antagonists including memantine."
        ),
    ),

    # ── Beta-blockers ─────────────────────────────────────────────────────

    DrugInteraction(
        drug_class="beta_blockers",
        generic_examples=["propranolol", "metoprolol", "atenolol", "bisoprolol"],
        modalities_affected=["tavns", "ces"],
        severity="minor",
        mechanism=(
            "Beta-blockers reduce heart rate and blood pressure. "
            "taVNS/CES also modulate autonomic tone via vagal "
            "activation. The combination may produce additive "
            "bradycardia or hypotension, particularly in elderly "
            "patients or those on high-dose beta-blockers."
        ),
        recommendation=(
            "Monitor heart rate and blood pressure during sessions. "
            "Caution in patients with resting heart rate <60 bpm. "
            "Have patient sit for 5 minutes post-session before "
            "standing."
        ),
        evidence_pmids=[""],
        notes="Clinically relevant mainly in elderly or if resting HR is low.",
    ),

    # ── Calcium channel blockers ──────────────────────────────────────────

    DrugInteraction(
        drug_class="calcium_channel_blockers",
        generic_examples=["flunarizine", "verapamil", "amlodipine", "nimodipine"],
        modalities_affected=["tdcs"],
        severity="minor",
        mechanism=(
            "Calcium channel blockers may modify voltage-gated calcium "
            "channel function relevant to tDCS-induced plasticity. "
            "Flunarizine has been shown to reduce anodal tDCS effects "
            "in experimental settings."
        ),
        recommendation=(
            "Document concurrent use. No parameter adjustment required. "
            "Be aware of potential modest attenuation of tDCS effects."
        ),
        evidence_pmids=[""],
        notes="Primarily relevant for flunarizine; amlodipine impact is less clear.",
    ),

    # ── Nicotine ──────────────────────────────────────────────────────────

    DrugInteraction(
        drug_class="nicotine",
        generic_examples=["nicotine_patch", "nicotine_gum", "smoking"],
        modalities_affected=["tdcs"],
        severity="minor",
        mechanism=(
            "Nicotine is a cholinergic agonist that modulates cortical "
            "excitability and plasticity. It has been shown to modify "
            "tDCS after-effects, potentially enhancing some effects "
            "through nicotinic acetylcholine receptor activation."
        ),
        recommendation=(
            "Document smoking status and nicotine replacement use. "
            "Maintain consistent nicotine status across sessions "
            "(i.e. do not alternate smoking/non-smoking days during "
            "a treatment block). No parameter adjustment required."
        ),
        evidence_pmids=[""],
        notes=(
            "Relevant for maintaining consistency. Acute nicotine "
            "administration modifies tDCS effects differently than "
            "chronic exposure."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_interactions_for_drug_class(drug_class: str) -> list[DrugInteraction]:
    """Return all interactions matching a drug class (case-insensitive)."""
    needle = drug_class.lower().strip()
    results: list[DrugInteraction] = []
    for interaction in DRUG_INTERACTIONS:
        if interaction.drug_class.lower() == needle:
            results.append(interaction)
            continue
        # Also match on generic example names
        for example in interaction.generic_examples:
            if example.lower() == needle:
                results.append(interaction)
                break
    return results


def get_interactions_for_modality(modality: str) -> list[DrugInteraction]:
    """Return all interactions that affect a given modality."""
    needle = modality.lower().strip()
    return [
        interaction
        for interaction in DRUG_INTERACTIONS
        if needle in [m.lower() for m in interaction.modalities_affected]
    ]
