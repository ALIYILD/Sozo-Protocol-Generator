"""
Generate 4 FNON reference YAML files + fnon_framework.yaml from the Excel.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl

XLSX = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\SOZO_Brain_Networks_qEEG_FNON.xlsx'
REF = r'C:\Users\yildi\sozo_generator\data\reference'
SHARED = r'C:\Users\yildi\sozo_generator\sozo_knowledge\knowledge\shared'

wb = openpyxl.load_workbook(XLSX, read_only=True)

def rows(sheet, skip=1):
    ws = wb[sheet]
    data = list(ws.iter_rows(min_row=skip+1, values_only=True))
    header = data[0]
    return header, [dict(zip(header, r)) for r in data[1:] if any(v is not None for v in r)]

def s(v, maxlen=None):
    if v is None: return 'null'
    t = str(v).strip()
    if maxlen: t = t[:maxlen]
    if not t: return 'null'
    # quote if has YAML special chars
    if any(c in t for c in ':#{}[]&*?|<>=!%@`') or t[0] in '-' or '"' in t or "'" in t or '\n' in t:
        t2 = t.replace('\\','\\\\').replace('"','\\"').replace('\n',' ')
        return '"' + t2 + '"'
    return t

def slist(v):
    if not v: return '[]'
    items = [x.strip() for x in str(v).split(',') if x.strip()]
    return '[' + ', '.join('"' + i + '"' for i in items) + ']'

def block(v, indent=2):
    if not v: return 'null'
    t = str(v).strip().replace('\n', ' ')
    return '>\n' + ' '*indent + t

# ── 1. brain_regions.yaml ─────────────────────────────────────────────────────
header, regions = rows('Brain_Regions')
lines = [
    '# SOZO Brain Center — Brain Regions Reference (48 regions)',
    '# Source: SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026',
    '',
    'meta:',
    f'  total_regions: {len(regions)}',
    '  source: "SOZO_Brain_Networks_qEEG_FNON.xlsx"',
    '  date: "2026-04-04"',
    '',
    'regions:',
]
col = list(header)
for r in regions:
    name = r.get('Brain Region') or r.get(col[0])
    if not name: continue
    abbrev = r.get('Abbrev') or r.get(col[1])
    lobe = r.get('Lobe') or r.get(col[2])
    depth = r.get('Depth') or r.get(col[3])
    eeg = r.get('10-20 EEG') or r.get(col[4])
    brod = r.get('Brodmann') or r.get(col[5])
    funcs = r.get('Primary Functions') or r.get(col[6])
    nets = r.get('FNON Network') or r.get(col[7])
    qnorm = r.get('qEEG (Normal)') or r.get(col[8])
    qpath = r.get('Pathological qEEG') or r.get(col[9])
    conds = r.get('Clinical Conditions') or r.get(col[10])
    mods = r.get('Modalities') or r.get(col[11])
    notes = r.get('FNON Notes') or r.get(col[12])

    lines.append(f'  - name: {s(name)}')
    lines.append(f'    abbreviation: {s(abbrev)}')
    lines.append(f'    lobe: {s(lobe)}')
    lines.append(f'    depth: {s(depth)}')
    lines.append(f'    eeg_positions: {s(eeg)}')
    lines.append(f'    brodmann: {s(brod)}')
    lines.append(f'    primary_functions: {s(funcs)}')
    lines.append(f'    fnon_networks: {slist(nets)}')
    lines.append(f'    qeeg_normal: {s(qnorm)}')
    lines.append(f'    qeeg_pathological: {s(qpath)}')
    lines.append(f'    clinical_conditions: {slist(conds)}')
    lines.append(f'    modalities: {slist(mods)}')
    lines.append(f'    fnon_notes: {s(notes)}')

with open(os.path.join(REF, 'brain_regions.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print(f'brain_regions.yaml: {len(regions)} regions')

# ── 2. qeeg_biomarkers.yaml ───────────────────────────────────────────────────
header2, bands = rows('qEEG_Biomarkers')
lines2 = [
    '# SOZO Brain Center — qEEG Biomarkers Reference',
    '# Source: SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026',
    '',
    'bands:',
]
col2 = list(header2)
for r in bands:
    name = r.get('Band') or r.get(col2[0])
    if not name: continue
    hz = r.get('Hz Range') or r.get(col2[1])
    state = r.get('Brain State (Normal)') or r.get(col2[2])
    kregs = r.get('Key Regions') or r.get(col2[3])
    epos = r.get('EEG Positions') or r.get(col2[4])
    cinc = r.get('Clinical ↑ (pathological increase)') or r.get(col2[5])
    cdec = r.get('Clinical ↓ (pathological decrease)') or r.get(col2[6])
    dis = r.get('Disorders') or r.get(col2[7])
    ftarget = r.get('FNON Target') or r.get(col2[8])
    mods = r.get('Modalities') or r.get(col2[9])
    metrics = r.get('Key Metrics') or r.get(col2[10])
    notes = r.get('Notes') or r.get(col2[11])

    lines2.append(f'  - name: {s(name)}')
    lines2.append(f'    hz_range: {s(hz)}')
    lines2.append(f'    brain_state_normal: {s(state)}')
    lines2.append(f'    key_regions: {slist(kregs)}')
    lines2.append(f'    eeg_positions: {slist(epos)}')
    lines2.append(f'    clinical_increase: {s(cinc)}')
    lines2.append(f'    clinical_decrease: {s(cdec)}')
    lines2.append(f'    disorders: {slist(dis)}')
    lines2.append(f'    fnon_target: {s(ftarget)}')
    lines2.append(f'    modalities: {slist(mods)}')
    lines2.append(f'    key_metrics: {slist(metrics)}')
    lines2.append(f'    notes: {s(notes)}')

with open(os.path.join(REF, 'qeeg_biomarkers.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines2) + '\n')
print(f'qeeg_biomarkers.yaml: {len(bands)} bands')

# ── 3. fnon_protocol_matrix.yaml ─────────────────────────────────────────────
SLUG_MAP = {
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
header3, protocols = rows('FNON_Protocols')
col3 = list(header3)
lines3 = [
    '# SOZO Brain Center — FNON Protocol Matrix',
    '# Source: SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026',
    f'# {len(protocols)} conditions with full FNON protocol specifications',
    '',
    'protocols:',
]
for r in protocols:
    cond = r.get('Condition') or r.get(col3[0])
    if not cond: continue
    slug = SLUG_MAP.get(str(cond).strip(), str(cond).strip().lower().replace(' ','_').replace("'",""))
    pnet = r.get('Primary Network') or r.get(col3[1])
    fband = r.get('F-Band') or r.get(col3[2])
    nodes = r.get('N-Nodes (EEG)') or r.get(col3[3])
    ogoal = r.get('O-Oscillation Goal') or r.get(col3[4])
    pmod = r.get('N-Primary Modality & Parameters') or r.get(col3[5])
    addon = r.get('Add-on Modality') or r.get(col3[6])
    sess = r.get('Sessions') or r.get(col3[7])
    evlev = r.get('Evidence Level') or r.get(col3[8])
    litcnt = r.get('Lit Count') or r.get(col3[9])
    keyrefs = r.get('Key References') or r.get(col3[10])
    fnotes = r.get('FNON Notes') or r.get(col3[11])

    def bl(v):
        if not v: return 'null'
        t = str(v).strip().replace('"', "'")
        return '>\n      ' + t

    lines3.append(f'  {slug}:')
    lines3.append(f'    condition: {s(cond)}')
    lines3.append(f'    primary_network: {s(pnet)}')
    lines3.append(f'    f_band: {s(fband)}')
    lines3.append(f'    eeg_nodes: {s(nodes)}')
    lines3.append(f'    oscillation_goal: {bl(ogoal)}')
    lines3.append(f'    primary_modality_params: {bl(pmod)}')
    lines3.append(f'    addon_modality: {bl(addon)}')
    lines3.append(f'    sessions: {s(sess)}')
    lines3.append(f'    evidence_level: {s(evlev)}')
    lines3.append(f'    lit_count: {s(litcnt)}')
    lines3.append(f'    key_references: {s(keyrefs)}')
    lines3.append(f'    fnon_notes: {bl(fnotes)}')

with open(os.path.join(REF, 'fnon_protocol_matrix.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines3) + '\n')
print(f'fnon_protocol_matrix.yaml: {len(protocols)} protocols')

# ── 4. conditions_modality_matrix.yaml ───────────────────────────────────────
CN_SLUG_MAP = {
    "Alzheimer's Disease": 'alzheimers',
    "Parkinson's Disease": 'parkinsons',
    'MCI': 'mci',
    'Depression (MDD)': 'depression',
    'PTSD': 'ptsd',
    'OCD': 'ocd',
    'ADHD': 'adhd',
    'Autism (ASD)': 'asd',
    'Chronic Pain': 'chronic_pain',
    'Epilepsy (resistant)': 'epilepsy',
    'Tinnitus': 'tinnitus',
    'Essential Tremor': 'essential_tremor',
    'Insomnia': 'insomnia',
    'Schizophrenia': 'schizophrenia',
    'Stroke (Motor)': 'stroke_rehab',
    'TBI (Cognitive)': 'tbi',
    'Anxiety (GAD)': 'anxiety',
    'DOC': 'doc',
}
header4, cn_rows = rows('Conditions_Network')
col4 = list(header4)
lines4 = [
    '# SOZO Brain Center — Conditions x Modality Evidence Matrix',
    '# Source: SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026',
    f'# {len(cn_rows)} conditions x 10 modalities with paper counts',
    '',
    'conditions:',
]

def stars(v):
    if not v: return 0
    return str(v).count('\u2b50')

for r in cn_rows:
    cond = r.get('Condition') or r.get(col4[0])
    if not cond: continue
    slug = CN_SLUG_MAP.get(str(cond).strip(), str(cond).strip().lower().replace(' ','_').replace("'",""))
    pnet = r.get('Primary Network') or r.get(col4[1])
    snet = r.get('Secondary Network') or r.get(col4[2])
    qeeg = r.get('qEEG Biomarker') or r.get(col4[3])
    fb = r.get('F Band') or r.get(col4[4])

    def cnt(key):
        v = r.get(key)
        if v is None: return 'null'
        try: return int(v)
        except: return 'null'

    tps = cnt('TPS'); tms = cnt('TMS'); tdcs = cnt('tDCS')
    tavns = cnt('taVNS'); ces = cnt('CES'); tacs = cnt('tACS')
    pbm = cnt('PBM'); lifu = cnt('LIFU'); pemf = cnt('PEMF'); dbs = cnt('DBS')
    bl1 = r.get('Best 1st Line') or r.get(col4[15])
    bl2 = r.get('Best 2nd Line') or r.get(col4[16])
    score_raw = r.get('FNON Score') or r.get(col4[17])
    score = stars(score_raw)

    lines4.append(f'  {slug}:')
    lines4.append(f'    condition: {s(cond)}')
    lines4.append(f'    primary_network: {s(pnet)}')
    lines4.append(f'    secondary_network: {s(snet)}')
    lines4.append(f'    qeeg_biomarker: {s(qeeg)}')
    lines4.append(f'    f_band: {s(fb)}')
    lines4.append('    paper_counts:')
    lines4.append(f'      tps: {tps}')
    lines4.append(f'      tms: {tms}')
    lines4.append(f'      tdcs: {tdcs}')
    lines4.append(f'      tavns: {tavns}')
    lines4.append(f'      ces: {ces}')
    lines4.append(f'      tacs: {tacs}')
    lines4.append(f'      pbm: {pbm}')
    lines4.append(f'      lifu: {lifu}')
    lines4.append(f'      pemf: {pemf}')
    lines4.append(f'      dbs: {dbs}')
    lines4.append(f'    best_first_line: {s(bl1)}')
    lines4.append(f'    best_second_line: {s(bl2)}')
    lines4.append(f'    fnon_score: {score}')

with open(os.path.join(REF, 'conditions_modality_matrix.yaml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines4) + '\n')
print(f'conditions_modality_matrix.yaml: {len(cn_rows)} conditions')

# ── 5. fnon_framework.yaml in shared/ ────────────────────────────────────────
framework = """# SOZO Brain Center — FNON Framework Knowledge
# Frequency-Network-Oscillation-Neuromodulation
# Source: SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026

