#!/usr/bin/env node
// Publishes work-specific skills as sanitized copies: live skill in, public-safe skill out.
// Usage: node Tooling/sanitize-skills.mjs <skill> [<skill>...]   (run from the kit root)
// The name map is Private/sanitize-map.json (gitignored) so the public repo never lists the names it removes.
import fs from "node:fs"; import path from "node:path"; import os from "node:os";
const kit = process.cwd(), live = path.join(os.homedir(), ".claude/skills");
const { words } = JSON.parse(fs.readFileSync(path.join(kit, "Private/sanitize-map.json"), "utf8"));
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const wordRules = Object.keys(words).sort((a, b) => b.length - a.length)
  .map(k => [new RegExp(`(?<![A-Za-z0-9])${esc(k)}(?![A-Za-z0-9])`, "g"), words[k]]);
const patternRules = [
  [/glpat-[A-Za-z0-9._-]+/g, "glpat-REDACTED"], [/xox[bap]-[A-Za-z0-9-]+/g, "xoxb-REDACTED"],
  [/Bearer [A-Za-z0-9._-]{12,}/g, "Bearer REDACTED"], [/eyJ[A-Za-z0-9_-]{20,}(\.[A-Za-z0-9_-]+)*/g, "REDACTED_JWT"],
  [/pcsk_[A-Za-z0-9_]+/g, "pcsk_REDACTED"], [/AKIA[0-9A-Z]{16}/g, "AKIA_REDACTED"],
  [/(?<![A-Za-z0-9])[CDG]0[0-9A-Z]{8,10}(?![A-Za-z0-9])/g, "C0XXXXXXXXX"],
  [/(docs\.google\.com\/[a-z]+\/d\/)[A-Za-z0-9_-]{20,}/g, "$1DOC_ID"], [/\d{12}(\.dkr\.ecr)/g, "000000000000$1"],
  [/\/Users\/Dhiraj/g, "~"],
  // employer subdomains other than the public sites are internal hosts
  [/(?<![A-Za-z0-9.-])(?!www\.|app\.)[a-z0-9-]+(?:\.[a-z0-9-]+)*\.jove\.com/g, "internal-host.example.com"],
];
const isText = b => !b.subarray(0, 8000).includes(0);
let files = 0, changed = 0;
const walk = (src, dst) => { fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) { if (e.name === ".git") continue;
    const s = path.join(src, e.name), d = path.join(dst, e.name), st = fs.statSync(s); // statSync follows symlinks
    if (st.isDirectory()) { walk(s, d); continue; }
    const buf = fs.readFileSync(s); files++;
    if (!isText(buf)) { fs.writeFileSync(d, buf); continue; }
    let t = buf.toString("utf8"); const before = t;
    for (const [re, to] of [...wordRules, ...patternRules]) t = t.replace(re, to);
    if (t !== before) changed++; fs.writeFileSync(d, t); } };
for (const s of process.argv.slice(2)) { const dst = path.join(kit, "Skills", s);
  fs.rmSync(dst, { recursive: true, force: true }); walk(fs.realpathSync(path.join(live, s)), dst); }
console.log(`sanitized ${process.argv.length - 2} skills: ${files} files, ${changed} rewritten`);
