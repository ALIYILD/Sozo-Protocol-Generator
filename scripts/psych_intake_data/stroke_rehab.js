'use strict';
module.exports = {
  conditionFull:  'Post-Stroke Rehabilitation',
  conditionShort: 'Stroke',
  primarySymptoms: [
    'Arm / hand strength', 'Leg strength & mobility', 'Hand dexterity',
    'Walking ability', 'Balance', 'Speech & language',
    'Swallowing', 'Facial movement',
  ],
  secondarySymptoms: [
    'Fatigue', 'Post-stroke depression', 'Cognitive impairment',
    'Post-stroke pain', 'Sleep disturbance', 'Visual field deficit',
    'Spatial / perceptual awareness', 'ADL independence',
  ],
  functionalDomains: [
    'Motor function & mobility',
    'Communication & speech',
    'Self-care & ADL independence',
    'Community participation',
    'Emotional & psychological wellbeing',
  ],
  networkMapping: [
    { network: 'Motor / Corticospinal',    role: 'Primary motor cortex lesion → contralateral deficit', evidence: 'Arm/leg strength, dexterity, walking',     priority: 'Primary' },
    { network: 'Language (Broca/Wernicke)', role: 'Aphasia / dysarthria from perisylvian lesion',        evidence: 'Speech, language, communication',         priority: 'Primary' },
    { network: 'Left DLPFC (CEN-L)',       role: 'Post-stroke cognitive impairment',                    evidence: 'Cognition, attention, executive function', priority: 'Secondary' },
    { network: 'Salience (SN)',            role: 'Post-stroke depression & fatigue regulation',         evidence: 'Depression, fatigue, emotional lability',  priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on stroke location and dominant deficit: Motor-predominant / Aphasia-predominant / Cognitive / Mixed. Record stroke chronicity (acute/subacute/chronic). Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents for post-stroke rehabilitation. Motor deficits suggest primary motor cortex / corticospinal involvement. TPS targeting perilesional cortex combined with excitatory tDCS (ipsilesional M1) and inhibitory (contralesional M1) is indicated. Post-stroke depression and fatigue warrant concurrent FNON protocol pending full phenotyping.',
};
