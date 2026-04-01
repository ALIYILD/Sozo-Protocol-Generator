'use strict';
module.exports = {
  conditionFull:  'Major Depressive Disorder (MDD)',
  conditionShort: 'Depression',
  primarySymptoms: [
    'Depressed mood', 'Anhedonia', 'Guilt / worthlessness',
    'Fatigue', 'Psychomotor change', 'Concentration difficulty',
    'Appetite disturbance', 'Suicidal ideation',
  ],
  secondarySymptoms: [
    'Sleep disturbance', 'Anxiety', 'Irritability',
    'Social withdrawal', 'Libido reduction', 'Pain / somatic',
    'Low self-esteem', 'Loss of motivation',
  ],
  functionalDomains: [
    'Occupational / academic functioning',
    'Social & interpersonal functioning',
    'Self-care & activities of daily living',
    'Leisure & recreational activities',
    'Physical health & exercise',
  ],
  networkMapping: [
    { network: 'Default Mode (DMN)',    role: 'Rumination & self-referential processing', evidence: 'Guilt, worthlessness, anhedonia', priority: 'Primary' },
    { network: 'Salience (SN)',         role: 'Aberrant threat & reward salience',         evidence: 'Depressed mood, irritability',   priority: 'Primary' },
    { network: 'Left DLPFC (CEN-L)',    role: 'Cognitive control deficit',                 evidence: 'Concentration, decision-making', priority: 'Secondary' },
    { network: 'Reward / Limbic',       role: 'Anhedonia & motivational deficits',         evidence: 'Anhedonia, loss of motivation',  priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant cluster: Melancholic / Atypical / Anxious-Distressed / Mixed Features. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with features consistent with MDD. Dominant symptom clusters suggest DMN hyperactivity with SN dysregulation. Left DLPFC hypoactivation likely contributes to cognitive symptoms. Partners-tier FNON protocol targeting left DLPFC (excitatory tDCS/TPS) and DMN modulation is indicated pending full phenotyping.',
};
