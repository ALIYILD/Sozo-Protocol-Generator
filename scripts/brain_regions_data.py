# -*- coding: utf-8 -*-
"""
SOZO Brain Center -- Neuroanatomy Reference.
22 brain regions with neuromodulation targeting information.
Source: SOZO Master Neuromodulation Protocols Excel, April 2026.
"""

# BRAIN_REGIONS[abbreviation] = {
#   "name", "abbreviation", "eeg_position", "hemisphere", "depth",
#   "functions", "key_conditions" (list), "modalities" (list), "notes"
# }
BRAIN_REGIONS = {
    "DLPFC": {
        "name": "Dorsolateral Prefrontal Cortex",
        "abbreviation": "DLPFC",
        "eeg_position": "F3 (L), F4 (R)",
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Executive function, working memory, cognitive control, mood regulation, cognitive flexibility",
        "key_conditions": ["Depression", "OCD", "ADHD", "Schizophrenia", "Cognitive impairment", "Addiction"],
        "modalities": ["TMS", "tDCS", "TPS", "tACS", "PBM", "LIFU", "tRNS", "PEMF"],
        "notes": "Primary TMS target for depression. L-DLPFC for depression; R-DLPFC for anxiety/PTSD",
    },
    "M1": {
        "name": "Primary Motor Cortex",
        "abbreviation": "M1",
        "eeg_position": "C3 (L), C4 (R)",
        "hemisphere": "Contralateral to limb",
        "depth": "Cortical",
        "functions": "Motor execution, voluntary movement generation, corticospinal tract origin",
        "key_conditions": ["Parkinson's", "Stroke", "Chronic pain", "Dystonia", "MS"],
        "modalities": ["TMS", "tDCS", "TPS", "tACS", "PBM", "PEMF", "tRNS"],
        "notes": "Contralateral targeting -- L-M1 controls R body and vice versa. rMT measured here.",
    },
    "SMA": {
        "name": "Supplementary Motor Area",
        "abbreviation": "SMA",
        "eeg_position": "Fz / FCz",
        "hemisphere": "Bilateral (midline)",
        "depth": "Cortical",
        "functions": "Motor planning, movement sequencing, bimanual coordination, gait initiation",
        "key_conditions": ["Parkinson's", "OCD", "Dystonia"],
        "modalities": ["TMS", "TPS", "tDCS"],
        "notes": "Medial frontal location. TPS/TMS target for PD motor sequencing.",
    },
    "ACC": {
        "name": "Anterior Cingulate Cortex",
        "abbreviation": "ACC",
        "eeg_position": "Fz / AFz / Cz",
        "hemisphere": "Bilateral (midline)",
        "depth": "Cortical (deep cortex)",
        "functions": "Error monitoring, emotional regulation, conflict detection, pain modulation, attention",
        "key_conditions": ["OCD", "Depression", "Chronic pain", "ADHD"],
        "modalities": ["TMS", "tDCS", "LIFU", "tACS"],
        "notes": "Difficult to reach with surface stimulation. LIFU and deep TMS (H coils) reach better.",
    },
    "IFG": {
        "name": "Inferior Frontal Gyrus",
        "abbreviation": "IFG",
        "eeg_position": "F7 (L=Broca), F8 (R)",
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Language production (Broca area L), inhibitory control, cognitive flexibility",
        "key_conditions": ["Alzheimer's (TPS)", "Aphasia", "OCD"],
        "modalities": ["TMS", "TPS", "LIFU"],
        "notes": "Broca area (L-IFG) critical for language. TPS targets as part of DMN network.",
    },
    "LPC": {
        "name": "Lateral Parietal Cortex",
        "abbreviation": "LPC",
        "eeg_position": "P3 (L), P4 (R)",
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Attention, spatial processing, visuospatial awareness, working memory buffer",
        "key_conditions": ["Alzheimer's", "MCI", "Hemineglect"],
        "modalities": ["TMS", "tDCS", "TPS", "tRNS"],
        "notes": "TPS targets as part of AD/MCI multi-site protocol. Right LPC for hemineglect.",
    },
    "TC": {
        "name": "Temporal Cortex / Auditory Cortex",
        "abbreviation": "TC",
        "eeg_position": "T3/T5 (L), T4/T6 (R)",
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Auditory processing, language comprehension (Wernicke L), memory encoding, semantic processing",
        "key_conditions": ["Tinnitus", "Schizophrenia (hallucinations)", "Alzheimer's", "Epilepsy (temporal lobe)"],
        "modalities": ["TMS", "tDCS", "tACS", "taVNS", "tRNS"],
        "notes": "Primary target for tinnitus (inhibitory TMS) and auditory hallucinations (schizophrenia).",
    },
    "PCu": {
        "name": "Precuneus",
        "abbreviation": "PCu",
        "eeg_position": "Pz",
        "hemisphere": "Bilateral (midline)",
        "depth": "Cortical",
        "functions": "Self-referential processing, episodic memory retrieval, visual-spatial imagery, consciousness",
        "key_conditions": ["Alzheimer's", "MCI", "Depression", "DOC"],
        "modalities": ["TMS", "TPS", "tDCS"],
        "notes": "Key default mode network hub. TPS targets as part of AD protocol.",
    },
    "OFC": {
        "name": "Orbitofrontal Cortex",
        "abbreviation": "OFC",
        "eeg_position": "Fp1 (L), Fp2 (R)",
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Decision-making, reward/punishment processing, emotion regulation, impulse control",
        "key_conditions": ["OCD", "Addiction", "Depression"],
        "modalities": ["TMS", "tDCS", "LIFU"],
        "notes": "Important node in corticostriatal OCD and addiction circuits.",
    },
    "S1": {
        "name": "Primary Somatosensory Cortex",
        "abbreviation": "S1",
        "eeg_position": "C3p / C4p",
        "hemisphere": "Contralateral",
        "depth": "Cortical",
        "functions": "Tactile sensation, proprioception, pain processing (somatotopic map)",
        "key_conditions": ["Chronic pain", "Stroke", "Phantom limb"],
        "modalities": ["TMS", "tDCS"],
        "notes": "Adjacent to M1. Targeted in stroke and pain protocols.",
    },
    "HC": {
        "name": "Hippocampus",
        "abbreviation": "HC",
        "eeg_position": "Deep (T3/T5 approximate surface)",
        "hemisphere": "Bilateral",
        "depth": "Subcortical (temporal lobe)",
        "functions": "Memory consolidation, spatial navigation, new learning (declarative memory), fear extinction",
        "key_conditions": ["Alzheimer's", "Epilepsy (temporal)", "PTSD", "Depression"],
        "modalities": ["LIFU", "DBS", "taVNS (indirect)", "TPS (indirect via DMN)"],
        "notes": "Cannot be directly targeted by surface stimulation. LIFU, DBS, and intranasal PBM can reach it.",
    },
    "Amy": {
        "name": "Amygdala",
        "abbreviation": "Amy",
        "eeg_position": "Deep (T3/T4 approximate)",
        "hemisphere": "Bilateral",
        "depth": "Subcortical (temporal lobe)",
        "functions": "Fear processing, emotional learning, stress response, threat detection",
        "key_conditions": ["PTSD", "Anxiety", "Depression", "Addiction"],
        "modalities": ["LIFU", "DBS (NAc adjacent)", "taVNS (indirect)"],
        "notes": "Deep structure, not directly accessible by surface stimulation. LIFU can modulate.",
    },
    "Th": {
        "name": "Thalamus",
        "abbreviation": "Th",
        "eeg_position": "Deep (central)",
        "hemisphere": "Bilateral",
        "depth": "Deep subcortical",
        "functions": "Sensory relay, consciousness regulation, gating of motor output, arousal, attention",
        "key_conditions": ["Essential tremor (VIM)", "Pain", "DOC", "Epilepsy (ANT)", "PD (CM-Pf)"],
        "modalities": ["DBS", "LIFU", "tACS (indirect)", "taVNS (indirect)"],
        "notes": "Multiple nuclei: VIM (tremor), ANT (epilepsy), CM-Pf (Tourette), MD (depression).",
    },
    "STN": {
        "name": "Subthalamic Nucleus",
        "abbreviation": "STN",
        "eeg_position": "Deep basal ganglia",
        "hemisphere": "Bilateral",
        "depth": "Deep subcortical",
        "functions": "Motor control (indirect pathway), behavioral inhibition, decision-making",
        "key_conditions": ["Parkinson's disease (primary)", "OCD"],
        "modalities": ["DBS", "LIFU (emerging)"],
        "notes": "Primary DBS target for PD. Smaller target than GPi. Risk of dysarthria and mood effects.",
    },
    "GPi": {
        "name": "Globus Pallidus Internus",
        "abbreviation": "GPi",
        "eeg_position": "Deep basal ganglia",
        "hemisphere": "Bilateral",
        "depth": "Deep subcortical",
        "functions": "Motor output regulation (indirect and direct pathways), movement suppression/facilitation",
        "key_conditions": ["Parkinson's", "Dystonia", "Tourette's", "Huntington's"],
        "modalities": ["DBS"],
        "notes": "Larger target than STN, less dysarthria risk. Preferred for dyskinesia and dystonia.",
    },
    "NAc": {
        "name": "Nucleus Accumbens",
        "abbreviation": "NAc",
        "eeg_position": "Deep striatum",
        "hemisphere": "Bilateral",
        "depth": "Deep subcortical",
        "functions": "Reward processing, motivation, addiction, pleasure, aversion",
        "key_conditions": ["Addiction", "OCD", "Depression (via VC/VS)"],
        "modalities": ["DBS", "LIFU (emerging)"],
        "notes": "Core of reward system. DBS target for addiction and OCD. Overlap with VC/VS target.",
    },
    "IC": {
        "name": "Insula",
        "abbreviation": "IC",
        "eeg_position": "Deep (T3/T4 adjacent)",
        "hemisphere": "Bilateral",
        "depth": "Cortical (buried in Sylvian fissure)",
        "functions": "Interoception, pain integration, emotional awareness, taste, autonomic regulation, addiction",
        "key_conditions": ["Chronic pain", "Addiction", "Smoking cessation", "Depression"],
        "modalities": ["TMS (H-coil deep)", "LIFU", "DBS (emerging)"],
        "notes": "Targeted by deep TMS for smoking cessation. LIFU can reach with precision.",
    },
    "Cereb": {
        "name": "Cerebellum",
        "abbreviation": "Cereb",
        "eeg_position": "Oz / posterior region",
        "hemisphere": "Bilateral",
        "depth": "Posterior fossa",
        "functions": "Motor coordination, balance, fine movement, procedural learning, cognitive functions (emerging)",
        "key_conditions": ["Ataxia", "Essential tremor", "ASD (cerebellar-cortical circuits)"],
        "modalities": ["TMS", "tDCS", "TPS (emerging)"],
        "notes": "Cerebellar TMS increasingly studied. Modulates cerebello-thalamo-cortical circuit.",
    },
    "ABVN": {
        "name": "Vagus Nerve (auricular branch)",
        "abbreviation": "ABVN",
        "eeg_position": "Ear (cymba conchae, tragus)",
        "hemisphere": "Left side preferred",
        "depth": "Peripheral nerve (brain interface)",
        "functions": "Autonomic regulation, anti-inflammatory, neuromodulation of brainstem nuclei (NTS), parasympathetic tone",
        "key_conditions": ["Depression", "Epilepsy", "Pain", "Inflammation", "Stroke (paired)"],
        "modalities": ["taVNS", "CES (indirect)"],
        "notes": "Auricular branch of vagus nerve provides non-invasive access to vagal signaling pathway.",
    },
    "SCC": {
        "name": "Subgenual Cingulate Cortex",
        "abbreviation": "SCC (Cg25)",
        "eeg_position": "Deep medial frontal",
        "hemisphere": "Bilateral (midline)",
        "depth": "Deep cortical (buried)",
        "functions": "Emotion regulation, depression circuitry, autonomous nervous system regulation, hedonia",
        "key_conditions": ["Treatment-resistant depression"],
        "modalities": ["DBS", "TMS (deep H-coil, indirect)"],
        "notes": "Mayberg original DBS target for TRD. Aka Brodmann area 25. Defines depression circuit hub.",
    },
    "PPN": {
        "name": "Pedunculopontine Nucleus",
        "abbreviation": "PPN",
        "eeg_position": "Deep brainstem",
        "hemisphere": "Bilateral",
        "depth": "Deep brainstem",
        "functions": "Gait control, posture, wakefulness, REM sleep",
        "key_conditions": ["PD (gait freezing)", "Falls", "DOC"],
        "modalities": ["DBS (emerging)"],
        "notes": "PPN DBS for gait freezing in PD. Complex target in brainstem. Requires skilled placement.",
    },
}

