'use strict';
module.exports = {
  conditionFull:  'Chronic Pain / Fibromyalgia',
  conditionShort: 'Chronic Pain',
  primarySymptoms: [
    'Pain intensity (NRS 0–10)', 'Pain frequency', 'Pain interference with activity',
    'Widespread tenderness', 'Stiffness', 'Fatigue related to pain',
    'Physical function capacity', 'Flare frequency',
  ],
  secondarySymptoms: [
    'Sleep disturbance', 'Depression', 'Anxiety',
    'Cognitive fog (fibro-fog)', 'Social withdrawal', 'Medication dependence',
    'Exercise tolerance', 'Quality of life',
  ],
  functionalDomains: [
    'Physical mobility & activity',
    'Occupational functioning',
    'Social & recreational activities',
    'Sleep quality & rest',
    'Medication use & side-effects',
  ],
  networkMapping: [
    { network: 'Salience (SN)',         role: 'Central sensitisation & pain amplification',  evidence: 'Pain intensity, tenderness, flares',          priority: 'Primary' },
    { network: 'Default Mode (DMN)',     role: 'Pain rumination & catastrophising',           evidence: 'Cognitive fog, depression, withdrawal',       priority: 'Primary' },
    { network: 'Left DLPFC (CEN-L)',    role: 'Descending pain inhibition deficit',          evidence: 'Pain interference, anxiety, concentration',   priority: 'Secondary' },
    { network: 'Insula / Interoception', role: 'Somatic amplification & interoceptive bias', evidence: 'Fatigue, stiffness, widespread tenderness',   priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant pattern: Nociceptive / Nociplastic (central sensitisation) / Neuropathic / Mixed. For fibromyalgia confirm WPI ≥7 + SS ≥5. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with chronic pain / fibromyalgia consistent with central sensitisation syndrome. Salience Network hyperexcitability drives pain amplification. Anodal tDCS to left DLPFC (descending inhibition enhancement) combined with TPS and taVNS (anti-inflammatory / vagal pathway) is indicated pending full phenotyping.',
};
