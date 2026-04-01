'use strict';
module.exports = {
  conditionFull:  'Traumatic Brain Injury (TBI)',
  conditionShort: 'TBI',
  primarySymptoms: [
    'Headache frequency & severity', 'Concentration difficulty', 'Memory impairment',
    'Processing speed', 'Balance / vestibular symptoms', 'Fatigue',
    'Light sensitivity (photophobia)', 'Noise sensitivity (phonophobia)',
  ],
  secondarySymptoms: [
    'Mood disturbance', 'Sleep disruption', 'Anxiety',
    'Frustration & irritability', 'Social functioning', 'Motivation deficits',
    'Word-finding difficulty', 'Decision-making',
  ],
  functionalDomains: [
    'Return-to-work / study capacity',
    'Physical activity & exercise tolerance',
    'Social & interpersonal relationships',
    'Self-care & daily routines',
    'Driving & community independence',
  ],
  networkMapping: [
    { network: 'Left DLPFC (CEN-L)',   role: 'Cognitive control & processing speed deficits', evidence: 'Concentration, memory, processing speed',      priority: 'Primary' },
    { network: 'Default Mode (DMN)',    role: 'Disrupted resting-state connectivity (DAI)',    evidence: 'Fatigue, mood, memory consolidation',          priority: 'Primary' },
    { network: 'Salience (SN)',         role: 'Aberrant pain / threat / interoception',        evidence: 'Headache, light/noise sensitivity, anxiety',  priority: 'Secondary' },
    { network: 'Cerebellum / Vestibular', role: 'Balance & co-ordination pathology',          evidence: 'Balance, dizziness, vestibular symptoms',     priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on TBI severity (mild/mTBI-concussion / moderate / severe) and dominant symptom cluster: Cognitive / Affective / Somatic / Mixed. Record chronicity (acute <6 weeks / subacute / chronic >6 months). Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with post-TBI syndrome. Diffuse axonal injury pattern likely underlies network-level dysconnectivity. Anodal tDCS to left DLPFC, TPS targeting pericontusional cortex, and taVNS for vagal anti-inflammatory and noradrenergic modulation is indicated pending full phenotyping.',
};
