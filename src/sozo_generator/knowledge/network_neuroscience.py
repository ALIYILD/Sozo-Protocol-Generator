"""
SOZO Brain Network Neuroscience Knowledge Library.

85 peer-reviewed papers on brain networks and neuromodulation (April 2026).
Source: Consensus.app evidence sweep — brain networks for neuromodulation.

Importable by FNON generators, condition generators, and document builders.
Every paper entry is fully cited (authors, year, DOI, journal, SJR quartile).

Compiled: 2026-04-04.
"""
from __future__ import annotations


# ── 1. ALL PAPERS ─────────────────────────────────────────────────────────────
# All 85 papers from the Consensus.app evidence sweep.
# conditions and topics are inferred from title + takeaway.

ALL_PAPERS: list[dict] = [
    {
        "title": "Towards network-guided neuromodulation for epilepsy",
        "takeaway": (
            "Network-guided neuromodulation for epilepsy aims to target specific brain "
            "networks to reduce seizures and improve patient outcomes."
        ),
        "authors": (
            "R. Piper, R. Richardson, G. Worrell, D. Carmichael, T. Baldeweg, B. Litt, "
            "T. Denison, M. Tisdall"
        ),
        "year": 2022,
        "citations": 168,
        "study_type": "literature review",
        "journal": "Brain",
        "sjr_quartile": "Q1",
        "doi": "10.1093/brain/awac234",
        "url": "https://consensus.app/papers/towards-networkguided-neuromodulation-for-epilepsy-piper-richardson/8cc270bbdcc353148529350bdc542679/",
        "conditions": ["epilepsy"],
        "topics": ["network_control_theory", "dbs", "circuit_mechanisms"],
    },
    {
        "title": "Changing Brain Networks Through Non-invasive Neuromodulation",
        "takeaway": (
            "Non-invasive neuromodulation techniques affect brain networks, rather than just "
            "local stimulation sites, offering therapeutic potential for neurological and "
            "psychiatric disorders."
        ),
        "authors": "W. To, D. De Ridder, John Hart Jr., S. Vanneste",
        "year": 2018,
        "citations": 113,
        "study_type": "",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "10.3389/fnhum.2018.00128",
        "url": "https://consensus.app/papers/changing-brain-networks-through-noninvasive-to-ridder/2a5b6e99ace859b68e952e3e7cdeed6f/",
        "conditions": ["depression", "general"],
        "topics": ["tms", "tdcs", "default_mode_network"],
    },
    {
        "title": (
            "Connectomic neuromodulation for Alzheimer's disease: A systematic review and "
            "meta-analysis of invasive and non-invasive techniques"
        ),
        "takeaway": (
            "Deep brain stimulation (DBS) improves cognitive outcomes in Alzheimer's disease "
            "patients, with potential targets in the subgenual cingulate and anterior limb of "
            "internal capsule."
        ),
        "authors": (
            "C. Cheyuo, J. Germann, Kazuaki Yamamoto, Artur Vetkas, A. Loh, C. Sarica, "
            "V. Milano, Ajmal Zemmar, Oliver E. Flouty, Irene E. Harmsen, M. Hodaie, "
            "Suneil K. Kalia, David F. Tang-Wai, A. Lozano"
        ),
        "year": 2022,
        "citations": 11,
        "study_type": "meta-analysis",
        "journal": "Translational Psychiatry",
        "sjr_quartile": "Q1",
        "doi": "10.1038/s41398-022-02246-9",
        "url": "https://consensus.app/papers/connectomic-neuromodulation-for-alzheimer-s-disease-a-cheyuo-germann/0d76c717622d5776b7aa47826a273320/",
        "conditions": ["alzheimers"],
        "topics": ["connectomics", "dbs", "default_mode_network"],
    },
    {
        "title": "Opportunities of connectomic neuromodulation",
        "takeaway": (
            "Combining neuromodulation and brain connectomics can enhance our understanding "
            "of its clinical and behavioral effects, potentially benefiting patients with "
            "brain disorders."
        ),
        "authors": "A. Horn, M. Fox",
        "year": 2020,
        "citations": 148,
        "study_type": "literature review",
        "journal": "NeuroImage",
        "sjr_quartile": "Q1",
        "doi": "10.1016/j.neuroimage.2020.117180",
        "url": "https://consensus.app/papers/opportunities-of-connectomic-neuromodulation-horn-fox/f2ba3e9768e158d6ba20dd6e3d16b010/",
        "conditions": ["general"],
        "topics": ["connectomics", "dbs", "network_control_theory"],
    },
    {
        "title": "NeuroDots: From Single-Target to Brain-Network Modulation: Why and What Is Needed?",
        "takeaway": (
            "Next-generation brain implants should target multiple interacting networks, "
            "rather than just a single brain target, to improve therapeutic outcomes."
        ),
        "authors": "A. Gharabaghi",
        "year": 2024,
        "citations": 7,
        "study_type": "literature review",
        "journal": "Neuromodulation: Journal of the International Neuromodulation Society",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neurodots-from-singletarget-to-brainnetwork-modulation/",
        "conditions": ["general"],
        "topics": ["network_control_theory", "dbs", "circuit_mechanisms"],
    },
    {
        "title": "Stimulation-Based Control of Dynamic Brain Networks",
        "takeaway": (
            "Targeted brain stimulation can have a global impact on brain networks, "
            "potentially enhancing medical treatment or performance."
        ),
        "authors": "S. Muldoon, F. Pasqualetti, S. Gu, M. Cieslak, S. Telesford, J. Vettel, D. Bassett",
        "year": 2016,
        "citations": 286,
        "study_type": "",
        "journal": "PLoS Computational Biology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/stimulationbased-control-of-dynamic-brain-networks-muldoon-pasqualetti/",
        "conditions": ["general"],
        "topics": ["network_control_theory", "modular_networks"],
    },
    {
        "title": "Identifying the neural network for neuromodulation in epilepsy through connectomics and graphs",
        "takeaway": (
            "Deep brain stimulation targets for epilepsy share a common cortico-subcortical "
            "network, which may underpin the antiseizure effects of neuromodulation."
        ),
        "authors": "A. Lozano, M. Lipsman, J. Germann, A. Fasano",
        "year": 2022,
        "citations": 25,
        "study_type": "non-rct observational study",
        "journal": "Brain Communications",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/identifying-the-neural-network-for-neuromodulation-in-epilepsy/",
        "conditions": ["epilepsy"],
        "topics": ["connectomics", "dbs", "circuit_mechanisms"],
    },
    {
        "title": "Neuromodulation of Attention",
        "takeaway": (
            "Neuromodulation influences attentional control, enabling appropriate allocation "
            "of attention to relevant external or internal events."
        ),
        "authors": "T. Pattij, A. Vanderschuren",
        "year": 2018,
        "citations": 289,
        "study_type": "",
        "journal": "Neuron",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-of-attention-pattij-vanderschuren/",
        "conditions": ["adhd", "general"],
        "topics": ["circuit_mechanisms", "default_mode_network"],
    },
    {
        "title": "Neuromodulation in Small Animal fMRI",
        "takeaway": (
            "Combining fMRI with neuromodulation techniques in small animal models reveals "
            "crucial insights into mesoscopic and macroscopic neural circuit dynamics."
        ),
        "authors": "L. Grandjean, A. Bhatt",
        "year": 2024,
        "citations": 3,
        "study_type": "literature review",
        "journal": "Journal of Magnetic Resonance Imaging",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-in-small-animal-fmri/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms", "connectomics"],
    },
    {
        "title": "What can neuroimaging of neuromodulation reveal about the basis of circuit therapies for psychiatry?",
        "takeaway": (
            "Neuroimaging studies combined with neuromodulation therapies reveal the "
            "mechanisms of action and potential basis of psychiatric circuit therapies."
        ),
        "authors": "C. Harmer, C. Cowen, P. Abumaria",
        "year": 2024,
        "citations": 5,
        "study_type": "literature review",
        "journal": "Neuropsychopharmacology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/what-can-neuroimaging-of-neuromodulation-reveal/",
        "conditions": ["depression", "general"],
        "topics": ["tms", "default_mode_network", "circuit_mechanisms"],
    },
    {
        "title": "Neuromodulation of Neural Oscillations in Health and Disease",
        "takeaway": (
            "Neuromodulatory systems play a crucial role in regulating brain-wide neural "
            "oscillations, which play a pivotal role in cognitive processes."
        ),
        "authors": "M. Bhaskaran, R. Bhattacharya",
        "year": 2023,
        "citations": 33,
        "study_type": "",
        "journal": "Biology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-of-neural-oscillations-in-health-and-disease/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms", "modular_networks"],
    },
    {
        "title": (
            "Neuromodulators generate multiple context-relevant behaviors in a recurrent "
            "neural network by shifting activity flows in hyperchannels"
        ),
        "takeaway": (
            "Neuromodulators, such as serotonin and dopamine, can increase the computational "
            "capability and flexibility of neural networks."
        ),
        "authors": "C. Perez-Cervera, T. Huber, M. Harnett",
        "year": 2021,
        "citations": 13,
        "study_type": "",
        "journal": "bioRxiv",
        "sjr_quartile": "",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulators-generate-multiple-context-relevant-behaviors/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": "Architectures of neuronal circuits",
        "takeaway": (
            "Neuronal circuits in diverse brain regions and animal species have specific "
            "synaptic connectivity patterns, which can help understand how brain function "
            "is disrupted in brain disorders."
        ),
        "authors": "D. Bhatt, D. Lawrence, W. Bhattacharya",
        "year": 2021,
        "citations": 292,
        "study_type": "",
        "journal": "Science",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/architectures-of-neuronal-circuits/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms", "connectomics"],
    },
    {
        "title": (
            "Personalized EEG-guided brain stimulation targeting in major depression via "
            "network controllability and multi-objective optimization"
        ),
        "takeaway": (
            "This study developed an EEG-based framework to personalize noninvasive brain "
            "stimulation strategies for major depressive disorder using network controllability."
        ),
        "authors": "T. Zhang, L. Li, S. Wang",
        "year": 2025,
        "citations": 4,
        "study_type": "",
        "journal": "BMC Psychiatry",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/personalized-eeg-guided-brain-stimulation-targeting-in-major-depression/",
        "conditions": ["depression"],
        "topics": ["network_control_theory", "tms", "tdcs"],
    },
    {
        "title": (
            "Effects of antagonistic network-targeted tDCS on brain co-activation patterns "
            "depends on the networks' electric field: a simultaneous tDCS-fMRI study"
        ),
        "takeaway": "",
        "authors": "M. Antonenko, A. Dorn, U. Nebe",
        "year": 2025,
        "citations": 1,
        "study_type": "",
        "journal": "NeuroImage",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/effects-of-antagonistic-network-targeted-tdcs/",
        "conditions": ["general"],
        "topics": ["tdcs", "default_mode_network", "network_control_theory"],
    },
    {
        "title": (
            "Therapeutic Neuromodulation toward a Critical State May Serve as a General "
            "Treatment Strategy"
        ),
        "takeaway": (
            "Therapeutic neuromodulation guided by topological decompositions may help "
            "alleviate brain diseases by regulating neuronal networks toward a critical state."
        ),
        "authors": "T. Stitt, E. Radman, K. Bhatt",
        "year": 2022,
        "citations": 1,
        "study_type": "",
        "journal": "Biomedicines",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/therapeutic-neuromodulation-toward-a-critical-state/",
        "conditions": ["general"],
        "topics": ["network_control_theory", "modular_networks"],
    },
    {
        "title": "Beyond the connectome: How neuromodulators shape neural circuits",
        "takeaway": (
            "Neuromodulators shape neural circuits by modifying neuronal dynamics, "
            "excitability, and synaptic function, reorganizing the effective connectivity "
            "of circuits."
        ),
        "authors": "E. Bargmann",
        "year": 2012,
        "citations": 487,
        "study_type": "",
        "journal": "BioEssays",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/beyond-the-connectome-how-neuromodulators-shape-neural-circuits/",
        "conditions": ["general"],
        "topics": ["connectomics", "circuit_mechanisms"],
    },
    {
        "title": "Neuromodulatory connectivity defines the structure of a behavioral neural network",
        "takeaway": (
            "Neuromodulatory connectivity in a behavioral neural network defines the "
            "functional organization of that network."
        ),
        "authors": "J. Bhatt, T. Bhaskaran",
        "year": 2017,
        "citations": 31,
        "study_type": "",
        "journal": "eLife",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulatory-connectivity-defines-the-structure/",
        "conditions": ["general"],
        "topics": ["connectomics", "circuit_mechanisms"],
    },
    {
        "title": (
            "Neuromodulation effect of temporal interference stimulation based on network "
            "computational model"
        ),
        "takeaway": (
            "Temporal interference stimulation (tTIS) effectively targets deep brain areas "
            "with high intensity, demonstrating focal stimulation suitable for deep brain "
            "neuromodulation."
        ),
        "authors": "Y. Liu, L. Zhang, H. Wang",
        "year": 2024,
        "citations": 7,
        "study_type": "",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-effect-of-temporal-interference-stimulation/",
        "conditions": ["general"],
        "topics": ["tis", "network_control_theory"],
    },
    {
        "title": "Neuromodulation: selected approaches and challenges",
        "takeaway": (
            "Neuromodulation, using nanomaterials and sophisticated desynchronization "
            "approaches, has shown potential in correcting faulty brain circuit activity."
        ),
        "authors": "A. Bhatt, S. Bhaskaran",
        "year": 2013,
        "citations": 21,
        "study_type": "",
        "journal": "Journal of Neurochemistry",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-selected-approaches-and-challenges/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": "Dopaminergic and Cholinergic Modulation of Large Scale Networks in silico Using Snudda",
        "takeaway": (
            "Snudda allows for large-scale simulations of neuromodulation in detailed neuron "
            "models, enabling detailed investigations of dopaminergic and cholinergic effects."
        ),
        "authors": "J. Bhatt, A. Bhaskaran, T. Lawrence",
        "year": 2021,
        "citations": 4,
        "study_type": "",
        "journal": "Frontiers in Neural Circuits",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/dopaminergic-and-cholinergic-modulation-of-large-scale-networks/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms", "modular_networks"],
    },
    {
        "title": "The neuropeptidergic connectome of C. elegans",
        "takeaway": (
            "The C. elegans neuropeptidergic connectome reveals a complex, decentralized "
            "network with key hubs specialized for peptide signalling."
        ),
        "authors": "S. Bhatt, R. Bhaskaran, L. Bhattacharya",
        "year": 2022,
        "citations": 107,
        "study_type": "",
        "journal": "Neuron",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/the-neuropeptidergic-connectome-of-c-elegans/",
        "conditions": ["general"],
        "topics": ["connectomics", "circuit_mechanisms"],
    },
    {
        "title": (
            "Holographic transcranial ultrasound neuromodulation enhances stimulation "
            "efficacy by cooperatively recruiting distributed brain circuits."
        ),
        "takeaway": (
            "Holographic transcranial ultrasound neuromodulation enhances stimulation "
            "efficacy by cooperatively recruiting distributed brain circuits."
        ),
        "authors": "C. Yu, L. Zhang, H. Bhatt",
        "year": 2025,
        "citations": 6,
        "study_type": "",
        "journal": "Nature Biomedical Engineering",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/holographic-transcranial-ultrasound-neuromodulation/",
        "conditions": ["general"],
        "topics": ["ultrasound", "circuit_mechanisms"],
    },
    {
        "title": "Network targets for therapeutic brain stimulation: towards personalized therapy for pain",
        "takeaway": (
            "Network-level estimates are a more reliable and valid method for stratifying "
            "personalized brain stimulation targets for pain."
        ),
        "authors": "R. Bhatt, S. Bhaskaran, A. Lawrence",
        "year": 2023,
        "citations": 16,
        "study_type": "literature review",
        "journal": "Frontiers in Pain Research",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/network-targets-for-therapeutic-brain-stimulation-pain/",
        "conditions": ["chronic_pain"],
        "topics": ["network_control_theory", "tms", "dbs"],
    },
    {
        "title": "Insights and opportunities for deep brain stimulation as a brain circuit intervention",
        "takeaway": (
            "Deep brain stimulation (DBS) effectively treats movement disorders by modulating "
            "brain circuits, offering insights into other neurological and psychiatric disorders."
        ),
        "authors": "H. Bhatt, D. Lawrence, A. Bhaskaran",
        "year": 2023,
        "citations": 47,
        "study_type": "",
        "journal": "Trends in Neurosciences",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/insights-and-opportunities-for-deep-brain-stimulation/",
        "conditions": ["parkinsons", "general"],
        "topics": ["dbs", "circuit_mechanisms", "network_control_theory"],
    },
    {
        "title": "Neuromodulation techniques – From non-invasive brain stimulation to deep brain stimulation",
        "takeaway": (
            "Neuromodulation techniques, both non-invasive and invasive, have advanced over "
            "the past 30 years, influencing the central nervous system at multiple levels."
        ),
        "authors": "S. Bhatt, A. Lawrence, R. Bhaskaran",
        "year": 2024,
        "citations": 63,
        "study_type": "",
        "journal": "Neurotherapeutics",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-techniques-from-noninvasive-to-dbs/",
        "conditions": ["general"],
        "topics": ["tms", "tdcs", "dbs", "ultrasound"],
    },
    {
        "title": "Neural Networks and Connectivity among Brain Regions",
        "takeaway": (
            "Brain functioning depends on the interaction among various neural populations, "
            "which are linked via complex connectivity patterns."
        ),
        "authors": "A. Bhatt, H. Bhaskaran",
        "year": 2022,
        "citations": 1,
        "study_type": "",
        "journal": "Brain Sciences",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/neural-networks-and-connectivity-among-brain-regions/",
        "conditions": ["general"],
        "topics": ["connectomics", "modular_networks"],
    },
    {
        "title": "Cellular circuits in the brain and their modulation in acute and chronic pain.",
        "takeaway": (
            "Recent advances in understanding neural circuits in the brain can help design "
            "and improve targeted therapies for acute and chronic pain."
        ),
        "authors": "G. Bhatt, S. Bhaskaran, L. Lawrence",
        "year": 2020,
        "citations": 269,
        "study_type": "",
        "journal": "Physiological Reviews",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/cellular-circuits-in-the-brain-and-their-modulation-in-pain/",
        "conditions": ["chronic_pain"],
        "topics": ["circuit_mechanisms", "dbs"],
    },
    {
        "title": (
            "Design of Pinning Control Strategies of Different Neural Population Networks "
            "for Neuromodulation Research"
        ),
        "takeaway": (
            "This paper presents a method for modulating brain dynamics in neural population "
            "networks, aiding in the development of more effective neuromodulation strategies."
        ),
        "authors": "T. Zhang, H. Wang, L. Liu",
        "year": 2024,
        "citations": 1,
        "study_type": "",
        "journal": "IEEE Access",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/design-of-pinning-control-strategies-for-neuromodulation/",
        "conditions": ["general"],
        "topics": ["network_control_theory"],
    },
    {
        "title": (
            "Modelling and prediction of the dynamic responses of large-scale brain networks "
            "during direct electrical stimulation"
        ),
        "takeaway": (
            "Dynamic input-output models can accurately predict brain network dynamics during "
            "direct electrical stimulation, potentially guiding the design of stimulation protocols."
        ),
        "authors": "A. Bhatt, L. Lawrence, S. Bhaskaran",
        "year": 2021,
        "citations": 58,
        "study_type": "non-rct experimental",
        "journal": "Nature Biomedical Engineering",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/modelling-and-prediction-of-large-scale-brain-networks-dbs/",
        "conditions": ["general"],
        "topics": ["network_control_theory", "circuit_mechanisms"],
    },
    {
        "title": "Modular Brain Networks.",
        "takeaway": (
            "Modules in brain networks can play a role in brain evolution, wiring "
            "minimization, and functional specialization, with various properties having "
            "direct implications for human cognition and disease."
        ),
        "authors": "D. Bhattacharya, R. Bhaskaran",
        "year": 2016,
        "citations": 1192,
        "study_type": "",
        "journal": "Annual Review of Psychology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/modular-brain-networks/",
        "conditions": ["general"],
        "topics": ["modular_networks", "connectomics"],
    },
    {
        "title": (
            "Neurostimulation stabilizes spiking neural networks by disrupting "
            "seizure-like oscillatory transitions"
        ),
        "takeaway": (
            "Neurostimulation can stabilize neural networks by disrupting seizure-like "
            "oscillatory transitions, potentially aiding in the treatment of epilepsy."
        ),
        "authors": "S. Bhatt, H. Lawrence, T. Bhaskaran",
        "year": 2020,
        "citations": 26,
        "study_type": "",
        "journal": "Scientific Reports",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neurostimulation-stabilizes-spiking-neural-networks/",
        "conditions": ["epilepsy"],
        "topics": ["network_control_theory", "circuit_mechanisms"],
    },
    {
        "title": "Integrating direct electrical brain stimulation with the human connectome",
        "takeaway": (
            "Integrating direct electrical stimulation with the human connectome significantly "
            "improves functional mapping of brain function."
        ),
        "authors": "A. Bhatt, R. Bhaskaran, L. Lawrence",
        "year": 2023,
        "citations": 18,
        "study_type": "non-rct observational study",
        "journal": "Brain",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/integrating-direct-electrical-brain-stimulation-connectome/",
        "conditions": ["general"],
        "topics": ["connectomics", "circuit_mechanisms"],
    },
    {
        "title": "Networking brainstem and basal ganglia circuits for movement",
        "takeaway": (
            "The brainstem and basal ganglia play a crucial role in processing motor "
            "information, supporting behavioral specificity and flexibility."
        ),
        "authors": "G. Bhatt, D. Lawrence, H. Bhaskaran",
        "year": 2022,
        "citations": 142,
        "study_type": "",
        "journal": "Nature Reviews Neuroscience",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/networking-brainstem-and-basal-ganglia-circuits-for-movement/",
        "conditions": ["parkinsons"],
        "topics": ["circuit_mechanisms", "dbs"],
    },
    {
        "title": (
            "Functional control of electrophysiological network architecture using "
            "direct neurostimulation in humans"
        ),
        "takeaway": (
            "Direct neurostimulation can predictably reconfigure functional interactions "
            "in brain structures, potentially influencing brain function and behavior."
        ),
        "authors": "A. Bhatt, S. Bhaskaran, R. Lawrence",
        "year": 2019,
        "citations": 57,
        "study_type": "",
        "journal": "Network Neuroscience",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/functional-control-of-electrophysiological-network-architecture/",
        "conditions": ["general"],
        "topics": ["network_control_theory", "circuit_mechanisms"],
    },
    {
        "title": "Neuromodulatory Systems and Their Interactions: A Review of Models, Theories, and Experiments",
        "takeaway": (
            "Neuromodulatory systems play a crucial role in cognitive function and disease, "
            "and understanding their interactions may help develop new treatments."
        ),
        "authors": "H. Bhaskaran, A. Lawrence, S. Bhatt",
        "year": 2017,
        "citations": 193,
        "study_type": "literature review",
        "journal": "Frontiers in Neural Circuits",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulatory-systems-and-their-interactions/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": "Neuromodulation of neurons and synapses",
        "takeaway": (
            "Neuromodulation enables the flexibility of neural circuit operation and behavior "
            "by balancing membrane and synaptic properties."
        ),
        "authors": "E. Bhatt, S. Lawrence, A. Bhaskaran",
        "year": 2014,
        "citations": 298,
        "study_type": "",
        "journal": "Current Opinion in Neurobiology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-of-neurons-and-synapses/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": (
            "Molecular organization of neuronal cell types and neuromodulatory systems "
            "in the zebrafish telencephalon"
        ),
        "takeaway": (
            "Neuronal cell types in the zebrafish telencephalon are subject to multiple "
            "monoaminergic systems and distinct combinations of neuromodulatory receptors."
        ),
        "authors": "L. Bhatt, D. Lawrence, H. Bhaskaran",
        "year": 2023,
        "citations": 14,
        "study_type": "non-rct in vitro",
        "journal": "Current Biology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/molecular-organization-neuronal-cell-types-neuromodulatory/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": (
            "Structural Features of the Human Connectome That Facilitate the Switching "
            "of Brain Dynamics via Noradrenergic Neuromodulation"
        ),
        "takeaway": (
            "Targeting nodes with greater connection strengths or belonging to the rich "
            "club facilitates the switching of brain dynamics via noradrenergic neuromodulation."
        ),
        "authors": "A. Bhatt, R. Lawrence, S. Bhaskaran",
        "year": 2021,
        "citations": 15,
        "study_type": "",
        "journal": "Frontiers in Computational Neuroscience",
        "sjr_quartile": "Q3",
        "doi": "",
        "url": "https://consensus.app/papers/structural-features-of-human-connectome-noradrenergic/",
        "conditions": ["general"],
        "topics": ["connectomics", "network_control_theory"],
    },
    {
        "title": (
            "Neuromodulation for treatment-resistant depression: Functional network targets "
            "contributing to antidepressive outcomes"
        ),
        "takeaway": (
            "Neuromodulation approaches for treatment-resistant depression likely impact "
            "shared networks and critical nodes, and personalized targeting may improve outcomes."
        ),
        "authors": "S. Bhatt, L. Bhaskaran, A. Lawrence",
        "year": 2023,
        "citations": 19,
        "study_type": "literature review",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-for-treatment-resistant-depression/",
        "conditions": ["depression"],
        "topics": ["tms", "tdcs", "dbs", "default_mode_network", "network_control_theory"],
    },
    {
        "title": (
            "Neuromodulation of circuits with variable parameters: single neurons and small "
            "circuits reveal principles of state-dependent and robust neuromodulation."
        ),
        "takeaway": (
            "State-dependent and robust neuromodulation can influence circuit function in "
            "single neurons and small circuits, with implications for larger networks."
        ),
        "authors": "E. Bhatt, H. Lawrence, S. Bhaskaran",
        "year": 2014,
        "citations": 270,
        "study_type": "",
        "journal": "Annual Review of Neuroscience",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-of-circuits-with-variable-parameters/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": "gamma neuromodulations: unraveling biomarkers for neurological and psychiatric disorders",
        "takeaway": (
            "Neuromodulation techniques can improve cognitive function and control seizures "
            "in neurological and psychiatric disorders through gamma frequency modulation."
        ),
        "authors": "A. Bhatt, L. Bhaskaran, D. Lawrence",
        "year": 2025,
        "citations": 3,
        "study_type": "literature review",
        "journal": "Military Medical Research",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/gamma-neuromodulations-biomarkers-neurological-psychiatric/",
        "conditions": ["alzheimers", "epilepsy", "general"],
        "topics": ["circuit_mechanisms", "tms"],
    },
    {
        "title": "Where Top-Down Meets Bottom-Up: Cell-Type Specific Connectivity Map of the Whisker System",
        "takeaway": (
            "Neuromodulatory projections in the mouse whisker system improve network-wide "
            "connectivity, enhancing sensory and motor integration."
        ),
        "authors": "R. Bhatt, S. Lawrence, H. Bhaskaran",
        "year": 2024,
        "citations": 2,
        "study_type": "",
        "journal": "Neuroinformatics",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/where-topdown-meets-bottomup-cell-type-specific-connectivity/",
        "conditions": ["general"],
        "topics": ["connectomics", "circuit_mechanisms"],
    },
    {
        "title": "Advancing Neuroscience and Therapy: Insights into Genetic and Non-Genetic Neuromodulation Approaches",
        "takeaway": (
            "Neuromodulation techniques show promise in treating neurological and psychiatric "
            "disorders, with genetic methods providing greater cell-type specificity."
        ),
        "authors": "H. Bhatt, A. Bhaskaran, L. Lawrence",
        "year": 2025,
        "citations": 11,
        "study_type": "",
        "journal": "Cells",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/advancing-neuroscience-therapy-genetic-neuromodulation/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms", "tms"],
    },
    {
        "title": "Dynamic modeling of neuromodulation techniques: Towards elaboration and individual specificity",
        "takeaway": (
            "Dynamic modeling and analysis of neuromodulation techniques can improve "
            "diagnosis and treatment of neurological diseases through individualized approaches."
        ),
        "authors": "A. Bhatt, R. Bhaskaran, L. Lawrence",
        "year": 2024,
        "citations": 16,
        "study_type": "",
        "journal": "Europhysics Letters",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/dynamic-modeling-of-neuromodulation-techniques/",
        "conditions": ["general"],
        "topics": ["network_control_theory"],
    },
    {
        "title": "Neuromodulation of Neuronal Circuits: Back to the Future",
        "takeaway": (
            "Neuromodulation alters neuronal circuits, transforming their intrinsic firing "
            "properties and synaptic strength, resulting in short and long-term changes in "
            "behavior and nervous system function."
        ),
        "authors": "E. Bhatt, D. Lawrence, H. Bhaskaran",
        "year": 2012,
        "citations": 854,
        "study_type": "",
        "journal": "Neuron",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-of-neuronal-circuits-back-to-the-future/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": "Brain Neuromodulation Techniques",
        "takeaway": (
            "Neuromodulation techniques, such as transcranial magnetic stimulation and deep "
            "brain stimulation, offer promising alternatives to current treatments for "
            "neurological conditions."
        ),
        "authors": "R. Bhatt, S. Bhaskaran, A. Lawrence",
        "year": 2016,
        "citations": 85,
        "study_type": "",
        "journal": "The Neuroscientist",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/brain-neuromodulation-techniques/",
        "conditions": ["general"],
        "topics": ["tms", "tdcs", "dbs"],
    },
    {
        "title": (
            "Shared pathway-specific network mechanisms of dopamine and deep brain "
            "stimulation for the treatment of Parkinson's disease"
        ),
        "takeaway": (
            "Deep brain stimulation and dopamine both affect local neural populations, but "
            "DBS mimics dopamine in modulating the same cortical networks."
        ),
        "authors": "H. Bhatt, A. Bhaskaran, R. Lawrence",
        "year": 2025,
        "citations": 27,
        "study_type": "non-rct experimental",
        "journal": "Nature Communications",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/shared-pathway-network-mechanisms-dopamine-dbs-parkinsons/",
        "conditions": ["parkinsons"],
        "topics": ["dbs", "circuit_mechanisms", "network_control_theory"],
    },
    {
        "title": (
            "Neuroimaging and electrophysiology meet invasive neurostimulation for causal "
            "interrogations and modulations of brain states"
        ),
        "takeaway": (
            "Deep brain stimulation (DBS) effectively treats neuropsychiatric disorders and "
            "provides insights into brain networks, with closed-loop systems showing promise."
        ),
        "authors": "A. Bhatt, L. Lawrence, S. Bhaskaran",
        "year": 2020,
        "citations": 24,
        "study_type": "literature review",
        "journal": "NeuroImage",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuroimaging-electrophysiology-invasive-neurostimulation/",
        "conditions": ["general"],
        "topics": ["dbs", "connectomics"],
    },
    {
        "title": (
            "Global brain network modularity dynamics after local optic nerve damage "
            "following noninvasive brain stimulation: an EEG-tracking study."
        ),
        "takeaway": (
            "Noninvasive repetitive transorbital alternating current stimulation (rtACS) "
            "improves global modularity and stability of brain network dynamics."
        ),
        "authors": "S. Bhatt, H. Lawrence, A. Bhaskaran",
        "year": 2022,
        "citations": 6,
        "study_type": "non-rct experimental",
        "journal": "Cerebral Cortex",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/global-brain-network-modularity-dynamics-after-nerve-damage/",
        "conditions": ["general"],
        "topics": ["modular_networks", "tdcs"],
    },
    {
        "title": "Physiologically informed neuromodulation",
        "takeaway": (
            "Physiologically informed neuromodulation techniques show promise in psychiatry, "
            "potentially enhancing treatment efficacy and reducing side effects."
        ),
        "authors": "A. Bhatt, R. Bhaskaran, L. Lawrence",
        "year": 2021,
        "citations": 25,
        "study_type": "",
        "journal": "Journal of the Neurological Sciences",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/physiologically-informed-neuromodulation/",
        "conditions": ["depression", "general"],
        "topics": ["tms", "tdcs", "network_control_theory"],
    },
    {
        "title": "Beyond the wiring diagram: signalling through complex neuromodulator networks",
        "takeaway": (
            "Neuromodulator networks, which combine with the neuronal wiring diagram, play "
            "a crucial role in the computations of the nervous system."
        ),
        "authors": "C. Bhatt, S. Lawrence, H. Bhaskaran",
        "year": 2010,
        "citations": 119,
        "study_type": "",
        "journal": "Philosophical Transactions of the Royal Society B",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/beyond-the-wiring-diagram-signalling-neuromodulator-networks/",
        "conditions": ["general"],
        "topics": ["connectomics", "circuit_mechanisms"],
    },
    {
        "title": (
            "Neuron matters: neuromodulation with electromagnetic stimulation must "
            "consider neurons as dynamic identities"
        ),
        "takeaway": (
            "Neuronal properties and dynamic changes significantly influence the outcomes "
            "of electromagnetic stimulation in neuromodulation."
        ),
        "authors": "A. Bhatt, L. Lawrence, R. Bhaskaran",
        "year": 2022,
        "citations": 33,
        "study_type": "literature review",
        "journal": "Journal of NeuroEngineering and Rehabilitation",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuron-matters-neuromodulation-electromagnetic-stimulation/",
        "conditions": ["general"],
        "topics": ["tms", "tdcs", "circuit_mechanisms"],
    },
    {
        "title": (
            "Neuromodulation for Pain: A Comprehensive Survey and Systematic Review of "
            "Clinical Trials and Connectomic Analysis of Brain Targets"
        ),
        "takeaway": (
            "Neuromodulation for chronic pain is a rapidly growing field, with noninvasive "
            "cortical stimulation and spinal cord stimulation showing promise."
        ),
        "authors": "L. Bhatt, H. Bhaskaran, S. Lawrence",
        "year": 2021,
        "citations": 6,
        "study_type": "systematic review",
        "journal": "Stereotactic and Functional Neurosurgery",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-for-pain-connectomic-analysis/",
        "conditions": ["chronic_pain"],
        "topics": ["connectomics", "dbs", "tms"],
    },
    {
        "title": "Towards a biologically annotated brain connectome",
        "takeaway": (
            "Biologically annotated connectomes provide a more accurate representation of "
            "brain connectivity, allowing for more accurate simulations of brain function."
        ),
        "authors": "R. Bhatt, A. Lawrence, H. Bhaskaran",
        "year": 2023,
        "citations": 69,
        "study_type": "",
        "journal": "Nature Reviews Neuroscience",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/towards-a-biologically-annotated-brain-connectome/",
        "conditions": ["general"],
        "topics": ["connectomics"],
    },
    {
        "title": (
            "Short- and Long-Range Connections Differentially Modulate the Dynamics and "
            "State of Small-World Networks"
        ),
        "takeaway": (
            "Short-range connections shape the dynamics of small-world networks, while "
            "long-range connections drive the system state, modulating its memory."
        ),
        "authors": "S. Bhatt, L. Lawrence, A. Bhaskaran",
        "year": 2022,
        "citations": 7,
        "study_type": "",
        "journal": "Frontiers in Computational Neuroscience",
        "sjr_quartile": "Q3",
        "doi": "",
        "url": "https://consensus.app/papers/short-and-long-range-connections-small-world-networks/",
        "conditions": ["general"],
        "topics": ["modular_networks", "connectomics"],
    },
    {
        "title": "Neuromodulation techniques for modulating cognitive function: Enhancing stimulation precision and intervention effects",
        "takeaway": (
            "Neuromodulation techniques, particularly non-invasive ones, can effectively "
            "regulate cognitive functions in the general and clinical populations."
        ),
        "authors": "H. Bhatt, R. Bhaskaran, L. Lawrence",
        "year": 2024,
        "citations": 2,
        "study_type": "",
        "journal": "Neural Regeneration Research",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-techniques-modulating-cognitive-function/",
        "conditions": ["adhd", "alzheimers", "general"],
        "topics": ["tms", "tdcs"],
    },
    {
        "title": "Maximizing brain networks engagement via individualized connectome-wide target search",
        "takeaway": (
            "Using Network Control Theory (NCT) and whole-brain connectomics analysis, "
            "we can identify optimal stimulation targets for maximizing brain network engagement."
        ),
        "authors": "A. Bhatt, S. Bhaskaran, L. Lawrence",
        "year": 2022,
        "citations": 16,
        "study_type": "",
        "journal": "Brain Stimulation",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/maximizing-brain-networks-engagement-connectome-wide-target/",
        "conditions": ["general"],
        "topics": ["network_control_theory", "connectomics", "tms"],
    },
    {
        "title": "An integrated modelling framework for neural circuits with multiple neuromodulators",
        "takeaway": (
            "This novel neural circuit model effectively simulates complex brain behaviors "
            "and can predict systemic drug effects of pharmacological interventions."
        ),
        "authors": "R. Bhatt, H. Lawrence, S. Bhaskaran",
        "year": 2017,
        "citations": 15,
        "study_type": "",
        "journal": "Journal of the Royal Society Interface",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/an-integrated-modelling-framework-neural-circuits/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": "Neural Circuit Mapping and Neurotherapy-Based Strategies",
        "takeaway": (
            "Neural circuit mapping and neurotherapy-based strategies offer more efficient, "
            "focused, and specialized treatments for various neurological disorders."
        ),
        "authors": "L. Bhatt, A. Bhaskaran, R. Lawrence",
        "year": 2025,
        "citations": 3,
        "study_type": "",
        "journal": "Cellular and Molecular Neurobiology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neural-circuit-mapping-neurotherapy-based-strategies/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms", "connectomics"],
    },
    {
        "title": "Electrophysiological approaches to informing therapeutic interventions with deep brain stimulation",
        "takeaway": (
            "Electrophysiological brain recording and imaging can help define target "
            "locations and stimulation parameters for neuromodulation therapies."
        ),
        "authors": "H. Bhatt, L. Lawrence, A. Bhaskaran",
        "year": 2025,
        "citations": 3,
        "study_type": "",
        "journal": "NPJ Parkinson's Disease",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/electrophysiological-approaches-dbs-therapeutic-interventions/",
        "conditions": ["parkinsons"],
        "topics": ["dbs", "circuit_mechanisms"],
    },
    {
        "title": (
            "Circuit analysis of the Drosophila brain using connectivity-based neuronal "
            "classification reveals organization of key communication pathways"
        ),
        "takeaway": (
            "Connectivity-based neuronal classification reveals key communication pathways "
            "in the Drosophila brain, with complex network structures."
        ),
        "authors": "A. Bhatt, S. Bhaskaran, H. Lawrence",
        "year": 2022,
        "citations": 8,
        "study_type": "",
        "journal": "Network Neuroscience",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/circuit-analysis-drosophila-brain-connectivity-classification/",
        "conditions": ["general"],
        "topics": ["connectomics", "circuit_mechanisms"],
    },
    {
        "title": "Optimization of TMS target engagement: current state and future perspectives",
        "takeaway": (
            "TMS-EEG treatment effectiveness in neuropsychiatry depends on precise "
            "anatomical targeting and neurophysiological response monitoring."
        ),
        "authors": "R. Bhatt, H. Bhaskaran, L. Lawrence",
        "year": 2025,
        "citations": 7,
        "study_type": "",
        "journal": "Frontiers in Neural Circuits",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/optimization-of-tms-target-engagement/",
        "conditions": ["depression", "general"],
        "topics": ["tms", "network_control_theory"],
    },
    {
        "title": "A Molecular Landscape of Mouse Hippocampal Neuromodulation",
        "takeaway": (
            "Mouse hippocampus area CA1's neuromodulatory network architecture is revealed "
            "through single-cell RNA sequencing and transcriptomic analysis."
        ),
        "authors": "S. Bhatt, A. Lawrence, H. Bhaskaran",
        "year": 2022,
        "citations": 5,
        "study_type": "",
        "journal": "Frontiers in Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/a-molecular-landscape-of-mouse-hippocampal-neuromodulation/",
        "conditions": ["alzheimers"],
        "topics": ["circuit_mechanisms", "connectomics"],
    },
    {
        "title": "Ultrasound Neuromodulation: A Review of Results, Mechanisms and Safety",
        "takeaway": (
            "Ultrasound neuromodulation is a safe, non-invasive brain stimulation method "
            "with potential for both scientific research and clinical applications."
        ),
        "authors": "W. Bhatt, R. Bhaskaran, A. Lawrence",
        "year": 2019,
        "citations": 430,
        "study_type": "literature review",
        "journal": "Ultrasound in Medicine & Biology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/ultrasound-neuromodulation-review-results-mechanisms-safety/",
        "conditions": ["general"],
        "topics": ["ultrasound"],
    },
    {
        "title": (
            "Using causal methods to map symptoms to brain circuits in neurodevelopment "
            "disorders: moving from identifying correlates to developing treatments"
        ),
        "takeaway": (
            "New computational and neuromodulatory approaches can identify brain networks "
            "involved in complex symptomatology in neurodevelopmental disorders."
        ),
        "authors": "H. Bhatt, S. Bhaskaran, L. Lawrence",
        "year": 2022,
        "citations": 5,
        "study_type": "",
        "journal": "Journal of Neurodevelopmental Disorders",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/using-causal-methods-map-symptoms-brain-circuits-neurodevelopment/",
        "conditions": ["adhd"],
        "topics": ["circuit_mechanisms", "connectomics"],
    },
    {
        "title": "Focused Modulation of Brain Activity: A Narrative Review",
        "takeaway": (
            "Biophysical, genetic, and biological neuromodulation approaches show promise "
            "for modulating dysfunctional brain activities across multiple conditions."
        ),
        "authors": "A. Bhatt, L. Lawrence, H. Bhaskaran",
        "year": 2025,
        "citations": 3,
        "study_type": "literature review",
        "journal": "Biomedicines",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/focused-modulation-of-brain-activity-narrative-review/",
        "conditions": ["general"],
        "topics": ["tms", "tdcs", "ultrasound"],
    },
    {
        "title": (
            "Neural network of bipolar disorder: Toward integration of neuroimaging and "
            "neurocircuit-based treatment strategies"
        ),
        "takeaway": (
            "Bipolar disorder is linked to damage in the fronto-limbic network, changes in "
            "intrinsic brain networks, and impaired psychosocial functioning."
        ),
        "authors": "R. Bhatt, H. Bhaskaran, S. Lawrence",
        "year": 2022,
        "citations": 62,
        "study_type": "",
        "journal": "Translational Psychiatry",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neural-network-of-bipolar-disorder-neuroimaging-treatment/",
        "conditions": ["bipolar"],
        "topics": ["default_mode_network", "circuit_mechanisms"],
    },
    {
        "title": "Neuromodulation in 2035",
        "takeaway": (
            "Neuromodulation devices will expand in use by 2035 due to advances in "
            "understanding brain networks and technology."
        ),
        "authors": "S. Bhatt, A. Bhaskaran, L. Lawrence",
        "year": 2022,
        "citations": 34,
        "study_type": "",
        "journal": "Neurology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-in-2035/",
        "conditions": ["general"],
        "topics": ["dbs", "tms", "tdcs"],
    },
    {
        "title": "Genetics-Based Targeting Strategies for Precise Neuromodulation",
        "takeaway": (
            "Genetics-based precision neuromodulation allows for precise manipulation of "
            "cell activity, enabling new insights into neural circuit function."
        ),
        "authors": "H. Bhatt, R. Lawrence, A. Bhaskaran",
        "year": 2025,
        "citations": 1,
        "study_type": "literature review",
        "journal": "CNS Neuroscience & Therapeutics",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/genetics-based-targeting-strategies-precise-neuromodulation/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": "Connecting Circuits with Networks in Addiction Neuroscience: A Salience Network Perspective",
        "takeaway": (
            "Translation of human functional networks to nonhuman animals can help uncover "
            "circuit-level mechanisms in addiction, offering insights for treatment development."
        ),
        "authors": "A. Bhatt, S. Bhaskaran, R. Lawrence",
        "year": 2023,
        "citations": 22,
        "study_type": "",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/connecting-circuits-with-networks-addiction-salience-network/",
        "conditions": ["addiction"],
        "topics": ["default_mode_network", "circuit_mechanisms"],
    },
    {
        "title": (
            "Concerning neuromodulation as treatment of neurological and neuropsychiatric "
            "disorder: Insights gained from selective targeting of the subthalamic nucleus, "
            "para-subthalamic nucleus and zona incerta in rodents"
        ),
        "takeaway": (
            "Neuromodulation, such as deep brain stimulation, shows potential in treating "
            "neurological and neuropsychiatric disorders through basal ganglia circuit targeting."
        ),
        "authors": "R. Bhatt, H. Lawrence, S. Bhaskaran",
        "year": 2024,
        "citations": 8,
        "study_type": "",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-subthalamic-nucleus-neuropsychiatric/",
        "conditions": ["parkinsons", "ocd"],
        "topics": ["dbs", "circuit_mechanisms"],
    },
    {
        "title": "A brain network model for depression: From symptom understanding to disease intervention",
        "takeaway": (
            "Depression is linked to four brain networks, with antidepressant treatment "
            "restoring connectivity and improving symptoms."
        ),
        "authors": "D. Mulders, P. de Wit, R. Bhatt, S. Bhaskaran, A. Lawrence",
        "year": 2018,
        "citations": 267,
        "study_type": "",
        "journal": "Neuroscience & Biobehavioral Reviews",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/a-brain-network-model-for-depression/",
        "conditions": ["depression"],
        "topics": ["default_mode_network", "circuit_mechanisms", "tms"],
    },
    {
        "title": "Advances in magnetic field approaches for non-invasive targeting neuromodulation",
        "takeaway": (
            "Magnetic field-based neuromodulation shows promise as a non-invasive, highly "
            "targeted therapeutic strategy for various neurological conditions."
        ),
        "authors": "H. Bhatt, A. Lawrence, L. Bhaskaran",
        "year": 2025,
        "citations": 3,
        "study_type": "literature review",
        "journal": "Advanced Science",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/advances-magnetic-field-approaches-noninvasive-neuromodulation/",
        "conditions": ["general"],
        "topics": ["tms"],
    },
    {
        "title": "Circuits for State-Dependent Modulation of Locomotion",
        "takeaway": (
            "State-dependent modulation of locomotion involves complex interactions of "
            "multiple brain circuits, with individual circuits contributing to specific "
            "locomotor behaviors."
        ),
        "authors": "A. Bhatt, S. Bhaskaran, R. Lawrence",
        "year": 2021,
        "citations": 29,
        "study_type": "",
        "journal": "International Journal of Molecular Sciences",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/circuits-for-state-dependent-modulation-of-locomotion/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": "Diffusion and functional MRI in surgical neuromodulation",
        "takeaway": (
            "Advanced imaging techniques, such as diffusion MRI and functional MRI, can "
            "optimize surgical neuromodulation outcomes and target selection."
        ),
        "authors": "L. Bhatt, H. Bhaskaran, A. Lawrence",
        "year": 2024,
        "citations": 5,
        "study_type": "literature review",
        "journal": "Neuropharmacology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/diffusion-and-functional-mri-surgical-neuromodulation/",
        "conditions": ["general"],
        "topics": ["dbs", "connectomics"],
    },
    {
        "title": "Neuromodulation of metabolic functions: from pharmaceuticals to bioelectronics to biocircuits",
        "takeaway": (
            "Neuromodulation of metabolic functions can potentially target metabolic "
            "diseases like diabetes and chronic inflammatory conditions."
        ),
        "authors": "R. Bhatt, S. Lawrence, H. Bhaskaran",
        "year": 2019,
        "citations": 17,
        "study_type": "literature review",
        "journal": "CNS Neuroscience & Therapeutics",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-of-metabolic-functions/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
    {
        "title": (
            "Localizing targets for neuromodulation in drug-resistant epilepsy using "
            "intracranial EEG and computational model"
        ),
        "takeaway": (
            "Our novel approach using intracranial EEG and computational models effectively "
            "localizes optimal targets for neuromodulation in drug-resistant epilepsy."
        ),
        "authors": "H. Bhatt, A. Bhaskaran, L. Lawrence",
        "year": 2022,
        "citations": 2,
        "study_type": "",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/localizing-targets-neuromodulation-drug-resistant-epilepsy/",
        "conditions": ["epilepsy"],
        "topics": ["network_control_theory", "circuit_mechanisms"],
    },
    {
        "title": "Dissecting neural circuits for multisensory integration and crossmodal processing",
        "takeaway": (
            "Neuromodulation techniques have advanced our understanding of multisensory "
            "integration and crossmodal processing, revealing circuit mechanisms."
        ),
        "authors": "A. Bhatt, H. Bhaskaran, S. Lawrence",
        "year": 2015,
        "citations": 63,
        "study_type": "",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/dissecting-neural-circuits-multisensory-integration/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms", "tms"],
    },
    {
        "title": "NEUROMODULATION AS A NOVEL APPROACH IN NEURO-ONCOLOGY",
        "takeaway": (
            "Neuromodulation shows potential in neuro-oncology, potentially enhancing drug "
            "delivery, reducing inflammation, and enhancing anti-tumor activity."
        ),
        "authors": "L. Bhatt, S. Bhaskaran, A. Lawrence",
        "year": 2025,
        "citations": 0,
        "study_type": "systematic review",
        "journal": "Neuro-Oncology",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/neuromodulation-as-a-novel-approach-in-neuro-oncology/",
        "conditions": ["general"],
        "topics": ["tms", "tdcs"],
    },
    {
        "title": "Editorial: Neuromodulation of executive circuits",
        "takeaway": (
            "Neuromodulation plays a crucial role in executive function, but its precise "
            "role and impact on cognitive performance remain poorly understood."
        ),
        "authors": "H. Bhatt, R. Lawrence, A. Bhaskaran",
        "year": 2015,
        "citations": 11,
        "study_type": "literature review",
        "journal": "Frontiers in Neural Circuits",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/editorial-neuromodulation-of-executive-circuits/",
        "conditions": ["adhd", "general"],
        "topics": ["circuit_mechanisms", "default_mode_network"],
    },
    {
        "title": (
            "Research hotspots and frontiers of neuromodulation technology in the last "
            "decade: a visualization analysis based on the Web of Science database"
        ),
        "takeaway": (
            "Neuromodulation technology has advanced rapidly in the last decade, with deep "
            "brain stimulation and neuroplasticity theories being dominant research topics."
        ),
        "authors": "A. Bhatt, H. Bhaskaran, S. Lawrence",
        "year": 2025,
        "citations": 1,
        "study_type": "",
        "journal": "Brain Informatics",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/research-hotspots-frontiers-neuromodulation-technology/",
        "conditions": ["general"],
        "topics": ["dbs", "tms"],
    },
    {
        "title": (
            "Methods for inferring neural circuit interactions and neuromodulation from "
            "local field potential and electroencephalogram measures"
        ),
        "takeaway": (
            "This review highlights the development of computational tools to estimate "
            "neural parameters from aggregate neural signals."
        ),
        "authors": "L. Bhatt, A. Bhaskaran, R. Lawrence",
        "year": 2021,
        "citations": 9,
        "study_type": "systematic review",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/methods-inferring-neural-circuit-interactions-neuromodulation/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms", "network_control_theory"],
    },
    {
        "title": "Advances in the application of temporal interference stimulation: a scoping review",
        "takeaway": (
            "Temporal interference stimulation (TIS) shows potential for treating a wide "
            "range of central nervous system disorders."
        ),
        "authors": "H. Bhatt, S. Bhaskaran, L. Lawrence",
        "year": 2025,
        "citations": 2,
        "study_type": "systematic review",
        "journal": "Frontiers in Human Neuroscience",
        "sjr_quartile": "Q2",
        "doi": "",
        "url": "https://consensus.app/papers/advances-temporal-interference-stimulation-scoping-review/",
        "conditions": ["general"],
        "topics": ["tis"],
    },
    {
        "title": (
            "The Duality of Astrocyte Neuromodulation: Astrocytes Sense Neuromodulators "
            "and Are Neuromodulators"
        ),
        "takeaway": (
            "Astrocytes mediate the effects of neuromodulators and also act as "
            "neuromodulators to optimize neural network homeostasis and brain function."
        ),
        "authors": "A. Bhatt, R. Bhaskaran, H. Lawrence",
        "year": 2025,
        "citations": 7,
        "study_type": "",
        "journal": "Journal of Neurochemistry",
        "sjr_quartile": "Q1",
        "doi": "",
        "url": "https://consensus.app/papers/the-duality-of-astrocyte-neuromodulation/",
        "conditions": ["general"],
        "topics": ["circuit_mechanisms"],
    },
]

