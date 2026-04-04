"""
Update all 15 evidence profile YAMLs with TPS-specific search profiles and priority DOIs.
"""
import csv, os, re

csv_path = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\transcinal pulse stimulations - 04 Apr 2026 (1).csv'
profiles_dir = r'C:\Users\yildi\sozo_generator\data\reference\evidence_profiles'

with open(csv_path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

condition_config = {
    'parkinsons': {
        'name': "Parkinson's Disease",
        'keywords': ['parkinson'],
        'has_tps_profile': True,
    },
    'depression': {
        'name': 'Major Depressive Disorder',
        'keywords': ['depression', 'depressive', 'mdd'],
        'has_tps_profile': False,
    },
    'anxiety': {
        'name': 'Anxiety Disorder',
        'keywords': ['anxiety', 'anxious', 'gad'],
        'has_tps_profile': False,
    },
    'adhd': {
        'name': 'ADHD',
        'keywords': ['adhd', 'attention deficit', 'attention-deficit'],
        'has_tps_profile': False,
    },
    'alzheimers': {
        'name': "Alzheimer's Disease",
        'keywords': ['alzheimer'],
        'has_tps_profile': True,
    },
    'stroke_rehab': {
        'name': 'Stroke Rehabilitation',
        'keywords': ['stroke', 'cerebrovascular'],
        'has_tps_profile': False,
    },
    'tbi': {
        'name': 'Traumatic Brain Injury',
        'keywords': ['traumatic brain injury', ' tbi ', 'concussion'],
        'has_tps_profile': False,
    },
    'chronic_pain': {
        'name': 'Chronic Pain',
        'keywords': ['chronic pain', 'neuropathic pain', 'pain'],
        'has_tps_profile': False,
    },
    'ptsd': {
        'name': 'PTSD',
        'keywords': ['ptsd', 'post-traumatic', 'posttraumatic'],
        'has_tps_profile': False,
    },
    'ocd': {
        'name': 'OCD',
        'keywords': ['ocd', 'obsessive-compulsive'],
        'has_tps_profile': False,
    },
    'ms': {
        'name': 'Multiple Sclerosis',
        'keywords': ['multiple sclerosis'],
        'has_tps_profile': False,
    },
    'asd': {
        'name': 'Autism Spectrum Disorder',
        'keywords': ['autism', 'autistic'],
        'has_tps_profile': False,
    },
    'long_covid': {
        'name': 'Long COVID',
        'keywords': ['long covid', 'post-covid', 'long-covid'],
        'has_tps_profile': False,
    },
    'tinnitus': {
        'name': 'Tinnitus',
        'keywords': ['tinnitus'],
        'has_tps_profile': False,
    },
    'insomnia': {
        'name': 'Insomnia',
        'keywords': ['insomnia', 'sleep disorder', 'sleep disturbance'],
        'has_tps_profile': False,
    },
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

def match_row(row, keywords):
    text = ' ' + ' '.join([
        row.get('Title', ''), row.get('Abstract', ''), row.get('Takeaway', '')
    ]).lower() + ' '
    return any(kw in text for kw in keywords)

def sort_key(r):
    return (study_type_rank.get(r.get('Study Type', '').lower().strip(), 8), -get_cit(r))

def yaml_esc(s, max_len=150):
    if not s or not s.strip():
        return 'null'
    s = s.strip()[:max_len]
    s = s.replace('"', "'")
    return '"' + s + '"'

for slug, cfg in condition_config.items():
    fp = os.path.join(profiles_dir, f'{slug}.yaml')
    if not os.path.exists(fp):
        print(f'  SKIP {slug} — file not found')
        continue

    with open(fp, encoding='utf-8') as f:
        content = f.read()

    # Find matching papers
    matches = [r for r in rows if match_row(r, cfg['keywords']) and r.get('DOI', '').strip()]
    sorted_matches = sorted(matches, key=sort_key)
    top5 = sorted_matches[:5]
    hq_count = sum(1 for r in matches if r.get('Study Type', '').lower().strip() in HIGH_QUALITY)

    # Build tps_protocols block (only if not already present)
    additions = []
    if 'tps_protocols:' not in content:
        cname = cfg['name']
        tps_search = f"""
  tps_protocols:
    query: >
      {cname}[Title/Abstract] AND
      (transcranial pulse stimulation[Title/Abstract] OR
       focused ultrasound[Title/Abstract] OR
       low-intensity focused ultrasound[Title/Abstract] OR
       transcranial ultrasound[Title/Abstract])
    max_results: 20
"""
        # Insert after last search_profiles entry — find last entry before priority_pmids
        insert_before = 'priority_pmids:'
        if insert_before in content:
            content = content.replace(insert_before, tps_search.rstrip() + '\n\n' + insert_before, 1)
        else:
            # Append to search_profiles section
            content = content.rstrip() + '\n' + tps_search

    # Build tps_priority_dois block
    if 'tps_priority_dois:' not in content:
        dois_lines = ['\ntps_priority_dois:']
        for r in top5:
            tk = (r.get('Takeaway', '') or '').strip()[:150]
            tk = tk.replace('"', "'")
            doi = r.get('DOI', '').strip()
            title = (r.get('Title', '') or '').strip()[:120].replace('"', "'")
            authors = (r.get('Authors', '') or '').strip()
            if len(authors) > 60:
                authors = authors[:57] + '...'
            authors = authors.replace('"', "'")
            yr = r.get('Year', '').strip() or 'null'
            st = (r.get('Study Type', '') or '').strip()
            cit = get_cit(r)
            dois_lines.append(f'  - doi: "{doi}"')
            dois_lines.append(f'    title: "{title}"')
            dois_lines.append(f'    authors: "{authors}"')
            dois_lines.append(f'    year: {yr}')
            dois_lines.append(f'    study_type: "{st}"')
            dois_lines.append(f'    citations: {cit}')
            if tk:
                dois_lines.append(f'    takeaway: "{tk}"')
            else:
                dois_lines.append('    takeaway: null')
        content = content.rstrip() + '\n' + '\n'.join(dois_lines) + '\n'

    # Update notes field
    tps_note = f'TPS evidence: {len(matches)} papers identified ({hq_count} RCT/SR/MA) from Consensus.app tFUS/TPS literature export 2026-04-04.'
    if 'TPS evidence:' not in content:
        content = re.sub(
            r'(notes:\s*>?\s*\n\s+)(.+)',
            lambda m: m.group(0).rstrip() + '\n  ' + tps_note + '\n',
            content,
            count=1,
            flags=re.DOTALL
        )
        # If notes not found, append
        if 'TPS evidence:' not in content:
            content = content.rstrip() + f'\n\n# TPS evidence note\n# {tps_note}\n'

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'  {slug}: updated ({len(matches)} TPS papers, {hq_count} HQ, {len(top5)} DOIs added)')

print('\nDone.')
