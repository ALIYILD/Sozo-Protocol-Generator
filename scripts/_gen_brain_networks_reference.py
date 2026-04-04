"""
Generate brain_networks_literature.yaml from brain networks CSV
and enrich fnon_framework.yaml with landmark network neuroscience citations.
"""
import sys, io, os, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CSV_PATH = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\brain networks - 04 Apr 2026.csv'
REF = r'C:\Users\yildi\sozo_generator\data\reference'
FNON_FW = r'C:\Users\yildi\sozo_generator\sozo_knowledge\knowledge\shared\fnon_framework.yaml'

OUT_YAML = os.path.join(REF, 'brain_networks_literature.yaml')

# ── Read CSV ──────────────────────────────────────────────────────────────────
with open(CSV_PATH, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = [r for r in reader if any(v.strip() for v in r.values())]

print(f'Loaded {len(rows)} papers from CSV')

def s(v, maxlen=400):
    if not v or not str(v).strip(): return 'null'
    t = str(v).strip()[:maxlen]
    t2 = t.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    return '"' + t2 + '"'

def bl(v, indent=4):
    if not v or not str(v).strip(): return 'null'
    t = str(v).strip().replace('"', "'").replace('\n', ' ')
    return '>\n' + ' ' * indent + t

def cit(v):
    if not v: return 0
    try: return int(float(str(v).replace(',', '')))
    except: return 0

# ── Classify papers into topic categories ─────────────────────────────────────
TOPIC_KEYWORDS = {
    'graph_theory_methods': [
        'graph theory', 'network topology', 'small-world', 'hub', 'modularity',
        'clustering coefficient', 'path length', 'betweenness centrality',
        'scale-free', 'rich club', 'connectome'
    ],
    'resting_state': [
        'resting state', 'resting-state', 'rsfmri', 'rs-fmri', 'default mode',
        'intrinsic activity', 'spontaneous', 'bold fluctuation'
    ],
    'structure_function': [
        'structure-function', 'structural connectivity', 'functional connectivity',
        'white matter', 'tractography', 'diffusion', 'dti', 'axonal',
        'anatomical', 'myelin'
    ],
    'disease_networks': [
        'disorder', 'disease', 'schizophrenia', 'depression', 'alzheimer',
        'parkinson', 'epilepsy', 'autism', 'adhd', 'psychiatric',
        'neurological', 'clinical', 'patient'
    ],
    'network_communication': [
        'communication', 'spreading', 'propagation', 'oscillation', 'synchrony',
        'synchronization', 'coupling', 'coherence', 'signal propagation',
        'neural communication', 'information flow'
    ],
    'multilayer': [
        'multilayer', 'multi-layer', 'multiplex', 'temporal network',
        'time-varying', 'dynamic network', 'dynamic connectivity'
    ],
}

def classify(row):
    text = ' '.join([
        str(row.get('Title', '')),
        str(row.get('Abstract', '')),
        str(row.get('Takeaway', ''))
    ]).lower()
    topics = []
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(kw in text for kw in kws):
            topics.append(topic)
    return topics if topics else ['general']

papers_by_topic = {t: [] for t in list(TOPIC_KEYWORDS.keys()) + ['general']}
all_papers = []

for r in rows:
    title = str(r.get('Title', '') or '').strip()
    if not title:
        continue
    citations = cit(r.get('Citations') or r.get('Citation Count') or 0)
    doi = str(r.get('DOI', '') or '').strip()
    year = str(r.get('Year', '') or '').strip()
    authors = str(r.get('Authors', '') or '').strip()
    journal = str(r.get('Journal', '') or '').strip()
    takeaway = str(r.get('Takeaway', '') or '').strip()
    study_type = str(r.get('Study Type', '') or '').strip()
    sjr = str(r.get('Journal SJR Quartile', '') or '').strip()
    consensus = str(r.get('Consensus Link', '') or '').strip()

    topics = classify(r)
    paper = {
        'title': title,
        'authors': authors,
        'year': year,
        'journal': journal,
        'citations': citations,
        'doi': doi,
        'study_type': study_type,
        'sjr': sjr,
        'takeaway': takeaway,
        'topics': topics,
        'consensus': consensus,
    }
    all_papers.append(paper)
    for t in topics:
        papers_by_topic[t].append(paper)

# Sort by citations desc within each topic
for t in papers_by_topic:
    papers_by_topic[t].sort(key=lambda x: x['citations'], reverse=True)

all_papers.sort(key=lambda x: x['citations'], reverse=True)

# ── Build YAML ────────────────────────────────────────────────────────────────
lines = [
    '# SOZO Brain Center — Brain Networks Neuroscience Literature',
    '# Source: brain networks - 04 Apr 2026.csv',
    f'# {len(all_papers)} papers on brain network science, graph theory, connectomics',
    '# Organized by topic category; sorted by citation count',
    '',
    'meta:',
    f'  total_papers: {len(all_papers)}',
    '  source: "brain networks - 04 Apr 2026.csv"',
    '  date: "2026-04-04"',
    '  topics: [graph_theory_methods, resting_state, structure_function, disease_networks, network_communication, multilayer, general]',
    '',
    '# ── Top landmark papers (all topics, top 20 by citation) ────────────────',
    'landmark_papers:',
]

for p in all_papers[:20]:
    safe_title = p['title'].replace('\\', '\\\\').replace('"', '\\"')[:120]
    lines.append(f'  - title: "{safe_title}"')
    lines.append(f'    authors: {s(p["authors"][:100])}')
    lines.append(f'    year: {s(p["year"])}')
    lines.append(f'    journal: {s(p["journal"])}')
    lines.append(f'    citations: {p["citations"]}')
    lines.append(f'    doi: {s(p["doi"])}')
    lines.append(f'    study_type: {s(p["study_type"])}')
    if p["takeaway"]:
        lines.append(f'    takeaway: {bl(p["takeaway"])}')
    lines.append(f'    topics: [{", ".join(p["topics"])}]')

lines.append('')
lines.append('# ── Papers by topic category ─────────────────────────────────────────────')
lines.append('by_topic:')

for topic, papers in papers_by_topic.items():
    if not papers:
        continue
    lines.append(f'  {topic}:')
    lines.append(f'    count: {len(papers)}')
    lines.append(f'    top_papers:')
    for p in papers[:10]:
        safe_title = p['title'].replace('\\', '\\\\').replace('"', '\\"')[:120]
        lines.append(f'      - title: "{safe_title}"')
        lines.append(f'        authors: {s(p["authors"][:80])}')
        lines.append(f'        year: {s(p["year"])}')
        lines.append(f'        citations: {p["citations"]}')
        lines.append(f'        doi: {s(p["doi"])}')
        if p["takeaway"]:
            lines.append(f'        takeaway: {bl(p["takeaway"], 8)}')

with open(OUT_YAML, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print(f'brain_networks_literature.yaml: {len(all_papers)} papers written')

# ── Enrich fnon_framework.yaml with landmark citations ────────────────────────
if not os.path.exists(FNON_FW):
    print(f'  SKIP fnon_framework.yaml enrichment — file not found at {FNON_FW}')
else:
    with open(FNON_FW, encoding='utf-8') as f:
        fw_content = f.read()

    if 'network_neuroscience_foundations:' in fw_content:
        print('  SKIP fnon_framework.yaml — already has network_neuroscience_foundations')
    else:
        # Pick top 15 landmark papers
        top_papers = all_papers[:15]

        block_lines = [
            '\n',
            '# ── Network Neuroscience Foundations (brain networks CSV, April 2026) ──',
            'network_neuroscience_foundations:',
            '  rationale: >',
            '    FNON methodology is grounded in brain network neuroscience. The following',
            '    landmark papers provide the theoretical basis for network-targeted',
            '    neuromodulation: graph-theoretic analysis of connectomes, resting-state',
            '    network discovery, structure-function mapping, and disease network models.',
            '  landmark_citations:',
        ]

        for p in top_papers:
            safe_title = p['title'].replace('\\', '\\\\').replace('"', '\\"')[:100]
            block_lines.append(f'    - title: "{safe_title}"')
            block_lines.append(f'      authors: {s(p["authors"][:80])}')
            block_lines.append(f'      year: {s(p["year"])}')
            block_lines.append(f'      citations: {p["citations"]}')
            block_lines.append(f'      doi: {s(p["doi"])}')
            if p["takeaway"]:
                block_lines.append(f'      takeaway: {bl(p["takeaway"], 6)}')
            block_lines.append(f'      relevance_topics: [{", ".join(p["topics"][:3])}]')

        block_lines.append('')
        block_lines.append('  key_principles:')
        block_lines.append('    - "Brain function emerges from complex network interactions, not isolated regions"')
        block_lines.append('    - "Neurological/psychiatric conditions reflect network-level dysfunction"')
        block_lines.append('    - "Targeted neuromodulation can restore pathological network states"')
        block_lines.append('    - "QEEG biomarkers index network connectivity and oscillatory dynamics"')
        block_lines.append('    - "Small-world architecture: balance of local clustering and global integration"')
        block_lines.append('    - "Hub regions (high betweenness centrality) are preferential stimulation targets"')

        with open(FNON_FW, 'a', encoding='utf-8') as f:
            f.write('\n'.join(block_lines) + '\n')
        print(f'fnon_framework.yaml: enriched with {len(top_papers)} landmark network citations')

print('\nAll done.')
