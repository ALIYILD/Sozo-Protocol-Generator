'use strict';
module.exports = {
  conditionFull:  'Long COVID (Post-Acute Sequelae of SARS-CoV-2)',
  conditionShort: 'Long COVID',
  primarySymptoms: [
    'Brain fog', 'Fatigue severity', 'Post-exertional malaise (PEM)',
    'Memory impairment', 'Concentration difficulty', 'Word-finding difficulty',
    'Processing speed', 'Headache',
  ],
  secondarySymptoms: [
    'Depression / low mood', 'Anxiety', 'Sleep disturbance',
    'Heart rate / palpitations (dysautonomia)', 'Breathlessness', 'Muscle / joint pain',
    'Dizziness / orthostatic intolerance', 'Social & occupational function',
  ],
  functionalDomains: [
    'Return-to-work / study capacity',
    'Physical activity & exertion tolerance',
    'Social & recreational activities',
    'Cognitive functioning in daily life',
    'Emotional & psychological wellbeing',
  ],
  networkMapping: [
    { network: 'Left DLPFC (CEN-L)',     role: 'Neuroinflammatory cognitive impairment',          evidence: 'Brain fog, memory, processing speed',          priority: 'Primary' },
    { network: 'Default Mode (DMN)',      role: 'Disrupted resting-state due to neuroinflammation', evidence: 'Fatigue, brain fog, mood disturbance',        priority: 'Primary' },
    { network: 'Autonomic / Interoception', role: 'Dysautonomia & autonomic nervous system dysfunction', evidence: 'Heart rate, dizziness, breathlessness', priority: 'Secondary' },
    { network: 'Salience (SN)',           role: 'Amplified fatigue & pain signals',                evidence: 'PEM, headache, fatigue',                       priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant cluster: Cognitive-predominant (PASC-neuro) / Cardiorespiratory / Fatigue-predominant (ME/CFS-like) / Multisystem. Record COVID episode date and vaccination status. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with Long COVID syndrome. Neuroinflammatory mechanisms likely underlie cognitive network disruption and autonomic dysregulation. Anodal tDCS to left DLPFC combined with taVNS (anti-inflammatory / vagal pathway activation) and TPS is indicated pending full phenotyping.',
};
