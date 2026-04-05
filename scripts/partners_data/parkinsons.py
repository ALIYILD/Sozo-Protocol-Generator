"""
Partners-tier All-In-One Protocol data — parkinsons.
Auto-split from partners_all_in_one_data.py. Edit this file to modify parkinsons data.
"""
from ._shared import _plato_programs_default  # noqa: F401

PARTNERS_CONDITIONS = {}

PARTNERS_CONDITIONS['parkinsons'] = {
    'display_name': "Parkinson's Disease",
    'short': "Parkinson's",
    'condition_slug': 'parkinsons',
    'icd10': 'G20',
    'tps_warning': (
        "TPS use in Parkinson\u2019s Disease is INVESTIGATIONAL / OFF-LABEL. "
        "NEUROLITH\u00ae is CE-marked for musculoskeletal indications only. Evidence for PD "
        "motor and cognitive symptom modulation is emerging (pilot RCTs, open-label studies). "
        "Informed consent and Doctor supervision mandatory."
    ),
    'fnon_classification': 'Primary Motor Network hypoactivation / basal ganglia-thalamic circuit disruption / CEN hypo / Executive Network impairment',
    'fnon_montage_selection': [
        ['Motor predominant (M1/SMA)', 'HDCstim tDCS C3/C4 anodes bilateral + Cz'],
        ['Cognitive / MCI', 'HDCstim F3/F4 anodes / Oz cathode'],
        ['Gait freezing', 'tDCS Cz anode (SMA) + F3/F4 DLPFC'],
        ['Depression comorbid', 'tDCS F3 anode / F4 cathode + CES'],
        ['Autonomic dysregulation', 'tDCS C3/C4 + taVNS extended'],
    ],
    'tps': [
        ['T1', 'M1 motor facilitation', 'C3/C4 bilateral M1', '0.25 mJ/mm²', '1000 pulses', 'Evidence B'],
        ['T2', 'SMA gait initiation', 'Cz / SMA-proxy', '0.25 mJ/mm²', '1000 pulses', 'Evidence B'],
        ['T3', 'DLPFC cognitive', 'F3/F4 bilateral', '0.25 mJ/mm²', '1000 pulses', 'Evidence B'],
        ['T4', 'Cerebellum coordination', 'Oz / cerebellar proxy', '0.20 mJ/mm²', '800 pulses', 'Emerging'],
        ['T5', 'Autonomic/insula', 'C3 insula proxy', '0.20 mJ/mm²', '800 pulses', 'Emerging'],
    ],
    'fnon_tps': [
        ['FT1', 'Motor network upregulation', 'Primary Motor Network hypo', 'M1 C3/C4 + SMA Cz', 'Motor circuit reactivation', '0.25 mJ/mm²', '1000 pulses', '12 sessions'],
        ['FT2', 'Executive restore', 'Executive Control Network hypo', 'DLPFC F3/F4 bilateral', 'Prefrontal executive activation', '0.25 mJ/mm²', '1000 pulses', '12 sessions'],
        ['FT3', 'Attention upregulate', 'Dorsal Attention Network', 'F4/P4 bilateral', 'Attention and visuospatial', '0.22 mJ/mm²', '1000 pulses', '10 sessions'],
        ['FT4', 'Gait freezing circuit', 'SMA-basal ganglia', 'Cz + F3 bilateral', 'Freezing of gait reduce', '0.25 mJ/mm²', '1000 pulses', '12 sessions'],
        ['FT5', 'DMN normalize', 'DMN disrupted PD-MCI', 'mPFC + PCC bilateral', 'Default mode reset', '0.20 mJ/mm²', '800 pulses', '10 sessions'],
        ['FT6', 'Mood-motor unified', 'LIMBIC-motor overlap', 'DLPFC L + C3 anode', 'PD depression motor unified', '0.22 mJ/mm²', '1000 pulses', '12 sessions'],
        ['FT7', 'Autonomic balance', 'Autonomic dysregulation', 'Insula C3 + C4', 'HRV and vagal tone', '0.20 mJ/mm²', '800 pulses', '10 sessions'],
        ['FT8', 'Salience network', 'Salience Network altered', 'Cz + insula C3', 'SN recalibration', '0.22 mJ/mm²', '1000 pulses', '10 sessions'],
        ['FT9', 'Comprehensive PD', 'Multi-network', 'Rotating M1+SMA+DLPFC', 'Holistic PD protocol', '0.25 mJ/mm²', '1200 pulses', '12 sessions'],
    ],
    'tdcs': [
        ['C1', 'M1 bilateral motor', 'C3/C4 anodes / Oz cathode', '2 mA', '20 min', 'Evidence A'],
        ['C2', 'Anodal L-DLPFC cognitive', 'F3 anode / Fp2 cathode', '2 mA', '20 min', 'Evidence B'],
        ['C3', 'SMA gait/initiation', 'Cz anode / Oz cathode', '2 mA', '20 min', 'Evidence B'],
        ['C4', 'Bilateral DLPFC cognitive', 'F3/F4 anodes / Oz cathode', '2 mA', '20 min', 'Evidence B'],
        ['C5', 'Motor + cognitive unified', 'C3/F3 anodes / Oz cathode', '2 mA', '20 min', 'Emerging'],
        ['C6', 'Depression PD', 'F3 anode / F4 cathode', '2 mA', '20 min', 'Evidence B'],
        ['C7', 'Fatigue PD', 'F3/Cz anodes / Oz cathode', '2 mA', '20 min', 'Emerging'],
        ['C8', 'Tremor bilateral', 'C3/C4 anodes / Oz cathode', '1.5 mA', '20 min', 'Emerging'],
    ],
    'fnon_tdcs': [
        ['F1', 'Motor network activate', 'Primary Motor Network hypo', 'C3/C4 anodes / Oz cathode', 'M1 bilateral facilitation', '2 mA', '20 min'],
        ['F2', 'Executive restore', 'Executive Control Network hypo', 'F3/F4 anodes / Oz cathode', 'DLPFC bilateral activation', '2 mA', '20 min'],
        ['F3', 'SMA gait circuit', 'SMA hypoactivation', 'Cz anode / Oz cathode', 'Gait initiation support', '2 mA', '20 min'],
        ['F4', 'Attention dorsal', 'Dorsal Attention Network', 'F4/P4 anodes / Oz cathode', 'Visuospatial attention', '2 mA', '20 min'],
        ['F5', 'Mood-motor PD', 'LIMBIC-motor overlap', 'F3 anode / F4 cathode', 'Depression + motor unified', '2 mA', '20 min'],
        ['F6', 'Autonomic vagal', 'Autonomic dysregulation', 'C3 anode / shoulder cathode', 'HRV and POTS support', '2 mA', '20 min'],
    ],
    'plato': [
        ['C1-PS', 'Motor facilitation', 'Parkinson\'s motor protocol', 'F3+C3', '1.6 mA', '20 min', 'Motor predominant PD'],
        ['C2-PS', 'Cognitive PD', 'Focus variant', 'F3/F4', '1.4 mA', '20 min', 'PD-MCI / cognitive'],
        ['C3-PS', 'Mood + motor', 'Mood+ variant', 'F3/C3', '1.4 mA', '20 min', 'Depression-motor PD'],
        ['C4-PS', 'Gait support', 'Performance variant', 'Cz/F3', '1.4 mA', '20 min', 'Gait freezing phenotype'],
        ['C5-PS', 'Fatigue PD', 'Energy variant', 'F3/F4', '1.4 mA', '20 min', 'Fatigue-dominant PD'],
        ['C6-PS', 'Autonomic balance', 'Calm variant', 'C3/C4', '1.4 mA', '20 min', 'Autonomic dysregulation'],
        ['C7-PS', 'Sleep PD', 'Sleep variant', 'Fp1/Cz', '1.2 mA', '20 min', 'PD sleep disturbance'],
        ['C8-PS', 'Tremor motor', 'Performance variant', 'C3/C4', '1.6 mA', '20 min', 'Tremor predominant'],
    ],
    'fnon_plato': [
        ['FP1', 'Motor network', 'Primary Motor Network hypo', 'Performance variant', 'C3/C4', '1.6 mA', '20 min'],
        ['FP2', 'Executive PD', 'Executive Control Network hypo', 'Focus variant', 'F3/F4', '1.4 mA', '20 min'],
        ['FP3', 'Gait SMA', 'SMA hypoactivation', 'Performance variant', 'Cz/F3', '1.4 mA', '20 min'],
        ['FP4', 'Mood PD', 'LIMBIC-motor overlap', 'Mood+ variant', 'F3/C3', '1.4 mA', '20 min'],
        ['FP5', 'Autonomic PD', 'Autonomic dysregulation', 'Calm variant', 'C3/C4', '1.4 mA', '20 min'],
        ['FP6', 'Attention PD', 'Dorsal Attention Network', 'Focus variant', 'F4/P4', '1.4 mA', '20 min'],
    ],
    'phenotypes': [
        {
            'code': 'P1', 'name': 'Motor Predominant (Tremor / Rigidity / Bradykinesia)',
            'sozo_bar': ['taVNS 30 min', 'tDCS C3/C4 bilateral', 'TPS M1+SMA', 'Motor rehab tasks'],
            'card_left': ['Network: Primary Motor Network hypo + SMA circuit', 'Key target: M1, SMA, basal ganglia', 'Priority: Motor facilitation'],
            'card_right': ['TPS: T1 + FT1', 'tDCS: C1/F1', 'PlatoScience: C1-PS/FP1', 'taVNS: 30 min'],
            'brain_targets': [
                ['M1 (C3/C4)', 'Primary motor cortex', 'Activate', 'T1 / C1 / FP1', 'Evidence A'],
                ['SMA (Cz)', 'Motor initiation', 'Activate', 'T2 / C3 / FP3', 'Evidence B'],
                ['DLPFC (F3/F4)', 'Cognitive-motor', 'Upregulate', 'T3 / C2', 'Evidence B'],
                ['Cerebellum', 'Coordination', 'Modulate', 'T4 / TPS', 'Emerging'],
                ['Basal ganglia', 'Beta-band suppression', 'Indirect modulation', 'taVNS protocol', 'Emerging'],
            ],
            'combinations': [
                ['taVNS 30 min', 'tDCS C3/C4 bilateral', 'TPS M1+SMA', 'Gait + balance exercises'],
                ['CES 20 min', 'PlatoScience C1-PS', 'TPS M1 bilateral', 'Upper limb motor tasks'],
                ['taVNS 20 min', 'tDCS C1', 'TPS SMA Cz', 'Gait initiation drills'],
                ['CES 20 min', 'tDCS C3', 'TPS motor unified', 'Physiotherapy concurrent'],
            ],
            'task_pairing': 'Gait training, balance exercises, upper limb motor tasks, physiotherapy concurrent with stimulation.',
            'fnon_hypothesis': 'PD motor predominant reflects basal ganglia-thalamic circuit failure causing beta-band excess and M1/SMA hypoactivation. TPS + tDCS facilitate motor cortex excitability.',
        },
        {
            'code': 'P2', 'name': 'Cognitive Predominant (MCI / Dementia Risk)',
            'sozo_bar': ['taVNS 30 min', 'tDCS F3/F4 bilateral', 'TPS DLPFC+PPC', 'Cognitive rehab tasks'],
            'card_left': ['Network: Executive Control Network hypo + DMN disrupted', 'Key target: DLPFC, PPC, hippocampus', 'Priority: Executive + memory'],
            'card_right': ['TPS: T3 + FT2', 'tDCS: C4/F2', 'PlatoScience: C2-PS/FP2', 'taVNS: 30 min'],
            'brain_targets': [
                ['DLPFC (F3/F4)', 'Executive control', 'Activate', 'T3 / C4 / FP2', 'Evidence B'],
                ['PPC (P3/P4)', 'Visuospatial', 'Upregulate', 'T3 / F4', 'Evidence B'],
                ['Hippocampus', 'Memory', 'Support via taVNS', 'taVNS protocol', 'Emerging'],
                ['ACC (Fz)', 'Attention', 'Modulate', 'T4 / C3', 'Emerging'],
                ['mPFC', 'Self-referential / DMN', 'Normalize', 'FT5 / TPS', 'Emerging'],
            ],
            'combinations': [
                ['taVNS 30 min', 'tDCS F3/F4', 'TPS DLPFC', 'N-back cognitive training'],
                ['CES 20 min', 'PlatoScience C2-PS', 'TPS PPC', 'Visuospatial exercises'],
                ['taVNS 30 min', 'tDCS C4', 'TPS bilateral DLPFC', 'Memory diary tasks'],
                ['CES 20 min', 'tDCS F4', 'TPS PPC+DLPFC', 'Cognitive rehabilitation session'],
            ],
            'task_pairing': 'Cognitive rehabilitation tasks: N-back, verbal fluency, visuospatial exercises, memory training during stimulation.',
            'fnon_hypothesis': 'PD-MCI reflects DLPFC-PPC Executive Control Network hypoactivation with disrupted hippocampal memory circuits. Bilateral DLPFC tDCS + TPS restores cognitive network function.',
        },
        {
            'code': 'P3', 'name': 'Autonomic Predominant',
            'sozo_bar': ['taVNS 40 min', 'tDCS C3/C4 bilateral', 'TPS insula', 'HRV biofeedback'],
            'card_left': ['Network: Autonomic dysregulation + insula hypo', 'Key target: Insula, vagal axis, ACC', 'Priority: HRV restoration + orthostatic'],
            'card_right': ['TPS: T5 + FT7', 'tDCS: C7/F6', 'PlatoScience: C6-PS/FP5', 'taVNS: 40 min'],
            'brain_targets': [
                ['Insula (C3/C4)', 'Autonomic control', 'Normalize', 'T5 / C5', 'Emerging'],
                ['ACC (Fz)', 'Autonomic monitoring', 'Upregulate', 'T4 / C3', 'Emerging'],
                ['Brainstem NTS', 'Vagal output', 'Stimulate (taVNS)', 'taVNS extended', 'Emerging'],
                ['DLPFC', 'Cognitive-autonomic', 'Balance', 'T3 / C2', 'Evidence B'],
                ['M1 (C3/C4)', 'Motor-autonomic', 'Facilitate', 'T1 / C1', 'Evidence A'],
            ],
            'combinations': [
                ['taVNS 40 min', 'tDCS C3/C4', 'TPS insula', 'HRV biofeedback 20 min'],
                ['CES 20 min', 'PlatoScience C6-PS', 'TPS ACC', 'Paced breathing 6 cpm'],
                ['taVNS 40 min', 'tDCS F6', 'TPS insula bilateral', 'Autonomic rehab protocol'],
                ['CES 20 min', 'tDCS C5', 'TPS autonomic proxy', 'Orthostatic training'],
            ],
            'task_pairing': 'HRV biofeedback, paced breathing, orthostatic training, autonomic regulation exercises.',
            'fnon_hypothesis': 'PD autonomic predominant reflects brainstem-vagal circuit degeneration (Lewy body pathology stage 1-2). taVNS extended protocol targets vagal-cardiac axis directly.',
        },
    ],
    'task_pairing_rows': [
        ['Gait training', 'During tDCS', 'Motor rehab', 'P1'],
        ['Physiotherapy', 'Post-TPS', 'Motor', 'P1'],
        ['Cognitive training', 'During tDCS', 'Cognitive', 'P2'],
        ['N-back / verbal fluency', 'During tDCS', 'Cognitive', 'P2'],
        ['HRV biofeedback', 'During taVNS', 'Autonomic', 'P3'],
        ['Paced breathing', 'During taVNS', 'Autonomic', 'P3'],
        ['Balance exercises', 'Post-TPS', 'Motor', 'P1, P3'],
        ['Speech therapy', 'Post-session', 'Communication', 'All'],
    ],
    'followup_rows': [
        ['Week 2', 'UPDRS-III, H&Y', 'Motor status', 'Adjust motor protocol if <20% change'],
        ['Week 4', 'UPDRS-III, MoCA, PDQ-39', 'Motor + cognitive + QoL', 'Add cognitive track if MoCA <26'],
        ['Week 6', 'Full battery + NMS', 'Non-motor symptoms', 'Phase 2 intensification'],
        ['Week 10', 'UPDRS-III, PDQ-39, QoL', 'Function + motor', 'Maintenance planning'],
        ['Month 4', 'Full reassessment', 'All domains', 'Maintenance protocol decision'],
        ['Month 6', 'UPDRS-III, MoCA, PDQ-39', 'Long-term outcome', 'Annual review schedule'],
    ],
    'plato_programs': _plato_programs_default(3, 3, 3, 4, 4, 4, 2, 5, 4),
}
