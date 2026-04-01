'use strict';
module.exports = {
  conditionFull:  'Obsessive-Compulsive Disorder (OCD)',
  conditionShort: 'OCD',
  primarySymptoms: [
    'Obsession frequency', 'Obsession-related distress', 'Time occupied by obsessions',
    'Compulsion frequency', 'Compulsion-related distress', 'Resistance to compulsions',
    'Control over compulsions', 'Insight / overvalued ideation',
  ],
  secondarySymptoms: [
    'Anxiety', 'Depression', 'Avoidance behaviours',
    'Social impairment', 'Work / academic impact', 'Sleep disturbance',
    'Decision-making difficulty', 'Frustration & distress tolerance',
  ],
  functionalDomains: [
    'Time lost to obsessions / compulsions daily',
    'Occupational & academic functioning',
    'Social & family relationships',
    'Avoidance impact on activities',
    'Emotional regulation & distress tolerance',
  ],
  networkMapping: [
    { network: 'Cortico-Striato-Thalamo-Cortical (CSTC)', role: 'Hyperactive loop driving obsessions & compulsions', evidence: 'Obsession/compulsion frequency, distress',   priority: 'Primary' },
    { network: 'Left DLPFC / OFC',  role: 'Inhibitory control failure over intrusive thoughts',   evidence: 'Control, resistance, insight deficits',          priority: 'Primary' },
    { network: 'Salience (SN)',      role: 'Error-detection hyperactivity (anterior cingulate)',   evidence: 'Distress, anxiety, intolerance of uncertainty',  priority: 'Secondary' },
    { network: 'Default Mode (DMN)', role: 'Ego-dystonic rumination & threat appraisal',           evidence: 'Obsessive thinking, avoidance',                  priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on predominant dimension: Contamination-Washing / Symmetry-Ordering / Harm-Checking / Intrusive Thoughts / Hoarding. Record insight level (good / fair / poor). Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with OCD. CSTC loop hyperactivity with OFC/DLPFC inhibitory failure is the likely neurobiological substrate. Inhibitory tDCS to right DLPFC / OFC combined with SMA modulation and taVNS is indicated pending full phenotyping.',
};
