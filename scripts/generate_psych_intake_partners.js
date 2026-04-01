/**
 * SOZO Psychological Intake & PRS Baseline — Partners Tier Generator
 * Usage: node scripts/generate_psych_intake_partners.js <condition_slug>
 * Saves to: outputs/documents/<slug>/partners/Psychological_Intake_PRS_Baseline_Partners_<slug>.docx
 */
'use strict';

const path = require('path');
const fs   = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, BorderStyle, ShadingType, VerticalAlign,
  convertInchesToTwip,
} = require('docx');

// ── Colours ──────────────────────────────────────────────────────────────────
const NAVY   = '1B3A5C';
const BLUE   = '2E75B6';
const PURPLE = '7B2D8E';
const RED    = 'CC0000';
const WHITE  = 'FFFFFF';
const BLACK  = '000000';

const PAGE_W  = convertInchesToTwip(8.5);
const PAGE_H  = convertInchesToTwip(11);
const MARGIN  = convertInchesToTwip(1);
const CONTENT = PAGE_W - 2 * MARGIN; // ≈9360

// ── Border style ─────────────────────────────────────────────────────────────
const BORDERS = {
  top:    { style: BorderStyle.SINGLE, size: 4, color: '999999' },
  bottom: { style: BorderStyle.SINGLE, size: 4, color: '999999' },
  left:   { style: BorderStyle.SINGLE, size: 4, color: '999999' },
  right:  { style: BorderStyle.SINGLE, size: 4, color: '999999' },
};

// ── Low-level helpers ─────────────────────────────────────────────────────────
function tr(text, color = BLACK, bold = false, size = 22) {
  return new TextRun({ text: String(text), color, bold, size, font: 'Calibri' });
}

function p(runs, { align = AlignmentType.LEFT, before = 0, after = 120 } = {}) {
  const arr = Array.isArray(runs) ? runs : [runs];
  return new Paragraph({ children: arr, alignment: align, spacing: { before, after } });
}

function empty() { return p(tr(''), { after: 60 }); }

function hCell(text) {
  return new TableCell({
    children: [new Paragraph({
      children: [new TextRun({ text: String(text), color: WHITE, bold: true, size: 20, font: 'Calibri' })],
      alignment: AlignmentType.LEFT,
      spacing: { before: 40, after: 40 },
    })],
    shading: { type: ShadingType.SOLID, color: NAVY },
    borders: BORDERS,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    verticalAlign: VerticalAlign.CENTER,
  });
}

function bCell(text, color = BLACK, shade = null, span = 1) {
  return new TableCell({
    children: [new Paragraph({
      children: [new TextRun({ text: String(text || ''), color, size: 18, font: 'Calibri' })],
      alignment: AlignmentType.LEFT,
      spacing: { before: 40, after: 40 },
    })],
    shading: shade ? { type: ShadingType.SOLID, color: shade } : undefined,
    borders: BORDERS,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    verticalAlign: VerticalAlign.TOP,
    columnSpan: span,
  });
}

function tbl(headers, rows, widths) {
  const w = widths || headers.map(() => Math.floor(CONTENT / headers.length));
  return new Table({
    rows: [
      new TableRow({ children: headers.map(h => hCell(h)), tableHeader: true }),
      ...rows.map(r => new TableRow({ children: r.map((v, i) => bCell(v)) })),
    ],
    width: { size: CONTENT, type: WidthType.DXA },
    columnWidths: w,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
  });
}

