'use strict';
module.exports = {
  conditionFull:  'Chronic Tinnitus',
  conditionShort: 'Tinnitus',
  primarySymptoms: [
    'Tinnitus loudness (NRS)', 'Distress / emotional impact', 'Intrusiveness into daily life',
    'Sound sensitivity (hyperacusis)', 'Concentration impact', 'Severity in quiet environments',
    'Perceived hearing loss', 'Effectiveness of masking',
  ],
  secondarySymptoms: [
    'Sleep onset difficulty', 'Sleep maintenance', 'Depression / low mood',
    'Anxiety', 'Irritability', 'Social avoidance',
    'Work / occupational impact', 'Relaxation ability',
  ],
  functionalDomains: [
    'Sleep quality & quantity',
    'Occupational & concentration tasks',
    'Social & recreational activities',
    'Emotional wellbeing',
    'Communication & hearing function',
  ],
  networkMapping: [
    { network: 'Auditory Cortex / Tonotopy', role: 'Maladaptive cortical reorganisation → phantom sound', evidence: 'Tinnitus loudness, intrusiveness, masking', priority: 'Primary' },
    { network: 'Salience (SN)',               role: 'Hypervigilance to tinnitus signal & distress',       evidence: 'Distress, concentration impact, anxiety',  priority: 'Primary' },
    { network: 'Default Mode (DMN)',          role: 'Tinnitus rumination & catastrophising',               evidence: 'Intrusiveness, depression, withdrawal',     priority: 'Secondary' },
    { network: 'Left DLPFC (CEN-L)',          role: 'Top-down auditory gating deficit',                   evidence: 'Concentration, sleep, work impact',         priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on audiological profile and dominant distress dimension: Compensated / Decompensated / Hyperacusis-predominant / Sleep-predominant. Record audiogram findings and tinnitus duration. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with chronic tinnitus causing significant distress. Maladaptive auditory cortical reorganisation with Salience Network hyperactivation is the likely neurobiological substrate. TPS targeting auditory cortex combined with cathodal tDCS (inhibitory) and anodal left DLPFC, plus taVNS for salience modulation, is indicated pending full phenotyping.',
};
