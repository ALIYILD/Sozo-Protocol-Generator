"""
1. Append assessment_profile block to all 15 sozo_knowledge/knowledge/conditions/*.yaml
2. Enrich data/reference/scales_catalog.yaml with missing scales from Excel
"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl

XLSX = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\SOZO_Assessments_Master.xlsx'
CONDITIONS_DIR = r'C:\Users\yildi\sozo_generator\sozo_knowledge\knowledge\conditions'
SCALES_CATALOG = r'C:\Users\yildi\sozo_generator\data\reference\scales_catalog.yaml'

wb = openpyxl.load_workbook(XLSX, read_only=True)

def get_rows(sheet):
    ws = wb[sheet]
    data = list(ws.iter_rows(min_row=2, values_only=True))
    header = [str(h) if h else f'col{i}' for i, h in enumerate(data[0])]
    return [dict(zip(header, r)) for r in data[1:] if any(v is not None for v in r)]

am_rows = get_rows('Assessment_Master')
cs_rows = get_rows('Clinical_Scales')
qeeg_rows = get_rows('Conditions_qEEG')

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
}

def slug(v):
    return SLUG_MAP.get(str(v).strip())

am_by_slug = {slug(r['Condition']): r for r in am_rows if slug(r.get('Condition'))}
cs_by_slug = {slug(r['Condition']): r for r in cs_rows if slug(r.get('Condition'))}
qeeg_by_slug = {slug(r['Condition']): r for r in qeeg_rows if slug(r.get('Condition'))}

def safe_yaml(v, maxlen=400):
    if v is None: return 'null'
    t = str(v).strip()[:maxlen]
    if not t: return 'null'
    t2 = t.replace('\\', '\\\\').replace('"', '\\"')
    return '"' + t2 + '"'

def block(v, indent=4):
    if not v: return 'null'
    t = str(v).strip().replace('"', "'")
    return '>\n' + ' '*indent + t

SOZO_SLUGS = [
    'alzheimers', 'parkinsons', 'depression', 'anxiety', 'adhd',
    'stroke_rehab', 'tbi', 'chronic_pain', 'ptsd', 'ocd',
    'ms', 'asd', 'long_covid', 'tinnitus', 'insomnia'
]

updated = 0
for sl in SOZO_SLUGS:
    fp = os.path.join(CONDITIONS_DIR, f'{sl}.yaml')
    if not os.path.exists(fp):
        print(f'  SKIP {sl} — file not found')
        continue

    with open(fp, encoding='utf-8') as f:
        content = f.read()

    if 'assessment_profile:' in content:
        print(f'  SKIP {sl} — already has assessment_profile')
        continue

    am = am_by_slug.get(sl)
    cs = cs_by_slug.get(sl)
    qe = qeeg_by_slug.get(sl)

    lines = ['\n', 'assessment_profile:']

    if am:
        lines.append(f'  primary_clinical_scales: {block(am.get("Primary Clinical Scales (validated)"))}')
        lines.append(f'  neuropsychological_battery: {block(am.get("Neuropsychological Battery"))}')
        lines.append(f'  physiological_assessments: {block(am.get("Physiological Assessments"))}')
        lines.append(f'  functional_assessments: {block(am.get("Functional / Behavioural Assessments"))}')
        lines.append(f'  neuroimaging: {block(am.get("Neuroimaging"))}')
        lines.append(f'  assessment_rationale: {block(am.get("Assessment Clinical Rationale"))}')
    else:
        lines.append('  primary_clinical_scales: null')
        lines.append('  neuropsychological_battery: null')

    if cs:
        lines.append(f'  primary_scale: {block(cs.get("Primary Scale (main outcome)"))}')
        lines.append(f'  screening_scales: {block(cs.get("Screening Scale(s)"))}')
        lines.append(f'  severity_staging: {block(cs.get("Severity/Staging Scale"))}')
        lines.append(f'  qol_scale: {block(cs.get("Quality of Life / Function Scale"))}')
        lines.append(f'  follow_up_frequency: {block(cs.get("Follow-up Frequency"))}')
        lines.append(f'  comorbidity_screens: {block(cs.get("Comorbidity Screens"))}')
        lines.append(f'  safety_screens: {block(cs.get("Safety Screens"))}')
        lines.append(f'  score_thresholds: {block(cs.get("Score Thresholds & Clinical Interpretation"))}')
    else:
        lines.append('  primary_scale: null')

    if qe:
        lines.append(f'  qeeg_primary_signature: {block(qe.get("Primary qEEG Signature"))}')
        lines.append(f'  qeeg_key_electrodes: {safe_yaml(qe.get("Key Electrodes"))}')
        lines.append(f'  qeeg_key_metrics: {block(qe.get("Key qEEG Metrics"))}')
        lines.append(f'  qeeg_eyes_open: {block(qe.get("Eyes-Open Findings"))}')
        lines.append(f'  qeeg_eyes_closed: {block(qe.get("Eyes-Closed Findings"))}')
        lines.append(f'  qeeg_event_related: {block(qe.get("Event-Related Paradigm"))}')
        lines.append(f'  qeeg_pathological_threshold: {block(qe.get("Pathological Threshold"))}')
        lines.append(f'  qeeg_treatment_target: {block(qe.get("FNON Treatment Target"))}')
        lines.append(f'  qeeg_response_biomarker: {block(qe.get("Response Biomarker"))}')
    else:
        lines.append('  qeeg_primary_signature: null')

    with open(fp, 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'  {sl}: appended assessment_profile')
    updated += 1

print(f'\nCondition YAMLs updated: {updated}/15')

# ── Enrich scales_catalog.yaml ────────────────────────────────────────────────
# Extract scale names from Clinical_Scales that aren't already in the catalog
with open(SCALES_CATALOG, encoding='utf-8') as f:
    catalog_content = f.read()

# New scales to add (from Excel, not currently in catalog)
new_scales = {
    'cssrs': {
        'name': 'Columbia Suicide Severity Rating Scale',
        'abbreviation': 'C-SSRS',
        'conditions': ['depression', 'ptsd', 'bipolar'],
        'domains': ['safety', 'suicidality'],
        'type': 'clinician_administered',
        'frequency': 'Every session',
        'threshold': 'Any ideation with intent or plan = immediate escalation',
    },
    'shaps': {
        'name': 'Snaith-Hamilton Pleasure Scale',
        'abbreviation': 'SHAPS',
        'conditions': ['depression', 'parkinsons'],
        'domains': ['anhedonia'],
        'type': 'self_report',
        'threshold': 'Score >= 3 = significant anhedonia',
    },
    'wsas': {
        'name': 'Work and Social Adjustment Scale',
        'abbreviation': 'WSAS',
        'conditions': ['depression', 'anxiety', 'ocd'],
        'domains': ['functional_impairment'],
        'type': 'self_report',
        'threshold': '0-10 subclinical; 11-20 moderate; >20 severe impairment',
    },
    'ybocs': {
        'name': 'Yale-Brown Obsessive Compulsive Scale',
        'abbreviation': 'Y-BOCS',
        'conditions': ['ocd'],
        'domains': ['ocd_severity'],
        'type': 'clinician_administered',
        'threshold': '0-7 subclinical; 8-15 mild; 16-23 moderate; 24-31 severe; 32-40 extreme',
    },
    'pcl5': {
        'name': 'PTSD Checklist for DSM-5',
        'abbreviation': 'PCL-5',
        'conditions': ['ptsd', 'tbi'],
        'domains': ['ptsd_severity'],
        'type': 'self_report',
        'threshold': '>= 33 = probable PTSD diagnosis',
    },
    'caps5': {
        'name': 'Clinician-Administered PTSD Scale for DSM-5',
        'abbreviation': 'CAPS-5',
        'conditions': ['ptsd'],
        'domains': ['ptsd_severity'],
        'type': 'clinician_administered',
        'threshold': 'Gold standard PTSD severity measure; total >25 = moderate',
    },
    'caars': {
        'name': 'Conners Adult ADHD Rating Scale',
        'abbreviation': 'CAARS',
        'conditions': ['adhd'],
        'domains': ['adhd_severity', 'inattention', 'hyperactivity'],
        'type': 'self_report',
        'threshold': 'T-score >= 65 = clinically significant',
    },
    'asrs': {
        'name': 'Adult ADHD Self-Report Scale',
        'abbreviation': 'ASRS-v1.1',
        'conditions': ['adhd'],
        'domains': ['adhd_screening', 'inattention'],
        'type': 'self_report',
        'threshold': 'Part A >= 4 of 6 items = screen positive',
    },
    'isi': {
        'name': 'Insomnia Severity Index',
        'abbreviation': 'ISI',
        'conditions': ['insomnia', 'depression', 'anxiety'],
        'domains': ['insomnia_severity'],
        'type': 'self_report',
        'threshold': '0-7 no insomnia; 8-14 subthreshold; 15-21 moderate; 22-28 severe',
    },
    'psqi': {
        'name': 'Pittsburgh Sleep Quality Index',
        'abbreviation': 'PSQI',
        'conditions': ['insomnia', 'depression', 'ptsd', 'tbi'],
        'domains': ['sleep_quality'],
        'type': 'self_report',
        'threshold': '> 5 = poor sleep quality (sensitivity 89%, specificity 86%)',
    },
    'thi': {
        'name': 'Tinnitus Handicap Inventory',
        'abbreviation': 'THI',
        'conditions': ['tinnitus'],
        'domains': ['tinnitus_severity', 'handicap'],
        'type': 'self_report',
        'threshold': '0-16 slight; 18-36 mild; 38-56 moderate; 58-76 severe; 78-100 catastrophic',
    },
    'trs': {
        'name': 'Tinnitus Reaction Scale',
        'abbreviation': 'TRS',
        'conditions': ['tinnitus'],
        'domains': ['tinnitus_distress'],
        'type': 'self_report',
        'threshold': '>= 30 = clinically significant distress',
    },
    'edss': {
        'name': 'Expanded Disability Status Scale',
        'abbreviation': 'EDSS',
        'conditions': ['ms'],
        'domains': ['ms_disability', 'neurological_function'],
        'type': 'clinician_administered',
        'threshold': '0 = normal; 4.0 = ambulatory without aid but limited; 6.0 = requires walking aid; 7.0+ = restricted to wheelchair',
    },
    'sdmt': {
        'name': 'Symbol Digit Modalities Test',
        'abbreviation': 'SDMT',
        'conditions': ['ms', 'tbi', 'stroke_rehab'],
        'domains': ['cognitive_speed', 'processing_speed'],
        'type': 'clinician_administered',
        'threshold': 'Z-score < -1.5 = cognitively impaired; sensitive MS cognitive marker',
    },
    'npi': {
        'name': 'Neuropsychiatric Inventory',
        'abbreviation': 'NPI',
        'conditions': ['alzheimers', 'parkinsons', 'tbi'],
        'domains': ['neuropsychiatric_symptoms', 'behavioural'],
        'type': 'carer_reported',
        'threshold': 'Severity x Frequency per domain; total > 12 = significant NPS burden',
    },
    'cdr': {
        'name': 'Clinical Dementia Rating',
        'abbreviation': 'CDR',
        'conditions': ['alzheimers', 'mci'],
        'domains': ['dementia_staging', 'cognition'],
        'type': 'clinician_administered',
        'threshold': '0=Normal; 0.5=MCI; 1=Mild AD; 2=Moderate AD; 3=Severe AD',
    },
    'brief_pain': {
        'name': 'Brief Pain Inventory',
        'abbreviation': 'BPI',
        'conditions': ['chronic_pain', 'ms', 'tbi'],
        'domains': ['pain_severity', 'pain_interference'],
        'type': 'self_report',
        'threshold': 'Severity 0-10; Interference 0-10; > 4 = moderate-severe pain',
    },
    'fma': {
        'name': 'Fugl-Meyer Assessment',
        'abbreviation': 'FMA',
        'conditions': ['stroke_rehab'],
        'domains': ['motor_function', 'stroke_recovery'],
        'type': 'clinician_administered',
        'threshold': '0-66 upper limb; 0-34 lower limb. MCID = 5-6 points',
    },
    'zbi': {
        'name': 'Zarit Burden Interview',
        'abbreviation': 'ZBI',
        'conditions': ['alzheimers'],
        'domains': ['carer_burden'],
        'type': 'self_report',
        'threshold': '0-20 little/no burden; 21-40 mild-moderate; 41-60 moderate-severe; 61-88 severe',
    },
}

# Build new scales text
new_scales_yaml = '\n  # ── Additional scales from Assessment Master (April 2026) ──\n'
for key, data in new_scales.items():
    if key in catalog_content:
        continue  # already exists
    conds = '[' + ', '.join(f'"{c}"' for c in data['conditions']) + ']'
    doms = '[' + ', '.join(f'"{d}"' for d in data['domains']) + ']'
    new_scales_yaml += f'\n  {key}:\n'
    new_scales_yaml += f'    name: "{data["name"]}"\n'
    new_scales_yaml += f'    abbreviation: "{data["abbreviation"]}"\n'
    new_scales_yaml += f'    conditions: {conds}\n'
    new_scales_yaml += f'    domains: {doms}\n'
    new_scales_yaml += f'    type: "{data["type"]}"\n'
    if 'threshold' in data:
        thresh = data['threshold'].replace('"', "'")
        new_scales_yaml += f'    threshold: "{thresh}"\n'
    if 'frequency' in data:
        new_scales_yaml += f'    frequency: "{data["frequency"]}"\n'

with open(SCALES_CATALOG, 'a', encoding='utf-8') as f:
    f.write(new_scales_yaml)

added = sum(1 for k in new_scales if k not in catalog_content)
print(f'scales_catalog.yaml: {added} new scales added')
print('\nAll done.')
