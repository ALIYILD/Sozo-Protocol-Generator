'use strict';
module.exports = {
  conditionFull:  'Chronic Insomnia Disorder',
  conditionShort: 'Insomnia',
  primarySymptoms: [
    'Sleep onset latency (mins)', 'Night-time awakenings (count)', 'Early morning awakening',
    'Subjective sleep quality', 'Total sleep time (hrs)', 'Daytime sleepiness',
    'Bedtime anticipatory anxiety', 'Sleep effort (hyper-arousal)',
  ],
  secondarySymptoms: [
    'Daytime fatigue', 'Concentration & memory', 'Mood disturbance',
    'Motivation & energy', 'Physical energy level', 'Work / occupational performance',
    'Social functioning', 'Hypnotic / medication dependence',
  ],
  functionalDomains: [
    'Sleep scheduling & environment',
    'Daytime cognitive performance',
    'Occupational & academic functioning',
    'Physical health & activity',
    'Emotional regulation & mood',
  ],
  networkMapping: [
    { network: 'Salience (SN) / Arousal', role: 'Hyperarousal: cognitive, somatic, cortical',       evidence: 'Sleep effort, bedtime anxiety, night awakenings', priority: 'Primary' },
    { network: 'Default Mode (DMN)',        role: 'Pre-sleep cognitive rumination & worry',           evidence: 'Sleep onset latency, anticipatory anxiety',     priority: 'Primary' },
    { network: 'Circadian / Thalamic',      role: 'Disrupted sleep-wake homeostasis',               evidence: 'Sleep onset, early awakening, sleep quality',    priority: 'Secondary' },
    { network: 'Left DLPFC (CEN-L)',        role: 'Daytime cognitive consequence of sleep debt',     evidence: 'Concentration, memory, work performance',        priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant phenotype: Sleep-onset (SONI) / Sleep-maintenance (SMNI) / Combined / Hyperarousal-predominant. Assess conditioned arousal and sleep-effort syndrome. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with chronic insomnia. Hyperarousal driven by Salience Network dysregulation and DMN rumination is the primary mechanism. Slow-oscillation tDCS (SO-tDCS) during sleep combined with taVNS for autonomic regulation and parasympathetic tone enhancement is indicated alongside CBT-I principles. Full phenotyping required.',
};
