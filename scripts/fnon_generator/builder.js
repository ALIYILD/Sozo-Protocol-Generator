/**
 * SOZO FNON Clinical Protocol — Document A (Partners Tier) Builder
 * Generates all 13 sections + references matching the PD template exactly.
 *
 * Usage:
 *   const builder = require('./builder');
 *   const doc = builder.buildDocument(conditionData);
 *   const Packer = require('docx').Packer;
 *   Packer.toBuffer(doc).then(buf => fs.writeFileSync(outPath, buf));
 */
'use strict';

const {
  Document,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  HeadingLevel,
  AlignmentType,
  WidthType,
  BorderStyle,
  ShadingType,
  VerticalAlign,
  PageOrientation,
  convertInchesToTwip,
  Packer,
} = require('docx');

const S = require('./styles');
const T = require('./tables');

// ─── CONSTANTS ────────────────────────────────────────────────────────────────

const PAGE_W  = convertInchesToTwip(8.5);
const PAGE_H  = convertInchesToTwip(11);
const MARGIN  = convertInchesToTwip(1);
const CONTENT = PAGE_W - 2 * MARGIN; // ~9360

// ─── SECTION BUILDERS ─────────────────────────────────────────────────────────

function coverPage(d) {
  return [
    S.emptyPara(),
    S.emptyPara(),
    S.emptyPara(),
    new Paragraph({
      children: [new TextRun({ text: 'SOZO BRAIN CENTER — CYPRUS', color: S.NAVY, bold: true, size: 36, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
    }),
    new Paragraph({
      children: [new TextRun({ text: 'FNON CLINICAL PROTOCOL', color: S.BLUE, bold: true, size: 32, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
    }),
    new Paragraph({
      children: [new TextRun({ text: 'Functional Network-Oriented Neuromodulation for', color: S.NAVY, size: 26, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 60 },
    }),
    new Paragraph({
      children: [new TextRun({ text: d.conditionFull.toUpperCase(), color: S.NAVY, bold: true, size: 32, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 160 },
    }),
    new Paragraph({
      children: [new TextRun({ text: `Integrating tDCS (Newronika HDCkit & PlatoScience) & TPS (NEUROLITH®) with taVNS & CES`, color: S.NAVY, size: 22, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 160 },
    }),
    new Paragraph({
      children: [new TextRun({ text: 'DOCUMENT A — FULL CLINICAL PROTOCOL', color: S.NAVY, bold: true, size: 26, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 100 },
    }),
    new Paragraph({
      children: [new TextRun({ text: 'PARTNERS TIER — FNON + Evidence-Based Protocols', color: S.PURPLE, bold: true, size: 24, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 160 },
    }),
    new Paragraph({
      children: [new TextRun({ text: 'Version 7.0 | February 2026 | For use by the treating Doctor only', color: S.NAVY, size: 22, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 120 },
    }),
    new Paragraph({
      children: [new TextRun({ text: 'CONFIDENTIAL — For authorised SOZO personnel only.', color: S.RED, bold: true, size: 22, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 80 },
    }),
    new Paragraph({
      children: [new TextRun({ text: d.offLabelCoverText || `TPS use in ${d.conditionShort} is INVESTIGATIONAL / OFF-LABEL.`, color: S.RED, bold: true, size: 22, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),
    S.emptyPara(),
    S.emptyPara(),
    S.emptyPara(),
    S.emptyPara(),
    S.emptyPara(),
    S.emptyPara(),
    new Paragraph({
      children: [new TextRun({ text: '© 2026 SOZO Brain Center. All rights reserved.', color: S.NAVY, size: 18, font: 'Calibri' })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 120 },
    }),
  ];
}

function tableOfContents() {
  const sections = [
    '1. Document Control & Clinical Responsibility',
    '2. Inclusion and Exclusion Criteria',
    `3. Condition Overview`,
    '4. Pathophysiology, Symptoms & Standard Guidelines',
    '5. Key Brain Structures and Networks Involved',
    '6. Clinical Phenotypes and Symptom–Network Mapping',
    '7. Applying NIBS According to the SOZO FNON Concept',
    '8. Most Studied and FNON-Based Montages',
    '9. Combination of NIBS Techniques',
    '10. Side Effects and Monitoring',
    '11. In-Clinic and Home-Based Tasks',
    '12. Follow-Up Assessments and Decision-Making',
    '13. References',
  ];
  return [
    S.h1('Table of Contents'),
    S.emptyPara(),
    ...sections.map(s => new Paragraph({
      children: [new TextRun({ text: s, color: S.BLACK, size: 22, font: 'Calibri' })],
      spacing: { after: 60 },
    })),
    S.emptyPara(),
  ];
}

function section1(d) {
  const items = [];

  items.push(S.h1('1. Document Control & Clinical Responsibility'));
  items.push(S.bodyPara(`This section establishes the governance framework for the SOZO FNON Clinical Protocol for ${d.conditionFull}. All clinical activities described in this document must be conducted under the supervision and authorisation of a qualified Doctor. Clinical Assistants and Partners operate within clearly defined scopes of practice.`));

  items.push(S.h2('Document Information'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Field', 'Details'],
    [
      ['Document Title', `SOZO FNON Clinical Protocol — ${d.conditionFull}`],
      ['Document Number', d.documentNumber || `SOZO-${d.conditionSlug.toUpperCase()}-PROT-001`],
      ['Version', '7.0'],
      ['Date', 'February 2026'],
      ['Author', 'SOZO Brain Center Clinical Team'],
      ['Approved By', 'Medical Director, SOZO Brain Center'],
      ['Review Cycle', 'Annual or upon significant new evidence'],
      ['Classification', 'PARTNERS TIER — Restricted Distribution'],
    ],
    { widths: [Math.floor(CONTENT * 0.35), Math.floor(CONTENT * 0.65)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2('Roles and Responsibilities'));
  items.push(S.bodyPara(`Clear delineation of clinical responsibilities ensures patient safety and regulatory compliance. The Doctor retains full clinical and legal responsibility for all treatment decisions.`));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Role', 'Clinical Scope', 'Responsibilities'],
    [
      ['Doctor', 'Overall governance; protocol approval; treatment decisions', 'Approves protocols; authorises off-label use; reviews outcomes; manages adverse events'],
      ['Clinical Assistant / Partner', 'Device operation; session delivery; data recording', 'Delivers sessions per Doctor-prescribed protocol; documents all sessions; escalates concerns immediately'],
    ],
    { widths: [Math.floor(CONTENT * 0.2), Math.floor(CONTENT * 0.35), Math.floor(CONTENT * 0.45)] }
  ));
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [
      new TextRun({ text: '⚠ ', color: S.RED, bold: true, size: 22, font: 'Calibri' }),
      new TextRun({ text: 'No Clinical Assistant may independently modify a treatment plan, change a montage, or adjust parameters without Doctor authorisation. All deviations must be documented and countersigned by the supervising Doctor.', color: S.RED, bold: true, size: 22, font: 'Calibri' }),
    ],
    spacing: { after: 120 },
  }));

  items.push(S.h2('Off-Label Disclosure'));
  items.push(S.bodyPara(`Standard informed consent is used for all modalities. The table below outlines the regulatory status of each technique as applied to ${d.conditionShort}.`));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Modality', 'Regulatory Status', `Classification for ${d.conditionShort}`, 'Disclosure'],
    d.offLabelTable || [
      ['tDCS', 'CE-marked (Class IIa)', 'Off-label; growing evidence base', 'Standard informed consent'],
      ['TPS', 'CE-marked (Class IIa)', 'INVESTIGATIONAL / OFF-LABEL', 'Mandatory off-label disclosure; Doctor signature required'],
      ['taVNS', 'CE-marked (Class IIa)', 'Off-label; evidence emerging', 'Standard informed consent + off-label note'],
      ['CES (Alpha-Stim)', 'FDA-cleared; CE-marked', 'Off-label for specific indication', 'Standard informed consent'],
    ],
    { widths: [Math.floor(CONTENT*0.15), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.3), Math.floor(CONTENT*0.35)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2('Document Structure'));
  items.push(new Paragraph({
    children: [new TextRun({ text: 'This protocol is organised into thirteen integrated sections covering the full clinical pathway from patient selection through to outcome monitoring and follow-up decision-making.', color: S.BLACK, size: 22, font: 'Calibri' })],
    spacing: { after: 80 },
  }));
  const docStructure = [
    'Document control and clinical responsibility',
    'Inclusion and exclusion criteria',
    'Condition overview',
    'Pathophysiology, symptoms, and standard guidelines',
    'Key brain structures and networks involved',
    'Clinical phenotypes and dominant network features',
    'Symptom–Network–Modality mapping',
    'Applying NIBS according to the SOZO FNON concept',
    'Most studied and FNON-based montages',
    'Combination of NIBS techniques',
    'Side effects and monitoring',
    'In-clinic and home-based tasks',
    'Follow-up assessments and decision-making',
  ];
  docStructure.forEach(s => {
    items.push(new Paragraph({
      children: [new TextRun({ text: s, color: S.BLACK, size: 22, font: 'Calibri' })],
      spacing: { after: 60 },
    }));
  });

  return items;
}

function section2(d) {
  const items = [];
  items.push(S.h1('2. Inclusion and Exclusion Criteria'));
  items.push(S.bodyPara(`Careful patient selection is essential for both safety and efficacy. The following criteria guide eligibility for the SOZO FNON programme in ${d.conditionShort}.`));

  items.push(S.h2('Inclusion Criteria'));
  items.push(S.emptyPara());
  const inclRows = (d.inclusionCriteria || [
    [`Confirmed diagnosis of ${d.conditionShort} by a qualified clinician`],
    ['Age 18–80 years (exceptions at Doctor discretion with documented rationale)'],
    ['Stable pharmacological treatment for ≥4 weeks prior to enrolment'],
    ['Capacity to provide informed consent'],
    ['Willing and able to attend sessions as prescribed'],
    ['No absolute contraindications to any planned modality'],
    ['Baseline clinical assessment completed and documented'],
  ]).map((r, i) => [String(i + 1), Array.isArray(r) ? r[0] : r]);
  items.push(T.buildTable(['#', 'Criterion'], inclRows,
    { widths: [Math.floor(CONTENT*0.08), Math.floor(CONTENT*0.92)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2('Exclusion Criteria (Absolute)'));
  items.push(S.emptyPara());
  const exclRows = (d.exclusionCriteria || [
    ['Intracranial metallic hardware in the stimulation field'],
    ['Cochlear implant'],
    ['Active deep brain stimulator (DBS)'],
    ['Skull defect or craniotomy site over target area'],
    ['Open scalp wound or infection at electrode site'],
    ['Active psychosis or acute suicidality requiring urgent psychiatric care'],
    ['Pregnancy (TPS contraindicated; tDCS/taVNS at Doctor discretion)'],
    ['Known hypersensitivity to electrical stimulation'],
  ]).map((r, i) => [String(i + 1), Array.isArray(r) ? r[0] : r]);
  items.push(T.buildTable(['#', 'Exclusion Criterion'], exclRows,
    { widths: [Math.floor(CONTENT*0.08), Math.floor(CONTENT*0.92)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2('Conditions Requiring Discussion (NOT Absolute)'));
  items.push(S.emptyPara());
  const condRows = (d.conditionsRequiringDiscussion || [
    ['Cardiac pacemaker or defibrillator — individual risk-benefit by Doctor'],
    ['Epilepsy or seizure history — formal risk assessment required'],
    ['Severe anxiety or panic disorder — protocol modification may be needed'],
    ['Active dermatological conditions at electrode sites'],
    ['Recent major surgery (within 3 months)'],
    ['Significant cognitive impairment affecting consent capacity'],
    ['Concurrent participation in another interventional trial'],
    ['Substance misuse — stability and capacity assessment required'],
    ['Severe medical comorbidities — Doctor-led review required'],
  ]).map((r, i) => [String(i + 1), Array.isArray(r) ? r[0] : r]);
  items.push(T.buildTable(['#', 'Condition'], condRows,
    { widths: [Math.floor(CONTENT*0.08), Math.floor(CONTENT*0.92)] }
  ));
  items.push(S.emptyPara());
  items.push(S.bodyPara('The following conditions require a formal, documented risk–benefit assessment by the Doctor prior to enrolment. These are not absolute contraindications but require careful clinical judgement and may necessitate protocol modifications.'));
  items.push(S.emptyPara());
  items.push(S.emptyPara());

  return items;
}

function section3(d) {
  const items = [];
  items.push(S.h1(`3. Condition Overview: ${d.conditionFull}`));
  items.push(S.bodyPara(d.overviewParagraph || `${d.conditionFull} is a significant neuropsychiatric condition affecting millions worldwide. It is characterised by a constellation of symptoms that substantially impair daily functioning and quality of life. SOZO Brain Center applies the FNON framework to address the underlying network-level dysregulation driving these symptoms.`));
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [new TextRun({ text: d.fnonNetworkParagraph || `${d.conditionShort} is not only a symptom-defined disorder — it is a large-scale network dysregulation condition. The FNON framework identifies the distributed brain circuits contributing to each symptom domain, enabling precise neuromodulation targeting beyond single-region approaches.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());
  items.push(S.h2(`${d.conditionShort} as a Distributed Brain Network Disorder`));
  (d.networkDisorderParagraphs || [
    `Contemporary neuroscience frames ${d.conditionShort} as a disorder of large-scale brain network organisation rather than localised pathology. Converging evidence from neuroimaging, electrophysiology, and connectomics demonstrates that symptoms arise from dysregulated interactions among key brain networks including the Default Mode Network (DMN), Central Executive Network (CEN), Salience Network (SN), and Sensorimotor Network (SMN).`,
    `Functional connectivity studies consistently demonstrate altered coupling between nodes of the DMN and CEN, with the SN showing aberrant gating that impairs appropriate network switching. These network-level disruptions provide the mechanistic rationale for FNON-based neuromodulation targeting.`,
    `Network-focused neuromodulation targets the physiological mechanisms underlying these circuit-level dysfunctions, offering a more precise therapeutic approach than symptom-only interventions.`,
  ]).forEach(p => items.push(S.bodyPara(p)));
  items.push(S.emptyPara());

  return items;
}

function section4(d) {
  const items = [];
  items.push(S.h1('4. Pathophysiology, Symptoms & Standard Guidelines'));
  items.push(S.bodyPara(d.pathophysiologyText || `${d.conditionFull} pathophysiology involves complex interactions across multiple neurobiological systems. Current models emphasise dysregulation of monoaminergic neurotransmitter systems, hypothalamic-pituitary-adrenal axis dysfunction, and neuroinflammatory processes. Structural and functional neuroimaging studies consistently demonstrate abnormalities in prefrontal-limbic circuits, hippocampal volume, and default mode network connectivity.`));

  items.push(S.h2('Cardinal Symptoms'));
  items.push(S.emptyPara());
  const symptomRows = (d.cardinalSymptoms || []).map(row =>
    row.length >= 4 ? row.slice(0, 4) : [...row, ...Array(4 - row.length).fill('')]
  );
  if (symptomRows.length > 0) {
    items.push(T.buildTable(
      ['Symptom Domain', 'Key Features', 'Prevalence', 'References'],
      symptomRows,
      { widths: [Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.38), Math.floor(CONTENT*0.15), Math.floor(CONTENT*0.25)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2('Standard Treatment Guidelines'));
  (d.standardGuidelinesText || [`Current evidence-based clinical guidance positions pharmacological intervention as first-line treatment for ${d.conditionShort}. Non-pharmacological approaches including psychotherapy and neuromodulation are increasingly recognised as important adjunctive and, in selected cases, primary interventions. SOZO FNON protocols are designed to complement and enhance standard-of-care treatments.`]).forEach(t =>
    items.push(S.bodyPara(t))
  );
  items.push(S.emptyPara());

  return items;
}

function section5(d) {
  const items = [];
  items.push(S.h1('5. Key Brain Structures and Networks Involved'));
  items.push(new Paragraph({
    children: [new TextRun({ text: d.fnonFrameworkParagraph || `The FNON framework is built on the principle that ${d.conditionShort} symptoms arise from dysfunction within interconnected brain networks rather than isolated brain regions. SOZO's approach targets the specific network nodes most implicated in each patient's dominant symptom profile, with each modality selected for its capacity to reach and modulate those specific circuits.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());

  items.push(S.h2('Key Brain Regions and Neuromodulation Rationale'));
  items.push(S.emptyPara());
  if (d.keyBrainRegions && d.keyBrainRegions.length > 0) {
    items.push(T.buildTable(
      ['Brain Region', `Role in ${d.conditionShort}`, 'Neuromodulation Rationale', 'References'],
      d.keyBrainRegions.map(r => r.length >= 4 ? r.slice(0,4) : [...r, ...Array(4-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.22)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2(`Additional Brain Structures`));
  items.push(S.bodyPara(d.additionalStructuresIntro || `Beyond the primary cortical targets, several subcortical and brainstem structures play critical roles in ${d.conditionShort} pathophysiology and neuromodulation response.`));
  items.push(S.emptyPara());
  if (d.additionalBrainStructures && d.additionalBrainStructures.length > 0) {
    items.push(T.buildTable(
      ['Brain Region', `Role in ${d.conditionShort}`, 'Neuromodulation Rationale', 'References'],
      d.additionalBrainStructures.map(r => r.length >= 4 ? r.slice(0,4) : [...r, ...Array(4-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.22)] }
    ));
  }
  items.push(S.emptyPara());
  items.push(S.emptyPara());

  items.push(S.h2('Key Functional Networks'));
  items.push(new Paragraph({
    children: [new TextRun({ text: `Functional brain networks provide the organising principle for the FNON treatment approach. Rather than targeting single brain regions, SOZO protocols are designed to modulate the activity and connectivity of specific networks implicated in ${d.conditionShort} symptomatology.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());
  if (d.keyFunctionalNetworks && d.keyFunctionalNetworks.length > 0) {
    items.push(T.buildTable(
      ['Network', 'Key Nodes', `${d.conditionShort} Dysfunction`, `SOZO FNON Application`, 'References'],
      d.keyFunctionalNetworks.map(r => r.length >= 5 ? r.slice(0,5) : [...r, ...Array(5-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.15), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.25), Math.floor(CONTENT*0.18)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2('Network-Level Pathophysiological Abnormalities'));
  items.push(S.bodyPara(d.networkPathophysiologyIntro || `${d.conditionFull} is characterised by distributed network-level abnormalities that extend beyond single-region pathology.`));
  items.push(S.h3('Key Network Abnormalities'));
  (d.networkAbnormalities || [
    `Default Mode Network (DMN): Hyperconnectivity within the DMN is a hallmark finding, associated with rumination, self-referential processing, and impaired cognitive engagement.`,
    `Central Executive Network (CEN): Hypoactivation of the DLPFC and associated CEN nodes underlies cognitive symptoms including poor concentration, working memory deficits, and executive dysfunction.`,
    `Salience Network (SN): Aberrant salience gating impairs the ability to appropriately switch between DMN and CEN activity, perpetuating maladaptive cognitive-affective patterns.`,
    `Limbic Network: Dysregulation of amygdala-prefrontal circuitry contributes to emotional dysregulation, affective instability, and altered threat processing.`,
    `Sensorimotor Network (SMN): Psychomotor symptoms reflect SMN-prefrontal disconnection, particularly relevant in conditions with motor slowing or agitation.`,
  ]).forEach(a => items.push(S.bodyPara(a)));
  items.push(S.emptyPara());
  items.push(S.emptyPara());

  items.push(S.h3('Conceptual Framework'));
  items.push(S.bodyPara(d.conceptualFramework || `${d.conditionShort} is best understood as a network excitability and connectivity disorder. The FNON framework targets modifiable network states — particularly the balance between DMN hyperactivity and CEN hypoactivity — using multi-modal neuromodulation to restore adaptive network dynamics.`));

  return items;
}

function section6(d) {
  const items = [];
  items.push(S.h1('6. Clinical Phenotypes and Symptom–Network Mapping'));
  items.push(new Paragraph({
    children: [new TextRun({ text: `The FNON approach begins with clinical phenotyping: identifying the dominant symptom cluster in each patient and mapping it to the most likely dysfunctional network or network combination. This phenotype-to-network mapping guides modality selection, montage choice, and session structure for each individual patient with ${d.conditionShort}.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));

  items.push(S.h2('Clinical Phenotypes and Dominant Network Features'));
  items.push(S.emptyPara());
  if (d.clinicalPhenotypes && d.clinicalPhenotypes.length > 0) {
    items.push(T.buildTable(
      ['Clinical Phenotype', 'Hypothesised Dominant Network Dysfunction', 'Supporting References'],
      d.clinicalPhenotypes.map(r => r.length >= 3 ? r.slice(0,3) : [...r, ...Array(3-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.3), Math.floor(CONTENT*0.42), Math.floor(CONTENT*0.28)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2('Symptom–Network–Modality Mapping'));
  items.push(S.bodyPara(`The table below integrates symptom domains with their primary and secondary network associations and the recommended SOZO device integration for each target.`));
  if (d.symptomNetworkMapping && d.symptomNetworkMapping.length > 0) {
    items.push(T.buildTable(
      ['Symptom', 'Primary Network', 'Secondary Networks', 'SOZO Device Integration (FNON-Based)', 'Evidence'],
      d.symptomNetworkMapping.map(r => r.length >= 5 ? r.slice(0,5) : [...r, ...Array(5-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.15), Math.floor(CONTENT*0.17), Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.22)] }
    ));
  }
  items.push(S.emptyPara());

  return items;
}

function section7(d) {
  const items = [];
  items.push(S.h1('7. Applying NIBS According to the SOZO FNON Concept'));
  items.push(new Paragraph({
    children: [new TextRun({ text: `FNON (Functional Network-Oriented Neuromodulation) is a proprietary clinical framework developed by SOZO Brain Center. It translates functional neuroimaging-based network knowledge into actionable clinical protocols. For ${d.conditionShort}, the FNON concept moves beyond symptom-based stimulation targets to address the underlying network architecture sustaining the disorder.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(new Paragraph({
    children: [new TextRun({ text: '⚠ SOZO Brain Center Proprietary System. Not to be reproduced or applied outside SOZO-authorised centres without written permission from the Medical Director.', color: S.RED, bold: true, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());

  items.push(S.h2('FNON Classification System'));
  items.push(S.bodyPara('The FNON model follows a five-level clinical decision pathway. Each level builds on the previous, creating a structured and auditable treatment rationale.'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Level', 'Domain', 'Action', 'Responsible'],
    [
      ['1', 'Phenotype', `Identify dominant clinical phenotype in ${d.conditionShort}`, 'Doctor'],
      ['2', 'Network Hypothesis', 'Map phenotype to dysfunctional networks', 'Doctor'],
      ['3', 'Modality Selection', 'Select modalities based on depth, network reach, and evidence', 'Doctor'],
      ['4', 'Reassessment', 'Review response at 5 and 10 sessions; adjust if needed', 'Doctor + Clinical Assistant'],
      ['5', 'Optimisation', 'Titrate parameters; adjust montage; add/remove modalities', 'Doctor'],
    ],
    { widths: [Math.floor(CONTENT*0.08), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.5), Math.floor(CONTENT*0.22)] }
  ));
  items.push(S.emptyPara());
  items.push(S.emptyPara());

  items.push(S.h2('Montage Selection Guide'));
  items.push(S.emptyPara());
  items.push(S.bodyPara('The following table provides a clinical decision aid for translating the dominant phenotype into a SOZO FNON treatment strategy.'));
  items.push(S.emptyPara());
  if (d.montageSelectionRows && d.montageSelectionRows.length > 0) {
    items.push(T.buildTable(
      ['IF... (Dominant Phenotype)', 'THEN... (SOZO Device & Network Strategy)'],
      d.montageSelectionRows.map(r => r.length >= 2 ? r.slice(0,2) : [...r, '']),
      { widths: [Math.floor(CONTENT*0.35), Math.floor(CONTENT*0.65)] }
    ));
  }
  items.push(S.emptyPara());
  items.push(S.emptyPara());

  return items;
}

function section8(d) {
  const items = [];
  items.push(S.h1('8. Most Studied and FNON-Based Montages'));

  items.push(S.h2('tDCS Devices Used at SOZO Brain Center'));
  items.push(S.h3('Newronika HDCkit (Primary Clinical Device)'));
  items.push(S.bodyPara('Class IIa CE-certified (CE 0476). Two-channel anodal stimulation; maximum 2 mA per channel. Electrodes: Active 25 cm² / Reference 35 cm². HD electrode options available. Software-controlled montage programming. Real-time impedance monitoring.'));
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [new TextRun({ text: `Clinical Role at SOZO: Primary in-clinic tDCS system for all FNON motor, cognitive, cerebellar, and dual-channel montages for ${d.conditionShort}. The HDCkit enables the full range of FNON tDCS protocols requiring bilateral or multi-site configurations.`, color: S.NAVY, bold: true, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));

  items.push(S.h3('PlatoScience (Wireless Controlled Through App)'));
  items.push(S.bodyPara('CE-marked wearable tDCS system one-size fits all design. Configuration: 3 stimulation electrodes with 1 channel anodal stimulation. Maximum current: 2 mA. App-guided, suitable for home use with Doctor-prescribed protocols.'));
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [new TextRun({ text: `PlatoScience is considered a structured continuation device, not a replacement for HDCkit tDCS when advanced montage flexibility is required. It is suitable for home-based DLPFC or frontal montages in stable ${d.conditionShort} patients who have been trained in-clinic.`, color: S.NAVY, bold: true, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());

  items.push(S.h2(`Role of Anodal and Cathodal Stimulation in ${d.conditionShort}`));
  items.push(S.bodyPara(`Transcranial Direct Current Stimulation (tDCS) modulates cortical excitability through polarity-dependent mechanisms. In ${d.conditionShort}, the selection of anodal versus cathodal stimulation is guided by the target network state and the direction of desired excitability change.`));
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [new TextRun({ text: `From a FNON perspective, tDCS effects are not simply "excitation vs. inhibition" — they are state-dependent modulatory influences on network dynamics. In ${d.conditionShort}, the primary goal is to restore adaptive excitability balance: upregulating hypoactive circuits (e.g., DLPFC, CEN) and downregulating hyperactive networks (e.g., DMN, amygdala-driven threat circuits) where clinically indicated.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());
  items.push(S.bodyPara('Anode (+): Causes subthreshold depolarization; increases neuronal firing probability; enhances cortical excitability; facilitates long-term potentiation-like plasticity.'));
  items.push(S.bodyPara('Cathode (−): Causes subthreshold hyperpolarization; decreases neuronal firing probability; reduces cortical excitability; may suppress maladaptive hyperactivity.'));
  items.push(S.bodyPara(d.polarityPrincipleText || `In ${d.conditionShort} according to the SOZO FNON concept: Anode is typically applied over hypoactive targets (e.g., DLPFC for executive/mood symptoms); Cathode is placed over hyperactive or reference regions. The specific polarity strategy is determined by the patient's dominant phenotype and network assessment.`));

  items.push(S.h3(`Clinical Polarity Principle in ${d.conditionShort}`));
  items.push(S.emptyPara());
  if (d.polarityTable) {
    items.push(T.buildTable(
      ['Network State', 'Polarity Strategy'],
      d.polarityTable,
      { widths: [Math.floor(CONTENT*0.4), Math.floor(CONTENT*0.6)] }
    ));
  } else {
    items.push(T.buildTable(
      ['Network State', 'Polarity Strategy'],
      [
        ['Hypoactive prefrontal/DLPFC', `Anode F3/F4/Fz; Cathode Pz, extracephalic or contralateral shoulder`],
        ['Hyperactive DMN / rumination', `Cathode Pz/Cz; Anode DLPFC to redirect network control`],
        ['Limbic hyperactivity', `Anode DLPFC (top-down regulation); Cathode reference`],
        ['Sensorimotor hypofunction', `Anode C3/C4/Cz; Cathode extracephalic or Fz`],
      ],
      { widths: [Math.floor(CONTENT*0.4), Math.floor(CONTENT*0.6)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2(`Classic tDCS Protocols — Evidence-Based (C1–C8)`));
  items.push(S.bodyPara(`These protocols represent the most studied and replicated tDCS configurations for ${d.conditionShort} in the published literature. They form the evidence base from which FNON extensions are developed.`));
  items.push(S.emptyPara());
  if (d.classicTdcsProtocols && d.classicTdcsProtocols.length > 0) {
    items.push(T.buildTable(
      ['ID', 'Symptom Target', 'Anode', 'Cathode', 'Parameters', 'Evidence'],
      d.classicTdcsProtocols.map(r => r.length >= 6 ? r.slice(0,6) : [...r, ...Array(6-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.06), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.14), Math.floor(CONTENT*0.14), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.28)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2('FNON tDCS Protocols — Network-Oriented (F1–F6)'));
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [new TextRun({ text: `The FNON tDCS protocols extend the evidence-based classics by incorporating network-level reasoning. Each protocol targets a specific network dysfunction identified in the patient's FNON phenotype assessment, using the Newronika HDCkit's dual-channel capability for broader network engagement.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());
  if (d.fnonTdcsProtocols && d.fnonTdcsProtocols.length > 0) {
    items.push(T.buildTable(
      ['ID', 'Clinical Focus', 'Network Hypothesis', 'SOZO Montage (Newronika)', 'Network Goal'],
      d.fnonTdcsProtocols.map(r => r.length >= 5 ? r.slice(0,5) : [...r, ...Array(5-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.06), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.26)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2('tDCS Parameters & Safety Limits'));
  items.push(S.h3('A) Session Frequency Rule'));
  items.push(S.bodyPara('Two sessions per day is ONLY permitted under a Doctor-defined plan, with a minimum interval of 4–6 hours between sessions. Single daily sessions are the standard for outpatient and home-based protocols. Higher frequency should only be used during intensive in-clinic treatment blocks.'));

  items.push(S.h3('B) tDCS Safety Limits'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Parameter', 'Standard (SOZO)', 'DO NOT EXCEED'],
    [
      ['Intensity', 'Up to 2 mA/channel', '2 mA per channel (HDCkit); 2 mA total (PlatoScience)'],
      ['Duration', '20–30 min/session', '30 min per session'],
      ['Electrode size (active)', '25 cm²', 'Do not use HD without Doctor approval'],
      ['Current density', '0.08 mA/cm²', '0.08 mA/cm²'],
      ['Sessions per course', '10–20 standard', '30 without reassessment'],
      ['Charge density', '<40 µC/cm²', '40 µC/cm²'],
      ['Inter-session interval', '≥4 hours (same day)', 'Never <2 hours'],
      ['Course duration', '2–4 weeks standard', 'Continuous >6 wks without break and reassessment'],
    ],
    { widths: [Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.36), Math.floor(CONTENT*0.36)] }
  ));
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [new TextRun({ text: '⚠ DO NOT EXCEED LIMITS. Any parameter change requires Doctor authorisation and documentation.', color: S.RED, bold: true, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());

  items.push(S.h3('C) Device Operational Constraints'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Device', 'Regulatory/Class', 'Channels', 'Role at SOZO', 'Home Use Control'],
    [
      ['Newronika HDCkit', 'CE Class IIa (CE 0476)', '2-channel (anodal)', `Full FNON montage library incl. dual-channel protocols for ${d.conditionShort}`, 'Controlled mode (Doctor programs; patient activates only)'],
      ['PlatoScience', 'CE-marked (home)', '1 channel', `Continuation protocols; simple DLPFC montages for ${d.conditionShort}`, 'App-guided; follow prescriptions'],
    ],
    { widths: [Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.16), Math.floor(CONTENT*0.12), Math.floor(CONTENT*0.3), Math.floor(CONTENT*0.24)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2(`Classic TPS Protocols — Evidence-Based (T1–T5)`));
  items.push(S.bodyPara(`Transcranial Pulse Stimulation (TPS) provides the ability to reach deeper brain structures that are inaccessible to surface tDCS. For ${d.conditionShort}, TPS targets are selected based on the condition's specific network pathology and the published evidence for each brain region.`));
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  if (d.classicTpsProtocols && d.classicTpsProtocols.length > 0) {
    items.push(T.buildTable(
      ['ID', 'Symptom Target', 'Brain Targets', 'SOZO Parameters', 'Pulse Allocation', 'Evidence'],
      d.classicTpsProtocols.map(r => r.length >= 6 ? r.slice(0,6) : [...r, ...Array(6-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.06), Math.floor(CONTENT*0.15), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.19)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2('FNON TPS Protocols — Network-Oriented (FT1–FT9)'));
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [new TextRun({ text: `The FNON TPS protocols extend classical approaches by targeting distributed brain networks rather than single anatomical sites. Each protocol is mapped to a specific ${d.conditionShort} phenotype with a defined network hypothesis, enabling personalised pulse allocation across multiple functionally connected regions.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(new Paragraph({
    children: [new TextRun({ text: `⚠ TPS in ${d.conditionShort} remains investigational. Network-oriented pulse allocation at SOZO ranges from 6,000 to 12,000 pulses per session. Doctor authorisation and documented off-label consent are required for all TPS sessions.`, color: S.RED, bold: true, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());
  if (d.fnonTpsProtocols && d.fnonTpsProtocols.length > 0) {
    items.push(T.buildTable(
      ['ID', `${d.conditionShort} Phenotype`, 'Dominant Dysfunctional Networks', 'TPS Targets', 'Session Structure (10,000 pulses)', 'Course'],
      d.fnonTpsProtocols.map(r => r.length >= 6 ? r.slice(0,6) : [...r, ...Array(6-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.06), Math.floor(CONTENT*0.14), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.26), Math.floor(CONTENT*0.16)] }
    ));
  }
  items.push(S.emptyPara());

  items.push(S.h2('TPS Safety Limits & Device Specifications'));
  items.push(S.emptyPara());
  items.push(new Paragraph({
    children: [new TextRun({ text: `⚠ TPS use in ${d.conditionShort} is INVESTIGATIONAL / OFF-LABEL. Doctor authorisation and documented off-label consent required before any TPS session.`, color: S.RED, bold: true, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.h3(''));
  items.push(S.h3('ROI → Brain Region Mapping'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['ROI', 'Core Brain Region', 'Anatomical Label', 'Functional Network(s)', 'Sub-Targeting Notes'],
    [
      ['DLPFC', 'Dorsolateral prefrontal cortex', 'Middle frontal gyrus', 'CEN; Frontoparietal control', 'Primary cognitive/affective entry point'],
      ['mPFC', 'Medial prefrontal cortex', 'Superior frontal gyrus (medial)', 'DMN; Limbic', 'Self-referential and emotional regulation'],
      ['ACC', 'Anterior cingulate cortex', 'Cingulate gyrus (anterior)', 'Salience; Limbic', 'Error monitoring, emotional conflict'],
      ['PPC', 'Posterior parietal cortex', 'Superior/inferior parietal lobule', 'CEN; Attention', 'Attention and sensorimotor integration'],
      ['Hippocampus', 'Hippocampus proper', 'Hippocampal formation', 'DMN; Memory', 'Memory encoding and consolidation'],
      ['Insula', 'Insular cortex', 'Insular lobe', 'Salience; Interoception', 'Interoceptive awareness, autonomic regulation'],
      ['Amygdala', 'Amygdaloid complex', 'Medial temporal lobe', 'Limbic; Salience', 'Fear, threat detection, emotional memory'],
      ['Cerebellum', 'Cerebellar cortex + deep nuclei', 'Cerebellar hemispheres', 'Sensorimotor; Cognitive', 'Motor coordination; cognitive cerebellar loops'],
      ['Holocranial', 'Global cortical coverage', 'Whole scalp', 'All networks', 'Used for generalized or multi-network protocols'],
    ],
    { widths: [Math.floor(CONTENT*0.1), Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.3)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h3('Energy & Frequency Limits'));
  items.push(S.h3(''));
  items.push(T.buildTable(
    ['Parameter', 'SOZO Standard'],
    [
      ['Energy Flux Density', '0.01–0.25 mJ/mm²'],
      ['Frequency', '1–8 Hz (8 Hz only up to 0.02 mJ/mm² max energy)'],
      ['Pulses per session', '3,000–12,000 (standard: 6,000–10,000)'],
      ['Maximum single-site pulses', '4,000 per session'],
      ['Minimum inter-session interval', '48 hours'],
      ['Standard course', '6–12 sessions over 2–4 weeks'],
    ],
    { widths: [Math.floor(CONTENT*0.45), Math.floor(CONTENT*0.55)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h3('Daily & Weekly Limits'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Parameter', 'Rule'],
    [
      ['Sessions per Day', 'Maximum 1 TPS session per day'],
      ['Minimum Interval', '≥48 hours between TPS sessions (standard)'],
      ['Weekly Sessions', 'Maximum 3 sessions per week during intensive block'],
      ['Pulse Total per Week', 'Maximum 30,000 pulses per week'],
      ['Rest Period', 'Minimum 1 week break after 12-session course'],
    ],
    { widths: [Math.floor(CONTENT*0.45), Math.floor(CONTENT*0.55)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h3('Peripheral Stimulation'));
  items.push(S.h3(''));
  items.push(S.bodyPara('Peripheral stimulation refers to cranio-cervical interface targeting, mastoid–retroauricular regions, suboccipital regions, and peripheral nerve stimulation targets. These are used adjunctively to modulate brainstem and cranial nerve inputs.'));
  items.push(new Paragraph({
    children: [new TextRun({ text: `⚠ PRE is not standalone primary therapy for core ${d.conditionShort} symptoms. Avoid carotid sinus and major vascular structures.`, color: S.RED, bold: true, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());

  items.push(S.h3('NEUROLITH® TPS System (Storz Medical)'));
  items.push(S.h3(''));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Specification', 'Details'],
    [
      ['Technology', 'Transcranial Pulse Stimulation (focused ultrasound pulse waves)'],
      ['Maximum Depth', 'Up to ~8 cm (device-dependent anatomical configuration)'],
      ['Frequency Range', '1–8 Hz'],
      ['Energy Range', '0.01–0.25 mJ/mm²'],
      ['Pulse Mode', 'Single focused pulses; no thermal effect'],
      ['Navigation', 'Neuronavigation-guided (optional) or anatomical landmark-based'],
      ['Regulatory', 'CE-marked Class IIa medical device'],
    ],
    { widths: [Math.floor(CONTENT*0.35), Math.floor(CONTENT*0.65)] }
  ));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Parameter', 'Limit'],
    [
      ['Maximum Daily Duration', 'Single session per day; up to 12,000 pulses'],
      ['Contraindications', 'Metal implants, DBS, skull defects, coagulopathy, active infection at site'],
      ['Minimum operator qualification', 'Doctor training certification in TPS application'],
      ['Informed consent', 'Off-label consent form, signed by Doctor and patient'],
    ],
    { widths: [Math.floor(CONTENT*0.45), Math.floor(CONTENT*0.55)] }
  ));
  items.push(S.emptyPara());
  items.push(S.bodyPara(`According to the SOZO FNON concept, TPS sessions range from 3,000 to 12,000 pulses per session. Pulses are allocated between targeted ROIs and holocranial/peripheral regions based on the patient's dominant phenotype.`));

  return items;
}

function section9(d) {
  const items = [];
  items.push(S.h1('9. Combination of NIBS Techniques'));
  items.push(new Paragraph({
    children: [new TextRun({ text: `A key advantage of the FNON framework is its capacity to combine multiple neuromodulation modalities in a single treatment programme. For ${d.conditionShort}, this multimodal approach addresses the multi-level nature of network dysfunction — from cortical excitability (tDCS) to deep network engagement (TPS) and autonomic/brainstem regulation (taVNS, CES).`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));

  items.push(S.h2('taVNS Protocols'));
  items.push(S.bodyPara(`Transcutaneous auricular vagus nerve stimulation (tVNS) is used at SOZO as an important neuromodulation technique providing autonomic and brainstem modulation that complements cortical-level tDCS and TPS interventions. In ${d.conditionShort}, tVNS targets the vagal-brainstem-limbic axis to modulate arousal, affect, and autonomic tone.`));
  items.push(new Paragraph({
    children: [new TextRun({ text: '⚠ Maximum total tVNS exposure: 4 hours per day (across all sessions combined).', color: S.RED, bold: true, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.h3(''));
  items.push(T.buildTable(
    ['ID', 'Target', 'Ear', 'Frequency', 'Pulse Width', 'Duration', 'Clinical Use'],
    d.tavnsProtocols || [
      ['V1', 'Autonomic regulation / arousal', 'Left (cymba conchae)', '25 Hz', '200–300 µs', '30–60 min', `Baseline stabilisation before tDCS/TPS in all ${d.conditionShort} phenotypes`],
      ['V2', 'Mood / limbic modulation', 'Left (cymba conchae)', '10–25 Hz', '250 µs', '30–45 min', 'Affective symptoms; depression comorbidity'],
      ['V3', 'Cognitive enhancement', 'Left (cymba conchae)', '25 Hz', '250 µs', '30 min', 'Cognitive phenotypes; pre-tDCS priming'],
      ['V4', 'Sleep regulation', 'Left (cymba conchae)', '1–10 Hz', '200 µs', '30–45 min', 'Insomnia, hyperarousal, sleep disruption'],
      ['V5', 'Pain / autonomic', 'Left or bilateral', '25 Hz', '250 µs', '30–60 min', 'Pain comorbidity; autonomic dysregulation'],
    ],
    { widths: [Math.floor(CONTENT*0.06), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.12), Math.floor(CONTENT*0.1), Math.floor(CONTENT*0.1), Math.floor(CONTENT*0.1), Math.floor(CONTENT*0.34)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h3('Clinical Integration'));
  items.push(S.bodyPara(`tVNS is not primary therapy for core ${d.conditionShort} symptoms. It is used as a network regulator targeting the salience network, brainstem nuclei (NTS, LC), and limbic-autonomic circuits. Its primary roles are: (1) pre-session state stabilisation, (2) autonomic co-regulation during tDCS/TPS, and (3) post-session consolidation.`));

  items.push(S.h3('tVNS Safety Limits'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Parameter', 'SOZO Standard', 'DO NOT EXCEED'],
    [
      ['Maximum daily duration', '4 hours total', '4 hours (all sessions combined)'],
      ['Frequency range', '1–25 Hz', '30 Hz without Doctor review'],
      ['Pulse width', '200–300 µs', '500 µs'],
      ['Current', '0.1–4 mA (perception threshold)', '6 mA'],
      ['Ear side', 'Left preferred (cardiac vagal)', 'Bilateral only with Doctor review'],
    ],
    { widths: [Math.floor(CONTENT*0.3), Math.floor(CONTENT*0.35), Math.floor(CONTENT*0.35)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h3('Mechanism of Action'));
  items.push(S.bodyPara('tVNS does not directly stimulate deep brain structures. Its effects are mediated through the Nucleus Tractus Solitarius (NTS) → Locus Coeruleus (noradrenergic) → raphe nuclei (serotonergic) pathway. This produces widespread neuromodulatory effects on arousal, attention, emotional processing, and autonomic regulation, making it a powerful adjunct to cortical neuromodulation.'));

  items.push(S.h3('SOZO Integration Principles'));
  items.push(S.bodyPara(`tVNS may be delivered before tDCS (priming), concurrent with tDCS, or on alternate days during a TPS block. In ${d.conditionShort}, the preferred integration sequence is: tVNS stabilisation → tDCS excitability optimisation → TPS network targeting → tVNS/CES consolidation. The treating Doctor determines the integration schedule based on the patient's phenotype and response.`));
  items.push(S.emptyPara());

  items.push(S.h2('CES Protocols (Alpha-Stim®)'));
  items.push(S.bodyPara(`Alpha-Stim® Cranial Electrotherapy Stimulation (CES) is an FDA-cleared, CE-marked microcurrent device used at SOZO as an adjunct for anxiety reduction, sleep improvement, and mood stabilisation. In ${d.conditionShort}, CES provides a gentle modulatory effect on cortical oscillatory patterns, particularly in the alpha and theta frequency bands.`));
  items.push(S.h3(''));
  items.push(S.h3('Alpha-Stim Device Specifications'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Parameter', 'Device Capability', 'SOZO Clinical Range'],
    [
      ['Output Current', '50–500 µA', '100–400 µA typical'],
      ['Waveform', 'Proprietary biphasic', 'Device-controlled'],
      ['Frequency', '0.5 Hz (primary mode)', '0.5 Hz standard'],
      ['Application', 'Ear clip electrodes', 'Standard bilateral ear clip placement'],
      ['Session Duration', '20–60 minutes', '20–40 minutes standard'],
    ],
    { widths: [Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.36), Math.floor(CONTENT*0.36)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h3('CES Safety Limits'));
  items.push(S.h3(''));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Parameter', 'Limit'],
    [
      ['Maximum Current', '500 µA (device limit)'],
      ['Typical Range', '100–300 µA'],
      ['Session Duration', 'Maximum 60 minutes per session'],
      ['Frequency', 'Maximum 2 sessions per day'],
    ],
    { widths: [Math.floor(CONTENT*0.45), Math.floor(CONTENT*0.55)] }
  ));
  items.push(S.emptyPara());
  items.push(S.emptyPara());
  items.push(S.emptyPara());

  items.push(S.h2('Multimodal Combinations — SOZO Framework'));
  items.push(new Paragraph({
    children: [new TextRun({ text: `The FNON model leverages multiple neuromodulation modalities in combination to address different network levels and depths simultaneously. The SOZO S-O-Z-O sequencing framework provides a structured rationale for combining modalities within a single session or across a treatment programme for ${d.conditionShort}.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());
  items.push(S.bodyPara('S — Stabilize state: downshift sympathetic tone, reduce threat/arousal, improve sensory gating (tVNS or CES).'));
  items.push(S.bodyPara('O — Optimize excitability: prime target networks for plasticity and task engagement (tDCS).'));
  items.push(S.bodyPara('Z — Zone targeting: deliver focal/region-specific mechanotransduction + network engagement (TPS ROI + holocranial + peripheral).'));
  items.push(S.bodyPara('O — Outcome consolidation: post-session autonomic support + behavioral practice window (tVNS/CES and rehab tasks).'));
  items.push(S.emptyPara());

  // 9 phenotype combination tables
  const phenotypes = d.multimodalPhenotypes || [];
  for (let i = 0; i < 9; i++) {
    const ph = phenotypes[i] || {
      name: `Phenotype ${i+1}`,
      combinations: [
        ['TPS + tDCS', `O→Z: tDCS primes target network excitability; TPS drives deep network engagement`, 'tDCS 15–20 min before TPS; behavioural task in post-stimulation window', `${d.conditionShort} core symptom profile`],
        ['TPS + tVNS', `S→Z→O: tVNS stabilizes autonomic tone; TPS targets network nodes; tVNS consolidates`, 'tVNS 10–15 min pre-TPS; optional post-TPS for consolidation', 'Stress-sensitive or autonomically dysregulated presentations'],
        ['tDCS + tVNS', `S→O: tVNS primes salience/arousal state; tDCS optimises cortical excitability`, 'tVNS 15 min before tDCS; concurrent or sequential', 'Non-TPS days; home-based protocol'],
        ['Full SOZO (tVNS→tDCS→TPS→tVNS/CES)', 'Complete S-O-Z-O cycle for maximum network engagement', 'Full session ~90–120 min; Doctor-supervised only', 'Intensive in-clinic block for treatment-resistant cases'],
      ],
    };
    items.push(S.h3(`${i+1}) ${ph.name}`));
    items.push(S.h3(''));
    items.push(T.buildTable(
      ['Combination', 'Mechanistic Rationale (SOZO)', 'Timing', 'Clinical Indication'],
      ph.combinations.map(r => r.length >= 4 ? r.slice(0,4) : [...r, ...Array(4-r.length).fill('')]),
      { widths: [Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.3), Math.floor(CONTENT*0.25), Math.floor(CONTENT*0.23)] }
    ));
    items.push(S.emptyPara());
  }

  return items;
}

function section10(d) {
  const items = [];
  items.push(S.h1('10. Side Effects and Monitoring'));
  items.push(S.bodyPara(`Patient safety is paramount throughout the SOZO FNON programme. All side effects must be documented in the structured AE log. The following tables describe expected effects, grading criteria, and management protocols for ${d.conditionShort} patients.`));

  items.push(S.h2('Common Side Effects'));
  items.push(S.bodyPara(`TPS: mild headache, jaw discomfort, nausea (all rare). No major adverse events in published literature at standard SOZO parameters.`));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Side Effect', 'Frequency', 'Severity', 'Management'],
    [
      ['Tingling/itching (tDCS)', '50–70%', 'Mild', 'Normal; resolves after session'],
      ['Mild headache', '10–20%', 'Mild', 'Paracetamol; resolves within hours'],
      ['Skin redness at electrode', '5–15%', 'Mild', 'Normal; monitor for burns; adjust electrodes'],
      ['Nausea (TPS)', '1–5%', 'Mild', 'Rest; ensure adequate hydration; reduce energy if recurrent'],
      ['Dizziness (taVNS)', '1–5%', 'Mild', 'Reduce intensity; stop if persistent; check positioning'],
      ['Mood change (transient)', '1–5%', 'Mild', 'Document; Doctor review within 24h; monitor trajectory'],
    ],
    { widths: [Math.floor(CONTENT*0.28), Math.floor(CONTENT*0.15), Math.floor(CONTENT*0.15), Math.floor(CONTENT*0.42)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2('Adverse Event Grading'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Grade', 'Examples', 'Action'],
    [
      ['Grade 1 (Mild)', 'Tingling, mild headache, transient redness, brief dizziness', 'Continue. Document.'],
      ['Grade 2 (Moderate)', 'Persistent headache >4h, burning sensation, mood change persisting >24h', 'PAUSE. Doctor review within 24h. Resume with approved modification.'],
      ['Grade 3 (Severe)', 'Seizure, syncope, burn, prolonged neurological change', 'STOP immediately. Emergency assessment. Incident report. Do not resume without Doctor review.'],
    ],
    { widths: [Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.45), Math.floor(CONTENT*0.35)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2('Contraindications'));
  items.push(S.emptyPara());
  items.push(T.buildTable(
    ['Category', 'tDCS', 'TPS (Investigational)'],
    [
      ['Absolute', 'Metallic implants in field; DBS; cochlear implant; open wounds at electrode site', 'Metallic implants; DBS; skull defects; coagulation disorders; intracranial neoplasm'],
      ['Requires Discussion', 'Pacemaker; epilepsy; pregnancy; dermatological conditions at sites', 'Pacemaker; epilepsy; recent neurosurgery; anticoagulation therapy'],
    ],
    { widths: [Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.41), Math.floor(CONTENT*0.41)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2('Home-Use Safety (tDCS)'));
  items.push(S.bodyPara(`Home-based treatment is prescribed by SOZO Brain Center specialist. Patient/care-giver is trained on device use and provided with written instructions. The treating Doctor reviews home-use compliance and any adverse events at each in-clinic review. PlatoScience is the recommended home device for ${d.conditionShort} where home tDCS is indicated.`));

  return items;
}

function section11(d) {
  const items = [];
  items.push(S.h1('11. In-Clinic and Home-Based Tasks'));
  items.push(S.bodyPara(`Behavioural task pairing during neuromodulation sessions is a critical component of the FNON framework. Activity-dependent neuroplasticity is enhanced when stimulation is delivered concurrent with relevant cognitive or behavioural tasks that activate the target network. The following task pairings are recommended for ${d.conditionShort}.`));

  items.push(S.h2('In-Clinic Task Pairing (Montage-Specific)'));
  items.push(S.emptyPara());
  const taskRows = d.taskPairingRows || [
    ['DLPFC (F1/C3)', 'Cognition / Mood', `Computerised cognitive training (n-back, working memory, attention tasks); mood-relevant cognitive behavioural exercises`, 'Enhances executive network activation during stimulation window'],
    [`${d.conditionShort}-specific motor/sensory`, 'Motor / Sensory Integration', 'Graded activity tasks; sensory integration exercises', 'Activity-dependent plasticity in sensorimotor circuits'],
    ['mPFC/Limbic (F4/F5)', `Emotional regulation / ${d.conditionShort} core`, 'Mindfulness, emotion regulation exercises, exposure-based tasks (supervised)', 'DMN-limbic engagement for affective network remodelling'],
    ['SN/ACC (F6)', 'Salience / attention', 'Attention training, dual-task exercises', 'Salience network calibration'],
    ['Cerebellar', 'Coordination / cerebellar cognitive', 'Fine motor or balance tasks; cognitive cerebellar exercises', 'Cerebellar plasticity enhancement'],
    ['Full SOZO multimodal', `${d.conditionShort} integrated function`, `Integrated task combining ${d.conditionShort}-relevant cognitive and behavioural goals`, 'Full network engagement across S-O-Z-O sequence'],
  ];
  items.push(T.buildTable(
    ['Montage', 'Target Domain', 'Concurrent In-Clinic Tasks', 'Neuroplastic Rationale'],
    taskRows.map(r => r.length >= 4 ? r.slice(0,4) : [...r, ...Array(4-r.length).fill('')]),
    { widths: [Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.35), Math.floor(CONTENT*0.27)] }
  ));
  items.push(S.emptyPara());
  items.push(S.bodyPara(`Home-based tasks should mirror in-clinic activities where possible, adjusted for safety and feasibility. The treating Doctor provides written task prescriptions. Compliance is reviewed at each clinic visit.`));

  return items;
}

function section12(d) {
  const items = [];
  items.push(S.h1('12. Follow-Up Assessments and Decision-Making'));
  items.push(S.bodyPara(`Systematic outcome assessment is integral to the FNON model. Treatment efficacy is evaluated at defined timepoints using validated ${d.conditionShort}-specific instruments, with clinical decisions made based on objective response criteria.`));
  items.push(new Paragraph({
    children: [new TextRun({ text: `The iterative reassessment loop (FNON Levels 4–5) ensures treatment remains aligned with each patient's evolving clinical profile. For ${d.conditionShort}, network-level reassessment informs whether the initial phenotype hypothesis remains valid or whether phenotype switching has occurred.`, color: S.PURPLE, size: 22, font: 'Calibri' })],
    spacing: { after: 120 },
  }));
  items.push(S.emptyPara());
  items.push(S.emptyPara());

  items.push(S.h2('Outcome Measures'));
  items.push(S.bodyPara(`For outcome measures please use SOZO PRS system. Condition-specific validated instruments for ${d.conditionShort}:`));
  (d.outcomeMeasures || [`Primary: ${d.conditionShort}-specific validated rating scale (Doctor-selected based on clinical presentation)`]).forEach(m =>
    items.push(new Paragraph({
      children: [new TextRun({ text: `• ${m}`, color: S.BLACK, size: 22, font: 'Calibri' })],
      spacing: { after: 60 },
    }))
  );
  items.push(S.emptyPara());

  items.push(S.h2('Decision Timeline'));
  items.push(S.bodyPara('The FNON decision timeline ensures structured clinical review at each critical juncture of the treatment programme.'));
  items.push(T.buildTable(
    ['Timepoint', 'Assessment', 'Decision'],
    [
      ['Baseline', 'Full clinical assessment + outcome measures + FNON phenotyping', 'Confirm eligibility; set phenotype hypothesis; prescribe protocol'],
      ['Session 5', 'Brief outcome review; tolerability; side effect check', 'Continue / modify parameters / change montage if no trend'],
      ['Session 10', 'Full outcome measures; phenotype reassessment', 'Continue / extend / change protocol / pause for review'],
      ['End of course (12–20 sessions)', 'Full outcome measures; Doctor review', 'Maintenance protocol / repeat course / discharge / escalate'],
      ['3-month follow-up', 'Outcome measures; durability assessment', 'Re-enrol if relapse; maintain if stable; modify if partial'],
    ],
    { widths: [Math.floor(CONTENT*0.2), Math.floor(CONTENT*0.4), Math.floor(CONTENT*0.4)] }
  ));
  items.push(S.emptyPara());

  items.push(S.h2(`Responders and Non-Responders (tDCS in ${d.conditionShort})`));
  items.push(S.bodyPara(`Not all patients respond uniformly to tDCS. Inter-individual variability is influenced by anatomical differences in skull thickness and cortical geometry, baseline cortical excitability, pharmacological state, and phenotype characteristics. In ${d.conditionShort}, response is defined as ≥30% improvement on the primary outcome measure at session 10 reassessment.`));
  items.push(S.bodyPara(`Within the FNON framework, non-responders are managed through the Level 5 adjustment pathway: the phenotype is reassessed, the network hypothesis revised, and the montage or modality combination adjusted. TPS escalation should be considered for tDCS non-responders with treatment-resistant profiles.`));

  items.push(S.h2(d.medicationSectionTitle || `NIBS During Ongoing ${d.primaryMedication || 'Pharmacological'} Treatment`));
  items.push(S.bodyPara(d.medicationNibsText || `The majority of ${d.conditionShort} patients receiving FNON neuromodulation will be on concurrent pharmacological treatment. ${d.primaryMedication || 'Standard medications'} can modulate cortical excitability and may influence neuromodulation response. The treating Doctor should document all concurrent medications, review for potential interactions, and time NIBS sessions optimally relative to medication peaks where clinically relevant.`));
  items.push(S.emptyPara());

  return items;
}

function section13(d) {
  const items = [];
  items.push(S.h1('13. References'));
  items.push(S.bodyPara('Last 5 years + most cited foundational papers per technique.'));

  const refs = d.references || {};
  const sections = [
    { key: 'foundational', label: 'Foundational' },
    { key: 'tdcs',         label: 'tDCS' },
    { key: 'tps',          label: 'TPS (All Post-2018)' },
    { key: 'tavns',        label: 'taVNS' },
    { key: 'ces',          label: 'CES' },
    { key: 'network',      label: 'Network' },
  ];

  sections.forEach(sec => {
    const list = refs[sec.key] || [];
    if (list.length === 0) return;
    items.push(S.h2(sec.label));
    list.forEach(ref => {
      items.push(new Paragraph({
        children: [new TextRun({ text: String(ref), color: S.BLACK, size: 20, font: 'Calibri' })],
        spacing: { after: 80 },
      }));
    });
    items.push(S.emptyPara());
  });

  return items;
}

// ─── MAIN DOCUMENT BUILDER ────────────────────────────────────────────────────

function buildDocument(d) {
  const children = [
    ...coverPage(d),
    ...tableOfContents(),
    ...section1(d),
    ...section2(d),
    ...section3(d),
    ...section4(d),
    ...section5(d),
    ...section6(d),
    ...section7(d),
    ...section8(d),
    ...section9(d),
    ...section10(d),
    ...section11(d),
    ...section12(d),
    ...section13(d),
  ];

  return new Document({
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      children,
    }],
    styles: {
      default: {
        document: {
          run: { font: 'Calibri', size: 22 },
        },
      },
    },
  });
}

module.exports = { buildDocument };