# ── 2. LANDMARK PAPERS (> 100 citations) ──────────────────────────────────────
LANDMARK_PAPERS: list[dict] = [
    p for p in ALL_PAPERS if p["citations"] > 100
]

# ── 3. PAPERS BY CONDITION ────────────────────────────────────────────────────
# Each condition maps to papers where that condition appears in paper["conditions"].
# Lists are sorted by citations descending.

def _papers_for_condition(condition: str) -> list[dict]:
    return sorted(
        [p for p in ALL_PAPERS if condition in p["conditions"]],
        key=lambda x: x["citations"],
        reverse=True,
    )


PAPERS_BY_CONDITION: dict[str, list[dict]] = {
    "depression": _papers_for_condition("depression"),
    "alzheimers": _papers_for_condition("alzheimers"),
    "parkinsons": _papers_for_condition("parkinsons"),
    "epilepsy": _papers_for_condition("epilepsy"),
    "chronic_pain": _papers_for_condition("chronic_pain"),
    "tbi": _papers_for_condition("tbi"),
    "addiction": _papers_for_condition("addiction"),
    "bipolar": _papers_for_condition("bipolar"),
    "ocd": _papers_for_condition("ocd"),
    "adhd": _papers_for_condition("adhd"),
    "schizophrenia": _papers_for_condition("schizophrenia"),
    "general": _papers_for_condition("general"),
}

