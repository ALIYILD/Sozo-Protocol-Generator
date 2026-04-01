'use strict';
module.exports = {
  conditionFull:  'Autism Spectrum Disorder (ASD)',
  conditionShort: 'ASD',
  primarySymptoms: [
    'Social interaction quality', 'Communication (verbal / non-verbal)', 'Repetitive behaviours',
    'Sensory sensitivity (over / under)', 'Routine rigidity & inflexibility', 'Emotional regulation',
    'Eye contact & joint attention', 'Social reciprocity',
  ],
  secondarySymptoms: [
    'Anxiety', 'Sleep disturbance', 'Attention & concentration',
    'Executive function', 'Frustration & meltdowns', 'Self-care & adaptive skills',
    'Peer relationships', 'Meltdown / shutdown frequency',
  ],
  functionalDomains: [
    'Social & peer interactions',
    'Communication & language',
    'Academic / occupational functioning',
    'Adaptive behaviour & self-care',
    'Sensory processing in daily life',
  ],
  networkMapping: [
    { network: 'Social Brain (TPJ / mPFC)', role: 'Theory of mind & mentalising deficit',          evidence: 'Social interaction, reciprocity, eye contact', priority: 'Primary' },
    { network: 'Salience (SN)',              role: 'Sensory dysregulation & threat over-detection', evidence: 'Sensory sensitivity, meltdowns, anxiety',     priority: 'Primary' },
    { network: 'Left DLPFC (CEN-L)',         role: 'Executive function & cognitive flexibility',    evidence: 'Routine rigidity, executive function deficits', priority: 'Secondary' },
    { network: 'Default Mode (DMN)',          role: 'Reduced self-referential & social cognition',  evidence: 'Communication, repetitive behaviours, anxiety', priority: 'Secondary' },
  ],
  phenotypeNote: 'Assign based on support needs level (DSM-5 Level 1/2/3) and dominant profile: Social-communication predominant / Sensory-predominant / Executive-predominant / Anxiety-predominant. Record in SOZO Phenotype Classification document.',
  clinicalImpression: 'Patient presents with ASD. Social brain network hypoconnectivity combined with Salience Network hypersensitivity is the likely neurobiological basis. tDCS targeting right DLPFC / TPJ and taVNS for autonomic regulation and social engagement via vagal pathways is indicated pending full phenotyping.',
};
