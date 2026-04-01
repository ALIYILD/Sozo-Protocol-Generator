/**
 * SOZO FNON Clinical Protocol — Table creation helpers
 * Navy (#1B3A5C) header rows with white text; body rows with black text
 */
'use strict';

const {
  Table,
  TableRow,
  TableCell,
  Paragraph,
  TextRun,
  WidthType,
  BorderStyle,
  ShadingType,
  VerticalAlign,
  AlignmentType,
} = require('docx');

const { NAVY, WHITE, BLACK } = require('./styles');

// ─── CELL HELPERS ─────────────────────────────────────────────────────────────

const BORDERS = {
  top:    { style: BorderStyle.SINGLE, size: 4, color: '999999' },
  bottom: { style: BorderStyle.SINGLE, size: 4, color: '999999' },
  left:   { style: BorderStyle.SINGLE, size: 4, color: '999999' },
  right:  { style: BorderStyle.SINGLE, size: 4, color: '999999' },
};

function headerCell(text) {
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

function bodyCell(text, opts = {}) {
  const color = opts.color || BLACK;
  return new TableCell({
    children: [new Paragraph({
      children: [new TextRun({ text: String(text || ''), color, size: 18, font: 'Calibri', bold: opts.bold || false })],
      alignment: AlignmentType.LEFT,
      spacing: { before: 40, after: 40 },
    })],
    shading: opts.shading ? { type: ShadingType.SOLID, color: opts.shading } : undefined,
    borders: BORDERS,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    verticalAlign: VerticalAlign.TOP,
    columnSpan: opts.span || 1,
  });
}

// ─── TABLE BUILDER ────────────────────────────────────────────────────────────

/**
 * Build a table from headers array and rows array.
 * @param {string[]} headers - column header labels
 * @param {string[][]} rows - data rows (each row is array of cell values)
 * @param {object} opts - { widths: number[] (percentages), width: number (total twip) }
 */
function buildTable(headers, rows, opts = {}) {
  const colCount = headers.length;
  const tableWidth = opts.width || 9200; // ~6.4 inch in twips (~9200)

  // Auto-distribute widths if not specified
  const widths = opts.widths || headers.map(() => Math.floor(tableWidth / colCount));

  const headerRow = new TableRow({
    children: headers.map(h => headerCell(h)),
    tableHeader: true,
  });

  const dataRows = rows.map(row => {
    // Pad short rows
    const cells = headers.map((_, i) => {
      const val = row[i] !== undefined ? row[i] : '';
      return bodyCell(val);
    });
    return new TableRow({ children: cells });
  });

  return new Table({
    rows: [headerRow, ...dataRows],
    width: { size: tableWidth, type: WidthType.DXA },
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    columnWidths: widths,
  });
}

module.exports = { buildTable, headerCell, bodyCell, BORDERS };
