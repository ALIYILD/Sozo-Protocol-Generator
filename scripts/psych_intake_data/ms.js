'use strict';
module.exports = {
  conditionFull:  'Multiple Sclerosis (MS)',
  conditionShort: 'MS',
  primarySymptoms: [
    'Fatigue severity', 'Walking distance & speed', 'Hand & arm co-ordination',
    'Balance', 'Visual symptoms (blurring / diplopia)', 'Spasticity',
    'Bladder / bowel dysfunction', 'Sensory symptoms (numbness / tingling)',
  ],
  secondarySymptoms: [
    'Cognitive fog', 'Depression', 'Sleep disturbance',
    'Pain (neuropathic / musculoskeletal)', 'Heat sensitivity (Uhthoff)', 'Social functioning',
    'Work capacity', 'Independence with ADLs',
  ],
  functionalDomains: [
    'Mobility & physical function',
    'Occupational & community participation',
    'Self-care & ADL independence',
    'Social & recreational activities',
    'Emotional & psychological wellbeing',
  ],
  networkMapping: [
    { network: 'Motor / Corticospinal',  role: 'Demyelination → motor conduction failure',        evidence: 'Walking, co-ordination, spasticity',          priority: 'Primary' },
    { network: 'Left DLPFC (CEN-L)',     role: 'MS cognitive impairment (MSCI)',                  evidence: 'Cognitive fog, memory, processing speed',     priority: 'Primary' },
    { network: 'Salience (SN)',          role: 'MS fatigue & pain amplification',                 evidence: 'Fatigue, pain, bladder urgency',               priority: 'Secondary' },
    { network: 'Cerebellar / Vestibular', role: 'Co-ordination & balance pathology',              evidence: 'Balance, co-ordination, sensory symptoms',    priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant symptom profile and MS subtype: RRMS / SPMS / PPMS. Note EDSS score if available. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with MS. Dominant fatigue and cognitive fog suggest central network dysconnectivity beyond focal lesion load. Anodal tDCS to left DLPFC, TPS targeting motor cortex, and taVNS for neuroprotection and fatigue modulation is indicated pending full phenotyping.',
};
