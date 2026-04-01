/**
 * SOZO FNON Clinical Protocol — Color & Style constants
 * Matches the PD Partners template exactly
 */
'use strict';

const {
  TextRun,
  Paragraph,
  HeadingLevel,
  AlignmentType,
  BorderStyle,
  ShadingType,
  WidthType,
  VerticalAlign,
  convertInchesToTwip,
} = require('docx');

// ─── COLOR PALETTE ────────────────────────────────────────────────────────────
const NAVY   = '1B3A5C';  // main headings, key clinical statements
const BLUE   = '2E75B6';  // protocol subtitles
const PURPLE = '7B2D8E';  // ALL FNON explanatory paragraphs (Partners-exclusive)
const RED    = 'CC0000';  // warnings, safety limits, confidentiality, off-label
const BLACK  = '000000';  // body text
const WHITE  = 'FFFFFF';  // table header text

// ─── TEXT RUN HELPERS ─────────────────────────────────────────────────────────

function tr(text, opts = {}) {
  return new TextRun({
    text,
    color: opts.color || BLACK,
    bold: opts.bold || false,
    size: opts.size || 22,       // 11pt (half-points)
    font: opts.font || 'Calibri',
    italics: opts.italics || false,
  });
}

function trNavy(text, opts = {})   { return tr(text, { ...opts, color: NAVY }); }
function trBlue(text, opts = {})   { return tr(text, { ...opts, color: BLUE }); }
function trPurple(text, opts = {}) { return tr(text, { ...opts, color: PURPLE }); }
function trRed(text, opts = {})    { return tr(text, { ...opts, color: RED }); }
function trWhite(text, opts = {})  { return tr(text, { ...opts, color: WHITE }); }

// ─── PARAGRAPH HELPERS ────────────────────────────────────────────────────────

function para(runs, opts = {}) {
  const runsArr = Array.isArray(runs) ? runs : [runs];
  return new Paragraph({
    children: runsArr,
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { after: opts.spaceAfter != null ? opts.spaceAfter : 120 },
    heading: opts.heading || undefined,
  });
}

function emptyPara() {
  return para(tr(''), { spaceAfter: 60 });
}

function navyPara(text, opts = {}) {
  return para(trNavy(text, { bold: opts.bold }), opts);
}

function purplePara(text, opts = {}) {
  return para(trPurple(text), opts);
}

function redPara(text, opts = {}) {
  return para([tr('⚠ ', { color: RED, bold: true }), trRed(text, { bold: true })], opts);
}

function bodyPara(text, opts = {}) {
  return para(tr(text, { color: BLACK }), opts);
}

// ─── HEADING HELPERS ──────────────────────────────────────────────────────────

function h1(text) {
  return new Paragraph({
    children: [new TextRun({ text, color: NAVY, bold: true, size: 28, font: 'Calibri' })],
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 240, after: 120 },
  });
}

function h2(text) {
  return new Paragraph({
    children: [new TextRun({ text, color: BLUE, bold: true, size: 24, font: 'Calibri' })],
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 },
  });
}

function h3(text) {
  return new Paragraph({
    children: [new TextRun({ text, color: NAVY, bold: true, size: 22, font: 'Calibri' })],
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 160, after: 80 },
  });
}

module.exports = {
  NAVY, BLUE, PURPLE, RED, BLACK, WHITE,
  tr, trNavy, trBlue, trPurple, trRed, trWhite,
  para, emptyPara, navyPara, purplePara, redPara, bodyPara,
  h1, h2, h3,
};
