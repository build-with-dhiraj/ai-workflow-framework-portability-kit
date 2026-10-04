#!/usr/bin/env node
// lint-manuscript.mjs MANUSCRIPT.md --sources a.md b.md ...
// Fails on: missing/misordered PNAS sections, em dashes, bullets inside Results or Discussion,
// numbers in the manuscript absent from every source file.
import { readFileSync } from "node:fs";
const args = process.argv.slice(2);
const file = args[0];
const sources = args.slice(args.indexOf("--sources") + 1).filter(Boolean);
if (!file || !sources.length) { console.error("usage: lint-manuscript.mjs MANUSCRIPT.md --sources ..."); process.exit(2); }
const text = readFileSync(file, "utf8");
const src = sources.map(f => readFileSync(f, "utf8")).join("\n");
const errs = [];
const order = ["Significance", "Abstract", "Introduction", "Results", "Discussion", "Materials and Methods", "Data Availability", "References"];
const heads = [...text.matchAll(/^#{1,3}\s+(.+)$/gm)].map(m => m[1].trim());
let last = -1;
for (const h of order) {
  const i = heads.findIndex(x => x.toLowerCase().startsWith(h.toLowerCase()));
  if (i < 0) errs.push(`missing section: ${h}`);
  else if (i < last) errs.push(`section out of order: ${h}`);
  else last = i;
}
text.split("\n").forEach((l, i) => { if (l.includes("—")) errs.push(`em dash at line ${i + 1}`); });
for (const sec of ["Results", "Discussion"]) {
  const m = text.match(new RegExp(`^#{1,3}\\s+${sec}[\\s\\S]*?(?=^#{1,2}\\s|(?![\\s\\S]))`, "m"));
  if (m && /^\s*[-*]\s/m.test(m[0])) errs.push(`bulleted list inside ${sec}`);
}
const srcNums = new Set((src.match(/\d[\d,.]*/g) || []).map(n => n.replace(/[,.]$/, "")));
const body = text.replace(/^---[\s\S]*?---/, "").replace(/\(\d{4}\)/g, "").replace(/doi:\S+/g, "");
const missing = new Set();
for (const n of body.match(/\d[\d,.]*/g) || []) {
  const k = n.replace(/[,.]$/, "");
  if (k.length < 2 || /^(19|20)\d\d$/.test(k) || /^\d$/.test(k)) continue; // years and single digits are not claims
  if (!srcNums.has(k)) missing.add(k);
}
if (missing.size) errs.push(`numbers not found in any source: ${[...missing].slice(0, 40).join(", ")}${missing.size > 40 ? " ..." : ""}`);
if (errs.length) { console.error(errs.join("\n")); process.exit(1); }
console.log(`ok: ${heads.length} headings, sources ${sources.length}, numbers checked`);
