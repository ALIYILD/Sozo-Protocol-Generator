"""
SOZO Brain Regions Reference Library.
21 brain regions with anatomical metadata, EEG positions, functions,
key conditions, and applicable modalities.
Source: SOZO_Master_Neuromodulation_Protocols_v2.xlsx (April 2026).
Importable by condition generators, agents, and document builders.
"""
from __future__ import annotations


def _parse_list(raw: str) -> list[str]:
    """Split a comma-separated string into a stripped list."""
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_eeg(raw: str) -> list[str]:
    """Parse EEG position strings that may use commas or slashes as delimiters."""
    # Normalize: replace '/' with ',' then split
    normalized = raw.replace("/", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


# ===========================================================================
# BRAIN_REGIONS
# dict: abbreviation -> full record
# ===========================================================================

BRAIN_REGIONS: dict[str, dict] = {
    "DLPFC": {
        "full_name": "Dorsolateral Prefrontal Cortex",
        "eeg_positions": ["F3", "F4"],
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Executive function, working memory, cognitive control, mood regulation, cognitive flexibility",
        "key_conditions": ["Depression", "OCD", "ADHD", "Schizophrenia", "Cognitive impairment", "Addiction"],
        "modalities": ["TMS", "tDCS", "TPS", "tACS", "PBM", "LIFU", "tRNS", "PEMF"],
        "notes": "Primary TMS target for depression. L-DLPFC for depression; R-DLPFC for anxiety/PTSD",
    },
    "M1": {
        "full_name": "Primary Motor Cortex",
        "eeg_positions": ["C3", "C4"],
        "hemisphere": "Contralateral to limb",
        "depth": "Cortical",
        "functions": "Motor execution, voluntary movement generation, corticospinal tract origin",
        "key_conditions": ["Parkinson's", "Stroke", "Chronic pain", "Dystonia", "MS"],
        "modalities": ["TMS", "tDCS", "TPS", "tACS", "PBM", "PEMF", "tRNS"],
        "notes": "Contralateral targeting — L-M1 controls R body and vice versa. rMT measured here.",
    },
    "SMA": {
        "full_name": "Supplementary Motor Area",
        "eeg_positions": ["Fz", "FCz"],
        "hemisphere": "Bilateral (midline)",
        "depth": "Cortical",
        "functions": "Motor planning, movement sequencing, bimanual coordination, gait initiation",
        "key_conditions": ["Parkinson's", "OCD", "Dystonia"],
        "modalities": ["TMS", "TPS", "tDCS"],
        "notes": "Medial frontal location. TPS/TMS target for PD motor sequencing.",
    },
    "ACC": {
        "full_name": "Anterior Cingulate Cortex",
        "eeg_positions": ["Fz", "AFz", "Cz"],
        "hemisphere": "Bilateral (midline)",
        "depth": "Cortical (deep cortex)",
        "functions": "Error monitoring, emotional regulation, conflict detection, pain modulation, attention",
        "key_conditions": ["OCD", "Depression", "Chronic pain", "ADHD"],
        "modalities": ["TMS", "tDCS", "LIFU", "tACS"],
        "notes": "Difficult to reach with surface stimulation. LIFU and deep TMS (H coils) reach better.",
    },
    "IFG": {
        "full_name": "Inferior Frontal Gyrus",
        "eeg_positions": ["F7", "F8"],
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Language production (Broca's area L), inhibitory control, cognitive flexibility",
        "key_conditions": ["Alzheimer's (TPS)", "Aphasia", "OCD"],
        "modalities": ["TMS", "TPS", "LIFU"],
        "notes": "Broca's area (L-IFG) critical for language. TPS targets as part of DMN network.",
    },
    "LPC": {
        "full_name": "Lateral Parietal Cortex",
        "eeg_positions": ["P3", "P4"],
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Attention, spatial processing, visuospatial awareness, working memory buffer",
        "key_conditions": ["Alzheimer's", "MCI", "Hemineglect"],
        "modalities": ["TMS", "tDCS", "TPS", "tRNS"],
        "notes": "TPS targets as part of AD/MCI multi-site protocol. Right LPC for hemineglect.",
    },
    "TC": {
        "full_name": "Temporal Cortex / Auditory Cortex",
        "eeg_positions": ["T3", "T5", "T4", "T6"],
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Auditory processing, language comprehension (Wernicke's L), memory encoding, semantic processing",
        "key_conditions": ["Tinnitus", "Schizophrenia (hallucinations)", "Alzheimer's", "Epilepsy (temporal lobe)"],
        "modalities": ["TMS", "tDCS", "tACS", "taVNS", "tRNS"],
        "notes": "Primary target for tinnitus (inhibitory TMS) and auditory hallucinations (schizophrenia).",
    },
    "PCu": {
        "full_name": "Precuneus",
        "eeg_positions": ["Pz"],
        "hemisphere": "Bilateral (midline)",
        "depth": "Cortical",
        "functions": "Self-referential processing, episodic memory retrieval, visual-spatial imagery, consciousness",
        "key_conditions": ["Alzheimer's", "MCI", "Depression", "DOC"],
        "modalities": ["TMS", "TPS", "tDCS"],
        "notes": "Key default mode network hub. TPS targets as part of AD protocol.",
    },
    "OFC": {
        "full_name": "Orbitofrontal Cortex",
        "eeg_positions": ["Fp1", "Fp2"],
        "hemisphere": "Bilateral",
        "depth": "Cortical",
        "functions": "Decision-making, reward/punishment processing, emotion regulation, impulse control",
        "key_conditions": ["OCD", "Addiction", "Depression"],
        "modalities": ["TMS", "tDCS", "LIFU"],
        "notes": "Important node in corticostriatal OCD and addiction circuits.",
    },
    "S1": {
        "full_name": "Primary Somatosensory Cortex",
        "eeg_positions": ["C3'", "C4'"],
        "hemisphere": "Contralateral",
        "depth": "Cortical",
        "functions": "Tactile sensation, proprioception, pain processing (somatotopic map)",
        "key_conditions": ["Chronic pain", "Stroke", "Phantom limb"],
        "modalities": ["TMS", "tDCS"],
        "notes": "Adjacent to M1. Targeted in stroke and pain protocols.",
    },
    "HC": {
        "full_name": "Hippocampus",
        "eeg_positions": ["T3", "T5"],
        "hemisphere": "Bilateral",
        "depth": "Subcortical (temporal lobe)",
        "functions": "Memory consolidation, spatial navigation, new learning (declarative memory), fear extinction",
        "key_conditions": ["Alzheimer's", "Epilepsy (temporal)", "PTSD", "Depression"],
        "modalities": ["LIFU", "DBS", "taVNS", "TPS"],
        "notes": "Cannot be directly targeted by surface stimulation. LIFU, DBS, and intranasal PBM can reach it.",
    },
    "Amy": {
        "full_name": "Amygdala",
        "eeg_positions": ["T3", "T4"],
        "hemisphere": "Bilateral",
        "depth": "Subcortical (temporal lobe)",
        "functions": "Fear processing, emotional learning, stress response, threat detection",
        "key_conditions": ["PTSD", "Anxiety", "Depression", "Addiction"],
        "modalities": ["LIFU", "DBS", "taVNS"],
        "notes": "Deep structure, not directly accessible by surface stimulation. LIFU can modulate.",
    },
    "Th": {
        "full_name": "Thalamus",
        "eeg_positions": [],
        "hemisphere": "Bilateral",
        "depth": "Deep subcortical",
        "functions": "Sensory relay, consciousness regulation, gating of motor output, arousal, attention",
        "key_conditions": ["Essential tremor (VIM)", "Pain", "DOC", "Epilepsy (ANT)", "PD (CM-Pf)"],
        "modalities": ["DBS", "LIFU", "tACS", "taVNS"],
        "notes": "Multiple nuclei with distinct functions: VIM (tremor), ANT (epilepsy), CM-Pf (Tourette's), MD (depression).",
    },
    "STN": {
        "full_name": "Subthalamic Nucleus",
        "eeg_positions": [],
        "hemisphere": "Bilateral",
        "depth": "Deep subcortical",
        "functions": "Motor control (indirect pathway), behavioral inhibition, decision-making",
        "key_conditions": ["Parkinson's disease (primary)", "OCD"],
        "modalities": ["DBS", "LIFU"],
        "notes": "Primary DBS target for PD. Smaller target than GPi. Risk of dysarthria and mood effects.",
    },
    "GPi": {
        "full_name": "Globus Pallidus Internus",
        "eeg_positions": [],
        "hemisphere": "Bilateral",
        "depth": "Deep subcortical",
        "functions": "Motor output regulation (indirect and direct pathways), movement suppression/facilitation",
        "key_conditions": ["Parkinson's", "Dystonia", "Tourette's", "Huntington's"],
        "modalities": ["DBS"],
        "notes": "Larger target than STN, less dysarthria risk. Preferred for dyskinesia and dystonia.",
    },
    "NAc": {
        "full_name": "Nucleus Accumbens",
        "eeg_positions": [],
        "hemisphere": "Bilateral",
        "depth": "Deep subcortical",
        "functions": "Reward processing, motivation, addiction, pleasure, aversion",
        "key_conditions": ["Addiction", "OCD", "Depression (via VC/VS)"],
        "modalities": ["DBS", "LIFU"],
        "notes": "Core of reward system. DBS target for addiction and OCD. Overlap with VC/VS target.",
    },
    "IC": {
        "full_name": "Insula",
        "eeg_positions": ["T3", "T4"],
        "hemisphere": "Bilateral",
        "depth": "Cortical (buried in Sylvian fissure)",
        "functions": "Interoception, pain integration, emotional awareness, taste, autonomic regulation, addiction",
        "key_conditions": ["Chronic pain", "Addiction", "Smoking cessation", "Depression"],
        "modalities": ["TMS", "LIFU", "DBS"],
        "notes": "Targeted by deep TMS for smoking cessation. LIFU can reach with precision.",
    },
    "Cereb": {
        "full_name": "Cerebellum",
        "eeg_positions": ["Oz"],
        "hemisphere": "Bilateral",
        "depth": "Posterior fossa",
        "functions": "Motor coordination, balance, fine movement, procedural learning, cognitive functions (emerging)",
        "key_conditions": ["Ataxia", "Essential tremor", "ASD (cerebellar-cortical circuits)"],
        "modalities": ["TMS", "tDCS", "TPS"],
        "notes": "Cerebellar TMS increasingly studied. Modulates cerebello-thalamo-cortical circuit.",
    },
    "ABVN": {
        "full_name": "Vagus Nerve (auricular branch)",
        "eeg_positions": [],
        "hemisphere": "Left side preferred",
        "depth": "Peripheral nerve (brain interface)",
        "functions": (
            "Autonomic regulation, anti-inflammatory, neuromodulation of brainstem nuclei (NTS), "
            "parasympathetic tone"
        ),
        "key_conditions": ["Depression", "Epilepsy", "Pain", "Inflammation", "Stroke (paired)"],
        "modalities": ["taVNS", "CES"],
        "notes": "Auricular branch of vagus nerve provides non-invasive access to vagal signaling pathway.",
    },
    "SCC": {
        "full_name": "Subgenual Cingulate Cortex (Cg25)",
        "eeg_positions": [],
        "hemisphere": "Bilateral (midline)",
        "depth": "Deep cortical (buried)",
        "functions": (
            "Emotion regulation, depression circuitry, autonomous nervous system regulation, hedonia"
        ),
        "key_conditions": ["Treatment-resistant depression"],
        "modalities": ["DBS", "TMS"],
        "notes": "Mayberg's original DBS target for TRD. Aka Brodmann area 25. Defines depression circuit hub.",
    },
    "PPN": {
        "full_name": "Pedunculopontine Nucleus",
        "eeg_positions": [],
        "hemisphere": "Bilateral",
        "depth": "Deep brainstem",
        "functions": "Gait control, posture, wakefulness, REM sleep",
        "key_conditions": ["PD (gait freezing)", "Falls", "DOC"],
        "modalities": ["DBS"],
        "notes": "PPN DBS for gait freezing in PD. Complex target in brainstem. Requires skilled placement.",
    },
}


# ===========================================================================
# EEG_TO_REGION
# dict: eeg_position -> list of region abbreviations
# (one EEG position can map to multiple regions)
# ===========================================================================

def _build_eeg_map() -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for abbrev, rec in BRAIN_REGIONS.items():
        for pos in rec["eeg_positions"]:
            if pos:
                mapping.setdefault(pos, [])
                if abbrev not in mapping[pos]:
                    mapping[pos].append(abbrev)
    return mapping


EEG_TO_REGION: dict[str, list[str]] = _build_eeg_map()


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def get_region_for_condition(condition: str) -> list[str]:
    """Return list of region abbreviations relevant to a condition (case-insensitive partial match)."""
    query = condition.lower()
    matches: list[str] = []
    for abbrev, rec in BRAIN_REGIONS.items():
        for cond in rec["key_conditions"]:
            if query in cond.lower():
                if abbrev not in matches:
                    matches.append(abbrev)
                break
    return matches


def get_regions_for_modality(modality: str) -> list[str]:
    """Return list of region abbreviations targeted by a given modality (case-insensitive partial match)."""
    query = modality.lower()
    matches: list[str] = []
    for abbrev, rec in BRAIN_REGIONS.items():
        for mod in rec["modalities"]:
            if query in mod.lower():
                if abbrev not in matches:
                    matches.append(abbrev)
                break
    return matches


def get_region(abbreviation: str) -> dict | None:
    """Return the full record for a region by its abbreviation, or None if not found."""
    return BRAIN_REGIONS.get(abbreviation)


def get_eeg_positions_for_region(abbreviation: str) -> list[str]:
    """Return the list of EEG positions for a region abbreviation."""
    rec = BRAIN_REGIONS.get(abbreviation)
    if rec is None:
        return []
    return rec["eeg_positions"]
