/**
 * SOZO FNON Clinical Protocol — Partners Tier Generator (Node.js)
 * Usage: node scripts/generate_fnon_condition.js <condition_slug>
 * Saves to: outputs/documents/<slug>/partners/FNON_Clinical_Protocol_Partners_<slug>.docx
 */
'use strict';

const path = require('path');
const fs = require('fs');
const { Packer } = require('docx');
const { buildDocument } = require('./fnon_generator/builder');

async function main() {
  const slug = process.argv[2];
  if (!slug) {
    console.error('Usage: node generate_fnon_condition.js <condition_slug>');
    process.exit(1);
  }

  const dataFile = path.join(__dirname, 'fnon_data', `${slug}.js`);
  if (!fs.existsSync(dataFile)) {
    console.error(`Condition data not found: ${dataFile}`);
    process.exit(1);
  }

  console.log(`Generating FNON Clinical Protocol for: ${slug}`);
  const conditionData = require(dataFile);

  const doc = buildDocument(conditionData);
  const buf = await Packer.toBuffer(doc);

  // Ensure output directory exists
  const projectRoot = path.join(__dirname, '..');
  const outDir = path.join(projectRoot, 'outputs', 'documents', slug, 'partners');
  fs.mkdirSync(outDir, { recursive: true });

  const outFile = path.join(outDir, `FNON_Clinical_Protocol_Partners_${slug}.docx`);
  fs.writeFileSync(outFile, buf);
  console.log(`✓ Saved: ${outFile}`);
}

main().catch(err => {
  console.error('Generation failed:', err.message);
  process.exit(1);
});
