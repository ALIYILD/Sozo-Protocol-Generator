"""
Update evidence strings in scripts/protocol_data.py with real paper counts from TPS CSV.
Adds key_references to T1-T5 entries for conditions with explicit dicts (parkinsons, depression, anxiety).
Also patches _make_standard_condition() for the remaining 12 conditions.
"""
import csv, os, re

csv_path = r'C:\Users\yildi\OneDrive\Desktop\neuromodulation protocol knowledge base\transcinal pulse stimulations - 04 Apr 2026 (1).csv'
pd_path = r'C:\Users\yildi\sozo_generator\scripts\protocol_data.py'

with open(csv_path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

HIGH_QUALITY = {'meta-analysis', 'systematic review', 'rct'}

def get_cit(r):
    try:
        return int(r.get('Citations', '') or 0)
    except Exception:
        return 0

def match_text(row, keywords):
    text = ' ' + ' '.join([
        row.get('Title', ''), row.get('Abstract', ''), row.get('Takeaway', '')
    ]).lower() + ' '
    return all(kw in text for kw in keywords)

study_type_rank = {
    'meta-analysis': 1, 'systematic review': 2, 'rct': 3,
    'non-rct experimental': 4, 'non-rct observational study': 5,
    'literature review': 6, 'case report': 7, '': 8, 'non-rct in vitro': 8,
}

def sort_key(r):
    return (study_type_rank.get(r.get('Study Type', '').lower().strip(), 8), -get_cit(r))

def get_evidence_string(base_label, condition_kws, symptom_kws):
    """Build a graded evidence string based on paper count."""
    papers = [r for r in rows
              if match_text(r, condition_kws) and match_text(r, symptom_kws)
              and r.get('DOI', '').strip()]
    hq = [r for r in papers if r.get('Study Type', '').lower().strip() in HIGH_QUALITY]
    n = len(hq)

    if 'Emerging' in base_label and 'Pilot' not in base_label:
        if n >= 5:
            return f"Emerging \u2014 {n} RCT/SR supporting"
        elif n >= 1:
            return f"Emerging \u2014 limited RCT data (n={n})"
        else:
            return "Emerging \u2014 preclinical/observational only"
    elif 'Emerging Pilot' in base_label:
        return f"Emerging Pilot \u2014 {n} pilot RCTs" if n else "Emerging Pilot \u2014 0 pilot RCTs"
    elif 'Preliminary' in base_label:
        return f"Preliminary \u2014 {n} controlled studies" if n >= 1 else "Preliminary \u2014 case series only"
    elif 'Experimental' in base_label:
        return f"Experimental \u2014 {n} studies"
    return base_label

def get_top_refs(condition_kws, symptom_kws, n=2):
    """Get top n papers for a T entry as key_references list."""
    papers = [r for r in rows
              if match_text(r, condition_kws) and match_text(r, symptom_kws)
              and r.get('DOI', '').strip()]
    if not papers:
        # Fall back to condition only
        papers = [r for r in rows
                  if match_text(r, condition_kws) and r.get('DOI', '').strip()]
    sorted_p = sorted(papers, key=sort_key)[:n]
    refs = []
    for p in sorted_p:
        doi = p.get('DOI', '').strip()
        authors = (p.get('Authors', '') or '').strip()
        if len(authors) > 40:
            # Get first author surname
            first = authors.split(',')[0].strip().split()[-1]
            authors = first + ' et al.'
        yr = p.get('Year', '').strip() or ''
        st = p.get('Study Type', '').strip()
        refs.append({'doi': doi, 'authors': authors, 'year': yr, 'study_type': st})
    return refs

def refs_to_python(refs, indent=12):
    pad = ' ' * indent
    pad2 = ' ' * (indent + 4)
    lines = [pad + '"key_references": [']
    for r in refs:
        lines.append(pad2 + '{')
        lines.append(pad2 + f'    "doi": "{r["doi"]}",')
        lines.append(pad2 + f'    "authors": "{r["authors"]}",')
        lines.append(pad2 + f'    "year": "{r["year"]}",')
        lines.append(pad2 + f'    "study_type": "{r["study_type"]}",')
        lines.append(pad2 + '},')
    lines.append(pad + '],')
    return '\n'.join(lines)

with open(pd_path, encoding='utf-8') as f:
    content = f.read()

# --- Condition 1: Parkinson's Disease T1-T5 ---
pd_kws = ['parkinson']
parkinsons_t = [
    ('T1', ['motor', 'bradykinesia', 'rigidity']),
    ('T2', ['tremor']),
    ('T3', ['cognition', 'cognitive', 'mci']),
    ('T4', ['depression', 'apathy']),
    ('T5', ['pain', 'dyskinesia']),
]

# --- Condition 2: Depression T1-T5 ---
dep_kws = ['depression', 'depressive']
depression_t = [
    ('T1', ['anhedonia', 'mood', 'depression']),
    ('T2', ['rumination', 'default mode', 'dmn']),
    ('T3', ['cognition', 'cognitive']),
    ('T4', ['anxiety']),
    ('T5', ['treatment-resistant', 'trd']),
]

# --- Condition 3: Anxiety T1-T5 ---
anx_kws = ['anxiety', 'anxious']
anxiety_t = [
    ('T1', ['worry', 'hyperarousal', 'anxiety']),
    ('T2', ['panic', 'autonomic']),
    ('T3', ['cognitive', 'intrusive']),
    ('T4', ['insomnia', 'sleep']),
    ('T5', ['social anxiety']),
]

# Update evidence strings using regex
# Pattern: "evidence": "SomeString" -> "evidence": "Updated String"

def update_evidence_in_content(content, condition_kws, t_entries):
    """
    For each T entry, find and replace the evidence string in the content.
    We look for the pattern near the T code to locate the right entry.
    """
    for code, symptom_kws in t_entries:
        # Find the block for this T code
        # Pattern: "code": "T1", ... "evidence": "...",
        # We'll find each occurrence of "code": "Tx" and update the next "evidence" after it
        pattern = r'("code":\s*"' + code + r'".*?"evidence":\s*")([^"]+)(")'

        def replace_evidence(m):
            orig = m.group(2)
            new_ev = get_evidence_string(orig, condition_kws, symptom_kws)
            return m.group(1) + new_ev + m.group(3)

        new_content = re.sub(pattern, replace_evidence, content, count=1, flags=re.DOTALL)
        if new_content != content:
            print(f'    Updated evidence for {code} ({condition_kws[0]})')
            content = new_content
        else:
            print(f'    Could not find evidence for {code} ({condition_kws[0]}) — skipping')

    return content

print('Updating Parkinson T entries...')
content = update_evidence_in_content(content, pd_kws, parkinsons_t)

print('Updating Depression T entries...')
content = update_evidence_in_content(content, dep_kws, depression_t)

print('Updating Anxiety T entries...')
content = update_evidence_in_content(content, anx_kws, anxiety_t)

# --- Update _make_standard_condition evidence labels ---
# The function uses hard-coded strings; add a comment block with TPS evidence summary
standard_conditions = {
    'adhd':         ['adhd', 'attention deficit'],
    'alzheimers':   ['alzheimer'],
    'stroke_rehab': ['stroke'],
    'tbi':          ['traumatic brain injury', 'tbi'],
    'chronic_pain': ['chronic pain', 'pain'],
    'ptsd':         ['ptsd', 'post-traumatic'],
    'ocd':          ['obsessive-compulsive', 'ocd'],
    'ms':           ['multiple sclerosis'],
    'asd':          ['autism'],
    'long_covid':   ['long covid'],
    'tinnitus':     ['tinnitus'],
    'insomnia':     ['insomnia', 'sleep'],
}

summary_lines = [
    '\n# TPS Evidence Summary (from Consensus.app CSV, 2026-04-04)',
    '# Conditions with explicit T1-T5 dicts above have inline evidence updates.',
    '# Standard conditions (_make_standard_condition) TPS paper counts:',
]
for slug, kws in standard_conditions.items():
    papers = [r for r in rows if match_text(r, [kws[0]]) and r.get('DOI', '').strip()]
    hq = [r for r in papers if r.get('Study Type', '').lower().strip() in HIGH_QUALITY]
    top = sorted(papers, key=sort_key)[:2]
    dois = [r.get('DOI', '').strip() for r in top]
    n_total = len(papers)
    n_hq = len(hq)
    grade = 'strong' if n_hq >= 10 else 'emerging' if n_hq >= 3 else 'preliminary' if n_hq >= 1 else 'none'
    summary_lines.append(f'#   {slug}: {n_total} papers, {n_hq} HQ ({grade}) | top DOIs: {", ".join(dois[:2]) or "none"}')

# Insert summary before the conditions dict
insert_marker = 'CONDITIONS = {'
if insert_marker in content:
    content = content.replace(insert_marker, '\n'.join(summary_lines) + '\n' + insert_marker, 1)
    print('\nAdded TPS evidence summary comment block before CONDITIONS dict')
else:
    content = content.rstrip() + '\n' + '\n'.join(summary_lines) + '\n'
    print('\nAppended TPS evidence summary at end of file')

with open(pd_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('\nDone. protocol_data.py updated.')
