"""
Normalizer functions — convert list-format protocol entries to dict-format.
Called by partners_data/__init__.py after all condition dicts are merged.
Auto-split from partners_all_in_one_data.py.
"""

# ════════════════════════════════════════════════════════════════════════════════
# NORMALIZER — converts list-format protocols to dict-format expected by generator
# ════════════════════════════════════════════════════════════════════════════════
def _normalize_list_protocols():
    for slug, cond in PARTNERS_CONDITIONS.items():
        # Skip already-dict conditions (depression, adhd, alzheimers)
        if cond.get('tps') and isinstance(cond['tps'][0], dict):
            continue

        # tps: [code, symptom, target, params_dose, pulses, evidence]
        new_tps = []
        for p in cond.get('tps', []):
            new_tps.append({
                'code': p[0], 'symptom': p[1],
                'targets': [p[2]],
                'params': f"NEUROLITH® · {p[3]} · {p[4]} · 3-5 Hz",
                'evidence': p[5], 'rationale': '',
            })
        cond['tps'] = new_tps

        # fnon_tps: [code, name, network, targets_str, sozo_integration, params, pulses, sessions]
        new_ftps = []
        for p in cond.get('fnon_tps', []):
            new_ftps.append({
                'code': p[0], 'name': p[1], 'network': p[2],
                'phenotype': p[2], 'targets': [p[3]],
                'sozo_integration': p[4],
                'params': f"NEUROLITH® · {p[5]} · {p[6]} · {p[7]}",
                'rationale': p[4],
            })
        cond['fnon_tps'] = new_ftps

        # tdcs: [code, symptom, montage, current, duration, evidence]
        new_tdcs = []
        for p in cond.get('tdcs', []):
            montage = p[2]
            parts = montage.split('/')
            anodes = [parts[0].strip()] if parts else [montage]
            cathodes = [parts[1].strip()] if len(parts) > 1 else []
            new_tdcs.append({
                'code': p[0], 'symptom': p[1],
                'anodes': anodes, 'cathodes': cathodes,
                'params': f"Newronika HDCkit · {p[3]} · {p[4]}",
                'evidence': p[5], 'rationale': '',
                'montage': montage,
            })
        cond['tdcs'] = new_tdcs

        # fnon_tdcs: [code, name, network, montage, sozo_integration, current, duration]
        new_ftdcs = []
        for p in cond.get('fnon_tdcs', []):
            new_ftdcs.append({
                'code': p[0], 'name': p[1], 'network': p[2],
                'phenotype': p[2], 'targets': [p[3]],
                'sozo_integration': p[4],
                'params': f"Newronika HDCkit · {p[5]} · {p[6]}",
                'rationale': p[4],
                'montage': p[3],
            })
        cond['fnon_tdcs'] = new_ftdcs

        # plato: [code, symptom, variant, positions, current, duration, indication]
        new_plato = []
        for p in cond.get('plato', []):
            new_plato.append({
                'code': p[0], 'symptom': p[1], 'variant': p[2],
                'targets': [p[3]],
                'params': f"PlatoScience PlatoWork · {p[2]} · {p[4]} · {p[5]}",
                'evidence': 'Emerging', 'rationale': p[6],
            })
        cond['plato'] = new_plato

        # fnon_plato: [code, name, network, variant, positions, current, duration]
        new_fplato = []
        for p in cond.get('fnon_plato', []):
            new_fplato.append({
                'code': p[0], 'name': p[1], 'network': p[2],
                'phenotype': p[2], 'derived': p[2],
                'variant': p[3], 'targets': [p[4]],
                'params': f"PlatoWork · {p[3]} · {p[5]} · {p[6]}",
                'rationale': p[2],
            })
        cond['fnon_plato'] = new_fplato


# ─── Post-process phenotype fields for new-format conditions ───────────────────
def _normalize_phenotypes():
    sozo_keys = ['S', 'O', 'Z', 'O2']
    for slug, cond in PARTNERS_CONDITIONS.items():
        for pheno in cond.get('phenotypes', []):
            # sozo_bar: list[4] → dict
            sb = pheno.get('sozo_bar')
            if isinstance(sb, list):
                pheno['sozo_bar'] = dict(zip(sozo_keys, sb + [''] * 4))
            # card_left / card_right: list → str
            for key in ('card_left', 'card_right'):
                val = pheno.get(key)
                if isinstance(val, list):
                    pheno[key] = '\n'.join(val)
            # brain_targets: list of 5-item lists — keep as-is (table rows)
            # combinations: list of 4-item lists — keep as-is (table rows)


# ─── Normalize brain_targets and combinations for new-format conditions ─────────
def _normalize_phenotype_tables():
    for slug, cond in PARTNERS_CONDITIONS.items():
        # Skip already-normalized conditions (depression, adhd, alzheimers have tuples)
        if cond.get('phenotypes') and cond['phenotypes'][0].get('brain_targets'):
            bt0 = cond['phenotypes'][0]['brain_targets'][0]
            if isinstance(bt0, tuple):
                continue  # already correct format

        for pheno in cond.get('phenotypes', []):
            # brain_targets: [region, role, rationale, protocol_code, evidence] → 2-tuple
            new_bt = []
            for bt in pheno.get('brain_targets', []):
                if isinstance(bt, (list, tuple)) and len(bt) >= 2:
                    region = bt[0]
                    desc_parts = [str(x) for x in bt[1:] if x]
                    desc = ' | '.join(desc_parts)
                    new_bt.append((region, desc))
                else:
                    new_bt.append(bt)
            pheno['brain_targets'] = new_bt

            # combinations: [S, O, Z, Task] → 4-tuple (Combination, Rationale, Timing, Indication)
            new_combos = []
            for c in pheno.get('combinations', []):
                if isinstance(c, (list, tuple)) and len(c) == 4:
                    combo_str = f"S: {c[0]}  |  O: {c[1]}  |  Z: {c[2]}"
                    rationale = "Sequential SOZO protocol — Stabilize → Optimize → Zone Target"
                    timing = "S→O→Z sequence (2-3 hr total)"
                    indication = str(c[3])
                    new_combos.append((combo_str, rationale, timing, indication))
                else:
                    new_combos.append(c)
            pheno['combinations'] = new_combos


def run(PARTNERS_CONDITIONS):
    """Apply all normalizers to the merged PARTNERS_CONDITIONS dict."""
    _normalize_list_protocols()
    _normalize_phenotypes()
    _normalize_phenotype_tables()
