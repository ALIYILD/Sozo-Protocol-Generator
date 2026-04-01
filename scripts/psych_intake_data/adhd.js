'use strict';
module.exports = {
  conditionFull:  'Attention-Deficit / Hyperactivity Disorder (ADHD)',
  conditionShort: 'ADHD',
  primarySymptoms: [
    'Inattention', 'Distractibility', 'Task completion difficulty',
    'Organisation problems', 'Forgetfulness', 'Hyperactivity',
    'Impulsivity', 'Time management',
  ],
  secondarySymptoms: [
    'Emotional dysregulation', 'Frustration tolerance', 'Sleep disturbance',
    'Low self-esteem', 'Relationship difficulties', 'Motivation deficits',
    'Procrastination', 'Restlessness',
  ],
  functionalDomains: [
    'Academic / occupational performance',
    'Organisation & time management',
    'Social & interpersonal relationships',
    'Self-care & routine maintenance',
    'Emotional regulation in daily life',
  ],
  networkMapping: [
    { network: 'Left DLPFC (CEN-L)',   role: 'Executive function & working memory deficit', evidence: 'Inattention, task completion, organisation',    priority: 'Primary' },
    { network: 'Default Mode (DMN)',    role: 'Task-inappropriate DMN activation (mind-wandering)', evidence: 'Distractibility, forgetfulness',        priority: 'Primary' },
    { network: 'Salience (SN)',         role: 'Impaired salience switching CEN↔DMN',        evidence: 'Impulsivity, emotional dysregulation',        priority: 'Secondary' },
    { network: 'Reward / Limbic',       role: 'Dopaminergic reward dysregulation',          evidence: 'Motivation deficits, procrastination',        priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant presentation: Inattentive / Hyperactive-Impulsive / Combined / Emotional-Dysregulation predominant. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with features consistent with ADHD. Left DLPFC hypoactivation underlies executive function deficits. DMN fails to suppress during task engagement. SOZO tDCS protocol targeting left DLPFC (anodal) with taVNS for dopaminergic modulation is indicated pending full phenotyping.',
};