framework:
  name: "FNON Framework"
  full_name: "Frequency-Network-Oscillation-Neuromodulation"
  evidence_sweep: "179 papers (94 brain networks + 85 neuromodulation), April 2026"
  description: >
    The FNON framework is SOZO Brain Center's clinical methodology for mapping each
    patient's condition to dysregulated brain networks, abnormal oscillatory patterns,
    and optimal multi-modal neuromodulation targets. It moves beyond single-region
    stimulation to address the distributed network architecture of neurological and
    psychiatric conditions.

  components:
    F_frequency:
      description: >
        Each clinical condition has a characteristic frequency band signature.
        qEEG biomarker mapping identifies the patient's individual frequency profile
        before FNON protocol selection.
      bands:
        - delta: "0.5-4 Hz — deep sleep, focal lesion, dementia"
        - theta: "4-8 Hz — memory, MDD/PTSD rumination, drowsiness"
        - alpha: "8-12 Hz — relaxed wakefulness, AD/MCI slowing, tinnitus"
        - beta: "13-30 Hz — active cognition, PD motor signature, anxiety"
        - gamma: "30-80 Hz — feature binding, AD (40Hz entrainment target)"

    N_network:
      description: >
        12 major resting-state networks mapped. Network targeting outperforms
        single-region approaches. Connectomics + qEEG identifies which network
        is dysfunctional.
      networks:
        - DMN: "Default Mode Network — self-referential, AD/MCI, depression rumination"
        - SN: "Salience Network — anxiety, OCD, PTSD, pain"
        - ECN: "Executive Control Network — depression, ADHD, schizophrenia"
        - SMN: "Sensorimotor Network — PD, stroke, chronic pain"
        - Limbic: "Limbic Network — PTSD, anxiety, depression, addiction"
        - Visual: "Visual Network — migraine, visual stroke"
        - Auditory: "Auditory Network — tinnitus, schizophrenia"
        - Language: "Language Network — aphasia, dyslexia"
        - Reward: "Reward/Mesolimbic — depression anhedonia, addiction"
        - DAN: "Dorsal Attention Network — ADHD, hemineglect"
        - FPCN: "Frontoparietal Control Network — OCD, MCI, ADHD"
        - CCN: "Cerebellar-Cortical Network — tremor, ataxia, autism"

    O_oscillation:
      description: >
        Oscillation goal defines what the neuromodulation must achieve in terms of
        frequency band normalisation. Each protocol specifies whether to suppress
        (e.g., pathological beta in PD), facilitate (e.g., alpha in AD), or entrain
        (e.g., 40Hz gamma for AD amyloid clearance).

    N_neuromodulation:
      description: >
        Primary modality and add-on modalities selected based on network topology,
        target depth, and oscillation goal. TPS reaches deep cortical/subcortical nodes;
        tDCS modulates cortical excitability; taVNS drives limbic theta suppression;
        CES entrains slow oscillations.

  reference_files:
    brain_regions: "data/reference/brain_regions.yaml"
    qeeg_biomarkers: "data/reference/qeeg_biomarkers.yaml"
    fnon_protocols: "data/reference/fnon_protocol_matrix.yaml"
    conditions_matrix: "data/reference/conditions_modality_matrix.yaml"

  key_principle: >
    Network = the biological substrate. Connectomics + qEEG identifies which network
    is dysfunctional. Frequency = the biomarker. Oscillation = the target state.
    Neuromodulation = the intervention to achieve it.
"""

with open(os.path.join(SHARED, 'fnon_framework.yaml'), 'w', encoding='utf-8') as f:
    f.write(framework)
print('fnon_framework.yaml: written to shared/')

print('\nAll files done.')
