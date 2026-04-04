"""
Generate 4 assessment reference YAMLs + enrich scales_catalog.yaml
from SOZO_Assessments_Master.xlsx
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl

XLSX = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\SOZO_Assessments_Master.xlsx'
REF = r'C:\Users\yildi\sozo_generator\data\reference'

wb = openpyxl.load_workbook(XLSX, read_only=True)

def get_rows(sheet):
    ws = wb[sheet]
    data = list(ws.iter_rows(min_row=2, values_only=True))
    header = [str(h) if h else f'col{i}' for i, h in enumerate(data[0])]
    return header, [dict(zip(header, r)) for r in data[1:] if any(v is not None for v in r)]

def s(v, maxlen=500):
    if v is None: return 'null'
    t = str(v).strip()[:maxlen]
    if not t: return 'null'
    t2 = t.replace('\\', '\\\\').replace('"', '\\"')
    return '"' + t2 + '"'

def bl(v, indent=4):
    if not v: return 'null'
    t = str(v).strip().replace('"', "'")
    return '>\n' + ' '*indent + t

def slist(v):
    if not v: return '[]'
    items = [x.strip() for x in str(v).split(';') if x.strip()]
    if len(items) <= 1:
        items = [x.strip() for x in str(v).split(',') if x.strip()]
    return '[' + ', '.join('"' + i.replace('"',"'") + '"' for i in items) + ']'

SLUG_MAP = {
    'Depression (MDD)': 'depression',
    "Alzheimer's Disease / Dementia": 'alzheimers',
    "Parkinson's Disease": 'parkinsons',
    'Anxiety Disorders (GAD/PD/SA)': 'anxiety',
    'ADHD': 'adhd',
    'Autism Spectrum Disorder (ASD)': 'asd',
    'Chronic Pain / Fibromyalgia': 'chronic_pain',
    'PTSD': 'ptsd',
    'OCD': 'ocd',
    'Multiple Sclerosis (MS)': 'ms',
    'Long COVID / PACS': 'long_covid',
    'Tinnitus': 'tinnitus',
    'Insomnia / Sleep Disorders': 'insomnia',
    'Stroke Rehabilitation': 'stroke_rehab',
    'TBI (Mild-Moderate)': 'tbi',
    'Schizophrenia': 'schizophrenia',
    'Epilepsy (drug-resistant)': 'epilepsy',
    'Essential Tremor': 'essential_tremor',
    'MCI (Mild Cognitive Impairment)': 'mci',
    'Bipolar Disorder': 'bipolar',
    'Eating Disorders': 'eating_disorders',
    'Addiction / Substance Use': 'addiction',
}

def slug(v):
    return SLUG_MAP.get(str(v).strip(), str(v).strip().lower().replace(' ', '_').replace('/', '_').replace("'", ''))

# ── 1. assessment_master.yaml ──────────────────────────────────────────────────
header, rows = get_rows('Assessment_Master')
lines = [
    '# SOZO Brain Center — Assessment Master Reference',
    '# Source: SOZO_Assessments_Master.xlsx, April 2026',
    '# 22 conditions x clinical scales x qEEG x brain regions x networks',
    '',
    'meta:',
    f'  total_conditions: {len(rows)}',
    '  source: "SOZO_Assessments_Master.xlsx"',
    '  date: "2026-04-04"',
    '',
    'conditions:',
]

for r in rows:
    cond = r.get('Condition')
    if not cond: continue
    sl = slug(cond)
    cat = r.get('Category')
    scales = r.get('Primary Clinical Scales (validated)')
    neuro = r.get('Neuropsychological Battery')
    qeeg_bands = r.get('qEEG Key Bands & Patterns')
    qeeg_elec = r.get('Key qEEG Electrodes (10-20 system)')
    qeeg_metrics = r.get('Key qEEG Metrics')
    brain_regions = r.get('Brain Regions Affected')
    network = r.get('Primary Network Disrupted')
    neuroimaging = r.get('Neuroimaging')
    physio = r.get('Physiological Assessments')
    functional = r.get('Functional / Behavioural Assessments')
    fnon_target = r.get('FNON qEEG Treatment Target')
    rationale = r.get('Assessment Clinical Rationale')

    lines.append(f'  {sl}:')
    lines.append(f'    condition: {s(cond)}')
    lines.append(f'    category: {s(cat)}')
    lines.append(f'    primary_clinical_scales: {bl(scales)}')
    lines.append(f'    neuropsychological_battery: {bl(neuro)}')
    lines.append(f'    qeeg_key_bands: {bl(qeeg_bands)}')
    lines.append(f'    qeeg_key_electrodes: {s(qeeg_elec)}')
    lines.append(f'    qeeg_key_metrics: {bl(qeeg_metrics)}')
    lines.append(f'    brain_regions_affected: {bl(brain_regions)}')
    lines.append(f'    primary_network_disrupted: {bl(network)}')
    lines.append(f'    neuroimaging: {bl(neuroimaging)}')
    lines.append(f'    physiological_assessments: {bl(physio)}')
    lines.append(f'    functional_assessments: {bl(functional)}')
    lines.append(f'    fnon_qeeg_treatment_target: {bl(fnon_target)}')
    lines.append(f'    assessment_rationale: {bl(rationale)}')

with open(os.path.join(REF, 'assessment_master.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print(f'assessment_master.yaml: {len(rows)} conditions')

# ── 2. conditions_qeeg_profiles.yaml ──────────────────────────────────────────
header2, rows2 = get_rows('Conditions_qEEG')
lines2 = [
    '# SOZO Brain Center — Conditions qEEG Profiles',
    '# Source: SOZO_Assessments_Master.xlsx, April 2026',
    '# Detailed qEEG signatures: eyes-open/closed, event-related, pathological thresholds, response biomarkers',
    '',
    'profiles:',
]
for r in rows2:
    cond = r.get('Condition')
    if not cond: continue
    sl = slug(cond)
    lines2.append(f'  {sl}:')
    lines2.append(f'    condition: {s(cond)}')
    lines2.append(f'    primary_qeeg_signature: {bl(r.get("Primary qEEG Signature"), 4)}')
    lines2.append(f'    key_electrodes: {s(r.get("Key Electrodes"))}')
    lines2.append(f'    key_metrics: {bl(r.get("Key qEEG Metrics"), 4)}')
    lines2.append(f'    eyes_open_findings: {bl(r.get("Eyes-Open Findings"), 4)}')
    lines2.append(f'    eyes_closed_findings: {bl(r.get("Eyes-Closed Findings"), 4)}')
    lines2.append(f'    event_related_paradigm: {bl(r.get("Event-Related Paradigm"), 4)}')
    lines2.append(f'    pathological_threshold: {bl(r.get("Pathological Threshold"), 4)}')
    lines2.append(f'    fnon_treatment_target: {bl(r.get("FNON Treatment Target"), 4)}')
    lines2.append(f'    response_biomarker: {bl(r.get("Response Biomarker"), 4)}')

with open(os.path.join(REF, 'conditions_qeeg_profiles.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines2) + '\n')
print(f'conditions_qeeg_profiles.yaml: {len(rows2)} conditions')

# ── 3. clinical_scales_schedule.yaml ──────────────────────────────────────────
header3, rows3 = get_rows('Clinical_Scales')
lines3 = [
    '# SOZO Brain Center — Clinical Scales Schedule',
    '# Source: SOZO_Assessments_Master.xlsx, April 2026',
    '# Validated scales with follow-up schedule, comorbidity/safety screens, score thresholds',
    '',
    'schedules:',
]
for r in rows3:
    cond = r.get('Condition')
    if not cond: continue
    sl = slug(cond)
    lines3.append(f'  {sl}:')
    lines3.append(f'    condition: {s(cond)}')
    lines3.append(f'    category: {s(r.get("Category"))}')
    lines3.append(f'    primary_scale: {bl(r.get("Primary Scale (main outcome)"), 4)}')
    lines3.append(f'    screening_scales: {bl(r.get("Screening Scale(s)"), 4)}')
    lines3.append(f'    severity_staging_scale: {bl(r.get("Severity/Staging Scale"), 4)}')
    lines3.append(f'    qol_function_scale: {bl(r.get("Quality of Life / Function Scale"), 4)}')
    lines3.append(f'    follow_up_frequency: {bl(r.get("Follow-up Frequency"), 4)}')
    lines3.append(f'    comorbidity_screens: {bl(r.get("Comorbidity Screens"), 4)}')
    lines3.append(f'    safety_screens: {bl(r.get("Safety Screens"), 4)}')
    lines3.append(f'    score_thresholds: {bl(r.get("Score Thresholds & Clinical Interpretation"), 4)}')

with open(os.path.join(REF, 'clinical_scales_schedule.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines3) + '\n')
print(f'clinical_scales_schedule.yaml: {len(rows3)} conditions')

# ── 4. network_assessment_matrix.yaml ─────────────────────────────────────────
header4, rows4 = get_rows('Network_Assessment')
NET_SLUG = {
    'Default Mode Network': 'dmn',
    'Executive Control Network': 'ecn',
    'Salience Network': 'sn',
    'Sensorimotor Network': 'smn',
    'Limbic Network': 'ln',
    'Dorsal Attention Network': 'dan',
    'Visual Network': 'visn',
    'Auditory Network': 'audn',
    'Language Network': 'langn',
    'Reward / Mesolimbic': 'reward',
    'Frontoparietal Control Network': 'fpcn',
    'Cerebellar-Cortical Network': 'ccn',
    'Pain Matrix / Network': 'pmn',
}
lines4 = [
    '# SOZO Brain Center — Network → Assessment Matrix',
    '# Source: SOZO_Assessments_Master.xlsx, April 2026',
    '# Brain network x disorders x assessments x FNON treatment',
    '',
    'networks:',
]
for r in rows4:
    net = r.get('Network')
    if not net: continue
    nslug = NET_SLUG.get(str(net).strip(), str(net).strip().lower().replace(' ', '_').replace('/', '_'))
    abbrev = r.get('Abbreviation')
    eeg_nodes = r.get('Primary EEG Nodes (10-20)')
    qeeg_sig = r.get('Key qEEG Signature')
    disorders = r.get('Associated Disorders (primary)')
    primary_scale = r.get('Primary Clinical Scale')
    neuropsych = r.get('Primary Neuropsych Test')
    qeeg_bm = r.get('Primary qEEG Biomarker')
    physio = r.get('Primary Physiological Test')
    fnon = r.get('FNON Treatment Approach')
    evidence = r.get('Evidence Modalities')

    lines4.append(f'  {nslug}:')
    lines4.append(f'    network: {s(net)}')
    lines4.append(f'    abbreviation: {s(abbrev)}')
    lines4.append(f'    eeg_nodes: {s(eeg_nodes)}')
    lines4.append(f'    qeeg_signature: {bl(qeeg_sig, 4)}')
    lines4.append(f'    associated_disorders: {bl(disorders, 4)}')
    lines4.append(f'    primary_clinical_scale: {bl(primary_scale, 4)}')
    lines4.append(f'    primary_neuropsych_test: {bl(neuropsych, 4)}')
    lines4.append(f'    primary_qeeg_biomarker: {bl(qeeg_bm, 4)}')
    lines4.append(f'    primary_physiological_test: {bl(physio, 4)}')
    lines4.append(f'    fnon_treatment_approach: {bl(fnon, 4)}')
    lines4.append(f'    evidence_modalities: {s(evidence)}')

with open(os.path.join(REF, 'network_assessment_matrix.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines4) + '\n')
print(f'network_assessment_matrix.yaml: {len(rows4)} networks')

# ── 5. region_eeg_network.yaml ────────────────────────────────────────────────
header5, rows5 = get_rows('Region_EEG_Network')
lines5 = [
    '# SOZO Brain Center — Brain Region → EEG Electrode → Network Bridge',
    '# Source: SOZO_Assessments_Master.xlsx, April 2026',
    '# Clinical bridge: which assessment leads to which region and FNON approach',
    '',
    'regions:',
]
for r in rows5:
    reg = r.get('Brain Region')
    if not reg: continue
    rslug = str(reg).strip().lower().replace(' ', '_').replace("'", '').replace('/', '_')
    lines5.append(f'  {rslug}:')
    lines5.append(f'    region: {s(reg)}')
    lines5.append(f'    abbreviation: {s(r.get("Abbreviation"))}')
    lines5.append(f'    primary_eeg_positions: {s(r.get("Primary 10-20 EEG Position(s)"))}')
    lines5.append(f'    adjacent_eeg_positions: {s(r.get("Adjacent EEG Positions"))}')
    lines5.append(f'    primary_network: {s(r.get("Primary Network"))}')
    lines5.append(f'    secondary_network: {s(r.get("Secondary Network"))}')
    lines5.append(f'    key_qeeg_biomarker: {bl(r.get("Key qEEG Biomarker at this Electrode"), 4)}')
    lines5.append(f'    target_conditions: {bl(r.get("Conditions Where This Region Is Primary Target"), 4)}')
    lines5.append(f'    fnon_approach: {bl(r.get("FNON Approach at This Site"), 4)}')
    lines5.append(f'    assessment_region_link: {bl(r.get("Assessment → This Region Link"), 4)}')

with open(os.path.join(REF, 'region_eeg_network.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines5) + '\n')
print(f'region_eeg_network.yaml: {len(rows5)} regions')

print('\nAll assessment reference files done.')
