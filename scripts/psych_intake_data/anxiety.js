'use strict';
module.exports = {
  conditionFull:  'Generalized Anxiety Disorder (GAD)',
  conditionShort: 'Anxiety',
  primarySymptoms: [
    'Worry frequency', 'Controllability of worry', 'Restlessness',
    'Muscle tension', 'Irritability', 'Concentration difficulty',
    'Fatigue', 'Panic attacks',
  ],
  secondarySymptoms: [
    'Sleep disturbance', 'Depression', 'Avoidance behaviours',
    'Social anxiety', 'GI / cardiac symptoms', 'Catastrophising',
    'Difficulty with decisions', 'Hypervigilance',
  ],
  functionalDomains: [
    'Occupational / academic performance',
    'Social & interpersonal functioning',
    'Avoidance impact on daily activities',
    'Physical health symptoms',
    'Leisure & quality of life',
  ],
  networkMapping: [
    { network: 'Salience (SN)',           role: 'Threat over-detection & alarm response',    evidence: 'Hypervigilance, panic, muscle tension', priority: 'Primary' },
    { network: 'Default Mode (DMN)',       role: 'Worry rumination & anticipatory processing', evidence: 'Controllability of worry, catastrophising', priority: 'Primary' },
    { network: 'Right DLPFC (CEN-R)',      role: 'Inhibitory control deficit',                evidence: 'Concentration, decision difficulty',       priority: 'Secondary' },
    { network: 'Insula / Interoception',   role: 'Somatic amplification',                     evidence: 'GI/cardiac symptoms, restlessness',        priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant cluster: Somatic-predominant / Cognitive-predominant / Panic-predominant / Social-predominant. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with features consistent with GAD. Salience Network hyperactivity drives threat over-detection and autonomic arousal. DMN rumination sustains worry cycles. Right DLPFC modulation (inhibitory tDCS) combined with taVNS for autonomic regulation is indicated pending full phenotyping.',
};