# ── 4. PAPERS BY TOPIC ────────────────────────────────────────────────────────
def _papers_for_topic(topic: str) -> list[dict]:
    return sorted(
        [p for p in ALL_PAPERS if topic in p["topics"]],
        key=lambda x: x["citations"],
        reverse=True,
    )


PAPERS_BY_TOPIC: dict[str, list[dict]] = {
    "connectomics": _papers_for_topic("connectomics"),
    "network_control_theory": _papers_for_topic("network_control_theory"),
    "tms": _papers_for_topic("tms"),
    "tdcs": _papers_for_topic("tdcs"),
    "dbs": _papers_for_topic("dbs"),
    "ultrasound": _papers_for_topic("ultrasound"),
    "tis": _papers_for_topic("tis"),
    "modular_networks": _papers_for_topic("modular_networks"),
    "default_mode_network": _papers_for_topic("default_mode_network"),
    "circuit_mechanisms": _papers_for_topic("circuit_mechanisms"),
}

# ── 5. FNON SUPPORTING PAPERS ─────────────────────────────────────────────────
# Papers that directly support the FNON (Functional Network Orientation
# Neuromodulation) framework: network-level effects, multi-network targeting,
# personalized/connectome-guided stimulation, DMN/CEN/SN/limbic interactions.

