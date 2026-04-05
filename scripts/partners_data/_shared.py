"""
Shared helpers for Partners-tier All-In-One Protocol data.
Imported directly by per-condition modules (not via __init__) to avoid circular imports.
"""

# ─── SHARED PLATO PROGRAMS (condition-adapted variants defined per condition) ─

def _plato_programs_default(focus_ind, memory_ind, mood_ind, calm_ind, energy_ind,
                             sleep_ind, pain_ind, perf_ind, recovery_ind):
    return [
        ("Focus",       "Anodal L-DLPFC stimulation",         focus_ind),
        ("Memory",      "Anodal temporal stimulation",         memory_ind),
        ("Mood+",       "L→R asymmetric prefrontal",           mood_ind),
        ("Calm",        "Cathodal prefrontal inhibition",       calm_ind),
        ("Energy",      "Bilateral frontal upregulation",       energy_ind),
        ("Sleep",       "Bilateral frontal downregulation",     sleep_ind),
        ("Pain Relief", "Anodal M1 stimulation",                pain_ind),
        ("Performance", "DLPFC bilateral activation",           perf_ind),
        ("Recovery",    "Cathodal motor/frontal protocol",      recovery_ind),
    ]
