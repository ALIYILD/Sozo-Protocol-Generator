'use strict';
module.exports = {
  conditionFull:  "Alzheimer's Disease / Mild Cognitive Impairment (MCI)",
  conditionShort: "Alzheimer's",
  primarySymptoms: [
    'Short-term memory', 'Long-term memory', 'Word-finding difficulty',
    'Orientation (time/place/person)', 'Decision-making', 'Problem-solving',
    'New learning ability', 'Recognition / recall',
  ],
  secondarySymptoms: [
    'Depression / low mood', 'Anxiety', 'Apathy',
    'Sleep disturbance', 'Agitation / restlessness', 'Wandering behaviour',
    'Appetite change', 'ADL independence',
  ],
  functionalDomains: [
    'Memory & instrumental ADLs',
    'Safety & supervision needs',
    'Social & family relationships',
    'Communication & language',
    'Physical health & mobility',
  ],
  networkMapping: [
    { network: 'Default Mode (DMN)',       role: 'Hippocampal-cortical memory consolidation failure', evidence: 'Short-term memory, learning deficits',        priority: 'Primary' },
    { network: 'Left DLPFC (CEN-L)',       role: 'Executive & working memory decline',               evidence: 'Decision-making, problem-solving',            priority: 'Primary' },
    { network: 'Salience (SN)',            role: 'Impaired attentional switching & interoception',   evidence: 'Agitation, apathy, orientation deficit',      priority: 'Secondary' },
    { network: 'Parietal / Temporal',      role: 'Language & visuospatial processing deficits',      evidence: 'Word-finding, recognition difficulty',        priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on dominant profile: Amnestic / Language / Visuospatial / Behavioural-Dysexecutive. Classify MCI vs mild-moderate-severe AD. Record in SOZO Phenotype Classification document.',
  clinicalImpression: "Patient presents with features consistent with Alzheimer's disease / MCI. DMN degeneration drives episodic memory failure. TPS (hippocampus/entorhinal) combined with anodal tDCS to left DLPFC and taVNS for cholinergic modulation is indicated pending full phenotyping.",
};