# ── Lookup tables (auto-built) ────────────────────────────────────────────────

def _build_lookups():
    eeg_to_region = {}
    condition_to_regions = {}
    modality_to_regions = {}

    for abbr, region in BRAIN_REGIONS.items():
        # EEG position lookup
        eeg_raw = region.get("eeg_position", "")
        for part in eeg_raw.split(","):
            part = part.strip()
            # Remove hemisphere annotations like "(L)", "(R)", "approximate"
            electrode = part.split("(")[0].strip().split("/")[0].strip()
            if electrode and not any(c.isdigit() is False and c not in "CFPOTzp0123456789'- " for c in electrode):
                if electrode and len(electrode) <= 6:
                    eeg_to_region.setdefault(electrode, [])
                    if abbr not in eeg_to_region[electrode]:
                        eeg_to_region[electrode].append(abbr)

        # Condition lookup
        for cond in region.get("key_conditions", []):
            cond_clean = cond.strip()
            condition_to_regions.setdefault(cond_clean, [])
            if abbr not in condition_to_regions[cond_clean]:
                condition_to_regions[cond_clean].append(abbr)

        # Modality lookup
        for mod_raw in region.get("modalities", []):
            mod = mod_raw.split("(")[0].strip().split(" ")[0].strip()
            if mod:
                modality_to_regions.setdefault(mod, [])
                if abbr not in modality_to_regions[mod]:
                    modality_to_regions[mod].append(abbr)

    return eeg_to_region, condition_to_regions, modality_to_regions


