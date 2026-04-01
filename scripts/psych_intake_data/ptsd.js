'use strict';
module.exports = {
  conditionFull:  'Post-Traumatic Stress Disorder (PTSD)',
  conditionShort: 'PTSD',
  primarySymptoms: [
    'Intrusive memories / thoughts', 'Flashbacks', 'Nightmares',
    'Emotional reactivity', 'Situational avoidance', 'Cognitive avoidance',
    'Hypervigilance', 'Exaggerated startle response',
  ],
  secondarySymptoms: [
    'Sleep disturbance', 'Depression', 'Anger / aggression',
    'Concentration difficulty', 'Guilt / shame', 'Emotional detachment',
    'Trust difficulties', 'Substance use',
  ],
  functionalDomains: [
    'Occupational & daily functioning',
    'Social & intimate relationships',
    'Avoidance impact on daily life',
    'Physical health & somatic symptoms',
    'Safety & risk behaviours',
  ],
  networkMapping: [
    { network: 'Salience (SN) / Amygdala', role: 'Threat hyperactivation & fear extinction failure', evidence: 'Hypervigilance, startle, emotional reactivity', priority: 'Primary' },
    { network: 'Left DLPFC (CEN-L)',        role: 'Impaired prefrontal inhibition of amygdala',      evidence: 'Emotional dysregulation, anger, reactivity',  priority: 'Primary' },
    { network: 'Default Mode (DMN)',         role: 'Trauma-related rumination & self-narrative',      evidence: 'Intrusions, flashbacks, guilt/shame',         priority: 'Secondary' },
    { network: 'Hippocampal / Memory',       role: 'Contextual fear memory reconsolidation deficit',  evidence: 'Nightmares, intrusions, avoidance',           priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant cluster: Re-experiencing / Avoidance-Numbing / Hyperarousal / Dissociative subtype. Assess complex trauma (C-PTSD) features. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with PTSD. Amygdala hyperactivation with left DLPFC hypoactivation drives fear dysregulation and extinction failure. Anodal tDCS to left DLPFC combined with taVNS (parasympathetic / vagal tone restoration) and TPS targeting prefrontal cortex is indicated pending full phenotyping.',
};
