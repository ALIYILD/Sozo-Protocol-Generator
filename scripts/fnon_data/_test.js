'use strict';
module.exports = {
  conditionFull: 'Test Condition',
  conditionShort: 'Test',
  conditionSlug: '_test',
  documentNumber: 'SOZO-TEST-PROT-001',
  overviewParagraph: 'Test overview.',
  cardinalSymptoms: [
    ['Symptom 1', 'Features', '80%', 'Ref 2024'],
    ['Symptom 2', 'Features', '70%', 'Ref 2023'],
  ],
  keyBrainRegions: [
    ['DLPFC', 'Role', 'Rationale', 'Ref'],
    ['ACC',   'Role', 'Rationale', 'Ref'],
  ],
  additionalBrainStructures: [['Hippocampus', 'Role', 'Rationale', 'Ref']],
  keyFunctionalNetworks: [
    ['DMN', 'mPFC, PCC', 'Hyperconnectivity', 'tDCS (DLPFC)', 'Ref'],
  ],
  clinicalPhenotypes: [['Phenotype 1', 'CEN hypofunction', 'Ref']],
  symptomNetworkMapping: [['Symptom', 'CEN', 'DMN', 'tDCS DLPFC', 'Emerging']],
  montageSelectionRows: [['Cognitive dominant', 'HDCstim tDCS F3/F4 anode']],
  classicTdcsProtocols: [['C1', 'Mood', 'F3', 'Pz', '2mA 20min', 'Level B']],
  fnonTdcsProtocols: [['F1', 'Executive', 'CEN hypofunction', 'F3/F4 anodes', 'Restore CEN']],
  classicTpsProtocols: [['T1', 'Core symptoms', 'DLPFC', '0.2mJ/mm²', '4000 pulses', 'Emerging']],
  fnonTpsProtocols: [['FT1', 'Phenotype 1', 'CEN', 'DLPFC + Holocranial', '6000 pulses', '10 sessions']],
  multimodalPhenotypes: [],
  references: {
    foundational: ['Author A. (2020). Title. Journal.'],
    tdcs: ['Author B. (2023). Title. Journal.'],
    tps: ['Author C. (2024). Title. Journal.'],
    tavns: ['Author D. (2022). Title. Journal.'],
    ces: ['Author E. (2021). Title. Journal.'],
    network: ['Author F. (2023). Title. Journal.'],
  },
};
