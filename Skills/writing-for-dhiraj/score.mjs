// Draft-vs-sent scorer: HAR + compression-based edit distance (zlib proxy for LZ77).
// Usage:
//   node score.mjs <draft-file> <sent-file>                    one-off score
//   node score.mjs --log <surface> <reader> <draft> <sent>     score + append to log.jsonl
//   node score.mjs --report                                    HAR + mean distance from log
// ponytail: zlib NCD approximates the paper's LZ77 metric; swap in real LZ77 if precision matters.
import { deflateSync } from 'zlib';
import fs from 'fs';
const z = s => deflateSync(Buffer.from(s), { level: 9 }).length;
const ncd = (a, b) => {
  if (a === b) return 0;
  const [ca, cb, cab] = [z(a), z(b), z(a + b)];
  return (cab - Math.min(ca, cb)) / Math.max(ca, cb);
};
const norm = s => s.replace(/\s+/g, ' ').trim();
const LOG = new URL('./log.jsonl', import.meta.url).pathname;

const args = process.argv.slice(2);
if (args[0] === '--report') {
  const rows = fs.existsSync(LOG) ? fs.readFileSync(LOG, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse) : [];
  if (!rows.length) { console.log('log empty'); process.exit(0); }
  const acc = rows.filter(r => r.distance < 0.05).length;
  console.log(`drafts: ${rows.length}`);
  console.log(`HAR (accepted ~unedited): ${(100 * acc / rows.length).toFixed(0)}%`);
  console.log(`mean edit distance: ${(rows.reduce((s, r) => s + r.distance, 0) / rows.length).toFixed(3)}`);
  for (const s of [...new Set(rows.map(r => r.surface))]) {
    const g = rows.filter(r => r.surface === s);
    console.log(`  ${s}: n=${g.length} mean=${(g.reduce((x, r) => x + r.distance, 0) / g.length).toFixed(3)}`);
  }
  process.exit(0);
}
const logging = args[0] === '--log';
const [surface, reader, draftF, sentF] = logging ? args.slice(1) : [null, null, ...args];
if (!draftF || !sentF) { console.log('usage: score.mjs [--log surface reader] draft sent | --report'); process.exit(1); }
const draft = norm(fs.readFileSync(draftF, 'utf8')), sent = norm(fs.readFileSync(sentF, 'utf8'));
const d = ncd(draft, sent);
console.log(`distance: ${d.toFixed(3)}  (0=accepted verbatim, >0.3=rewritten)`);
console.log(`words: draft ${draft.split(' ').length} -> sent ${sent.split(' ').length}`);
if (logging) {
  fs.appendFileSync(LOG, JSON.stringify({ date: new Date().toISOString().slice(0, 10), surface, reader, distance: +d.toFixed(3), draftWords: draft.split(' ').length, sentWords: sent.split(' ').length }) + '\n');
  console.log('logged');
}
// self-check: identical -> 0, disjoint -> high
if (process.env.SELFCHECK) {
  const eq = ncd('abc abc abc', 'abc abc abc'), df = ncd('quarterly revenue table', 'zx9 qq7 lmno pqrst');
  console.assert(eq === 0 && df > 0.3, `selfcheck failed eq=${eq} df=${df}`);
  console.log('selfcheck ok', eq, df.toFixed(2));
}
