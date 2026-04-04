"""
Append fnon_protocol, qeeg_biomarkers, modality_evidence_counts blocks
to all 15 sozo_knowledge/knowledge/conditions/*.yaml files.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl

XLSX = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\SOZO_Brain_Networks_qEEG_FNON.xlsx'
CONDITIONS_DIR = r'C:\Users\yildi\sozo_generator\sozo_knowledge\knowledge\conditions'

wb = openpyxl.load_workbook(XLSX, read_only=True)

def get_rows(sheet):
    ws = wb[sheet]
    data = list(ws.iter_rows(min_row=2, values_only=True))
    header = data[0]
    return [dict(zip(header, r)) for r in data[1:] if any(v is not None for v in r)]

fnon_rows = get_rows('FNON_Protocols')
cn_rows = get_rows('Conditions_Network')

# Build lookup dicts by slug
FNON_SLUG = {
    "Alzheimer's Disease": 'alzheimers',
    "Parkinson's Disease — Motor": 'parkinsons',
    'MCI': 'mci',
    'Depression (MDD)': 'depression',
    'PTSD': 'ptsd',
    'OCD': 'ocd',
    'ADHD': 'adhd',
    'Autism (ASD)': 'asd',
    'Chronic Pain': 'chronic_pain',
    'Epilepsy (drug-resistant)': 'epilepsy',
    'Insomnia': 'insomnia',
    'Tinnitus': 'tinnitus',
}
CN_SLUG = {
    "Alzheimer's Disease": 'alzheimers',
    "Parkinson's Disease": 'parkinsons',
    'MCI': 'mci',
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

def safe(v, maxlen=300):
    if v is None: return 'null'
    t = str(v).strip()[:maxlen]
    if not t: return 'null'
    # escape for YAML double-quoted string
    t2 = t.replace('\\', '\\\\').replace('"', '\\"')
    return '"' + t2 + '"'

def block_scalar(v, indent=4):
    if not v: return 'null'
    t = str(v).strip().replace('"', "'")
    # use literal block
    pad = ' ' * indent
    return '>\n' + pad + t

def int_or_null(v):
    if v is None: return 'null'
    try: return int(v)
    except: return 'null'

def stars(v):
    if not v: return 0
    return str(v).count('\u2b50')

SOZO_SLUGS = [
    'alzheimers', 'parkinsons', 'depression', 'anxiety', 'adhd',
    'stroke_rehab', 'tbi', 'chronic_pain', 'ptsd', 'ocd',
    'ms', 'asd', 'long_covid', 'tinnitus', 'insomnia'
]

for slug in SOZO_SLUGS:
    fp = os.path.join(CONDITIONS_DIR, f'{slug}.yaml')
    if not os.path.exists(fp):
        print(f'  SKIP {slug} — file not found')
        continue

    with open(fp, encoding='utf-8') as f:
        content = f.read()

    # Skip if already done
    if 'fnon_protocol:' in content:
        print(f'  SKIP {slug} — already has fnon_protocol')
        continue

    additions = ['\n']

    # ── fnon_protocol block ────────────────────────────────────────────────────
    fr = fnon_by_slug.get(slug)
    cn = cn_by_slug.get(slug)

    additions.append('fnon_protocol:')
    if fr:
        pnet = fr.get('Primary Network')
        fband = fr.get('F-Band')
        nodes = fr.get('N-Nodes (EEG)')
        ogoal = fr.get('O-Oscillation Goal')
        pmod = fr.get('N-Primary Modality & Parameters')
        addon = fr.get('Add-on Modality')
        sess = fr.get('Sessions')
        evlev = fr.get('Evidence Level')
        litcnt = fr.get('Lit Count')
        keyrefs = fr.get('Key References')
        fnotes = fr.get('FNON Notes')
        additions.append(f'  primary_network: {safe(pnet)}')
        additions.append(f'  secondary_network: {safe(cn.get("Secondary Network") if cn else None)}')
        additions.append(f'  f_band: {safe(fband)}')
        additions.append(f'  eeg_nodes: {safe(nodes)}')
        additions.append(f'  oscillation_goal: {block_scalar(ogoal, 4)}')
        additions.append(f'  primary_modality_params: {block_scalar(pmod, 4)}')
        additions.append(f'  addon_modality: {block_scalar(addon, 4)}')
        additions.append(f'  sessions: {safe(sess)}')
        additions.append(f'  evidence_level: {safe(evlev)}')
        additions.append(f'  lit_count: {safe(litcnt)}')
        additions.append(f'  key_references: {safe(keyrefs)}')
        additions.append(f'  fnon_notes: {block_scalar(fnotes, 4)}')
    elif cn:
        additions.append(f'  primary_network: {safe(cn.get("Primary Network"))}')
        additions.append(f'  secondary_network: {safe(cn.get("Secondary Network"))}')
        additions.append(f'  f_band: {safe(cn.get("F Band"))}')
        additions.append('  eeg_nodes: null')
        additions.append('  oscillation_goal: null')
        additions.append('  primary_modality_params: null')
        additions.append('  addon_modality: null')
        additions.append('  sessions: null')
        additions.append('  evidence_level: null')
        additions.append('  lit_count: null')
        additions.append('  key_references: null')
        additions.append('  fnon_notes: "Full FNON protocol pending. See conditions_modality_matrix.yaml."')
    else:
        additions.append('  primary_network: null')
        additions.append('  fnon_notes: "No FNON protocol data available for this condition."')

    # ── qeeg_biomarkers block ─────────────────────────────────────────────────
    additions.append('')
    additions.append('qeeg_biomarkers:')
    if cn:
        qb = cn.get('qEEG Biomarker')
        fb = cn.get('F Band')
        additions.append(f'  primary_biomarker: {safe(qb)}')
        additions.append(f'  f_band_target: {safe(fb)}')
    else:
        additions.append('  primary_biomarker: null')
        additions.append('  f_band_target: null')

    # ── modality_evidence_counts block ────────────────────────────────────────
    additions.append('')
    additions.append('modality_evidence_counts:')
    if cn:
        additions.append(f'  tps: {int_or_null(cn.get("TPS"))}')
        additions.append(f'  tms: {int_or_null(cn.get("TMS"))}')
        additions.append(f'  tdcs: {int_or_null(cn.get("tDCS"))}')
        additions.append(f'  tavns: {int_or_null(cn.get("taVNS"))}')
        additions.append(f'  ces: {int_or_null(cn.get("CES"))}')
        additions.append(f'  tacs: {int_or_null(cn.get("tACS"))}')
        additions.append(f'  pbm: {int_or_null(cn.get("PBM"))}')
        additions.append(f'  lifu: {int_or_null(cn.get("LIFU"))}')
        additions.append(f'  pemf: {int_or_null(cn.get("PEMF"))}')
        additions.append(f'  dbs: {int_or_null(cn.get("DBS"))}')
        additions.append(f'  best_first_line: {safe(cn.get("Best 1st Line"))}')
        additions.append(f'  best_second_line: {safe(cn.get("Best 2nd Line"))}')
        score_raw = cn.get('FNON Score')
        additions.append(f'  fnon_score: {stars(score_raw)}')
    else:
        additions.append('  tps: null')
        additions.append('  best_first_line: null')
        additions.append('  fnon_score: 0')

    block = '\n'.join(additions) + '\n'
    with open(fp, 'a', encoding='utf-8') as f:
        f.write(block)
    print(f'  {slug}: updated (fnon={fr is not None}, cn={cn is not None})')

print('\nDone.')