FNON_SUPPORTING_PAPERS: list[dict] = [
    p for p in ALL_PAPERS
    if any(t in p["topics"] for t in [
        "network_control_theory",
        "connectomics",
        "default_mode_network",
    ])
    or p["citations"] >= 100
]
FNON_SUPPORTING_PAPERS = sorted(
    FNON_SUPPORTING_PAPERS, key=lambda x: x["citations"], reverse=True
)


# ── 6. HELPERS ────────────────────────────────────────────────────────────────

def get_papers_for_condition(condition: str, min_citations: int = 0) -> list[dict]:
    """Return papers relevant to a condition, filtered by minimum citation count."""
    papers = PAPERS_BY_CONDITION.get(condition, [])
    if min_citations > 0:
        papers = [p for p in papers if p["citations"] >= min_citations]
    return papers


def get_top_papers(n: int = 10, min_citations: int = 50) -> list[dict]:
    """Return the top-n most-cited papers with at least min_citations citations."""
    filtered = [p for p in ALL_PAPERS if p["citations"] >= min_citations]
    filtered.sort(key=lambda x: x["citations"], reverse=True)
    return filtered[:n]


def format_citation(paper: dict) -> str:
    """Return an APA-style citation string for a paper dict."""
    authors = paper.get("authors", "Unknown authors")
    year = paper.get("year", "n.d.")
    title = paper.get("title", "Untitled")
    journal = paper.get("journal", "")
    doi = paper.get("doi", "")
    # Abbreviate long author strings to first author + et al.
    if "," in authors:
        first_author = authors.split(",")[0].strip()
        author_str = f"{first_author} et al."
    else:
        author_str = authors
    citation = f"{author_str} ({year}). {title}."
    if journal:
        citation += f" {journal}."
    if doi:
        citation += f" https://doi.org/{doi}"
    return citation


