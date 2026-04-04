"""
Add FNON protocol fields to scripts/fnon_data/*.js files.
"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl

XLSX = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\SOZO_Brain_Networks_qEEG_FNON.xlsx'
JS_DIR = r'C:\Users\yildi\sozo_generator\scripts\fnon_data'

wb = openpyxl.load_workbook(XLSX, read_only=True)

def get_rows(sheet):
    ws = wb[sheet]
    data = list(ws.iter_rows(min_row=2, values_only=True))
    header = data[0]
    return [dict(zip(header, r)) for r in data[1:] if any(v is not None for v in r)]

fnon_rows = get_rows('FNON_Protocols')
cn_rows = get_rows('Conditions_Network')

FNON_SLUG = {
    "Alzheimer's Disease": 'alzheimers',
    "Parkinson's Disease — Motor": 'parkinsons',
    'Depression (MDD)': 'depression',
    'PTSD': 'ptsd',
    'OCD': 'ocd',
    'ADHD': 'adhd',
    'Autism (ASD)': 'asd',
    'Chronic Pain': 'chronic_pain',
    'Insomnia': 'insomnia',
    'Tinnitus': 'tinnitus',
}
CN_SLUG = {
    "Alzheimer's Disease": 'alzheimers',
    "Parkinson's Disease": 'parkinsons',
    'Depression (MDD)': 'depression',
    'PTSD': 'ptsd',
    'OCD': 'ocd',
    'ADHD': 'adhd',
    'Autism (ASD)': 'asd',
    'Chronic Pain': 'chronic_pain',
    'Tinnitus': 'tinnitus',
    'Insomnia': 'insomnia',
    'Stroke (Motor)': 'stroke_rehab',
    'TBI (Cognitive)': 'tbi',
    'Anxiety (GAD)': 'anxiety',
}

fnon_by_slug = {}
for r in fnon_rows:
    cond = str(r.get('Condition') or '').strip()
    slug = FNON_SLUG.get(cond)
    if slug:
        fnon_by_slug[slug] = r

cn_by_slug = {}
for r in cn_rows:
    cond = str(r.get('Condition') or '').strip()
    slug = CN_SLUG.get(cond)
    if slug:
        cn_by_slug[slug] = r

def jstr(v, maxlen=400):
    if v is None: return 'null'
    t = str(v).strip()[:maxlen]
    if not t: return 'null'
    t2 = t.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')
    return "'" + t2 + "'"

def jint(v):
    if v is None: return 'null'
    try: return int(v)
    except: return 'null'

def stars(v):
    if not v: return 0
    return str(v).count('\u2b50')

JS_FILES = [
    'alzheimers', 'depression', 'anxiety', 'adhd', 'asd',
    'chronic_pain', 'insomnia', 'long_covid', 'ms', 'ocd',
    'ptsd', 'stroke_rehab', 'tbi', 'tinnitus'
]

for slug in JS_FILES:
    fp = os.path.join(JS_DIR, f'{slug}.js')
    if not os.path.exists(fp):
        print(f'  SKIP {slug}.js — not found')
        continue

    with open(fp, encoding='utf-8') as f:
        content = f.read()

    if 'fnonPrimaryNetwork' in content:
        print(f'  SKIP {slug}.js — already updated')
        continue

    fr = fnon_by_slug.get(slug)
    cn = cn_by_slug.get(slug)

    new_fields = [
        '',
        '  // ── FNON Protocol Data (SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026) ──',
    ]

    if fr:
        new_fields.append(f"  fnonPrimaryNetwork: {jstr(fr.get('Primary Network'))},")
        new_fields.append(f"  fnonSecondaryNetwork: {jstr(cn.get('Secondary Network') if cn else None)},")
        new_fields.append(f"  fnonFBand: {jstr(fr.get('F-Band'))},")
        new_fields.append(f"  fnonEegNodes: {jstr(fr.get('N-Nodes (EEG)'))},")
        new_fields.append(f"  fnonOscillationGoal: {jstr(fr.get('O-Oscillation Goal'))},")
        new_fields.append(f"  fnonPrimaryModalityParams: {jstr(fr.get('N-Primary Modality & Parameters'))},")
        new_fields.append(f"  fnonAddonModality: {jstr(fr.get('Add-on Modality'))},")
        new_fields.append(f"  fnonSessions: {jstr(fr.get('Sessions'))},")
        new_fields.append(f"  fnonEvidenceLevel: {jstr(fr.get('Evidence Level'))},")
        new_fields.append(f"  fnonLitCount: {jstr(fr.get('Lit Count'))},")
        new_fields.append(f"  fnonKeyReferences: {jstr(fr.get('Key References'))},")
        new_fields.append(f"  fnonNotes: {jstr(fr.get('FNON Notes'))},")
    elif cn:
        new_fields.append(f"  fnonPrimaryNetwork: {jstr(cn.get('Primary Network'))},")
        new_fields.append(f"  fnonSecondaryNetwork: {jstr(cn.get('Secondary Network'))},")
        new_fields.append(f"  fnonFBand: {jstr(cn.get('F Band'))},")
        new_fields.append('  fnonEegNodes: null,')
        new_fields.append('  fnonOscillationGoal: null,')
        new_fields.append('  fnonPrimaryModalityParams: null,')
        new_fields.append('  fnonAddonModality: null,')
        new_fields.append('  fnonSessions: null,')
        new_fields.append('  fnonEvidenceLevel: null,')
        new_fields.append('  fnonLitCount: null,')
        new_fields.append('  fnonKeyReferences: null,')
        new_fields.append("  fnonNotes: 'Full FNON protocol pending — see fnon_protocol_matrix.yaml.',")
    else:
        new_fields.append('  fnonPrimaryNetwork: null,')
        new_fields.append("  fnonNotes: 'No FNON data available for this condition.',")

    if cn:
        new_fields.append(f"  fnonQeegBiomarker: {jstr(cn.get('qEEG Biomarker'))},")
        new_fields.append('  fnonPaperCounts: {')
        new_fields.append(f"    tps: {jint(cn.get('TPS'))}, tms: {jint(cn.get('TMS'))}, tdcs: {jint(cn.get('tDCS'))},")
        new_fields.append(f"    tavns: {jint(cn.get('taVNS'))}, ces: {jint(cn.get('CES'))}, tacs: {jint(cn.get('tACS'))},")
        new_fields.append(f"    pbm: {jint(cn.get('PBM'))}, lifu: {jint(cn.get('LIFU'))}, pemf: {jint(cn.get('PEMF'))}, dbs: {jint(cn.get('DBS'))},")
        new_fields.append('  },')
        new_fields.append(f"  fnonBestFirstLine: {jstr(cn.get('Best 1st Line'))},")
        new_fields.append(f"  fnonBestSecondLine: {jstr(cn.get('Best 2nd Line'))},")
        new_fields.append(f"  fnonScore: {stars(cn.get('FNON Score'))},")
    else:
        new_fields.append('  fnonQeegBiomarker: null,')
        new_fields.append('  fnonPaperCounts: null,')
        new_fields.append('  fnonBestFirstLine: null,')
        new_fields.append('  fnonBestSecondLine: null,')
        new_fields.append('  fnonScore: 0,')

    insert_block = '\n'.join(new_fields)

    # Find last `};` that closes module.exports
    # Strategy: find the last occurrence of `};` at start of line
    last_close = content.rfind('\n};')
    if last_close == -1:
        last_close = content.rfind('};')
        if last_close == -1:
            print(f'  WARN {slug}.js — could not find closing }};')
            continue

    new_content = content[:last_close] + insert_block + '\n' + content[last_close:]

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'  {slug}.js: updated (fnon={fr is not None}, cn={cn is not None})')

print('\nDone.')
