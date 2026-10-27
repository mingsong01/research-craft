#!/usr/bin/env node
// Thin compatibility profile over the unmodified MIT-licensed Bybit svg-lint.
// It excludes only rules that conflict with this skill's explicit requirements:
// a project-owned semantic palette, orthogonal Manhattan routing, left-aligned
// scientific titles, and deliberately wide stage gutters.

import fs from 'node:fs';
import { lintSource } from './vendor/bybit-svg-lint/lib/lint.mjs';

const files = process.argv.slice(2);
if (!files.length) {
  console.error('usage: node bybit_svg_profile.mjs <file.svg...>');
  process.exit(2);
}

const excluded = (finding) =>
  finding.check === 'palette-conformance'
  || (finding.check === 'connector-geometry' && finding.code === 'curve-has-right-angle')
  || (finding.check === 'block-spacing' && ['spacing-too-loose', 'title-not-centered'].includes(finding.code));

const results = files.map((file) => {
  const source = fs.readFileSync(file, 'utf8');
  const report = lintSource(file, source);
  // Keep every upstream finding auditable. No additional rule is disabled by
  // this profile; the four pre-existing compatibility decisions remain visible.
  const dispositions = report.findings.filter(excluded).map((finding) => ({
    ...finding,
    disposition: 'profile-inapplicable',
    reason: finding.check === 'palette-conformance'
      ? 'Research semantic palette replaces the upstream brand palette; verify legend and rendered contrast separately.'
      : finding.code === 'curve-has-right-angle'
        ? 'Manhattan routes are intentional; local topology/obstacle QA and native rendering remain required.'
        : 'Stage gutters and scientific title alignment follow semantic grouping; verify final-size layout separately.',
  }));
  return { ...report, upstreamFindings: report.findings, dispositions,
    findings: report.findings.filter((finding) => !excluded(finding)) };
});
const errors = results.flatMap((result) => result.findings).filter((finding) => finding.severity === 'error').length;
const warnings = results.flatMap((result) => result.findings).filter((finding) => finding.severity === 'warning').length;
console.log(JSON.stringify({
  tool: 'bybit-svg-lint/research-diagram-profile',
  upstream: 'bybit-exchange/svg-diagram',
  summary: { files: results.length, errors, warnings, exitCode: errors ? 1 : 0 },
  files: results,
}, null, 2));
process.exit(errors ? 1 : 0);