EEG_POSITION_TO_REGION, CONDITION_TO_REGIONS, MODALITY_TO_REGIONS = _build_lookups()


def get_regions_for_condition(condition_keyword: str) -> list:
    """Return list of region abbreviations relevant to a condition (fuzzy match)."""
    kw = condition_keyword.lower()
    result = []
    for cond, regions in CONDITION_TO_REGIONS.items():
        if kw in cond.lower() or cond.lower() in kw:
            for r in regions:
                if r not in result:
                    result.append(r)
    return result


def get_regions_for_modality(modality: str) -> list:
    """Return list of region abbreviations targetable by this modality."""
    return MODALITY_TO_REGIONS.get(modality, [])


if __name__ == "__main__":
    print(f"Brain regions loaded: {len(BRAIN_REGIONS)}")
    print(f"EEG position mappings: {len(EEG_POSITION_TO_REGION)}")
    print(f"Condition mappings: {len(CONDITION_TO_REGIONS)}")
    print(f"Modality mappings: {len(MODALITY_TO_REGIONS)}")
    print()
    print("Modality -> Regions:")
    for mod, regions in sorted(MODALITY_TO_REGIONS.items()):
        print(f"  {mod}: {regions}")
    print()
    print("Sample: regions for Depression:", get_regions_for_condition("depression"))
    print("Sample: regions for TMS:", get_regions_for_modality("TMS"))