// ── Document builder ─────────────────────────────────────────────────────────
function buildDoc(d) {
  const items = [];

  // ── HEADER ────────────────────────────────────────────────────────────────
  items.push(
    p(tr('SOZO BRAIN CENTER — PARTNERS TIER', NAVY, true, 28), { align: AlignmentType.CENTER, after: 80 }),
    p(tr('Psychological Intake & SOZO PRS Baseline', BLUE, true, 26), { align: AlignmentType.CENTER, after: 80 }),
    p(tr('🟣 FNON + Evidence-Based Assessment — Includes Brain Network Analysis', PURPLE, true, 22), { align: AlignmentType.CENTER, after: 160 }),
  );

  // Patient info table (7r × 2c)
  items.push(tbl(
    ['Patient Information', 'Details'],
    [
      ['Patient Name', ''],
      ['Date of Birth / Age', ''],
      ['Date of Assessment', ''],
      ['Clinician', ''],
      ['Referral Source', ''],
      ['Primary Diagnosis', d.conditionFull],
      ['Tier', 'Partners'],
    ],
    [Math.floor(CONTENT * 0.35), Math.floor(CONTENT * 0.65)],
  ));

  items.push(empty());

  // ── SECTION A ─────────────────────────────────────────────────────────────
  items.push(p(tr('SECTION A: STRUCTURED CLINICAL INTERVIEW', NAVY, true, 24), { before: 200, after: 120 }));

  // A1 Chief Complaints
  items.push(p(tr('A1. Chief Complaints', BLUE, true, 22), { before: 160, after: 80 }));
  items.push(tbl(
    ['Chief Complaint', 'Duration', 'Severity (0–10)', 'Impact on Daily Life'],
    [
      ['', '', '', ''],
      ['', '', '', ''],
      ['', '', '', ''],
      ['', '', '', ''],
      ['', '', '', ''],
    ],
    [Math.floor(CONTENT*0.30), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.34)],
  ));

  items.push(empty());

  // A2 Psychiatric History
  items.push(p(tr('A2. Psychiatric History', BLUE, true, 22), { before: 160, after: 80 }));
  items.push(tbl(
    ['Domain', 'Details'],
    [
      ['Previous psychiatric diagnoses', ''],
      ['Current psychiatric medications', ''],
      ['Previous psychological therapies', ''],
      ['Family psychiatric history', ''],
      ['Substance use history', ''],
      ['Previous hospitalisations', ''],
    ],
    [Math.floor(CONTENT*0.35), Math.floor(CONTENT*0.65)],
  ));

  // Safety flag
  items.push(empty());
  items.push(new Paragraph({
    children: [
      new TextRun({ text: '⚠ SAFETY FLAG — ', color: RED, bold: true, size: 22, font: 'Calibri' }),
      new TextRun({ text: 'Suicidality / Self-Harm Screening: Current ideation? Plan? Intent? Recent attempt? ', color: RED, size: 22, font: 'Calibri' }),
      new TextRun({ text: 'Yes ☐  No ☐  (If Yes → immediate risk protocol)', color: RED, bold: true, size: 22, font: 'Calibri' }),
    ],
    spacing: { before: 80, after: 120 },
  }));

  // A3 Functional Limitations
  items.push(p(tr('A3. Functional Limitations', BLUE, true, 22), { before: 160, after: 80 }));
  items.push(tbl(
    ['Domain', 'Current Status'],
    d.functionalDomains.map(dom => [dom, '']),
    [Math.floor(CONTENT*0.40), Math.floor(CONTENT*0.60)],
  ));

  items.push(empty());

  // A4 Treatment History
  items.push(p(tr('A4. Treatment History Summary', BLUE, true, 22), { before: 160, after: 80 }));
  items.push(tbl(
    ['Treatment / Intervention', 'Duration', 'Response', 'Current Status'],
    [
      ['Pharmacotherapy', '', '', ''],
      ['Psychotherapy / Counselling', '', '', ''],
      ['Neuromodulation (TMS/tDCS/TPS)', '', '', ''],
      ['Other interventions', '', '', ''],
    ],
    [Math.floor(CONTENT*0.30), Math.floor(CONTENT*0.18), Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.30)],
  ));

  items.push(empty());

  // ── SECTION B ─────────────────────────────────────────────────────────────
  items.push(p(tr('SECTION B: SOZO PRS — PATIENT RATING SYSTEM (BASELINE)', NAVY, true, 24), { before: 200, after: 120 }));
  items.push(p(tr('Instructions: Rate each symptom 0–10 (0 = absent, 10 = most severe). Tick Relevant if applicable. Add notes as needed.', BLACK, false, 20), { after: 100 }));

  // B1 Primary Symptoms
  items.push(p(tr('B1. Primary Symptoms Domain', BLUE, true, 22), { before: 160, after: 80 }));
  items.push(tbl(
    ['Symptom', 'Score (0–10)', 'Relevant', 'Notes'],
    d.primarySymptoms.map(s => [s, '', '☐', '']),
    [Math.floor(CONTENT*0.34), Math.floor(CONTENT*0.16), Math.floor(CONTENT*0.14), Math.floor(CONTENT*0.36)],
  ));
  items.push(p(
    [tr('Primary Domain Score: ', BLACK, true, 20), tr('_____ / ', BLACK, false, 20), tr(String(d.primarySymptoms.length * 10), BLACK, false, 20)],
    { after: 80, before: 60 }
  ));

  items.push(empty());

  // B2 Secondary Symptoms
  items.push(p(tr('B2. Secondary Symptoms Domain', BLUE, true, 22), { before: 160, after: 80 }));
  items.push(tbl(
    ['Symptom', 'Score (0–10)', 'Relevant', 'Notes'],
    d.secondarySymptoms.map(s => [s, '', '☐', '']),
    [Math.floor(CONTENT*0.34), Math.floor(CONTENT*0.16), Math.floor(CONTENT*0.14), Math.floor(CONTENT*0.36)],
  ));
  items.push(p(
    [tr('Secondary Domain Score: ', BLACK, true, 20), tr('_____ / ', BLACK, false, 20), tr(String(d.secondarySymptoms.length * 10), BLACK, false, 20)],
    { after: 80, before: 60 }
  ));

  items.push(empty());

  // ── SECTION C ─────────────────────────────────────────────────────────────
  items.push(p(tr('SECTION C: BASELINE SUMMARY & CLINICAL IMPRESSION', NAVY, true, 24), { before: 200, after: 120 }));

  // FNON network-level impression (Partners-exclusive purple block)
  items.push(new Paragraph({
    children: [
      new TextRun({ text: '🟣 Network-Level Clinical Impression: ', color: PURPLE, bold: true, size: 22, font: 'Calibri' }),
      new TextRun({ text: 'Map dominant symptom cluster to hypothesised dysfunctional network(s)', color: PURPLE, size: 22, font: 'Calibri' }),
    ],
    spacing: { before: 120, after: 80 },
  }));

  items.push(tbl(
    ['FNON Network', 'Hypothesised Role', 'Evidence from Symptoms', 'Priority'],
    d.networkMapping.map(n => [n.network, n.role, n.evidence, n.priority]),
    [Math.floor(CONTENT*0.22), Math.floor(CONTENT*0.26), Math.floor(CONTENT*0.36), Math.floor(CONTENT*0.16)],
  ));

  items.push(empty());

  // Phenotype assignment
  items.push(p(tr('Phenotype Assignment:', NAVY, true, 22), { before: 120, after: 60 }));
  items.push(p(tr(d.phenotypeNote, BLACK, false, 20), { after: 100 }));

  // Clinical impression narrative
  items.push(p(tr('Clinical Impression:', NAVY, true, 22), { before: 120, after: 60 }));
  items.push(p(tr(d.clinicalImpression, BLACK, false, 20), { after: 100 }));

  // Recommended next steps
  items.push(p(tr('Recommended Next Steps:', NAVY, true, 22), { before: 120, after: 60 }));
  items.push(tbl(
    ['Step', 'Action', 'Priority'],
    [
      ['1', 'Complete SOZO network phenotyping assessment', 'High'],
      ['2', 'Review neuromodulation candidacy (TPS / tDCS / taVNS)', 'High'],
      ['3', `Condition-specific baseline measures for ${d.conditionShort}`, 'High'],
      ['4', 'Consent & psychoeducation (FNON protocol rationale)', 'Medium'],
      ['5', 'Schedule follow-up PRS at 4 weeks post-initiation', 'Medium'],
    ],
    [Math.floor(CONTENT*0.08), Math.floor(CONTENT*0.70), Math.floor(CONTENT*0.22)],
  ));

  items.push(empty());

  // Clinician sign-off
  items.push(tbl(
    ['Clinician Signature', 'Date', 'SOZO Tier'],
    [['', '', 'Partners']],
    [Math.floor(CONTENT*0.45), Math.floor(CONTENT*0.30), Math.floor(CONTENT*0.25)],
  ));

  // Confidentiality footer
  items.push(empty());
  items.push(new Paragraph({
    children: [new TextRun({
      text: 'CONFIDENTIAL — This document is intended solely for the named patient and authorised SOZO Brain Center clinicians. Not for distribution.',
      color: RED, size: 16, italics: true, font: 'Calibri',
    })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 0 },
  }));

  return new Document({
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
        },
      },
      children: items,
    }],
  });
}

// ── CLI entry ─────────────────────────────────────────────────────────────────
async function main() {
  const slug = process.argv[2];
  if (!slug) {
    console.error('Usage: node generate_psych_intake_partners.js <condition_slug>');
    process.exit(1);
  }

  const dataFile = path.join(__dirname, 'psych_intake_data', `${slug}.js`);
  if (!fs.existsSync(dataFile)) {
    console.error(`Condition data not found: ${dataFile}`);
    process.exit(1);
  }

  const d = require(dataFile);
  console.log(`Generating Psychological Intake & PRS Baseline (Partners) for: ${slug}`);

  const doc = buildDoc(d);
  const buf = await Packer.toBuffer(doc);

  const projectRoot = path.join(__dirname, '..');
  const outDir  = path.join(projectRoot, 'outputs', 'documents', slug, 'partners');
  fs.mkdirSync(outDir, { recursive: true });

  const outFile = path.join(outDir, `Psychological_Intake_PRS_Baseline_Partners_${slug}.docx`);
  fs.writeFileSync(outFile, buf);
  console.log(`✓ Saved: ${outFile}`);
}

main().catch(err => { console.error('Generation failed:', err.message); process.exit(1); });
