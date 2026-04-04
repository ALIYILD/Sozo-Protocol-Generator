import csv, os
from collections import defaultdict

csv_path = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\transcinal pulse stimulations - 04 Apr 2026 (1).csv'
out_path = r'C:\Users\yildi\sozo_generator\data\reference\tps_evidence.yaml'

with open(csv_path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

condition_keywords = {
    'parkinsons':    ['parkinson'],
    'depression':    ['depression', 'depressive', 'mdd'],
    'anxiety':       ['anxiety', 'anxious', 'gad'],
    'adhd':          ['adhd', 'attention deficit', 'attention-deficit'],
    'alzheimers':    ['alzheimer'],
    'stroke_rehab':  ['stroke', 'cerebrovascular'],
    'tbi':           ['traumatic brain injury', ' tbi ', 'concussion'],
    'chronic_pain':  ['chronic pain', 'neuropathic pain', 'pain'],
    'ptsd':          ['ptsd', 'post-traumatic', 'posttraumatic'],
    'ocd':           ['ocd', 'obsessive-compulsive'],
    'ms':            ['multiple sclerosis', ' ms '],
    'asd':           ['autism', 'autistic'],
    'long_covid':    ['long covid', 'post-covid', 'long-covid'],
    'tinnitus':      ['tinnitus'],
    'insomnia':      ['insomnia', 'sleep disorder', 'sleep disturbance'],
}

study_type_rank = {
    'meta-analysis': 1, 'systematic review': 2, 'rct': 3,
    'non-rct experimental': 4, 'non-rct observational study': 5,
    'literature review': 6, 'case report': 7, '': 8, 'non-rct in vitro': 8,
}
HIGH_QUALITY = {'meta-analysis', 'systematic review', 'rct'}

def get_cit(r):
    try:
        return int(r.get('Citations', '') or 0)
    except Exception:
        return 0

def sort_key(r):
    return (study_type_rank.get(r.get('Study Type', '').lower().strip(), 8), -get_cit(r))

def evidence_grade(hq):
    if hq >= 10:
        return 'strong'
    elif hq >= 3:
        return 'emerging'
    elif hq >= 1:
        return 'preliminary'
    return 'none'

def esc(s):
    if not s or not s.strip():
        return 'null'
    s = s.strip()[:200]
    needs_quote = any(c in s for c in ':#{}[]&*?|<>=!%@`') or s.startswith('-') or '"' in s or "'" in s
    if needs_quote:
        s2 = s.replace('\\', '\\\\').replace('"', '\\"')
        return '"' + s2 + '"'
    return s

def match_row(row, keywords):
    text = ' ' + ' '.join([
        row.get('Title', ''), row.get('Abstract', ''), row.get('Takeaway', '')
    ]).lower() + ' '
    return any(kw in text for kw in keywords)

condition_papers = defaultdict(list)
unmatched = []
for r in rows:
    if not r.get('DOI', '').strip():
        continue
    matched = [c for c, kws in condition_keywords.items() if match_row(r, kws)]
    if matched:
        for c in matched:
            condition_papers[c].append(r)
    else:
        unmatched.append(r)

lines = [
    '# SOZO Brain Center — TPS Evidence Database',
    '# Source: Consensus.app export, 2026-04-04',
    '# 2,994 papers on Transcranial Pulse Stimulation / Transcranial Ultrasound',
    '# Auto-generated from: neuromodulation protocol knowledge base CSV',
    '',
    'meta:',
    '  source: "Consensus.app TPS/tFUS literature export"',
    '  export_date: "2026-04-04"',
    '  total_papers: 2994',
    '  high_quality_papers: 225',
    '',
    'conditions:',
]

def paper_block(p, indent=6):
    pad = ' ' * indent
    pad2 = ' ' * (indent + 2)
    yr = p.get('Year', '').strip() or 'null'
    cit = get_cit(p)
    return [
        pad + '- title: ' + esc(p.get('Title', '')),
        pad2 + 'authors: ' + esc(p.get('Authors', '')),
        pad2 + 'year: ' + yr,
        pad2 + 'doi: ' + esc(p.get('DOI', '')),
        pad2 + 'study_type: ' + esc(p.get('Study Type', '')),
        pad2 + 'citations: ' + str(cit),
        pad2 + 'takeaway: ' + esc(p.get('Takeaway', '')),
        pad2 + 'consensus_link: ' + esc(p.get('Consensus Link', '')),
    ]

for slug in condition_keywords:
    papers = condition_papers[slug]
    sorted_p = sorted(papers, key=sort_key)
    total = len(papers)
    hq = sum(1 for p in papers if p.get('Study Type', '').lower().strip() in HIGH_QUALITY)
    grade = evidence_grade(hq)
    top10 = sorted_p[:10]
    lines += [
        '  ' + slug + ':',
        '    total_papers: ' + str(total),
        '    high_quality_count: ' + str(hq),
        '    evidence_grade: ' + grade,
        '    top_papers:',
    ]
    for p in top10:
        lines += paper_block(p, indent=6)
    lines.append('')

top15_gen = sorted(unmatched, key=lambda r: -get_cit(r))[:15]
lines += [
    'general_tps:',
    '  description: "General TPS/tFUS papers not matched to a specific condition"',
    '  total_unmatched_papers: ' + str(len(unmatched)),
    '  top_papers:',
]
for p in top15_gen:
    lines += paper_block(p, indent=4)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print('Done. Written to:', out_path)
print('Size:', os.path.getsize(out_path), 'bytes')
for slug in condition_keywords:
    papers = condition_papers[slug]
    hq = sum(1 for p in papers if p.get('Study Type', '').lower().strip() in HIGH_QUALITY)
    print(f'  {slug}: {len(papers)} papers, {hq} HQ')