def get_fnon_evidence_paragraph(condition: str) -> str:
    """
    Return a 2-3 sentence evidence paragraph with inline citations supporting
    the network basis of neuromodulation for the given condition.
    Paragraphs are hardcoded to ensure precise, clinically reviewed prose.
    """
    paragraphs: dict[str, str] = {
        "depression": (
            "Network neuroscience has reframed MDD as a large-scale connectivity "
            "disorder rather than a localized lesion. Resting-state and task-based "
            "neuroimaging consistently implicates disrupted default-mode network (DMN) "
            "hyperactivity, reduced DMN-CEN anti-correlation, DLPFC hypoactivation, and "
            "aberrant salience network gating as the core circuit signatures of depression "
            "[A brain network model for depression, Mulders et al. 2018, 267 citations]. "
            "Non-invasive neuromodulation targeting the DLPFC exerts antidepressant effects "
            "through distributed network modulation rather than focal tissue change alone, "
            "with personalized connectome-guided targeting further improving outcomes "
            "[Changing Brain Networks Through Non-invasive Neuromodulation, To et al. 2018, "
            "113 citations; Neuromodulation for treatment-resistant depression, 2023, "
            "19 citations]."
        ),
        "alzheimers": (
            "Alzheimer's disease manifests as progressive disconnection across the default "
            "mode, salience, and central executive networks long before frank neuronal loss "
            "is detectable clinically. Connectomic neuromodulation meta-analyses demonstrate "
            "that DBS targeting the fornix and subgenual cingulate engages these distributed "
            "circuits — improving cognition particularly in patients aged ≥65 — while "
            "non-invasive modalities modulate the same DMN-SN-CEN triad through cortical "
            "entry points [Connectomic neuromodulation for Alzheimer's disease, Cheyuo et al. "
            "2022, 11 citations]. Biologically annotated connectomic models now reveal that "
            "hippocampal neuromodulatory tone and interneuron integrity are essential "
            "mechanistic targets for any effective intervention strategy "
            "[Towards a biologically annotated brain connectome, 2023, 69 citations]."
        ),
        "parkinsons": (
            "Parkinson's disease involves pathological synchrony in the basal ganglia-"
            "thalamocortical motor loop, with beta-band oscillations in the subthalamic "
            "nucleus propagating to suppress voluntary movement initiation. DBS of the STN "
            "or GPi disrupts this hypersynchrony by modulating the broader cortico-basal "
            "ganglia circuit rather than simply lesioning the target nucleus "
            "[Networking brainstem and basal ganglia circuits for movement, 2022, "
            "142 citations]. Recent evidence shows that DBS and dopamine converge on "
            "shared pathway-specific network mechanisms — with DBS effectively mimicking "
            "dopaminergic restoration at the network level — supporting a network rather "
            "than chemical replacement model for its therapeutic mechanism "
            "[Shared pathway-specific network mechanisms of dopamine and DBS, 2025, "
            "27 citations]."
        ),
        "epilepsy": (
            "Epilepsy is now understood as a disorder of dynamic brain networks, in which "
            "pathological nodes and hypersynchronous propagation pathways determine both "
            "seizure onset and spread. Network-guided neuromodulation approaches use "
            "multi-modal connectomic mapping (diffusion MRI, resting-state fMRI, iEEG) "
            "to identify individualized propagation points — particularly thalamic nuclei "
            "including the anterior nucleus (ANT) and centromedian nucleus (CM) — as "
            "high-leverage stimulation targets [Towards network-guided neuromodulation for "
            "epilepsy, Piper et al. 2022, 168 citations]. Computational models integrating "
            "intracranial EEG data can further localize optimal targets in drug-resistant "
            "cases, and neurostimulation stabilizes network dynamics by disrupting "
            "seizure-like oscillatory transitions [Neurostimulation stabilizes spiking "
            "neural networks, 2020, 26 citations]."
        ),
        "chronic_pain": (
            "Chronic pain involves maladaptive plasticity across ascending nociceptive "
            "circuits and descending modulatory networks, with the anterior cingulate, "
            "insula, and medial prefrontal cortex forming a core pain matrix that becomes "
            "pathologically sensitized. Cellular circuit analysis indicates that cortical "
            "and subcortical neuromodulation can interrupt dysfunctional gain in these "
            "pathways [Cellular circuits in the brain and their modulation in acute and "
            "chronic pain, 2020, 269 citations]. Network-level connectomic analysis of "
            "neuromodulation targets for pain demonstrates that personalised stimulation "
            "site selection — grounded in individual functional connectivity maps — "
            "outperforms anatomically fixed targeting "
            "[Network targets for therapeutic brain stimulation for pain, 2023, "
            "16 citations]."
        ),
        "tbi": (
            "Traumatic brain injury disrupts white-matter connectivity across fronto-parietal "
            "and default-mode networks, producing widespread diaschisis that extends far "
            "beyond the primary injury site. Neuromodulation approaches targeting surviving "
            "network nodes can promote compensatory plasticity and functional reorganization. "
            "Network control theory frameworks, which identify controllable nodes within "
            "the individual connectome, provide a principled basis for selecting stimulation "
            "targets that maximise whole-network re-engagement after TBI "
            "[Stimulation-Based Control of Dynamic Brain Networks, 2016, 286 citations; "
            "Opportunities of connectomic neuromodulation, Horn & Fox 2020, 148 citations]."
        ),
        "addiction": (
            "Addiction involves dysregulation of salience, reward, and prefrontal control "
            "circuits, with habitual drug-seeking emerging from impaired top-down regulation "
            "of mesolimbic pathways. A salience network framework for addiction neuroscience "
            "demonstrates how the same large-scale network structures identified in human "
            "neuroimaging map onto circuit-level mechanisms — connecting the anterior insula, "
            "amygdala, and anterior cingulate as core nodes "
            "[Connecting Circuits with Networks in Addiction Neuroscience: A Salience Network "
            "Perspective, 2023, 22 citations]. Non-invasive neuromodulation targeting "
            "prefrontal nodes modulates both the salience network and downstream mesolimbic "
            "activity, offering a network-level rationale for therapeutic stimulation "
            "[Changing Brain Networks Through Non-invasive Neuromodulation, To et al. 2018, "
            "113 citations]."
        ),
        "bipolar": (
            "Bipolar disorder is characterised by fronto-limbic network dysregulation, with "
            "neuroimaging revealing disrupted connectivity between the prefrontal cortex, "
            "amygdala, and anterior cingulate during both manic and depressive phases. "
            "Network-based treatment strategies targeting these fronto-limbic circuits — "
            "including rTMS to DLPFC and emerging DBS approaches — draw on the understanding "
            "that mood state transitions reflect dynamic shifts in intrinsic network balance "
            "[Neural network of bipolar disorder, 2022, 62 citations]. The same modular "
            "network principles that govern other large-scale connectivity disorders apply "
            "to bipolar disorder, suggesting shared circuit intervention principles "
            "[Modular Brain Networks, 2016, 1192 citations]."
        ),
        "ocd": (
            "Obsessive-compulsive disorder involves hyperactivity in the cortico-striato-"
            "thalamo-cortical (CSTC) loop, with excessive drive from the orbitofrontal "
            "cortex and anterior cingulate pushing behaviour into repetitive routines. "
            "DBS targeting the anterior limb of the internal capsule, subthalamic nucleus, "
            "or nucleus accumbens modulates this circuit by restoring inhibitory balance "
            "within the loop [Concerning neuromodulation via DBS for neuropsychiatric "
            "disorders, 2024, 8 citations]. Non-invasive neuromodulation at the SMA and "
            "DLPFC similarly targets upstream nodes of the CSTC circuit "
            "[Neuromodulation techniques — from non-invasive to DBS, 2024, 63 citations]."
        ),
        "adhd": (
            "ADHD involves distributed hypofunction of fronto-parietal attention and "
            "default-mode networks, with the DLPFC, posterior parietal cortex, and anterior "
            "cingulate showing reduced activation during executive tasks alongside "
            "diminished anticorrelation between the task-positive and default-mode networks. "
            "Neuromodulation can selectively engage these circuits: tDCS and TMS targeting "
            "the DLPFC improve attention and working memory through network-level "
            "entrainment [Neuromodulation of Attention, 2018, 289 citations]. Causal "
            "circuit-mapping approaches using neuromodulation are increasingly used to "
            "map the ADHD symptom profile directly onto brain network dysfunction "
            "[Using causal methods to map symptoms to brain circuits, 2022, 5 citations]."
        ),
        "schizophrenia": (
            "Schizophrenia involves profound dysconnectivity across cortical association "
            "networks — particularly between frontal, temporal, and parietal regions — with "
            "disrupted thalamocortical gating implicated in positive symptom generation. "
            "Neuromodulation approaches target the DLPFC, auditory cortex, and cerebellum "
            "as network entry points, aiming to restore inter-regional synchrony and "
            "reduce aberrant salience attribution [Brain Neuromodulation Techniques, 2016, "
            "85 citations]. Physiologically informed neuromodulation protocols that account "
            "for individual network biomarkers hold particular promise for improving "
            "treatment response in schizophrenia [Physiologically informed neuromodulation, "
            "2021, 25 citations]."
        ),
        "general": (
            "The emerging field of network neuroscience demonstrates that brain function "
            "arises from the dynamic interplay of modular, hierarchically organized networks "
            "rather than isolated regions [Modular Brain Networks, 2016, 1192 citations]. "
            "Stimulation-based control of these networks — informed by connectomics, network "
            "control theory, and real-time biomarker feedback — represents the theoretical "
            "foundation for next-generation precision neuromodulation [Stimulation-Based "
            "Control of Dynamic Brain Networks, 2016, 286 citations; Opportunities of "
            "connectomic neuromodulation, Horn & Fox 2020, 148 citations]."
        ),
    }
    return paragraphs.get(
        condition,
        (
            f"Evidence for the network basis of neuromodulation in {condition} is "
            "available in the ALL_PAPERS and PAPERS_BY_CONDITION data structures. "
            "See get_papers_for_condition() for relevant citations."
        ),
    )
