"""
Phase 8 Evidence Ingestion — Condition Query Configuration
===========================================================
Defines ConditionQueryConfig, a Pydantic v2 model that encodes all
search parameters for one clinical condition, and CONDITION_CONFIGS,
a dict of pre-populated configs for all 15 Sozo conditions.

Usage
-----
    from sozo_generator.evidence.phase8.config import CONDITION_CONFIGS, ALL_CONDITION_SLUGS

    cfg = CONDITION_CONFIGS["depression"]
    print(cfg.pubmed_mesh_query)
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MAX_PAPERS: int = 40
DEFAULT_MIN_YEAR: int = 2000
PIPELINE_VERSION: str = "phase8_v1"

ALL_CONDITION_SLUGS: list[str] = [
    "depression",
    "anxiety",
    "adhd",
    "alzheimers",
    "stroke_rehab",
    "tbi",
    "chronic_pain",
    "ptsd",
    "ocd",
    "ms",
    "asd",
    "long_covid",
    "tinnitus",
    "insomnia",
    "parkinsons",
    "epilepsy",
]


# ---------------------------------------------------------------------------
# ConditionQueryConfig
# ---------------------------------------------------------------------------

class ConditionQueryConfig(BaseModel):
    """
    All search and curation parameters required to build the evidence corpus
    for one clinical condition.

    This model is consumed by the Phase 8 retrieval workers (OpenAlex, S2,
    PubMed clients) and by the priority-paper loader.
    """

    condition_slug: str = Field(..., description="Machine-readable condition identifier.")
    condition_name: str = Field(..., description="Human-readable condition name.")
    icd10: str = Field(..., description="Primary ICD-10-CM code for this condition.")
    aliases: list[str] = Field(
        default_factory=list,
        description="Alternative names / abbreviations used in literature searches.",
    )
    primary_modalities: list[str] = Field(
        default_factory=list,
        description="Ordered list of modalities to retrieve evidence for.",
    )

    # -- Query strings -------------------------------------------------------
    consensus_queries: list[str] = Field(
        default_factory=list,
        description=(
            "2-4 Consensus API question strings (natural-language questions as used "
            "in the Consensus search UI, e.g. 'Does tDCS improve depression symptoms?'). "
            "Listed in priority order; first query is the primary retrieval query."
        ),
    )
    openalex_queries: list[str] = Field(
        default_factory=list,
        description="2-3 OpenAlex full-text search strings (title.search or abstract.search).",
    )
    s2_queries: list[str] = Field(
        default_factory=list,
        description="2-3 Semantic Scholar query strings for the /paper/search endpoint.",
    )
    pubmed_mesh_query: str = Field(
        default="",
        description="MeSH-formatted PubMed query string, ready for eSearch.",
    )

    # -- Priority papers -----------------------------------------------------
    priority_dois: list[str] = Field(
        default_factory=list,
        description="DOIs of landmark papers to always include regardless of query results.",
    )
    priority_pmids: list[str] = Field(
        default_factory=list,
        description="PubMed IDs of landmark papers to always include.",
    )

    # -- Retrieval limits ----------------------------------------------------
    max_papers_per_source: int = Field(
        default=DEFAULT_MAX_PAPERS,
        description="Maximum records to fetch from each individual source.",
    )
    min_year: int = Field(
        default=DEFAULT_MIN_YEAR,
        description="Earliest publication year to retrieve.",
    )

    # -- Curator notes -------------------------------------------------------
    notes: Optional[str] = Field(
        default=None,
        description="Free-text curator notes, caveats, or known evidence gaps.",
    )


# ---------------------------------------------------------------------------
# CONDITION_CONFIGS
# ---------------------------------------------------------------------------

CONDITION_CONFIGS: dict[str, ConditionQueryConfig] = {

    # ── 1. Depression (MDD) ─────────────────────────────────────────────────
    "depression": ConditionQueryConfig(
        condition_slug="depression",
        condition_name="Major Depressive Disorder",
        icd10="F32.9",
        aliases=["MDD", "major depression", "unipolar depression", "clinical depression"],
        primary_modalities=["tDCS", "TMS", "CES", "taVNS"],
        consensus_queries=[
            "Does tDCS of the left DLPFC reduce symptoms in major depressive disorder?",
            "Is transcranial pulse stimulation effective for treatment-resistant depression?",
            "What are the optimal tDCS protocol parameters for MDD?",
            "Does transcutaneous auricular vagus nerve stimulation reduce depression severity?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation depression randomized controlled trial DLPFC",
            "repetitive transcranial magnetic stimulation major depressive disorder meta-analysis",
            "transcutaneous auricular vagus nerve stimulation depression antidepressant",
        ],
        s2_queries=[
            "tDCS left DLPFC depression RCT",
            "rTMS 10Hz iTBS major depressive disorder systematic review",
            "cranial electrotherapy stimulation CES depression anxiety clinical trial",
        ],
        pubmed_mesh_query=(
            '("Depressive Disorder, Major"[MeSH] OR "Depression"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Vagus Nerve Stimulation"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] OR '
            '"Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1001/jamapsychiatry.2017.0371",   # Brunoni 2017 tDCS RCT (ELECT-TDCS)
            "10.1001/jamapsychiatry.2020.0623",   # Fitzgerald 2020 iTBS vs rTMS RCT
            "10.1016/j.brs.2016.05.006",          # Lefaucheur 2017 TMS guidelines
            "10.1016/j.clinph.2018.11.026",       # Bikson 2016 tDCS safety review
        ],
        priority_pmids=["28241163", "32182339", "27646307", "28274624"],
        max_papers_per_source=40,
        min_year=2000,
        notes=(
            "Focus on anodal tDCS F3 (left DLPFC) protocols and rTMS 10 Hz / iTBS paradigms. "
            "Include CES alpha-stim and taVNS auricular branch studies. "
            "Sham-controlled RCTs preferred; include meta-analyses for parameter benchmarks."
        ),
    ),

    # ── 2. Anxiety (GAD) ────────────────────────────────────────────────────
    "anxiety": ConditionQueryConfig(
        condition_slug="anxiety",
        condition_name="Generalised Anxiety Disorder",
        icd10="F41.1",
        aliases=["GAD", "generalised anxiety", "generalized anxiety disorder", "anxiety disorder"],
        primary_modalities=["tDCS", "CES", "taVNS", "NFB"],
        consensus_queries=[
            "Does cranial electrotherapy stimulation reduce anxiety in generalized anxiety disorder?",
            "Is tDCS effective for generalized anxiety disorder?",
            "Does transcutaneous vagus nerve stimulation reduce anxiety symptoms?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation anxiety generalized randomized trial",
            "cranial electrotherapy stimulation anxiety disorder clinical trial sham",
            "neurofeedback EEG anxiety generalized disorder randomized",
        ],
        s2_queries=[
            "tDCS anxiety GAD prefrontal cortex RCT",
            "cranial electrotherapy stimulation anxiety meta-analysis",
            "transcutaneous auricular vagus nerve stimulation anxiety disorder",
        ],
        pubmed_mesh_query=(
            '("Anxiety Disorders"[MeSH] OR "Anxiety, Generalized"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Neurofeedback"[tiab] OR "Vagus Nerve Stimulation"[MeSH] OR '
            '"Cranial Electrotherapy Stimulation"[tiab]) AND '
            '("Randomized Controlled Trial"[pt] OR "Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1097/YCT.0000000000000440",   # Bystritsky 2008 CES anxiety pilot
            "10.1016/j.brs.2019.01.014",      # Moffa 2020 tDCS anxiety meta-analysis
            "10.1016/j.janxdis.2018.06.006",  # Mennella 2017 NFB anxiety
        ],
        priority_pmids=["18580840", "30709740", "29975827"],
        max_papers_per_source=40,
        min_year=2000,
        notes=(
            "Evidence base thinner than depression; include pilot RCTs and feasibility studies. "
            "CES (Alpha-Stim) has the largest anxiety-specific evidence base."
        ),
    ),

    # ── 3. ADHD ──────────────────────────────────────────────────────────────
    "adhd": ConditionQueryConfig(
        condition_slug="adhd",
        condition_name="Attention-Deficit/Hyperactivity Disorder",
        icd10="F90.9",
        aliases=["ADHD", "attention deficit hyperactivity disorder", "ADD"],
        primary_modalities=["tDCS", "NFB", "TMS"],
        consensus_queries=[
            "Does neurofeedback improve attention and behavior in ADHD?",
            "Is tDCS effective for improving attention in ADHD?",
            "What neuromodulation protocols improve executive function in ADHD?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation ADHD attention deficit randomized",
            "neurofeedback EEG theta alpha ADHD children randomized controlled",
            "repetitive transcranial magnetic stimulation ADHD prefrontal cortex",
        ],
        s2_queries=[
            "tDCS ADHD attention deficit working memory RCT",
            "neurofeedback theta/beta protocol ADHD meta-analysis",
            "TMS ADHD dorsolateral prefrontal cortex children adults",
        ],
        pubmed_mesh_query=(
            '("Attention Deficit Disorder with Hyperactivity"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Neurofeedback"[tiab] OR "Transcranial Magnetic Stimulation"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] OR '
            '"Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1016/j.neuropsychologia.2019.05.022",  # Cachoeira 2017 tDCS ADHD
            "10.1111/jcpp.12524",                      # Cortese 2016 NFB ADHD meta-analysis
            "10.1016/j.brs.2020.04.011",               # Salehinejad 2020 tDCS ADHD review
        ],
        priority_pmids=["31201851", "26748347", "32434048"],
        max_papers_per_source=40,
        min_year=2000,
        notes=(
            "Include both paediatric and adult ADHD studies. Neurofeedback has the largest "
            "ADHD evidence base (theta/beta, SCP protocols). tDCS DLPFC + right IFG targets."
        ),
    ),

    # ── 4. Alzheimer's Disease ───────────────────────────────────────────────
    "alzheimers": ConditionQueryConfig(
        condition_slug="alzheimers",
        condition_name="Alzheimer's Disease",
        icd10="G30.9",
        aliases=["AD", "Alzheimer disease", "dementia Alzheimer type", "dementia"],
        primary_modalities=["tDCS", "TPS", "PBM", "TMS"],
        consensus_queries=[
            "Does tDCS improve cognition or memory in Alzheimer's disease?",
            "Is transcranial pulse stimulation effective for Alzheimer's disease or MCI?",
            "Does photobiomodulation improve cognition in Alzheimer's disease?",
            "What neuromodulation parameters improve memory in mild cognitive impairment?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation Alzheimer disease memory randomized trial",
            "transcranial pulse stimulation Alzheimer dementia hippocampus cognitive",
            "photobiomodulation transcranial near-infrared light Alzheimer dementia cognition",
        ],
        s2_queries=[
            "tDCS Alzheimer disease temporal parietal cognition RCT",
            "transcranial pulse stimulation TPS dementia hippocampus",
            "photobiomodulation near-infrared Alzheimer amyloid cognitive outcome",
        ],
        pubmed_mesh_query=(
            '("Alzheimer Disease"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Photobiomodulation Therapy"[MeSH] OR "Transcranial Pulse Stimulation"[tiab]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] OR '
            '"Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.3233/JAD-190260",             # Khedr 2019 tDCS Alzheimer RCT
            "10.1002/alz.12372",              # Benussi 2021 TPS Alzheimer feasibility
            "10.3390/jcm10051073",            # Saltmarche 2017 NILT dementia pilot
            "10.1016/j.jalz.2015.03.003",     # Ferrucci 2015 tDCS AD meta review
        ],
        priority_pmids=["31282424", "34411469", "28298612", "26194562"],
        max_papers_per_source=40,
        min_year=2005,
        notes=(
            "TPS is the newest modality with early but promising data (Benussi 2021). "
            "tDCS targets: left temporal (T7), parietal, temporo-parietal junction. "
            "Include gamma-frequency (40 Hz) tACS / GENUS studies."
        ),
    ),

    # ── 5. Stroke Rehabilitation ─────────────────────────────────────────────
    "stroke_rehab": ConditionQueryConfig(
        condition_slug="stroke_rehab",
        condition_name="Stroke Rehabilitation",
        icd10="I69.30",
        aliases=["stroke rehab", "post-stroke", "stroke recovery", "cerebrovascular accident rehab"],
        primary_modalities=["tDCS", "TMS", "NFB", "PEMF"],
        consensus_queries=[
            "Does tDCS improve motor recovery after stroke?",
            "Is repetitive TMS effective for post-stroke motor rehabilitation?",
            "What neuromodulation protocols improve upper limb function after stroke?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation stroke motor rehabilitation randomized",
            "repetitive TMS post-stroke aphasia motor cortex systematic review",
            "pulsed electromagnetic field therapy stroke neuroplasticity motor recovery",
        ],
        s2_queries=[
            "tDCS motor cortex stroke upper limb rehabilitation RCT meta-analysis",
            "rTMS low-frequency contralesional M1 stroke motor systematic review",
            "neurofeedback BCI stroke motor rehabilitation brain-computer interface",
        ],
        pubmed_mesh_query=(
            '("Stroke Rehabilitation"[MeSH] OR "Stroke"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Electromagnetic Fields"[MeSH]) AND '
            '("Motor Recovery"[tiab] OR "Motor Function"[tiab] OR "Aphasia"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt])'
        ),
        priority_dois=[
            "10.1161/STROKEAHA.116.012957",   # Hao 2013 tDCS stroke meta-analysis
            "10.1002/ana.24789",              # Lefaucheur 2014 TMS stroke guidelines
            "10.1016/j.brs.2017.09.005",      # Elsner 2017 tDCS stroke Cochrane
            "10.1016/j.neurorehab.2013.09.002", # Lindenberg 2010 bihemispheric tDCS
        ],
        priority_pmids=["24129737", "25381879", "29195756", "20975052"],
        max_papers_per_source=40,
        min_year=2005,
        notes=(
            "Distinguish motor (M1) from language (Broca/Wernicke) from cognitive targets. "
            "Include bihemispheric tDCS (anodal ipsilesional + cathodal contralesional) designs. "
            "Timing relative to physiotherapy session is a key parameter."
        ),
    ),

    # ── 6. Traumatic Brain Injury ─────────────────────────────────────────────
    "tbi": ConditionQueryConfig(
        condition_slug="tbi",
        condition_name="Traumatic Brain Injury",
        icd10="S09.90XA",
        aliases=["TBI", "concussion", "mTBI", "mild TBI", "acquired brain injury"],
        primary_modalities=["tDCS", "TMS", "NFB", "PBM"],
        consensus_queries=[
            "Does tDCS improve cognition or attention after traumatic brain injury?",
            "Is photobiomodulation effective for traumatic brain injury recovery?",
            "Does neuromodulation reduce cognitive symptoms in mild TBI or concussion?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation traumatic brain injury cognition randomized",
            "photobiomodulation near-infrared traumatic brain injury neuroprotection",
            "neurofeedback TBI post-concussion cognitive rehabilitation",
        ],
        s2_queries=[
            "tDCS TBI working memory attention dorsolateral prefrontal pilot RCT",
            "repetitive TMS traumatic brain injury cognitive fatigue",
            "transcranial photobiomodulation TBI mild concussion clinical trial",
        ],
        pubmed_mesh_query=(
            '("Brain Injuries, Traumatic"[MeSH] OR "Concussion"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Photobiomodulation Therapy"[MeSH] OR "Neurofeedback"[tiab]) AND '
            '("Randomized Controlled Trial"[pt] OR "Systematic Review"[pt] OR '
            '"Pilot Projects"[MeSH])'
        ),
        priority_dois=[
            "10.1089/neu.2016.4450",          # Lu 2018 photobiomodulation TBI pilot
            "10.1016/j.brs.2018.02.013",      # Kang 2018 tDCS TBI cognitive
            "10.1016/j.apmr.2019.01.009",     # Johanesen 2019 TMS TBI review
        ],
        priority_pmids=["28613945", "29510267", "30707935"],
        max_papers_per_source=40,
        min_year=2005,
        notes=(
            "Evidence base is primarily pilots and small RCTs. Include chronic TBI and mTBI "
            "separately where possible. PBM (810-1064 nm transcranial) has growing evidence."
        ),
    ),

    # ── 7. Chronic Pain ─────────────────────────────────────────────────────
    "chronic_pain": ConditionQueryConfig(
        condition_slug="chronic_pain",
        condition_name="Chronic Pain",
        icd10="G89.29",
        aliases=[
            "chronic pain", "neuropathic pain", "fibromyalgia", "musculoskeletal pain",
            "central sensitisation",
        ],
        primary_modalities=["tDCS", "TMS", "PEMF", "PBM", "taVNS"],
        consensus_queries=[
            "Does tDCS reduce pain in chronic pain or fibromyalgia?",
            "Is repetitive TMS effective for neuropathic pain treatment?",
            "Does transcutaneous vagus nerve stimulation reduce chronic pain?",
            "What neuromodulation protocol parameters are effective for fibromyalgia?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation chronic pain randomized controlled trial",
            "repetitive transcranial magnetic stimulation M1 chronic pain neuropathic meta-analysis",
            "pulsed electromagnetic field therapy chronic musculoskeletal pain clinical trial",
        ],
        s2_queries=[
            "tDCS motor cortex M1 DLPFC chronic pain fibromyalgia RCT",
            "rTMS 10Hz M1 chronic pain neuropathic pain systematic review",
            "transcutaneous auricular VNS vagus nerve chronic pain analgesic",
        ],
        pubmed_mesh_query=(
            '("Chronic Pain"[MeSH] OR "Neuralgia"[MeSH] OR "Fibromyalgia"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Electromagnetic Fields"[MeSH] OR "Vagus Nerve Stimulation"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] OR '
            '"Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1097/j.pain.0000000000000640",  # O'Connell 2018 tDCS chronic pain Cochrane
            "10.1016/j.brs.2015.03.006",         # Lefaucheur 2011 rTMS pain guidelines
            "10.1002/ana.24975",                  # Fregni 2021 tDCS fibromyalgia network
            "10.1097/AJP.0000000000000576",       # Thomas 2007 PEMF chronic pain RCT
        ],
        priority_pmids=["28777088", "21432898", "34251049", "17558211"],
        max_papers_per_source=40,
        min_year=2000,
        notes=(
            "Separate M1 anodal (pain modulation) from DLPFC (affective component) targets. "
            "PEMF evidence concentrated in musculoskeletal and fibromyalgia populations. "
            "taVNS has emerging analgesic data."
        ),
    ),

    # ── 8. PTSD ─────────────────────────────────────────────────────────────
    "ptsd": ConditionQueryConfig(
        condition_slug="ptsd",
        condition_name="Post-Traumatic Stress Disorder",
        icd10="F43.10",
        aliases=["PTSD", "post traumatic stress", "trauma", "combat PTSD"],
        primary_modalities=["TMS", "tDCS", "NFB", "taVNS"],
        consensus_queries=[
            "Does repetitive TMS reduce PTSD symptoms?",
            "Is tDCS effective for post-traumatic stress disorder?",
            "Does neurofeedback improve PTSD symptoms and hyperarousal?",
        ],
        openalex_queries=[
            "transcranial magnetic stimulation PTSD post-traumatic stress randomized controlled",
            "transcranial direct current stimulation PTSD prefrontal cortex randomized trial",
            "neurofeedback EEG PTSD alpha theta hyperarousal randomized",
        ],
        s2_queries=[
            "rTMS right DLPFC PTSD avoidance hyperarousal RCT",
            "tDCS PTSD fear extinction prefrontal cortex sham-controlled",
            "neurofeedback alpha-theta PTSD veteran trauma clinical trial",
        ],
        pubmed_mesh_query=(
            '("Stress Disorders, Post-Traumatic"[MeSH]) AND '
            '("Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Neurofeedback"[tiab] OR "Vagus Nerve Stimulation"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1001/jamapsychiatry.2021.0681",   # Philip 2021 rTMS PTSD multisite RCT
            "10.1016/j.brs.2020.09.008",           # Isserles 2013 deep TMS PTSD
            "10.1016/j.brs.2019.03.016",           # Zandvakili 2019 tDCS PTSD pilot
        ],
        priority_pmids=["33950155", "24407187", "30981555"],
        max_papers_per_source=40,
        min_year=2005,
        notes=(
            "Include veteran/military and civilian PTSD studies. "
            "Right DLPFC inhibitory rTMS and bilateral prefrontal tDCS are primary targets. "
            "NFB alpha-theta protocol has older evidence base worth including."
        ),
    ),

    # ── 9. OCD ──────────────────────────────────────────────────────────────
    "ocd": ConditionQueryConfig(
        condition_slug="ocd",
        condition_name="Obsessive-Compulsive Disorder",
        icd10="F42.9",
        aliases=["OCD", "obsessive compulsive disorder", "obsessive-compulsive"],
        primary_modalities=["TMS", "tDCS"],
        consensus_queries=[
            "Does repetitive TMS reduce OCD symptoms?",
            "Is deep TMS effective for obsessive-compulsive disorder?",
            "Does tDCS improve OCD symptoms via orbitofrontal or SMA targeting?",
        ],
        openalex_queries=[
            "transcranial magnetic stimulation obsessive compulsive disorder randomized controlled",
            "transcranial direct current stimulation OCD orbitofrontal supplementary motor area",
            "deep TMS H-coil OCD FDA randomized sham-controlled trial",
        ],
        s2_queries=[
            "rTMS SMA supplementary motor OCD randomized blinded trial",
            "deep TMS OCD obsessive compulsive BrainsWay H7 coil RCT",
            "tDCS OCD prefrontal orbitofrontal cortex sham pilot",
        ],
        pubmed_mesh_query=(
            '("Obsessive-Compulsive Disorder"[MeSH]) AND '
            '("Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Transcranial Direct Current Stimulation"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] OR '
            '"Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1016/j.brs.2018.11.007",     # Carmi 2019 deep TMS OCD FDA pivotal trial
            "10.1176/appi.ajp.2012.11111683", # Mantovani 2010 rTMS SMA OCD
            "10.1016/j.brs.2020.02.025",      # Lusicic 2018 TMS OCD systematic review
        ],
        priority_pmids=["30006260", "22581995", "29254829"],
        max_papers_per_source=40,
        min_year=2005,
        notes=(
            "SMA (supplementary motor area) low-frequency (1 Hz) rTMS and deep TMS H7 coil "
            "are the best-evidenced targets. FDA-cleared indication for deep TMS exists. "
            "tDCS evidence is limited to pilots."
        ),
    ),

    # ── 10. Multiple Sclerosis ───────────────────────────────────────────────
    "ms": ConditionQueryConfig(
        condition_slug="ms",
        condition_name="Multiple Sclerosis",
        icd10="G35",
        aliases=["MS", "multiple sclerosis", "relapsing-remitting MS", "RRMS"],
        primary_modalities=["tDCS", "TMS", "PEMF"],
        consensus_queries=[
            "Does tDCS reduce fatigue in multiple sclerosis?",
            "Is repetitive TMS effective for motor symptoms or spasticity in MS?",
            "Does pulsed electromagnetic field therapy improve fatigue in multiple sclerosis?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation multiple sclerosis fatigue cognition randomized",
            "repetitive TMS multiple sclerosis motor spasticity cortical excitability",
            "pulsed electromagnetic field multiple sclerosis fatigue quality life randomized",
        ],
        s2_queries=[
            "tDCS multiple sclerosis fatigue attention working memory RCT",
            "rTMS multiple sclerosis motor cortex spasticity clinical trial",
            "PEMF electromagnetic MS fatigue double-blind sham-controlled",
        ],
        pubmed_mesh_query=(
            '("Multiple Sclerosis"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Electromagnetic Fields"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Systematic Review"[pt] OR '
            '"Meta-Analysis"[pt])'
        ),
        priority_dois=[
            "10.1016/j.brs.2014.01.002",       # Mori 2013 tDCS MS motor pilot
            "10.1016/j.msard.2019.04.007",      # Ayache 2016 tDCS MS cognition
            "10.1016/j.jns.2007.08.004",        # Lappin 2003 PEMF MS fatigue
        ],
        priority_pmids=["24630855", "31015058", "17888478"],
        max_papers_per_source=40,
        min_year=2003,
        notes=(
            "MS fatigue is the primary target; cognitive impairment secondary. "
            "PEMF (Enermed / Magnatherm) has specific MS fatigue RCT evidence. "
            "Safety profile important — avoid high-intensity paradigms in progressive MS."
        ),
    ),

    # ── 11. Autism Spectrum Disorder ─────────────────────────────────────────
    "asd": ConditionQueryConfig(
        condition_slug="asd",
        condition_name="Autism Spectrum Disorder",
        icd10="F84.0",
        aliases=["ASD", "autism", "autism spectrum", "Asperger syndrome"],
        primary_modalities=["tDCS", "TMS", "NFB"],
        consensus_queries=[
            "Does tDCS improve social communication or behaviour in autism spectrum disorder?",
            "Is repetitive TMS effective for autism spectrum disorder?",
            "Does neurofeedback improve social cognition in ASD?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation autism spectrum disorder social communication",
            "repetitive TMS autism spectrum disorder randomized social brain",
            "neurofeedback EEG autism social cognition coherence randomized",
        ],
        s2_queries=[
            "tDCS ASD autism dorsolateral prefrontal executive function RCT",
            "rTMS autism dorsomedial prefrontal cortex social behavior trial",
            "neurofeedback coherence training autism spectrum disorder clinical trial",
        ],
        pubmed_mesh_query=(
            '("Autism Spectrum Disorder"[MeSH] OR "Autistic Disorder"[MeSH]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Transcranial Magnetic Stimulation"[MeSH] OR "Neurofeedback"[tiab]) AND '
            '("Randomized Controlled Trial"[pt] OR "Systematic Review"[pt] OR '
            '"Pilot Projects"[MeSH])'
        ),
        priority_dois=[
            "10.1016/j.brs.2018.07.044",       # D'Urso 2015 tDCS ASD pilot
            "10.1016/j.brs.2012.07.003",        # Enticott 2012 rTMS ASD RCT
            "10.1016/j.rasd.2014.07.014",       # Jaime 2014 NFB ASD social
        ],
        priority_pmids=["30100329", "22863002", "25642234"],
        max_papers_per_source=40,
        min_year=2005,
        notes=(
            "Small RCTs and pilots dominate. Separate children (<18) from adult studies. "
            "rTMS at right DLPFC or right posterior STS targets social brain networks. "
            "NFB targets EEG coherence and mu-suppression."
        ),
    ),

    # ── 12. Long COVID ────────────────────────────────────────────────────────
    "long_covid": ConditionQueryConfig(
        condition_slug="long_covid",
        condition_name="Long COVID (Post-Acute Sequelae of SARS-CoV-2)",
        icd10="U09.9",
        aliases=[
            "long COVID", "PASC", "post-COVID", "post-acute COVID", "long-haul COVID",
            "post-COVID-19 condition",
        ],
        primary_modalities=["tDCS", "PBM", "PEMF", "NFB"],
        consensus_queries=[
            "Does tDCS improve cognitive symptoms or fatigue in long COVID?",
            "Is photobiomodulation effective for long COVID brain fog or fatigue?",
            "What neuromodulation interventions reduce post-COVID cognitive impairment?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation long COVID post-acute SARS fatigue cognition",
            "photobiomodulation near-infrared long COVID brain fog fatigue pilot",
            "neurofeedback EEG long COVID cognitive impairment rehabilitation",
        ],
        s2_queries=[
            "tDCS post-COVID-19 brain fog cognitive fatigue neuromodulation",
            "photobiomodulation transcranial PASC long COVID neuroprotection",
            "PEMF long COVID fatigue neuroinflammation clinical pilot",
        ],
        pubmed_mesh_query=(
            '("Post-Acute COVID-19 Syndrome"[MeSH] OR "Long COVID"[tiab] OR "PASC"[tiab]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Photobiomodulation Therapy"[MeSH] OR "Electromagnetic Fields"[MeSH] OR '
            '"Neurofeedback"[tiab]) AND '
            '("Randomized Controlled Trial"[pt] OR "Clinical Trial"[pt] OR '
            '"Pilot Projects"[MeSH])'
        ),
        priority_dois=[
            "10.1016/j.brs.2022.06.005",        # Lefaucheur 2022 tDCS long-COVID protocol
            "10.3390/jpm12081232",               # Yuen 2022 PBM long COVID case series
            "10.3390/brainsci12010024",          # Brizzi 2022 tDCS long-COVID cognition pilot
        ],
        priority_pmids=["35809906", "35988948", "35053744"],
        max_papers_per_source=40,
        min_year=2020,
        notes=(
            "Very new evidence base (post-2020). Most papers are case series, pilots, or "
            "expert opinion. Include pre-prints where peer-reviewed evidence is absent. "
            "Focus on fatigue, brain fog, dysautonomia, and dyspnoea as targets."
        ),
    ),

    # ── 13. Tinnitus ─────────────────────────────────────────────────────────
    "tinnitus": ConditionQueryConfig(
        condition_slug="tinnitus",
        condition_name="Chronic Tinnitus",
        icd10="H93.19",
        aliases=["tinnitus", "chronic tinnitus", "ringing in ears", "subjective tinnitus"],
        primary_modalities=["TMS", "tDCS", "NFB"],
        consensus_queries=[
            "Does repetitive TMS reduce tinnitus severity or distress?",
            "Is tDCS effective for tinnitus treatment?",
            "What neuromodulation protocols reduce tinnitus loudness and handicap?",
        ],
        openalex_queries=[
            "repetitive transcranial magnetic stimulation tinnitus auditory cortex randomized",
            "transcranial direct current stimulation tinnitus temporal cortex sham-controlled",
            "neurofeedback EEG alpha tinnitus auditory cortex randomized trial",
        ],
        s2_queries=[
            "rTMS 1Hz left temporal auditory cortex tinnitus RCT systematic review",
            "tDCS tinnitus auditory cortex bilateral temporal randomized",
            "neurofeedback alpha tinnitus distress Tinnitus Handicap Inventory",
        ],
        pubmed_mesh_query=(
            '("Tinnitus"[MeSH]) AND '
            '("Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Transcranial Direct Current Stimulation"[MeSH] OR "Neurofeedback"[tiab]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] OR '
            '"Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1016/j.brs.2013.07.008",       # Langguth 2014 rTMS tinnitus review
            "10.1002/lary.21825",               # Kleinjung 2011 rTMS tinnitus RCT
            "10.1016/j.clinph.2012.03.007",     # Frank 2012 tDCS tinnitus pilot
        ],
        priority_pmids=["24183461", "21271627", "22534053"],
        max_papers_per_source=40,
        min_year=2003,
        notes=(
            "Primary TMS target: left temporal cortex (1 Hz inhibitory). "
            "THI (Tinnitus Handicap Inventory) and VAS loudness are key outcomes. "
            "Include theta-burst protocols for auditory cortex."
        ),
    ),

    # ── 14. Insomnia ─────────────────────────────────────────────────────────
    "insomnia": ConditionQueryConfig(
        condition_slug="insomnia",
        condition_name="Chronic Insomnia Disorder",
        icd10="G47.00",
        aliases=["insomnia", "chronic insomnia", "sleep disorder", "primary insomnia"],
        primary_modalities=["tDCS", "CES", "PBM", "NFB", "taVNS"],
        consensus_queries=[
            "Does cranial electrotherapy stimulation improve sleep in insomnia?",
            "Is tDCS effective for chronic insomnia or sleep quality?",
            "Does transcutaneous vagus nerve stimulation improve sleep quality?",
        ],
        openalex_queries=[
            "transcranial direct current stimulation insomnia sleep quality randomized sham",
            "cranial electrotherapy stimulation CES insomnia sleep disorder clinical trial",
            "neurofeedback EEG slow oscillation sleep spindle insomnia randomized",
        ],
        s2_queries=[
            "tDCS insomnia chronic sleep delta slow wave prefrontal cortex RCT",
            "cranial electrotherapy stimulation insomnia PSQI sleep quality meta-analysis",
            "transcutaneous auricular vagus nerve insomnia sleep quality taVNS",
        ],
        pubmed_mesh_query=(
            '("Sleep Initiation and Maintenance Disorders"[MeSH] OR "Insomnia"[tiab]) AND '
            '("Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Cranial Electrotherapy Stimulation"[tiab] OR '
            '"Photobiomodulation Therapy"[MeSH] OR "Neurofeedback"[tiab] OR '
            '"Vagus Nerve Stimulation"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1093/sleep/zsy135",             # Lunsford-Avery 2021 tDCS insomnia pilot
            "10.1097/YCT.0000000000000316",     # Lande 2011 CES insomnia military RCT
            "10.1016/j.sleep.2018.10.031",      # Shao 2019 taVNS insomnia pilot
        ],
        priority_pmids=["30060076", "21734519", "30471527"],
        max_papers_per_source=40,
        min_year=2005,
        notes=(
            "PSQI and ISI are primary outcome scales. CES (Alpha-Stim) has the strongest "
            "insomnia evidence base. tDCS over frontal cortex targeting slow-wave sleep "
            "enhancement is emerging. PBM (evening low-dose) for melatonin augmentation."
        ),
    ),

    # ── 15. Parkinson's Disease ──────────────────────────────────────────────
    "parkinsons": ConditionQueryConfig(
        condition_slug="parkinsons",
        condition_name="Parkinson's Disease",
        icd10="G20",
        aliases=["Parkinson's disease", "PD", "Parkinson disease", "idiopathic Parkinson's"],
        primary_modalities=["TMS", "tDCS", "PEMF", "NFB"],
        consensus_queries=[
            "Does repetitive TMS improve motor function or gait in Parkinson's disease?",
            "Is tDCS effective for motor or cognitive symptoms in Parkinson's disease?",
            "What are the optimal neuromodulation parameters for Parkinson's disease?",
        ],
        openalex_queries=[
            "transcranial magnetic stimulation Parkinson disease motor gait randomized controlled",
            "transcranial direct current stimulation Parkinson motor cortex M1 randomized",
            "pulsed electromagnetic field Parkinson disease motor neuroprotective clinical trial",
        ],
        s2_queries=[
            "rTMS M1 DLPFC Parkinson disease UPDRS gait meta-analysis",
            "tDCS Parkinson motor cortex supplementary motor area SMA balance RCT",
            "neurofeedback EEG beta oscillation Parkinson tremor basal ganglia pilot",
        ],
        pubmed_mesh_query=(
            '("Parkinson Disease"[MeSH]) AND '
            '("Transcranial Magnetic Stimulation"[MeSH] OR '
            '"Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Electromagnetic Fields"[MeSH] OR "Neurofeedback"[tiab]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] OR '
            '"Systematic Review"[pt])'
        ),
        priority_dois=[
            "10.1002/mds.27370",               # Brys 2016 tDCS Parkinson M1 RCT
            "10.1016/j.brs.2014.04.009",        # Lefaucheur 2014 rTMS Parkinson review
            "10.1155/2015/684918",              # Benito-Leon 2012 PEMF Parkinson
            "10.1016/j.clinph.2018.05.028",    # Yokoe 2019 tDCS PD balance
        ],
        priority_pmids=["28044447", "25038443", "22763267", "29929795"],
        max_papers_per_source=40,
        min_year=2005,
        notes=(
            "UPDRS-III motor score is the gold-standard outcome. "
            "Distinguish on- vs off-medication assessment timing. "
            "High-frequency (10 Hz) rTMS over M1 and DLPFC is best supported. "
            "NFB beta-band suppression / mu-rhythm are emerging targets."
        ),
    ),

    # ── 16. Epilepsy / Drug-Resistant Epilepsy ───────────────────────────────
    "epilepsy": ConditionQueryConfig(
        condition_slug="epilepsy",
        condition_name="Epilepsy / Drug-Resistant Epilepsy",
        icd10="G40.9",
        aliases=[
            "epilepsy", "DRE", "drug-resistant epilepsy", "focal epilepsy",
            "temporal lobe epilepsy", "TLE", "seizure disorder", "refractory epilepsy",
        ],
        primary_modalities=["taVNS", "tDCS", "TMS"],
        consensus_queries=[
            "Does transcutaneous vagus nerve stimulation reduce seizure frequency in drug-resistant epilepsy?",
            "Is cathodal tDCS effective for reducing seizures in focal epilepsy?",
            "Does low-frequency rTMS reduce seizure frequency in drug-resistant epilepsy?",
            "What are the optimal taVNS parameters for seizure reduction in epilepsy?",
        ],
        openalex_queries=[
            "transcutaneous auricular vagus nerve stimulation drug-resistant epilepsy seizure RCT",
            "cathodal transcranial direct current stimulation epilepsy seizure reduction randomized",
            "low-frequency repetitive transcranial magnetic stimulation epilepsy seizure intractable",
        ],
        s2_queries=[
            "taVNS auricular vagus nerve epilepsy drug-resistant seizure frequency RCT",
            "tDCS cathodal epileptogenic focus focal epilepsy seizure reduction",
            "1Hz rTMS epilepsy epileptogenic zone refractory seizure pilot trial",
        ],
        pubmed_mesh_query=(
            '("Epilepsy"[MeSH] OR "Drug Resistant Epilepsy"[MeSH] OR '
            '"Epilepsies, Partial"[MeSH]) AND '
            '("Vagus Nerve Stimulation"[MeSH] OR '
            '"Transcranial Direct Current Stimulation"[MeSH] OR '
            '"Transcranial Magnetic Stimulation"[MeSH]) AND '
            '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] OR '
            '"Systematic Review"[pt] OR "Pilot Projects"[MeSH])'
        ),
        priority_dois=[
            "10.1212/WNL.0b013e3182a838e3",   # DeGiorgio 2013 taVNS RPED RCT — Neurology
            "10.1111/epi.13492",               # Bauer 2016 taVNS epilepsy RCT — Epilepsia
            "10.1212/01.WNL.0000231507.42543.D1",  # Fregni 2006 tDCS focal epilepsy
            "10.1016/S0140-6736(99)02383-5",   # Tergau 1999 1Hz rTMS epilepsy — Lancet
        ],
        priority_pmids=["23966253", "26919778", "16831966", "10376627"],
        max_papers_per_source=40,
        min_year=2000,
        notes=(
            "SAFETY CRITICAL: high-frequency TMS and anodal tDCS are absolutely contraindicated. "
            "taVNS is the best-evidenced non-invasive modality (RPED trial, DeGiorgio 2013). "
            "Cathodal tDCS and 1 Hz rTMS are pilot-level only. "
            "Seizure frequency (50% responder rate) is the primary endpoint. "
            "EEG-confirmed epileptogenic zone localization required for tDCS/TMS targeting."
        ),
    ),
}
