# DEPRECATED: This script is superseded by the canonical generation pipeline.
# Use instead: GenerationService.generate(condition="...", tier="...", doc_type="...")
# Or CLI: PYTHONPATH=src python -m sozo_generator.cli.main build condition --condition <slug> --tier <tier> --doc-type <type>
# See docs/MIGRATION_PLAN.md for details.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Appends Alzheimer's, Stroke, TBI conditions"""
from pathlib import Path

BLOCK = r'''
# ══════════════════════════════════════
# 5. ALZHEIMER'S DISEASE / MCI
# ══════════════════════════════════════
CONDITIONS["alzheimers"] = dict(
    name="Alzheimer's Disease / MCI", icd10="G30 / F06.7",
    doc_num="SOZO-ALZ-FEL-005",
    tps_status="CE-MARKED FOR ALZHEIMER'S (NEUROLITH) — primary approved indication",
    tdcs_class="Level B evidence; CE-marked",
    tps_class="CE-MARKED \u2014 Primary approved TPS indication",
    tavns_class="Emerging adjunctive; CE-marked",
    ces_class="Supportive adjunct for mood/sleep/anxiety",
    inclusion=[
        "Confirmed diagnosis of MCI or mild-to-moderate Alzheimer's disease (NIA-AA criteria)",
        "MMSE 15\u201326 or MoCA 10\u201325 at baseline",
        "Age 55+ years",
        "Caregiver available for consent support and session attendance if required",
        "Written informed consent (patient and/or legally authorised representative)",
        "Baseline assessments completed (MoCA, MMSE, ADAS-Cog, CDR, NPI)",
    ],
    exclusion=[
        "Intracranial metallic hardware in stimulation path",
        "Cochlear implant or DBS device",
        "Severe dementia (MMSE <10 or CDR \u22653)",
        "Skull defects, craniectomy, or recent craniotomy",
        "Active intracranial tumour",
        "Pregnancy (tDCS, TPS)",
        "Inability to provide any form of informed consent or assent",
    ],
    discussion=[
        "Cardiac pacemaker or defibrillator \u2014 individual risk\u2013benefit assessment",
        "Epilepsy or seizure history \u2014 increased risk in late-stage AD; formal risk\u2013benefit required",
        "Severe behavioural/neuropsychiatric symptoms (agitation, psychosis) \u2014 stabilise first",
        "Anticoagulant use (especially for TPS application)",
        "Dermatological conditions at electrode sites",
        "Significant vascular burden on MRI \u2014 may alter stimulation distribution",
        "Cholinesterase inhibitor or memantine use \u2014 note timing and potential interaction",
        "Moderate-to-severe hearing or vision impairment limiting engagement",
    ],
    overview=[
        "Alzheimer's disease (AD) is the most common cause of dementia, accounting for 60\u201380% of cases "
        "worldwide. Over 55 million people live with dementia globally, with AD representing the greatest "
        "burden. MCI (Mild Cognitive Impairment) represents a transitional state between normal ageing and "
        "dementia, with amnestic MCI carrying the highest AD conversion risk (Petersen et al., 2014).",
        "AD is characterised by progressive accumulation of amyloid-beta plaques and neurofibrillary tangles "
        "(tau hyperphosphorylation), leading to synaptic loss, neuroinflammation, and neuronal death. "
        "The entorhinal cortex and hippocampus are affected earliest; pathology then spreads to "
        "temporoparietal and frontal association cortices (Braak & Braak, 1991).",
        "TPS (NEUROLITH) is CE-marked for Alzheimer's disease \u2014 this is the primary approved clinical "
        "indication for TPS. Multiple pilot studies and early clinical trials have demonstrated improvements "
        "in cognitive function, memory, and activities of daily living in AD patients treated with TPS "
        "(Hescham et al., 2023; Koch et al., 2019). SOZO uses TPS as a primary modality in AD.",
        "tDCS targeting temporal-parietal and frontal regions has shown cognitive benefits in MCI and mild "
        "AD in multiple RCTs. The evidence for tDCS is strongest for memory consolidation (temporal anodal) "
        "and executive function (DLPFC anodal). The combination of TPS and tDCS represents the most "
        "comprehensive SOZO approach to AD (Ferrucci et al., 2008; Meinzer et al., 2015).",
    ],
    pathophysiology=[
        "AD pathophysiology begins with amyloid cascade: amyloid-beta oligomers disrupt synaptic function, "
        "triggering tau hyperphosphorylation, tangle formation, and neuroinflammation via microglial "
        "activation. Cholinergic neurons of the nucleus basalis of Meynert (NBM) are affected early, "
        "impairing the cholinergic projection to hippocampus and cortex \u2014 the basis of cholinesterase "
        "inhibitor therapy.",
        "Default mode network (DMN) disruption is a hallmark of AD: the DMN (particularly the posterior "
        "cingulate cortex, precuneus, and hippocampus) shows early amyloid accumulation and functional "
        "disconnection. This manifests as impaired episodic memory, spatial navigation, and self-referential "
        "processing. The CEN progressively fails as prefrontal involvement increases in moderate AD.",
    ],
    std_treatment=[
        "Pharmacological treatment includes cholinesterase inhibitors (donepezil, rivastigmine, galantamine) "
        "for mild-to-moderate AD, and memantine (NMDA antagonist) for moderate-to-severe AD. Anti-amyloid "
        "monoclonal antibodies (lecanemab, donanemab) represent a new disease-modifying class approved for "
        "early AD/MCI. Non-pharmacological approaches (cognitive stimulation, physical exercise, "
        "multidomain lifestyle interventions) are recommended alongside NIBS.",
    ],
    symptoms=[
        ["Episodic Memory Loss",    "Difficulty learning new information; forgetting recent events; repetition",      "Core criterion",    "Petersen 2014; McKhann 2011"],
        ["Language Impairment",     "Word-finding difficulties (anomia); reduced verbal fluency; paraphasia",         "60\u201380%",       "McKhann 2011"],
        ["Visuospatial Impairment", "Getting lost; difficulty with navigation; constructional apraxia",               "50\u201370%",       "McKhann 2011"],
        ["Executive Dysfunction",   "Planning, abstract reasoning, cognitive flexibility impairment",                 "50\u201380%",       "Salmon 2009"],
        ["Attention Deficits",      "Poor sustained attention; vulnerability to distraction; mental fatigue",         "50\u201380%",       "Salmon 2009"],
        ["Apraxia",                 "Impaired purposeful movements despite intact motor function",                    "30\u201360%",       "Grossman 2010"],
        ["Depression / Apathy",     "Apathy most common NPS; depression frequent; may precede cognitive symptoms",    "40\u201370%",       "Lyketsos 2011"],
        ["Agitation / Anxiety",     "Restlessness, anxiety, verbal and physical agitation",                          "30\u201350%",       "Lyketsos 2011"],
        ["Sleep Disturbance",       "Disrupted circadian rhythms; insomnia; sundowning",                             "40\u201370%",       "McCurry 2000"],
        ["Functional Decline",      "Progressive loss of instrumental and basic ADL abilities",                       "Progressive",       "Alzheimer's Association 2023"],
    ],
    brain_regions=[
        ["Hippocampus",               "Earliest site of AD pathology; episodic memory consolidation",                   "TPS deep target (CE-marked); tDCS temporal anodal (indirect hippocampal modulation)","Koch 2019; Hescham 2023"],
        ["Entorhinal Cortex",         "Grid cells; memory indexing; earliest neurofibrillary tangle site",              "TPS temporal deep target; indirect via tDCS temporal placement",                    "Braak & Braak 1991"],
        ["Temporal Cortex (T3/T4/P3/P4)","Semantic memory; language; visuospatial processing",                        "Anodal tDCS (T3/T4/P3/P4); TPS temporal targeted",                                 "Ferrucci 2008; Meinzer 2015"],
        ["DLPFC",                     "Executive function; working memory; top-down attention",                          "Anodal tDCS primary target; TPS targeted (investigational in AD)",                  "Ferrucci 2008"],
        ["Posterior Cingulate / Precuneus","DMN hub; early amyloid accumulation; connectivity hub",                    "TPS primary target (CE-marked indication); tDCS indirect modulation",               "Koch 2019"],
        ["Parietal Cortex",           "Visuospatial processing; attention; sensorimotor integration",                    "Anodal tDCS (P3/P4); TPS parietal targeted",                                        "McKhann 2011"],
        ["Nucleus Basalis of Meynert","Cholinergic projection source; early neuronal loss in AD",                       "TPS deep target (investigational as cholinergic augmentation strategy)",             "Hescham 2023"],
        ["Prefrontal Cortex",         "Executive control, attention, working memory \u2014 affected in moderate AD",    "DLPFC anodal tDCS; TPS frontal targeted",                                           "Salmon 2009"],
    ],
    brainstem=[
        ["Locus Coeruleus (LC)",         "Early noradrenergic degeneration in AD; arousal and attention impairment",    "taVNS modulates LC via NTS; augments noradrenergic tone for arousal",              "Braak 2004"],
        ["Dorsal Raphe Nucleus",         "Serotonergic degeneration; depression and sleep disturbance in AD",           "taVNS and tDCS (DLPFC) may influence serotonergic projections",                    "Rupprecht 2020"],
        ["Nucleus Tractus Solitarius",   "Vagal afferent relay; modulates hippocampal plasticity via NTS-LC pathway",  "Primary target of taVNS; hippocampal memory consolidation mechanism",             "Frangos 2015"],
        ["Brainstem Cholinergic Nuclei", "Ch5/Ch6 cholinergic neurons; REM sleep and arousal regulation",               "Indirectly modulated by taVNS and tDCS cortical pathways",                        "Mesulam 2013"],
        ["Raphe-Hippocampal Pathway",    "Serotonergic modulation of hippocampal neurogenesis and plasticity",           "taVNS and tDCS indirectly modulate serotonergic-hippocampal circuits",             "Rupprecht 2020"],
    ],
    phenotypes=[
        ["MCI \u2014 Amnestic (Single Domain)",  "Memory impairment only; MoCA/MMSE within norms; daily function preserved",         "Episodic memory loss; word-finding; navigation",         "TPS hippocampal (CE-marked); tDCS temporal anodal"],
        ["MCI \u2014 Multi-Domain",              "Multiple cognitive domains affected but ADL preserved",                             "Memory + executive + language + visuospatial impairment","TPS + tDCS bilateral temporal-parietal-frontal"],
        ["Typical AD \u2014 Mild (MMSE 21\u201326)","Episodic memory dominant; MMSE >20; functional impairment beginning",            "Memory, word-finding, ADL early impairment",            "TPS (CE-marked primary) + tDCS temporal/DLPFC"],
        ["Typical AD \u2014 Moderate (MMSE 15\u201320)","Progressive multi-domain decline; meaningful ADL support needed",            "Memory, language, visuospatial, ADL dependence",        "TPS (CE-marked) + tDCS supportive + caregiver training"],
        ["Posterior Cortical Atrophy",           "Visuospatial and apraxic features dominant; memory relatively preserved",          "Visuospatial, reading, object recognition impairment",  "TPS parietal targeted; tDCS P3/P4 anodal"],
        ["Dysexecutive AD",                      "Executive and frontal features dominant; memory less prominent initially",          "Planning, flexibility, behaviour dysregulation",         "TPS frontal + DLPFC; tDCS F3/F4 anodal"],
        ["AD + Neuropsychiatric (NPS dominant)", "Agitation, apathy, depression as primary burden alongside cognitive decline",       "Apathy, depression, agitation, anxiety, sleep disorder","tDCS DLPFC; TPS; taVNS; CES for NPS"],
    ],
    symptom_map=[
        ["Episodic Memory",           "Hippocampus, Entorhinal, Temporal","TPS deep hippocampal (CE-marked) + tDCS temporal anodal (T3/T4/P3/P4)",                    "Level A (TPS CE-marked; Koch 2019)"],
        ["Language / Anomia",         "Left temporal cortex, IFG",        "Left temporal anodal tDCS (T3/Broca) + TPS temporal-frontal targeted",                      "Moderate (Meinzer 2015)"],
        ["Visuospatial",              "Parietal, occipital, fusiform",     "Bilateral parietal anodal tDCS (P3/P4) + TPS parietal targeted",                           "Moderate (McKhann 2011)"],
        ["Executive Function",        "DLPFC, Frontal, Parietal",         "L-DLPFC anodal tDCS + TPS frontal targeted",                                                "Moderate (Ferrucci 2008)"],
        ["Attention / Vigilance",     "DLPFC, ACC, Parietal",             "DLPFC anodal tDCS + TPS frontal; taVNS for arousal",                                       "Moderate (Ferrucci 2008)"],
        ["Apathy / Depression (NPS)", "DLPFC, ACC, OFC",                  "L-DLPFC tDCS + TPS frontal; taVNS primary + CES",                                          "Moderate (Ferrucci 2008)"],
        ["Sleep Disturbance",         "Frontal, Thalamus, Circadian",     "CES primary; taVNS; tDCS evening slow-wave",                                               "Moderate (Philip 2017)"],
        ["General Cognitive Decline", "Temporal-Parietal-Frontal network","TPS holocranial (CE-marked global protocol) + tDCS bilateral temporal-DLPFC",               "Level A (TPS CE-marked; Koch 2019)"],
        ["Anxiety / Agitation",       "Amygdala, ACC, Insula",            "taVNS primary; CES; bilateral tDCS supportive; non-pharmacological behavioural strategies","Moderate (Lyketsos 2011)"],
    ],
    montage=[
        ["MCI \u2014 Amnestic",      "T3/T4 bilateral anode + P3/P4 anode; Fz cathode",                              "TPS hippocampal targeted + temporal cortex (CE-marked)","taVNS, CES (sleep)"],
        ["MCI \u2014 Multi-Domain",  "T3/T4 + P3/P4 bilateral anode + F3 anode; extracephalic cathode",              "TPS temporal-parietal-frontal targeted (CE-marked)",     "taVNS, CES supportive"],
        ["Mild AD",                  "T3/T4 + P3/P4 bilateral anodal + F3 anode; Fz cathode",                        "TPS holocranial + targeted (CE-marked primary)",         "taVNS, CES; caregiver support"],
        ["Moderate AD",              "T3/T4 bilateral anodal (simplified); F3 anode supportive",                     "TPS holocranial + targeted (CE-marked); lower energy threshold","taVNS, CES; simplified sessions"],
        ["Posterior Cortical",       "P3/P4 bilateral anode + T3/T4 anode; F3 cathode",                              "TPS parietal targeted + temporal",                       "taVNS, CES supportive"],
        ["Dysexecutive AD",          "F3/F4 bilateral anode + P3/P4 anode",                                          "TPS frontal + DLPFC targeted",                           "taVNS, CES supportive"],
        ["AD + NPS",                 "F3 anode + T3/T4 anodal; Pz cathode",                                          "TPS frontal + temporal targeted",                        "taVNS primary; CES"],
        ["No response after 8\u201310 sessions","Reassess cognitive baseline; adjust TPS energy/ROI; add tDCS parietal","Adjust TPS parameters; consider additional ROI",         "Review adjuncts; caregiver coaching"],
    ],
    tdcs_protocols=[
        ["C1","Memory (primary) \u2014 temporal anodal",    "T3/T4 bilateral anode","Fz / extracephalic",         "2 mA, 20\u201330 min, 5\u00d7/wk \u00d7 6\u201310 wks","Level B; memory improvement (Ferrucci 2008; Meinzer 2015)"],
        ["C2","Temporal-parietal bilateral",                 "T3 + T4 + P3 + P4 anode","Fz, extracephalic",      "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Ferrucci 2008)"],
        ["C3","Executive function / DLPFC",                  "F3 anode",         "Fp2 / extracephalic",           "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Ferrucci 2008)"],
        ["C4","Combined memory + executive",                 "F3 + T3/T4 anode", "Fp2 / extracephalic",          "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Meinzer 2015)"],
        ["C5","Attention / vigilance",                       "F3 + P3/P4 anode", "Fp2, extracephalic",           "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Ferrucci 2008)"],
        ["C6","Apathy / depression (NPS)",                   "F3 anode",         "Fp2, extracephalic",           "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Lyketsos 2011)"],
        ["C7","Sleep disturbance",                           "Fz anode",         "Pz / extracephalic",           "1\u20132 mA, 20 min, evening",                       "Moderate (Philip 2017)"],
        ["C8","Maintenance block (MCI)",                     "T3/T4 anode",      "Fz / extracephalic",           "2 mA, 20\u201330 min, 3\u00d7/wk maintenance",      "Moderate (Ferrucci 2008)"],
    ],
    plato_protocols=[
        ["C1-PS","Memory \u2014 temporal",  "Posterior temporal","T3/T4 area","Nape of neck",  "1.6 mA, 20\u201330 min","5\u00d7/wk","Pair with memory encoding tasks"],
        ["C2-PS","Temporal-parietal",        "Posterior temporal","T3/T4 area","Nape of neck",  "1.6 mA, 20\u201330 min","5\u00d7/wk","Adjust placement for parietal"],
        ["C3-PS","Executive / DLPFC",        "Frontal (F3 area)", "F3",         "Right shoulder","1.6 mA, 20\u201330 min","5\u00d7/wk","Cognitive activation during session"],
        ["C4-PS","Combined memory + EF",     "Frontal (F3 area)", "F3",         "Shoulder",      "1.6 mA, 20\u201330 min","5\u00d7/wk","After HDCkit induction phase"],
        ["C5-PS","Attention",               "Frontal (F3 area)", "F3",         "Shoulder",      "1.6 mA, 20\u201330 min","5\u00d7/wk","Caregiver-supervised session"],
        ["C6-PS","Apathy / NPS",             "Frontal (F3 area)", "F3",         "Shoulder",      "1.6 mA, 20\u201330 min","5\u00d7/wk","CES concurrent recommended"],
        ["C7-PS","Sleep disturbance",        "Frontal (Fz area)", "Fz",         "Shoulder",      "1.6 mA, 20 min",        "Evening",    "CES concurrent recommended"],
        ["C8-PS","Maintenance",              "Posterior temporal","T3/T4 area", "Nape of neck",  "1.6 mA, 20\u201330 min","3\u00d7/wk", "Caregiver-supervised maintenance"],
    ],
    tps_protocols=[
        ["T1","Memory / hippocampal (CE-marked primary)","Hippocampus, Entorhinal cortex, Temporal cortex","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz; 10 sessions/2 wks","4,000 Tgt (hippocampal region) + 4,000 Std; total 8\u201312K","CE-MARKED (Koch 2019; Hescham 2023)"],
        ["T2","Global cognitive decline \u2014 holocranial","Holocranial: Frontal + temporal + parietal + posterior cingulate","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz","6,000 Std + 4,000 Tgt; total 8\u201312K","CE-MARKED (Koch 2019)"],
        ["T3","Executive function / DLPFC",              "DLPFC bilateral, mPFC, ACC",        "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz","4,000 Tgt (DLPFC) + 2,000 PRE; total 6\u20138K","CE-MARKED (NEUROLITH AD indication)"],
        ["T4","Posterior cortical (visuospatial)",        "Parietal, precuneus, posterior temporal","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz","4,000 Tgt (parietal) + 2,000 Std; total 6\u20138K","CE-MARKED (NEUROLITH AD indication)"],
        ["T5","NPS (apathy, depression)",                 "DLPFC + ACC + OFC",                 "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz","4,000 Tgt + 2,000 PRE; total 6\u20138K","CE-MARKED (NEUROLITH AD indication)"],
    ],
    ces_role=[
        ["Sleep disturbance",    "Targets insomnia, sundowning, and circadian disruption common in AD",                 "Evening before bed; 20\u201340 min; caregiver-assisted"],
        ["Apathy / Depression",  "Supportive for mild NPS mood symptoms alongside primary tDCS/TPS",                   "Evening sessions; or non-tDCS days; 20\u201340 min"],
        ["Anxiety / Agitation",  "Reduces anxiety and agitation as adjunct to primary protocols",                      "As needed; 20\u201330 min; pre-session for anxious patients"],
        ["Arousal / Motivation", "May improve arousal and motivation; adjunct to cognitive engagement",                 "Morning; 20\u201330 min; caregiver-supervised"],
    ],
    tavns_role="taVNS modulates locus coeruleus noradrenergic tone and NTS-hippocampal circuits, potentially enhancing memory consolidation and arousal in Alzheimer's disease and MCI. It also supports mood and sleep in neuropsychiatric symptom burden.",
    combinations=[
        ("1) MCI \u2014 Amnestic", [
            ["TPS + tDCS (temporal)","TPS hippocampal (CE-marked) + temporal anodal tDCS; evidence-based combination (Koch 2019; Ferrucci 2008)","TPS session + tDCS on same or adjacent days","Episodic memory loss, word-finding, navigation difficulties"],
            ["taVNS + TPS/tDCS","taVNS primes hippocampal plasticity via NTS-LC pathway before primary sessions (Frangos 2015)","taVNS 20\u201330 min before TPS or tDCS","Attention, arousal, memory consolidation"],
            ["CES + Standard Care","CES for sleep and circadian stabilisation; supports memory consolidation overnight (Philip 2017)","Evening before bed","MCI with sleep disturbance and circadian dysregulation"],
        ]),
        ("2) Mild AD", [
            ["TPS + tDCS Combination","TPS holocranial (CE-marked) + tDCS temporal-parietal-frontal; most comprehensive approach (Koch 2019; Ferrucci 2008)","TPS and tDCS on alternating days or combined block","Multi-domain cognitive decline in mild AD"],
            ["taVNS + TPS/tDCS","taVNS augments noradrenergic and cholinergic circuits; additive with TPS and tDCS (Frangos 2015)","taVNS before TPS or tDCS sessions","Attention, arousal, mood, sleep"],
            ["CES + Caregiver Support","CES for NPS and sleep; caregiver education programme integral to mild AD management (Philip 2017)","Evening; caregiver-administered","NPS symptoms, sleep disturbance, anxiety"],
        ]),
        ("3) Moderate AD", [
            ["TPS (CE-marked) + Simplified tDCS","TPS primary; simplified single-site tDCS as adjunct (Koch 2019)","TPS primary; tDCS at reduced burden (3\u00d7/wk)","Moderate multi-domain decline with ADL impairment"],
            ["taVNS + Standard Care","taVNS for autonomic stability and NPS; low burden on patient and caregiver (Frangos 2015)","Daily or 5\u00d7/wk; caregiver-assisted","Agitation, anxiety, sleep disturbance in moderate AD"],
            ["CES + Caregiver Support","CES daily for sleep, agitation, and mood; caregiver programme essential (Philip 2017)","Evening daily if tolerated","Severe sleep disturbance, sundowning, NPS in moderate AD"],
        ]),
        ("4) Posterior Cortical AD", [
            ["TPS (parietal targeted) + tDCS (P3/P4)","TPS parietal + occipital + tDCS bilateral parietal anodal (Koch 2019; Ferrucci 2008)","TPS and tDCS combined block; visuospatial rehabilitation integrated","Visuospatial, reading, object recognition impairment"],
            ["taVNS + TPS/tDCS","taVNS augments overall cortical arousal and plasticity (Frangos 2015)","taVNS before TPS or tDCS","General attention, arousal support"],
            ["CES + Occupational Therapy","CES for sleep/anxiety; OT for visuospatial compensatory strategies (Philip 2017)","Evening (sleep); OT integration","Sleep, anxiety, ADL adaptation for visuospatial deficits"],
        ]),
        ("5) AD + NPS (Apathy/Depression)", [
            ["tDCS (DLPFC) + TPS (frontal)","L-DLPFC anodal tDCS + TPS frontal targeted; addresses NPS alongside cognitive decline (Koch 2019; Ferrucci 2008)","tDCS before TPS or alternating days","Apathy, depression, motivational loss"],
            ["taVNS + Primary Protocols","taVNS for NPS mood modulation and autonomic stabilisation (Frangos 2015)","taVNS before primary sessions; or standalone on off-days","Depression, anxiety, agitation in AD"],
            ["CES + Standard Care","CES for NPS mood, sleep, and anxiety; adjunct to primary protocol (Philip 2017)","Evening and/or morning as prescribed","NPS with sleep, anxiety, and mood burden"],
        ]),
        ("6) MCI Conversion Prevention Focus", [
            ["TPS + tDCS + Cognitive Stimulation","TPS hippocampal + temporal tDCS + structured cognitive stimulation; maximum neuroplasticity approach (Koch 2019)","TPS + tDCS on alternating days; cognitive stimulation daily","MCI with high AD conversion risk"],
            ["taVNS + Lifestyle Intervention","taVNS + multidomain lifestyle programme (exercise, diet, sleep, social engagement)","Daily taVNS; lifestyle programme concurrent","MCI with modifiable risk factor burden"],
            ["CES + Sleep Optimisation","CES for sleep; poor sleep accelerates AD pathology; prioritise sleep in MCI (Philip 2017; Holth 2019)","Evening; sleep hygiene concurrent","MCI with sleep disturbance as conversion risk factor"],
        ]),
    ],
    combination_summary=[
        ["MCI \u2014 Amnestic",    "TPS + tDCS (temporal)",    "TPS hippocampal (CE-marked) + temporal anodal tDCS (Koch 2019; Ferrucci 2008)",               "TPS + tDCS combined block",    "Episodic memory, word-finding",     "Level A (TPS CE-marked)"],
        ["Mild AD",                "TPS + tDCS Combination",   "TPS holocranial (CE-marked) + tDCS temporal-parietal-frontal (Koch 2019; Ferrucci 2008)",      "Alternating days or combined", "Multi-domain cognitive decline",    "Level A (TPS CE-marked)"],
        ["Moderate AD",            "TPS (CE-marked) primary",  "TPS primary with simplified tDCS adjunct (Koch 2019)",                                         "TPS primary 3\u20135\u00d7/wk","Moderate decline, ADL impairment",  "Level A (TPS CE-marked)"],
        ["Posterior Cortical",     "TPS parietal + tDCS P3/P4","TPS parietal + tDCS bilateral parietal anodal (Koch 2019; Ferrucci 2008)",                     "Combined block",               "Visuospatial, apraxia",             "Level A (TPS CE-marked)"],
        ["AD + NPS",               "tDCS (DLPFC) + TPS",       "L-DLPFC anodal tDCS + TPS frontal; addresses NPS alongside cognitive decline (Koch 2019)",      "tDCS before TPS",              "Apathy, depression in AD",          "Moderate"],
        ["MCI Conversion Focus",   "TPS + tDCS + Cognitive Stimulation","TPS hippocampal + temporal tDCS + cognitive stimulation; maximum neuroplasticity (Koch 2019)","TPS + tDCS + daily CST","MCI conversion prevention",        "Level A (TPS CE-marked)"],
    ],
    outcomes=[
        ["MoCA",               "Global cognition screening",             "Baseline, months 1, 3, 6",     "Score <26 impairment; track \u22652-point improvement"],
        ["MMSE",               "Global cognitive severity",              "Baseline, months 1, 3, 6",     "21\u201326 mild; 10\u201320 moderate; <10 severe AD"],
        ["ADAS-Cog",           "AD cognitive battery (primary outcome)", "Baseline, months 3, 6",        "\u22654-point improvement = clinically meaningful change"],
        ["CDR",                "Clinical Dementia Rating \u2014 global", "Baseline, months 3, 6",        "0 = normal; 0.5 = MCI; 1 = mild; 2 = moderate; 3 = severe"],
        ["NPI",                "Neuropsychiatric Inventory (NPS)",       "Baseline, months 3, 6",        "Track improvement in apathy, depression, agitation subscales"],
        ["ADL / IADL",         "Functional independence",                "Baseline, months 3, 6",        "Track maintenance or improvement in daily activities"],
        ["PHQ-9 or GDS",       "Comorbid depressive symptoms",          "Baseline, months 3, 6",        "\u226510 moderate depression (PHQ-9)"],
        ["Quality of Life \u2014 AD (QoL-AD)","Subjective wellbeing",   "Baseline, months 3, 6",        "Score range 13\u201352; higher = better QoL"],
        ["SOZO PRS",           "NIBS-specific functional outcome",       "Baseline, weeks 2, 4, 8, 12", "Proprietary; composite cognitive/NPS/functional domains"],
    ],
    outcomes_abbrev=["MoCA", "MMSE", "ADAS-Cog", "CDR", "SOZO PRS"],
)

# ══════════════════════════════════════
# 6. STROKE REHABILITATION
# ══════════════════════════════════════
CONDITIONS["stroke_rehab"] = dict(
    name="Post-Stroke Rehabilitation", icd10="I63 / I64",
    doc_num="SOZO-STR-FEL-006",
    tps_status="INVESTIGATIONAL / OFF-LABEL",
    tdcs_class="Level B evidence; CE-marked",
    tps_class="INVESTIGATIONAL / OFF-LABEL",
    tavns_class="Emerging adjunctive; CE-marked",
    ces_class="Supportive adjunct for mood/sleep",
    inclusion=[
        "Confirmed ischaemic or haemorrhagic stroke diagnosis (neuroimaging confirmed)",
        "At least 1 month post-stroke (subacute to chronic phase eligible)",
        "Residual motor, cognitive, language, or mood impairment amenable to rehabilitation",
        "Age 18+ years",
        "Medically stable; cleared for active rehabilitation by treating neurologist",
        "Baseline assessments completed (NIHSS, Fugl-Meyer, FIM, MoCA, PHQ-9)",
    ],
    exclusion=[
        "Intracranial metallic hardware or haemorrhagic transformation within stimulation path",
        "Cochlear implant or DBS device",
        "Active intracranial haemorrhage or unstable vascular lesion",
        "Skull defects or craniectomy at electrode/transducer sites",
        "Severe aphasia preventing informed consent (consider proxy consent pathway)",
        "Pregnancy (tDCS, TPS)",
        "Medically unstable (uncontrolled hypertension, cardiac instability, recent TIA)",
    ],
    discussion=[
        "Cardiac pacemaker or defibrillator \u2014 individual risk\u2013benefit assessment",
        "Epilepsy or post-stroke seizures \u2014 formal risk\u2013benefit with documented rationale",
        "Coagulation disorders or anticoagulants (especially TPS) \u2014 haematoma risk",
        "Large cortical or subcortical lesion in stimulation path \u2014 altered current distribution",
        "Severe neglect limiting session compliance",
        "Dermatological conditions at electrode sites",
        "Significant spasticity preventing electrode/transducer placement",
        "Severe post-stroke depression requiring psychiatric referral before NIBS initiation",
    ],
    overview=[
        "Stroke is the second leading cause of death and a major cause of disability worldwide. "
        "Approximately 15 million strokes occur annually; over 5 million result in permanent disability. "
        "Post-stroke rehabilitation addresses motor recovery, cognitive rehabilitation, language therapy, "
        "and mood management across the acute, subacute, and chronic phases.",
        "tDCS can modulate cortical excitability to support stroke recovery by enhancing ipsilesional "
        "motor cortex excitability (anodal tDCS) or suppressing contralesional hyperactivity (cathodal "
        "tDCS). Both strategies, and the bihemispheric approach (anodal ipsilesional + cathodal "
        "contralesional), have been investigated in multiple RCTs (Elsner et al., 2016; Bikson et al., 2016).",
        "The principle of use-dependent plasticity is central: tDCS administered during or immediately "
        "before rehabilitation (physical therapy, occupational therapy, aphasia therapy) amplifies "
        "practice-induced neuroplastic changes. TPS is investigational in stroke, targeting ipsilesional "
        "motor and premotor cortex.",
        "NIBS Evidence in Stroke: Level B evidence supports tDCS for post-stroke motor recovery. "
        "Meta-analyses demonstrate significant improvements in upper limb function, gait, and some "
        "cognitive outcomes with combined tDCS + rehabilitation. taVNS paired with rehabilitation "
        "has emerging evidence from the VNS-REHAB RCT.",
    ],
    pathophysiology=[
        "Stroke disrupts the balance between ipsilesional and contralesional hemispheres. The lesioned "
        "hemisphere loses excitatory input; the intact hemisphere becomes relatively hyperactive, "
        "exerting transcallosal inhibition on the damaged side. This interhemispheric imbalance is the "
        "primary target of tDCS in stroke rehabilitation.",
        "Cortical reorganisation following stroke involves perilesional tissue plasticity, recruitment "
        "of ipsilateral pathways, and diaschisis resolution. Neuromodulation during the critical "
        "plasticity window (subacute phase: weeks 1\u20133 months post-stroke) may amplify these processes. "
        "White matter tract integrity and lesion location are key predictors of tDCS response.",
    ],
    std_treatment=[
        "Standard stroke rehabilitation includes intensive physical therapy, occupational therapy, "
        "speech-language therapy, neuropsychological rehabilitation, and mood management. "
        "Evidence-based rehabilitation intensity (National Stroke Foundation guidelines) recommends "
        "at least 3 hours of active rehabilitation per day in the acute/subacute phase. "
        "NIBS is adjunctive to standard rehabilitation and should always be paired with active therapy.",
    ],
    symptoms=[
        ["Hemiplegia / Hemiparesis",  "Weakness or paralysis of ipsilesional limbs; upper limb most affected", "Majority",          "Langhorne 2011"],
        ["Spasticity",                "Velocity-dependent muscle tone increase; limb posturing",                 "30\u201340%",       "Sommerfeld 2004"],
        ["Gait Impairment",           "Reduced gait speed, step length, balance, fall risk",                    "60\u201380%",       "Langhorne 2011"],
        ["Post-Stroke Depression",    "Depressed mood, tearfulness, anhedonia, apathy post-stroke",             "30\u201340%",       "Robinson 2016"],
        ["Cognitive Impairment",      "Attention, memory, executive function, processing speed deficits",        "50\u201370%",       "Dichgans 2007"],
        ["Aphasia",                   "Expressive, receptive, or mixed language impairment",                    "30\u201335%",       "Berthier 2005"],
        ["Spatial Neglect",           "Failure to attend to or act on stimuli on one side (usually left)",       "20\u201330%",       "Ringman 2004"],
        ["Fatigue",                   "Post-stroke fatigue; central and peripheral components",                  "40\u201368%",       "Duncan 2012"],
        ["Dysphagia",                 "Swallowing impairment; aspiration risk",                                  "30\u201350%",       "Martino 2005"],
        ["Pain",                      "Central post-stroke pain, shoulder pain, spasticity-related pain",        "10\u201330%",       "Klit 2009"],
    ],
    brain_regions=[
        ["Ipsilesional M1",              "Reduced excitability post-stroke; primary motor execution",            "Anodal tDCS primary target; restores ipsilesional excitability (Level B)",    "Elsner 2016; Bikson 2016"],
        ["Contralesional M1",            "Relative hyperactivation; transcallosal inhibition of ipsilesional M1","Cathodal tDCS to reduce contralesional hyperactivity; bihemispheric approach","Fregni 2006"],
        ["Ipsilesional SMA / Premotor",  "Motor planning and sequencing; compensatory activation post-stroke",   "Anodal tDCS SMA/premotor; TPS ipsilesional premotor (investigational)",     "Zimerman 2012"],
        ["DLPFC",                        "Cognitive function; post-stroke depression; attention",                 "L-DLPFC anodal tDCS for PSD and cognitive recovery",                        "Bhogal 2003"],
        ["Broca / Left IFG",             "Expressive language; aphasia rehabilitation",                           "Left IFG anodal tDCS during aphasia therapy; TPS (investigational)",        "Baker 2010"],
        ["Right Parietal",               "Spatial attention; contralesional neglect circuit",                     "Cathodal tDCS right parietal or anodal left parietal for neglect",          "Brighina 2003"],
        ["Thalamus",                     "Relay for motor and sensory signals; diaschisis target",                "TPS deep target (investigational); indirect modulation via cortical tDCS",  "Yamamoto 2010"],
        ["Cerebellum",                   "Balance, coordination, gait; compensatory activation post-stroke",     "Cerebellar tDCS for gait/balance; TPS (investigational)",                   "Grimaldi 2016"],
    ],
    brainstem=[
        ["Corticospinal Tract",       "Descending motor pathways; lesion severity determinant",              "Not directly stimulated; integrity assessed for tDCS response prediction","Stinear 2017"],
        ["Locus Coeruleus (LC)",      "Noradrenergic arousal; post-stroke fatigue and mood regulation",      "taVNS modulates LC; addresses post-stroke fatigue and depression",          "Robinson 2016"],
        ["Nucleus Tractus Solitarius","Vagal afferent relay; central autonomic hub; post-stroke autonomic",  "Primary target of taVNS; VNS-REHAB mechanism for motor recovery",           "Dawson 2016"],
        ["Dorsal Raphe Nucleus",      "Serotonergic regulation; post-stroke depression and fatigue",         "taVNS and tDCS (DLPFC) modulate serotonergic tone",                         "Robinson 2016"],
        ["Periaqueductal Gray",       "Pain modulation; post-stroke central pain circuits",                  "Indirectly modulated via cortical and vagal neuromodulation",               "Klit 2009"],
    ],
    phenotypes=[
        ["Acute Motor Recovery (1\u20133 months)","Early post-stroke; maximum neuroplasticity window",           "Hemiplegia/hemiparesis, spasticity, gait impairment",          "Ipsilesional M1 anodal tDCS + intensive physio; TPS (investigational)"],
        ["Post-Stroke Depression (PSD)",          "Significant depression post-stroke; impairs rehab engagement", "Depressed mood, anhedonia, anergia, tearfulness, apathy",      "L-DLPFC anodal tDCS; taVNS; CES; antidepressant if indicated"],
        ["Post-Stroke Aphasia",                   "Expressive, receptive, or mixed language impairment",          "Language impairment, word-finding, comprehension difficulties","Left IFG anodal tDCS during language therapy; TPS (investigational)"],
        ["Spatial Neglect",                       "Failure to attend to or act on contralateral stimuli",          "Spatial neglect, attention asymmetry, functional impairment",  "Cathodal right parietal or anodal left parietal tDCS"],
        ["Chronic Motor Deficit (>6 months)",     "Chronic phase with plateau or slow recovery",                  "Residual weakness, spasticity, reduced gait speed",            "Bihemispheric tDCS; TPS motor cortex; VNS + physio (VNS-REHAB)"],
        ["Post-Stroke Cognitive Impairment",      "Attention, memory, executive deficits post-stroke",            "Cognitive slowing, attention, memory, executive dysfunction",   "DLPFC anodal tDCS; TPS frontal-temporal targeted"],
        ["Post-Stroke Fatigue",                   "Pervasive fatigue disproportionate to physical exertion",       "Fatigue, reduced endurance, poor engagement with rehab",       "tDCS DLPFC; taVNS primary; CES adjunct"],
    ],
    symptom_map=[
        ["Upper Limb Motor Deficit",   "Ipsilesional M1, SMA, Premotor","Ipsilesional M1 anodal tDCS + intensive upper limb therapy (Level B evidence; Elsner 2016)",   "Level B (Elsner 2016)"],
        ["Gait / Lower Limb",          "Ipsilesional M1, SMA",          "Ipsilesional M1/SMA anodal tDCS + gait training; TPS motor cortex (investigational)",         "Moderate (Elsner 2016)"],
        ["Post-Stroke Depression",     "L-DLPFC, sgACC",                "L-DLPFC anodal tDCS + psychotherapy; taVNS primary; CES adjunct",                           "Moderate (Bhogal 2003; Robinson 2016)"],
        ["Aphasia",                    "Left IFG (Broca), Temporal",    "Left IFG anodal tDCS during aphasia therapy; TPS left frontal-temporal (investigational)",    "Moderate (Baker 2010; Elsner 2016)"],
        ["Spatial Neglect",            "Right Parietal, Right TPJ",     "Right parietal cathodal tDCS or left parietal anodal; prism adaptation therapy",             "Moderate (Brighina 2003)"],
        ["Cognitive Impairment",       "DLPFC, Parietal, Temporal",     "DLPFC anodal tDCS + cognitive rehabilitation; TPS frontal-temporal targeted",               "Moderate (Elsner 2016)"],
        ["Post-Stroke Fatigue",        "DLPFC, SMA, Mesolimbic",        "DLPFC tDCS + taVNS primary; CES for arousal; graded exercise programme",                   "Moderate (taVNS: Dawson 2016)"],
        ["Pain",                       "Contralateral M1, ACC, Thalamus","Contralateral M1 anodal tDCS; TPS motor cortex + thalamus; taVNS; CES",                   "Moderate (Klit 2009; Fregni 2011)"],
        ["Spasticity",                 "Ipsilesional M1, SMA",          "Cathodal tDCS over spastic muscle area; TPS (investigational); stretching programme",        "Emerging (Elsner 2016)"],
    ],
    montage=[
        ["Motor deficit (upper limb)",  "Ipsilesional M1 anodal (C3 or C4 contralateral to weakness) + contralesional cathodal","Cranial (ipsilesional M1/SMA targeted) + peripheral (affected limb)","taVNS (VNS-REHAB)"],
        ["Bihemispheric (chronic motor)","Ipsilesional M1 anode + contralesional M1 cathode; simultaneous dual-site","Cranial ipsilesional + contralesional targeted",    "taVNS; CES supportive"],
        ["Post-Stroke Depression",       "F3 anode + Fp2 cathode (L-DLPFC anodal)",                                "Cranial (global + targeted L-DLPFC)",                        "taVNS primary; CES"],
        ["Aphasia",                      "Left IFG/Broca anode (F7/Broca area) + right shoulder cathode",          "Cranial (left frontal-temporal targeted)",                    "taVNS; language therapy concurrent"],
        ["Spatial Neglect",              "Right parietal (P4) cathode + left parietal (P3) anode",                 "Cranial (bilateral parietal targeted)",                       "taVNS; prism adaptation therapy"],
        ["Cognitive impairment",         "F3 + T3/T4 bilateral anode + P3/P4; extracephalic cathode",              "Cranial (frontal-temporal-parietal targeted)",                "taVNS, CES supportive"],
        ["Post-stroke fatigue",          "F3 anode + Fp2 cathode; taVNS as primary modality",                      "Cranial (global + targeted DLPFC)",                          "taVNS primary; CES; graded exercise"],
        ["No response after 8\u201310 sessions","Reassess lesion location; consider alternate montage; add TPS","TPS ipsilesional targeted; alternate ROI",                    "VNS-REHAB pairing if available"],
    ],
    tdcs_protocols=[
        ["C1","Upper limb motor (ipsilesional anodal)","C3/C4 (ipsilesional M1) anode","C3/C4 (contralesional) cathode / extracephalic","2 mA, 20\u201330 min, 5\u00d7/wk during upper limb therapy","Level B; UL function (Elsner 2016)"],
        ["C2","Bihemispheric motor",                  "Ipsilesional M1 anode","Contralesional M1 cathode; simultaneous",       "2 mA, 20\u201330 min, 5\u00d7/wk",            "Moderate (Fregni 2006)"],
        ["C3","Post-stroke depression",               "F3 anode (L-DLPFC)","Fp2 / extracephalic",                            "2 mA, 20\u201330 min, 5\u00d7/wk",            "Moderate (Bhogal 2003; Robinson 2016)"],
        ["C4","Aphasia rehabilitation",               "Left F7/Broca anode","Right shoulder cathode",                         "2 mA, 20\u201330 min during language therapy","Moderate (Baker 2010)"],
        ["C5","Spatial neglect",                      "Left P3 anode","Right P4 cathode",                                   "2 mA, 20\u201330 min + prism adaptation therapy","Moderate (Brighina 2003)"],
        ["C6","Cognitive rehabilitation",             "F3 + T3/T4 anode","Fp2, extracephalic",                              "2 mA, 20\u201330 min, 5\u00d7/wk + cognitive rehab","Moderate (Elsner 2016)"],
        ["C7","Gait / lower limb motor",              "Ipsilesional M1/SMA anode (Cz/Fz)","Extracephalic; or contralesional cathode","2 mA, 20\u201330 min + gait training", "Moderate (Elsner 2016)"],
        ["C8","Post-stroke fatigue",                  "F3 anode","Fp2, extracephalic",                                       "2 mA, 20\u201330 min, 5\u00d7/wk + graded exercise","Moderate (Elsner 2016)"],
    ],
    plato_protocols=[
        ["C1-PS","Upper limb motor",     "Motor (Cz area)",   "Cz (ipsilesional)","Shoulder (contralesional)","1.6 mA, 20\u201330 min","5\u00d7/wk during physio","Single-channel approximation of C3/C4"],
        ["C2-PS","Bihemispheric",        "Motor (Cz area)",   "Cz","Nape of neck",  "1.6 mA, 20\u201330 min","5\u00d7/wk",              "Limited bihemispheric; HDCkit preferred"],
        ["C3-PS","Post-stroke depression","Frontal (F3 area)","F3","Right shoulder", "1.6 mA, 20\u201330 min","5\u00d7/wk",              "L-DLPFC anodal primary"],
        ["C4-PS","Aphasia",              "Frontal (F3/F7 area)","F3","Right shoulder","1.6 mA, 20\u201330 min","5\u00d7/wk during language therapy","Limited; HDCkit preferred for left IFG"],
        ["C5-PS","Spatial neglect",      "Posterior (Pz area)","Pz","Shoulder",       "1.6 mA, 20\u201330 min","5\u00d7/wk + prism therapy","Parietal approximation"],
        ["C6-PS","Cognitive rehab",      "Frontal (F3 area)", "F3","Shoulder",        "1.6 mA, 20\u201330 min","5\u00d7/wk + cognitive tasks","Pair with cognitive rehabilitation"],
        ["C7-PS","Gait / lower limb",    "Motor (Cz area)",   "Cz","Nape of neck",   "1.6 mA, 20\u201330 min","5\u00d7/wk + gait training","Combine with gait training"],
        ["C8-PS","Fatigue",              "Frontal (F3 area)", "F3","Shoulder",        "1.6 mA, 20\u201330 min","5\u00d7/wk + graded exercise","Morning; graded exercise concurrent"],
    ],
    tps_protocols=[
        ["T1","Upper limb motor recovery","Ipsilesional M1, SMA, Premotor cortex",  "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz; 10 sessions/2 wks","4,000 Std + 4,000 Tgt (ipsilesional M1); total 8\u201312K","Emerging (investigational in stroke)"],
        ["T2","Gait / lower limb recovery","Ipsilesional M1 (leg area), SMA, Cerebellum","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",              "4,000 Tgt + 2,000 PRE; total 6\u20138K",             "Investigational"],
        ["T3","Post-stroke depression",    "DLPFC bilateral, ACC",                   "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                  "4,000 Tgt (DLPFC) + 2,000 PRE; total 6\u20138K",    "Investigational"],
        ["T4","Aphasia recovery",          "Left IFG, Left temporal cortex",          "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                  "4,000 Tgt (left IFG/temporal) + 2,000 Std; total 6\u20138K","Investigational"],
        ["T5","Cognitive rehabilitation",  "DLPFC, Temporal, Parietal",              "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                  "4,000 Tgt + 2,000 PRE; total 6\u20138K",             "Investigational"],
    ],
    ces_role=[
        ["Post-stroke depression", "Supportive for mild-to-moderate PSD alongside primary tDCS; FDA-cleared for mood", "Evening sessions; or non-tDCS days; 20\u201340 min"],
        ["Sleep disturbance",      "Targets post-stroke insomnia and circadian disruption",                             "Evening before bed; 20\u201340 min"],
        ["Anxiety / Autonomic",    "Stabilises post-stroke autonomic tone and anxiety",                                 "As needed; pre-session or evening; 20\u201330 min"],
        ["Fatigue",                "May improve post-stroke fatigue and arousal as adjunct",                            "Morning; 20\u201330 min; coordinate with rehabilitation schedule"],
    ],
    tavns_role="taVNS is supported by the VNS-REHAB RCT for upper limb motor recovery when paired with rehabilitation. It modulates locus coeruleus noradrenergic tone, neuroplasticity signalling, and autonomic balance; a primary adjunct modality in post-stroke rehabilitation at SOZO.",
    combinations=[
        ("1) Acute Motor Recovery", [
            ["tDCS + Intensive Physiotherapy","Ipsilesional M1 anodal tDCS + intensive upper limb/gait therapy during stimulation; most supported stroke NIBS combination (Elsner 2016)","tDCS during physiotherapy session","Hemiplegia, hemiparesis, gait impairment"],
            ["taVNS + Rehabilitation","taVNS + upper limb rehabilitation; VNS-REHAB RCT demonstrated significant UL motor gains (Dawson 2016; 2021)","taVNS concurrent with rehabilitation exercises","Upper limb motor deficit; use-dependent plasticity"],
            ["CES + Standard Care","CES for post-stroke fatigue and mood support; adjunct throughout acute rehabilitation (Philip 2017)","Evening; or before rehabilitation for arousal","Post-stroke fatigue, mood disturbance"],
        ]),
        ("2) Post-Stroke Depression", [
            ["tDCS (DLPFC) + Psychotherapy","L-DLPFC anodal tDCS + structured psychotherapy (CBT or IPT); addresses PSD whilst supporting cognitive recovery (Robinson 2016; Bhogal 2003)","tDCS before therapy session","Depressed mood, anhedonia, tearfulness post-stroke"],
            ["taVNS + tDCS","taVNS for autonomic and mood regulation; additive with DLPFC tDCS in PSD (Dawson 2016; Robinson 2016)","taVNS before tDCS","PSD with autonomic dysregulation and fatigue"],
            ["CES + Standard Care","CES for sleep and mood in PSD; FDA-cleared; well-tolerated in post-stroke population (Philip 2017)","Evening daily if tolerated","PSD with insomnia, anxiety, somatic complaints"],
        ]),
        ("3) Aphasia Rehabilitation", [
            ["tDCS (left IFG) + Speech-Language Therapy","Left IFG anodal tDCS during aphasia therapy; most supported language combination in stroke (Baker 2010; Elsner 2016)","tDCS during speech-language therapy session","Expressive aphasia, anomia, reduced verbal fluency"],
            ["taVNS + Language Therapy","taVNS augments cortical plasticity and noradrenergic tone; emerging for aphasia recovery (Dawson 2016)","taVNS before language therapy session","Aphasia with fatigue and motivational challenges"],
            ["CES + Standard Care","CES for sleep, mood, and arousal; supports therapy engagement (Philip 2017)","Evening","Aphasia with post-stroke depression and sleep disturbance"],
        ]),
        ("4) Chronic Motor Deficit", [
            ["Bihemispheric tDCS + Intensive Physio","Ipsilesional anodal + contralesional cathodal tDCS + intensive upper limb/gait therapy (Elsner 2016; Fregni 2006)","tDCS during physiotherapy; intensive daily programme","Chronic residual weakness, spasticity, reduced function"],
            ["taVNS + Rehabilitation","taVNS paired with rehabilitation in chronic stroke; VNS-REHAB showed sustained benefit (Dawson 2021)","taVNS concurrent with rehabilitation","Chronic upper limb deficit; plateau in recovery"],
            ["CES + Fatigue Management","CES for chronic post-stroke fatigue; enables better rehabilitation engagement (Philip 2017)","Morning and/or before rehabilitation session","Chronic fatigue limiting rehabilitation participation"],
        ]),
        ("5) Post-Stroke Cognitive Impairment", [
            ["tDCS (DLPFC/temporal) + Cognitive Rehabilitation","DLPFC + temporal anodal tDCS + structured cognitive rehabilitation; targets attention, memory, executive function (Elsner 2016)","tDCS before/during cognitive rehabilitation","Attention, memory, executive function impairment post-stroke"],
            ["taVNS + Cognitive Rehabilitation","taVNS augments noradrenergic tone for attention and memory; adjunct to cognitive rehabilitation (Dawson 2016)","taVNS before cognitive training","Attentional fatigue, processing speed reduction"],
            ["CES + Standard Care","CES for sleep and mood; supports cognitive rehabilitation engagement (Philip 2017)","Evening","Cognitive impairment with sleep disturbance and mood"],
        ]),
        ("6) Post-Stroke Fatigue", [
            ["tDCS (DLPFC) + Graded Exercise","DLPFC anodal tDCS + graded exercise programme; addresses central fatigue mechanisms (Elsner 2016)","tDCS before exercise/rehabilitation session","Persistent post-stroke fatigue limiting rehabilitation"],
            ["taVNS + Standard Care","taVNS primary for fatigue; modulates arousal and autonomic tone via LC-NE pathway (Dawson 2016)","taVNS daily; 20\u201330 min before activity","Central post-stroke fatigue with autonomic dysregulation"],
            ["CES + Standard Care","CES for sleep and energy; addresses fatigue maintaining cycle of poor sleep (Philip 2017)","Morning (energy) and evening (sleep) as prescribed","Fatigue with sleep disturbance and mood"],
        ]),
    ],
    combination_summary=[
        ["Acute Motor Recovery",   "tDCS + Intensive Physio",      "Ipsilesional M1 anodal tDCS + intensive rehabilitation; most supported combination (Elsner 2016)", "tDCS during physio", "Hemiplegia, hemiparesis",     "Level B"],
        ["Acute Motor Recovery",   "taVNS + Rehabilitation",        "VNS-REHAB RCT demonstrated significant UL motor gains (Dawson 2016; 2021)",                       "taVNS concurrent", "Upper limb motor deficit",    "Level B (VNS-REHAB)"],
        ["Post-Stroke Depression", "tDCS + Psychotherapy",          "L-DLPFC anodal tDCS + psychotherapy for PSD (Robinson 2016; Bhogal 2003)",                        "tDCS before therapy","Depressed mood, anhedonia",    "Moderate"],
        ["Aphasia",                "tDCS (left IFG) + SLT",         "Left IFG anodal tDCS + aphasia therapy; most supported language combination (Baker 2010)",          "tDCS during SLT",  "Expressive aphasia, anomia",  "Moderate"],
        ["Chronic Motor Deficit",  "Bihemispheric tDCS + Physio",   "Bihemispheric tDCS + intensive physio in chronic phase (Elsner 2016; Fregni 2006)",                "tDCS during physio","Chronic residual weakness",   "Moderate"],
        ["Post-Stroke Cognitive",  "tDCS + Cognitive Rehabilitation","DLPFC + temporal tDCS + structured cognitive rehabilitation (Elsner 2016)",                         "tDCS before cog rehab","Attention, memory, EF",     "Moderate"],
    ],
    outcomes=[
        ["NIHSS",                  "Neurological deficit severity",          "Baseline, weeks 4, 8, 12",     "Score 0 = no symptoms; \u226525 = severe; track improvement"],
        ["Fugl-Meyer (Upper Limb)","Upper limb motor function",              "Baseline, weeks 4, 8, 12",     "Maximum 66 (UL); \u226510% change = clinically meaningful"],
        ["FIM",                    "Functional Independence Measure",        "Baseline, months 1, 3",        "Score 18\u2013126; higher = more independent"],
        ["Barthel Index",          "Activities of daily living",             "Baseline, months 1, 3",        "Score 0\u2013100; \u226575 = mildly dependent"],
        ["MoCA",                   "Global cognition screening",             "Baseline, month 3",            "Score <26 cognitive impairment; track improvement"],
        ["PHQ-9",                  "Post-stroke depression",                 "Baseline, weeks 4, 8, 12",     "\u226510 moderate depression"],
        ["10-Meter Walk Test",     "Gait speed",                             "Baseline, weeks 4, 8, 12",     "Normal >0.8 m/s; post-stroke typically 0.2\u20130.6 m/s"],
        ["mRS",                    "Modified Rankin Scale",                  "Baseline, month 3",            "0\u20131 excellent; 2\u20133 moderate dependency; 4\u20135 severe"],
        ["SOZO PRS",               "NIBS-specific functional outcome",       "Baseline, weeks 2, 4, 8, 12", "Proprietary; composite motor/mood/cognitive/functional domains"],
    ],
    outcomes_abbrev=["NIHSS", "Fugl-Meyer", "FIM", "PHQ-9", "SOZO PRS"],
)

# ══════════════════════════════════════
# 7. TRAUMATIC BRAIN INJURY
# ══════════════════════════════════════
CONDITIONS["tbi"] = dict(
    name="Traumatic Brain Injury", icd10="S06 / F07.2",
    doc_num="SOZO-TBI-FEL-007",
    tps_status="INVESTIGATIONAL / OFF-LABEL",
    tdcs_class="Level B evidence; CE-marked",
    tps_class="INVESTIGATIONAL / OFF-LABEL",
    tavns_class="Emerging adjunctive; CE-marked",
    ces_class="FDA-cleared adjunctive for mood/anxiety/sleep",
    inclusion=[
        "Confirmed TBI diagnosis (neuroimaging or clinical criteria; Glasgow Coma Scale \u22658 on admission)",
        "At least 3 months post-injury (chronic/subacute phase eligible)",
        "Residual cognitive, motor, mood, or functional impairment amenable to rehabilitation",
        "Age 18+ years; medically stable",
        "Written informed consent (patient and/or legally authorised representative)",
        "Baseline assessments completed (RBANS, MoCA, NSI, PCL-5, PHQ-9)",
    ],
    exclusion=[
        "Intracranial metallic hardware, cranioplasty hardware, or retained metallic fragments in stimulation path",
        "Active intracranial haemorrhage or coagulopathy",
        "Skull defects or craniectomy at electrode/transducer sites",
        "Cochlear implant or DBS device",
        "Post-traumatic epilepsy (seizure within past 12 months) \u2014 absolute exclusion",
        "Pregnancy (tDCS, TPS)",
        "Severe cognitive impairment precluding informed consent without proxy",
    ],
    discussion=[
        "Cardiac pacemaker or defibrillator \u2014 individual risk\u2013benefit assessment",
        "Epilepsy risk / sub-clinical seizures \u2014 higher post-TBI; EEG monitoring if clinical concern",
        "Active suicidality \u2014 psychiatric referral and safety planning before NIBS initiation",
        "PTSD comorbidity \u2014 trauma-informed approach required; tailored stimulation protocol",
        "Coagulation disorders or anticoagulants (especially TPS)",
        "Dermatological conditions or scalp injuries at electrode sites",
        "Blast TBI \u2014 polytrauma context; multidisciplinary coordination required",
        "Vestibular dysfunction \u2014 may be exacerbated; careful taVNS titration",
    ],
    overview=[
        "Traumatic Brain Injury (TBI) results from external mechanical force to the head, causing focal "
        "or diffuse brain injury. TBI is a leading cause of disability worldwide: approximately 69 million "
        "TBIs occur annually (Dewan et al., 2018). Sequelae range from transient post-concussion symptoms "
        "in mild TBI to profound cognitive, motor, and behavioural impairment in severe TBI.",
        "Chronic TBI sequelae commonly include post-concussion syndrome (PCS), cognitive impairment "
        "(attention, memory, executive function), post-traumatic depression and anxiety, PTSD, "
        "post-traumatic headache, sleep disturbance, and fatigue. Diffuse axonal injury (DAI) disrupts "
        "white matter tracts, impairing network connectivity across frontal-parietal and frontal-subcortical "
        "circuits.",
        "tDCS targeting the DLPFC (anodal) has shown improvements in working memory, attention, and "
        "executive function in TBI across multiple studies. The prefrontal cortex is consistently affected "
        "in TBI, making it the primary NIBS target (Dmochowski et al., 2013; Pape et al., 2020).",
        "NIBS Evidence in TBI: Level B evidence supports DLPFC tDCS for post-TBI cognitive rehabilitation. "
        "TPS is investigational. taVNS has plausible mechanisms for post-TBI mood, sleep, and cognitive "
        "deficits. CES is FDA-cleared for anxiety and mood, highly relevant to TBI comorbidities.",
    ],
    pathophysiology=[
        "TBI pathophysiology involves primary injury (diffuse axonal injury, contusion, haematoma) and "
        "secondary injury cascades (neuroinflammation, excitotoxicity, oxidative stress, oedema, ischaemia). "
        "DAI disrupts major white matter tracts (corpus callosum, long association fibres), impairing "
        "fronto-parietal networks, attention circuits, and default mode network connectivity.",
        "Chronic neuroinflammation, tau accumulation (risk for CTE in repetitive TBI), and impaired "
        "glymphatic clearance contribute to progressive neurodegeneration. The orbitofrontal cortex and "
        "prefrontal regions are selectively vulnerable due to bony ridges causing contre-coup injury. "
        "Hypothalamic-pituitary dysfunction is common in moderate-severe TBI, affecting hormonal "
        "regulation and sleep.",
    ],
    std_treatment=[
        "TBI rehabilitation is multidisciplinary: cognitive rehabilitation, neuropsychological therapy, "
        "physical and occupational therapy, speech-language therapy, and mental health management. "
        "Pharmacological management targets specific symptoms: antidepressants for PCS mood symptoms, "
        "amantadine for consciousness and cognition, stimulants (methylphenidate, amantadine) for "
        "attention in chronic TBI. NIBS is adjunctive to comprehensive rehabilitation.",
    ],
    symptoms=[
        ["Cognitive Impairment",     "Attention, working memory, processing speed, executive function deficits",  "Most common",      "Dewan 2018; Pape 2020"],
        ["Post-Concussion Headache", "Tension-type, migraine-like, or mixed headache post-TBI",                   "50\u201390% (mTBI)","Lew 2006"],
        ["Fatigue",                  "Post-TBI mental and physical fatigue; often most disabling symptom",         "50\u201378%",      "Lew 2006"],
        ["Sleep Disturbance",        "Insomnia, hypersomnia, circadian disruption, sleep apnoea risk",             "50\u201380%",      "Castriotta 2011"],
        ["Depression",               "Post-TBI depression; often comorbid with PCS, PTSD, and anxiety",           "25\u201350%",      "Jorge 2016"],
        ["Anxiety / PTSD",           "Post-traumatic anxiety, PTSD in 10\u201340% of TBI survivors",              "10\u201340%",      "Bryant 2010"],
        ["Irritability / Aggression","Emotional dysregulation, aggression, impulsivity; frontal disinhibition",    "30\u201370%",      "Alderman 2003"],
        ["Balance / Vestibular",     "Dizziness, vestibular dysfunction, balance impairment",                      "30\u201365%",      "Lew 2006"],
        ["Sensory Sensitivity",      "Light sensitivity (photophobia), sound sensitivity (phonophobia)",           "50\u201370% (mTBI)","Lew 2006"],
        ["Motor Deficits",           "Hemiplegia/hemiparesis, spasticity, coordination impairment (mod-severe TBI)","Variable (severity-dependent)","Dewan 2018"],
    ],
    brain_regions=[
        ["DLPFC (bilateral)",         "Most consistently affected by TBI; executive function, WM, attention",    "Bilateral DLPFC anodal tDCS primary target; Level B evidence",              "Dmochowski 2013; Pape 2020"],
        ["OFC / Prefrontal",          "Vulnerable to coup-contre-coup; emotional regulation, impulse control",   "Prefrontal tDCS; TPS frontal targeted (investigational)",                   "Alderman 2003"],
        ["Parietal Cortex",           "Attention, sensorimotor integration, spatial processing impairment",       "Parietal anodal tDCS + tDCS-cognitive training combination",                "Dmochowski 2013"],
        ["Temporal Cortex",           "Memory consolidation; language; disrupted in lateral TBI impacts",         "Temporal anodal tDCS + memory rehabilitation",                              "Pape 2020"],
        ["Cerebellum",                "Balance, coordination, vestibular integration; disrupted in TBI",          "Cerebellar tDCS for balance/vestibular rehabilitation (emerging)",          "Grimaldi 2016"],
        ["Anterior Cingulate Cortex", "Pain, attention, conflict monitoring; disrupted in frontal TBI",           "Prefrontal tDCS modulates ACC; TPS ACC targeted (investigational)",        "Lew 2006"],
        ["Corpus Callosum",           "Interhemispheric transfer; DAI primary target in TBI",                     "Not directly stimulated; integrity informs bihemispheric tDCS approach",   "Dewan 2018"],
        ["Hippocampus",               "Memory consolidation; vulnerable to excitotoxic damage post-TBI",          "TPS temporal/hippocampal (investigational); temporal tDCS indirect",        "Dewan 2018"],
    ],
    brainstem=[
        ["Locus Coeruleus (LC)",       "Noradrenergic dysregulation post-TBI; fatigue, attention, mood",          "taVNS modulates LC; augments noradrenergic tone for attention/mood",       "Aston-Jones 2005"],
        ["Nucleus Tractus Solitarius", "Vagal afferent relay; autonomic regulation post-TBI",                     "Primary target of taVNS; modulates arousal and cortical plasticity",       "Frangos 2015"],
        ["Dorsal Raphe Nucleus",       "Serotonergic dysregulation; depression, sleep, pain post-TBI",            "taVNS and tDCS (DLPFC) may modulate serotonergic projections",            "Jorge 2016"],
        ["Reticular Activating System","Arousal and consciousness; damaged in severe TBI (DAI)",                  "taVNS and tDCS indirectly modulate ascending arousal pathways",            "Moruzzi 1949"],
        ["Periaqueductal Gray (PAG)",  "Pain modulation; post-TBI headache circuitry",                            "Indirectly modulated via cortical and vagal neuromodulation",              "Lew 2006"],
    ],
    phenotypes=[
        ["Mild TBI / Post-Concussion Syndrome","Cognitive symptoms, headache, fatigue, sleep disturbance post-mTBI","Cognitive symptoms, headache, fatigue, emotional lability","L-DLPFC anodal tDCS; CES (sleep/headache); taVNS"],
        ["Moderate-Severe TBI \u2014 Cognitive","Significant cognitive impairment; attention, memory, EF deficits","Attention, memory, EF, processing speed impairment",             "Bilateral DLPFC tDCS; TPS frontal; cognitive rehab"],
        ["TBI + Depression",                    "Post-TBI depression as primary psychiatric comorbidity",          "Depressed mood, anhedonia, anergia, irritability",                "L-DLPFC anodal tDCS; taVNS; CES; antidepressant if indicated"],
        ["TBI + PTSD",                          "PTSD superimposed on TBI; complex comorbidity",                   "Re-experiencing, avoidance, hyperarousal, mood, cognition",       "Bilateral DLPFC tDCS; taVNS primary; CES; trauma-informed Rx"],
        ["TBI \u2014 Frontal Dysexecutive",     "Frontal lobe syndrome; disinhibition, impulsivity, EF deficit",  "Impulsivity, disinhibition, planning failure, aggression",        "DLPFC anodal + OFC tDCS; TPS frontal; DBT integration"],
        ["Blast TBI",                           "Military/combat blast TBI; polytrauma context; often mTBI",       "PCS + PTSD + auditory + vestibular + headache",                   "Bilateral DLPFC tDCS; taVNS primary; CES; MDT approach"],
        ["TBI + Chronic Pain / Headache",       "Persistent headache or chronic pain as primary burden",           "Headache, pain, fatigue, sleep disturbance, mood",                "M1 + DLPFC tDCS; taVNS; CES primary for headache/sleep"],
    ],
    symptom_map=[
        ["Attention / Processing Speed","DLPFC, ACC, Parietal",        "Bilateral DLPFC anodal tDCS + attention rehabilitation; TPS DLPFC (investigational)",       "Level B (Dmochowski 2013)"],
        ["Working Memory",              "DLPFC, Parietal, Temporal",   "L-DLPFC anodal tDCS + WM training (n-back); TPS DLPFC targeted",                          "Level B (Pape 2020)"],
        ["Executive Function",          "DLPFC, OFC, ACC",             "Bilateral DLPFC anodal tDCS + executive training; TPS frontal (investigational)",          "Level B (Pape 2020)"],
        ["Post-TBI Depression",         "L-DLPFC, sgACC",              "L-DLPFC anodal tDCS + psychotherapy; taVNS primary; CES adjunct",                        "Moderate (Jorge 2016)"],
        ["PTSD",                        "vmPFC, DLPFC, Amygdala",      "Bilateral DLPFC tDCS + trauma-informed therapy; taVNS primary; CES",                      "Moderate (Bryant 2010)"],
        ["Sleep Disturbance",           "Frontal, Thalamus, Circadian", "CES primary; taVNS; tDCS evening slow-wave",                                             "Moderate (Philip 2017)"],
        ["Fatigue",                     "DLPFC, SMA, Arousal systems",  "DLPFC tDCS + taVNS primary; CES; graded activity programme",                             "Moderate (Lew 2006)"],
        ["Post-TBI Headache",           "M1, ACC, Thalamus",            "M1 + DLPFC tDCS; CES primary for headache; taVNS; headache management",                  "Moderate (Lew 2006)"],
        ["Emotional Dysregulation",     "OFC, DLPFC, Amygdala",        "DLPFC anodal tDCS; taVNS; CES; DBT or emotion regulation therapy",                       "Moderate (Alderman 2003)"],
    ],
    montage=[
        ["Mild TBI / PCS",           "F3 anode + Fp2 cathode (L-DLPFC primary); or bilateral F3 + F4 anode","Cranial (global + targeted DLPFC)","taVNS, CES (headache/sleep)"],
        ["Moderate-Severe Cognitive","F3 + F4 bilateral anode (bilateral DLPFC); T3/T4 + P3/P4 addition",   "Cranial (global + targeted DLPFC/temporal/parietal)","taVNS, CES supportive"],
        ["TBI + Depression",         "F3 anode + Fp2 cathode (L-DLPFC anodal)",                             "Cranial (global + targeted L-DLPFC)",              "taVNS primary; CES"],
        ["TBI + PTSD",               "F3 + F4 bilateral anode; or F4 anode + F3 anode (bilateral)",         "Cranial (global + targeted bilateral DLPFC)",      "taVNS primary; CES; trauma-informed approach"],
        ["Frontal Dysexecutive",      "F3 anode + OFC area; bilateral DLPFC approach",                      "Cranial (global + targeted frontal circuits)",     "taVNS, CES; DBT integration"],
        ["Blast TBI",                 "Bilateral DLPFC (F3 + F4 anode); slower titration protocol",         "Cranial (global + targeted bilateral DLPFC)",      "taVNS primary; CES; MDT"],
        ["Chronic Pain / Headache",   "F3 anode + C3/C4 (contra to pain) cathode / extracephalic",          "Cranial + peripheral (pain dermatomes if relevant)","taVNS; CES primary (headache)"],
        ["No response after 8\u201310 sessions","Reassess lesion imaging; adjust montage; add TPS","TPS DLPFC frontal targeted; adjust ROI",             "Review all adjuncts; MDT referral"],
    ],
    tdcs_protocols=[
        ["C1","Cognitive (attention, WM) \u2014 primary","F3 anode + F4 anode (bilateral)","Fp1 + Fp2 / extracephalic","2 mA, 20\u201330 min, 5\u00d7/wk \u00d7 6\u201310 wks","Level B; attention/WM (Dmochowski 2013; Pape 2020)"],
        ["C2","L-DLPFC (attention/memory)",               "F3 anode",            "Fp2 / extracephalic",          "2 mA, 20\u201330 min, 5\u00d7/wk",             "Level B (Pape 2020)"],
        ["C3","Executive function",                        "F3 + F4 bilateral",   "Fp1 + Fp2 / extracephalic",   "2 mA, 20\u201330 min, 5\u00d7/wk + EF training","Level B (Pape 2020)"],
        ["C4","Post-TBI depression",                       "F3 anode",            "Fp2 / extracephalic",          "2 mA, 20\u201330 min, 5\u00d7/wk",             "Moderate (Jorge 2016)"],
        ["C5","TBI + PTSD",                                "F3 + F4 bilateral",   "Extracephalic shoulders",      "2 mA, 20\u201330 min, 5\u00d7/wk",             "Moderate (Bryant 2010)"],
        ["C6","Sleep disturbance",                         "Fz anode",            "Pz / extracephalic",           "1\u20132 mA, 20 min, evening",                  "Moderate (Philip 2017)"],
        ["C7","Post-TBI headache + pain",                  "F3 anode + C3/C4","F4 / extracephalic",              "2 mA, 20\u201330 min, 5\u00d7/wk",             "Moderate (Lew 2006)"],
        ["C8","Emotional dysregulation",                   "F3 + F4 bilateral",   "Extracephalic shoulders",      "2 mA, 20\u201330 min, 5\u00d7/wk + DBT",       "Moderate (Alderman 2003)"],
    ],
    plato_protocols=[
        ["C1-PS","Cognitive (attention/WM)", "Frontal (F3 area)","F3","Right shoulder",  "1.6 mA, 20\u201330 min","5\u00d7/wk","Bilateral approach: HDCkit preferred"],
        ["C2-PS","L-DLPFC attention",        "Frontal (F3 area)","F3","Right shoulder",  "1.6 mA, 20\u201330 min","5\u00d7/wk","Pair with attention tasks"],
        ["C3-PS","Executive function",       "Frontal (F3 area)","F3","Shoulder",        "1.6 mA, 20\u201330 min","5\u00d7/wk","Combine with executive training"],
        ["C4-PS","Post-TBI depression",      "Frontal (F3 area)","F3","Right shoulder",  "1.6 mA, 20\u201330 min","5\u00d7/wk","Adjunct taVNS and CES recommended"],
        ["C5-PS","TBI + PTSD",               "Frontal (F3 area)","F3","Shoulder",        "1.6 mA, 20\u201330 min","5\u00d7/wk","Trauma-informed session approach"],
        ["C6-PS","Sleep disturbance",        "Frontal (Fz area)","Fz","Shoulder",        "1.6 mA, 20 min",        "Evening",    "CES concurrent recommended"],
        ["C7-PS","Headache + pain",          "Motor (Cz area)",  "Cz","Shoulder/arm",    "1.6 mA, 20\u201330 min","5\u00d7/wk","CES primary for headache adjunct"],
        ["C8-PS","Emotional dysregulation",  "Frontal (F3 area)","F3","Shoulder",        "1.6 mA, 20\u201330 min","5\u00d7/wk","DBT therapy concurrent"],
    ],
    tps_protocols=[
        ["T1","Cognitive rehabilitation (primary)","Bilateral DLPFC, ACC, mPFC",   "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz; 10 sessions/2 wks","4,000 Tgt (DLPFC bilateral) + 2,000 PRE; total 6\u20138K","Investigational"],
        ["T2","Frontal dysexecutive",               "DLPFC + OFC + ACC",            "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                  "4,000 Tgt + 2,000 Std; total 6\u20138K",             "Investigational"],
        ["T3","Post-TBI depression / PTSD",         "L-DLPFC + ACC + mPFC",        "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                  "4,000 Tgt (L-DLPFC) + 2,000 PRE; total 6\u20138K",  "Investigational"],
        ["T4","Memory rehabilitation",              "DLPFC + temporal cortex",      "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                  "4,000 Tgt + 2,000 PRE; total 6\u20138K",             "Investigational"],
        ["T5","Post-TBI pain / headache",           "M1 + ACC + Thalamus",          "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                  "4,000 Tgt + 2,000 PRE; total 6\u20138K",             "Investigational"],
    ],
    ces_role=[
        ["Sleep disturbance",      "Primary target: post-TBI insomnia; circadian disruption; nightmares; FDA-cleared",  "Evening before bed; 20\u201340 min"],
        ["Post-TBI depression",    "Supportive adjunct for PCS mood symptoms; FDA-cleared for mood",                    "Evening sessions or non-tDCS days; 20\u201340 min"],
        ["Anxiety / PTSD",         "FDA-cleared for anxiety; reduces physiological anxiety symptoms",                   "Before tDCS session or evening; 20\u201340 min"],
        ["Post-TBI headache",      "May reduce headache frequency and intensity as adjunct to primary protocols",        "As needed; 20\u201330 min; avoid during acute headache"],
    ],
    tavns_role="taVNS modulates locus coeruleus noradrenergic tone and autonomic balance relevant to post-TBI fatigue, mood, and cognitive deficits. It also modulates inflammatory cascades, potentially relevant to secondary neuroinflammation in TBI.",
    combinations=[
        ("1) Mild TBI / PCS", [
            ["tDCS + Cognitive Rehabilitation","L-DLPFC anodal tDCS + computerised attention and cognitive rehabilitation; most evidence-based TBI combination (Pape 2020; Dmochowski 2013)","tDCS before/during cognitive tasks","Attention, WM, processing speed, cognitive fatigue"],
            ["taVNS + tDCS","taVNS primes noradrenergic tone before tDCS; supports attention and mood recovery (Hein 2021; Aston-Jones 2005)","taVNS 20\u201330 min before tDCS","Cognitive fatigue, emotional dysregulation, autonomic symptoms"],
            ["CES + Standard Care","CES primary for post-TBI headache, sleep, and anxiety; FDA-cleared; well-tolerated in mTBI (Philip 2017)","Daily as prescribed; evening primary","PCS with headache, sleep disturbance, anxiety"],
        ]),
        ("2) TBI + Depression", [
            ["tDCS (DLPFC) + Psychotherapy","L-DLPFC anodal tDCS + CBT or trauma-informed therapy; addresses post-TBI depression (Jorge 2016)","tDCS before therapy session","Post-TBI depressed mood, anhedonia, anergia"],
            ["taVNS + tDCS","taVNS for autonomic and mood modulation; augments antidepressant tDCS effect (Hein 2021)","taVNS before tDCS","Depression with autonomic dysregulation and fatigue"],
            ["CES + Standard Care","CES for sleep, anxiety, and mood; integral to TBI depression management (Philip 2017)","Evening daily; morning for energy","Post-TBI depression with insomnia and anxiety"],
        ]),
        ("3) TBI + PTSD", [
            ["tDCS + Trauma-Informed Therapy","Bilateral DLPFC tDCS + EMDR or CPT; enhances prefrontal regulation of trauma responses (Bryant 2010)","tDCS before trauma-focused therapy","PTSD symptoms superimposed on TBI"],
            ["taVNS + Therapy","taVNS reduces physiological threat response before trauma therapy; key for hyperarousal (Hein 2021)","taVNS 20\u201330 min before therapy session","Hyperarousal, autonomic reactivity, sleep disturbance"],
            ["CES + Standard Care","CES FDA-cleared for anxiety; reduces hyperarousal symptoms in PTSD-TBI (Philip 2017)","Daily as prescribed","PTSD with severe anxiety, insomnia, and physiological arousal"],
        ]),
        ("4) TBI + Frontal Dysexecutive", [
            ["tDCS + Executive Training","Bilateral DLPFC anodal tDCS + executive function training (planning, WM, flexibility) (Pape 2020)","tDCS before/during executive training","Disinhibition, impulsivity, planning failure"],
            ["taVNS + DBT","taVNS for emotional dysregulation; DBT for skills-based regulation of impulsivity (Hein 2021)","taVNS before DBT session","Frontal disinhibition, emotional lability, aggression"],
            ["CES + Standard Care","CES for sleep and baseline arousal stabilisation; reduces emotional threshold (Philip 2017)","As needed; morning or evening","Emotional dysregulation with sleep and anxiety burden"],
        ]),
        ("5) TBI + Chronic Pain / Headache", [
            ["tDCS (M1 + DLPFC) + Pain Management","M1 + DLPFC tDCS + graded activity/pain psychology; top-down pain modulation (Lew 2006; Fregni 2011)","tDCS before activity or pain management session","Chronic post-TBI headache, central pain, musculoskeletal pain"],
            ["taVNS + Standard Care","taVNS modulates ascending pain pathways and autonomic arousal; analgesic adjunct (Adair 2020)","Before flare-prone periods or on off-days","Pain with autonomic arousal, anxiety-pain loop"],
            ["CES + Standard Care","CES reduces post-TBI headache, sleep disturbance, and anxiety-pain amplification (Philip 2017)","Daily; evening primary for sleep","Post-TBI headache with insomnia and anxiety"],
        ]),
        ("6) Blast TBI", [
            ["Bilateral tDCS + MDT Rehabilitation","Bilateral DLPFC tDCS + multidisciplinary rehabilitation (cognitive, physical, psychological); standard blast TBI approach (Pape 2020)","tDCS during cognitive/physical rehabilitation session","Blast TBI: PCS + PTSD + vestibular + headache"],
            ["taVNS + Bilateral tDCS","taVNS primary for autonomic hyperarousal and PTSD overlay; augments cognitive tDCS (Hein 2021)","taVNS before tDCS; gentler titration","Blast TBI with PTSD and autonomic features"],
            ["CES + Standard Care","CES daily for sleep, anxiety, and headache; essential in blast TBI management (Philip 2017)","Daily as prescribed","Blast TBI with sleep disturbance, anxiety, headache burden"],
        ]),
    ],
    combination_summary=[
        ["Mild TBI / PCS",         "tDCS + Cognitive Rehab",        "L-DLPFC anodal tDCS + cognitive rehabilitation (Pape 2020; Dmochowski 2013)",              "tDCS before/during tasks", "Attention, WM, cognitive fatigue", "Level B"],
        ["TBI + Depression",       "tDCS + Psychotherapy",           "L-DLPFC tDCS + CBT/trauma-informed therapy (Jorge 2016)",                                 "tDCS before therapy",       "Post-TBI depression",              "Moderate"],
        ["TBI + PTSD",             "tDCS + Trauma Therapy",          "Bilateral DLPFC tDCS + EMDR/CPT; prefrontal regulation of trauma (Bryant 2010)",            "tDCS before therapy",       "PTSD superimposed on TBI",         "Moderate"],
        ["Frontal Dysexecutive",   "tDCS + Executive Training",      "Bilateral DLPFC tDCS + EF training (planning, WM, flexibility) (Pape 2020)",               "tDCS before EF training",   "Disinhibition, impulsivity, EF",   "Level B"],
        ["TBI + Headache/Pain",    "tDCS (M1+DLPFC) + Pain Management","M1 + DLPFC tDCS + graded activity/pain psychology (Lew 2006; Fregni 2011)",               "tDCS before pain session",  "Chronic post-TBI headache, pain",  "Moderate"],
        ["Blast TBI",              "Bilateral tDCS + MDT",            "Bilateral DLPFC tDCS + multidisciplinary rehabilitation (Pape 2020)",                       "tDCS during MDT",           "Blast TBI: PCS + PTSD",            "Moderate"],
    ],
    outcomes=[
        ["RBANS",                  "Comprehensive neuropsychological battery",  "Baseline, months 1, 3",        "Normative z-scores; track improvement in attention, memory, EF"],
        ["MoCA",                   "Global cognition screening",                 "Baseline, months 1, 3",        "Score <26 cognitive impairment"],
        ["NSI",                    "Neurobehavioral Symptom Inventory (PCS)",    "Baseline, weeks 4, 8, 12",     "Score 0\u201388; higher = greater symptom burden; track improvement"],
        ["PHQ-9",                  "Post-TBI depression",                        "Baseline, weeks 4, 8, 12",     "\u226510 moderate depression"],
        ["PCL-5",                  "PTSD Checklist (DSM-5)",                     "Baseline, weeks 4, 8, 12",     "Score \u226533 probable PTSD; track \u226510-point improvement"],
        ["ISI",                    "Insomnia severity",                          "Baseline, weeks 4, 8, 12",     "Score \u226715 moderate insomnia"],
        ["GAD-7",                  "Comorbid anxiety",                           "Baseline, weeks 4, 8, 12",     "\u226510 moderate anxiety"],
        ["Timed Up and Go (TUG)", "Balance and motor function",                 "Baseline, months 1, 3",        ">14 seconds elevated fall risk (TBI/vestibular context)"],
        ["SOZO PRS",               "NIBS-specific functional outcome",          "Baseline, weeks 2, 4, 8, 12", "Proprietary; composite cognitive/mood/sleep/functional domains"],
    ],
    outcomes_abbrev=["RBANS", "MoCA", "NSI", "PHQ-9", "SOZO PRS"],
)
'''

with open(str(Path(__file__).resolve().parent / "generate_fellow_protocols.py"), "a", encoding="utf-8") as f:
    f.write(BLOCK)
print("Alzheimer's + Stroke + TBI appended OK")
