#!/usr/bin/env node
// A read-first Flowise client. No dependencies, Node 18+.
//
// Why this exists: a Flowise instance's real behaviour lives in its flow graph, and that
// graph is awkward to read. Prompts come back HTML-wrapped from the rich-text editor,
// custom-function code comes back with escaped newlines, and `flowData` is a JSON string
// inside JSON. Every one of those costs a debugging cycle if you meet it cold, so this
// handles them once.
//
// Usage:
//   flowise.mjs flows                       list every flow: type, node count, id
//   flowise.mjs nodes   <name|id>           node map with kinds, sizes and edges
//   flowise.mjs prompts <name|id>           every LLM prompt, decoded and readable
//   flowise.mjs code    <name|id> [--node L]  custom-function JS, unescaped
//   flowise.mjs vars    <name|id>           {{ }} references, so you can see the data contract
//   flowise.mjs flow    <name|id>           the whole flow object as JSON
//   flowise.mjs get     <api-path>          any endpoint, raw
//   flowise.mjs diff    <fileA> <fileB>     structural diff of two saved exports
//
// Flags: --out <file>   write instead of printing
//        --json         machine-readable where it makes sense
//        --endpoint/--key   override credentials
//
// Credentials, first match wins:
//   1. --endpoint / --key
//   2. FLOWISE_API_ENDPOINT / FLOWISE_API_KEY
//   3. ~/.flowise.json  ->  { "endpoint": "...", "apiKey": "..." }
// A key is never printed, never logged, and never passed as a shell argument by this file.

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const argv = process.argv.slice(2);
const cmd = argv[0];
const flag = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const has = (n) => argv.includes(n);
const positional = argv.slice(1).filter((a, i, arr) => !a.startsWith("--") && !(i > 0 && arr[i - 1]?.startsWith("--")));

function creds() {
  const endpoint = flag("--endpoint") || process.env.FLOWISE_API_ENDPOINT;
  const apiKey = flag("--key") || process.env.FLOWISE_API_KEY;
  if (endpoint && apiKey) return { endpoint: endpoint.replace(/\/$/, ""), apiKey };
  const cfg = join(homedir(), ".flowise.json");
  if (existsSync(cfg)) {
    const c = JSON.parse(readFileSync(cfg, "utf8"));
    if (c.endpoint && c.apiKey) return { endpoint: String(c.endpoint).replace(/\/$/, ""), apiKey: c.apiKey };
  }
  die("no credentials. Set FLOWISE_API_ENDPOINT and FLOWISE_API_KEY, or pass --endpoint and --key, or write ~/.flowise.json with {endpoint, apiKey}.");
}

function die(msg, code = 2) { console.error("flowise: " + msg); process.exit(code); }

async function api(path) {
  const { endpoint, apiKey } = creds();
  const url = endpoint + path;
  let res;
  try {
    res = await fetch(url, { headers: { Authorization: "Bearer " + apiKey }, signal: AbortSignal.timeout(60000) });
  } catch (e) {
    die(`request to ${path} failed: ${e.message}`);
  }
  const body = await res.text();
  if (res.status === 401 || res.status === 403) {
    die(`${res.status} on ${path}. The key was rejected. Some deployments expect the header \`x-api-key\` instead of \`Authorization: Bearer\`; check which your instance uses.`);
  }
  if (!res.ok) die(`${res.status} on ${path}: ${body.slice(0, 300)}`);
  // A 200 carrying the single-page app shell means the path is a UI route, not an API route.
  // `/api/v1/agentflows` is the classic instance of this: it looks alive and returns HTML.
  if (/^\s*<!DOCTYPE html/i.test(body)) {
    die(`${path} returned the app's HTML, not JSON. That path is a UI route on this version. Agentflows are served from /api/v1/chatflows?type=AGENTFLOW, not from an /agentflows path.`);
  }
  try { return JSON.parse(body); } catch { return body; }
}

// flowData is a JSON *string* nested inside the flow object. Forgetting to parse it is the
// most common reason a flow looks empty.
const graphOf = (flow) => { try { return JSON.parse(flow.flowData || "{}"); } catch { return {}; } };

// Prompts are authored in a rich-text editor, so they arrive as HTML with entities. The
// visible text is what you want to reason about; the markup is noise.
function decode(s) {
  if (typeof s !== "string") return s;
  return s
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/p>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&")
    .trim();
}

// Custom-function bodies survive JSON transport with literal \n sequences. Turning them back
// into real newlines is the difference between readable code and one 8,000-character line.
const unescape = (s) => typeof s === "string" ? s.replace(/\\r\\n/g, "\n").replace(/\\n/g, "\n").replace(/\\t/g, "\t").replace(/\\"/g, '"') : s;

function walk(o, path = "") {
  const out = [];
  (function rec(v, p) {
    if (v && typeof v === "object") {
      for (const [k, val] of Object.entries(v)) rec(val, `${p}/${k}`);
    } else if (typeof v === "string") out.push([p, v]);
  })(o, path);
  return out;
}

async function findFlow(want) {
  if (!want) die("this command needs a flow name or id.");
  const flows = await api("/api/v1/chatflows");
  const list = Array.isArray(flows) ? flows : [];
  const hit = list.find(f => f.id === want)
    || list.find(f => f.name === want)
    || list.find(f => String(f.name).toLowerCase().includes(String(want).toLowerCase()));
  if (!hit) {
    const names = list.map(f => `  ${f.type || "?"}  ${f.name}`).join("\n");
    die(`no flow matching "${want}". Available:\n${names}`);
  }
  return hit;
}

function emit(text) {
  const out = flag("--out");
  if (out) { writeFileSync(out, text); console.log(`wrote ${out} (${text.length} bytes)`); }
  else console.log(text);
}

// ── commands ────────────────────────────────────────────────────────────────

async function cmdFlows() {
  const flows = await api("/api/v1/chatflows");
  const list = Array.isArray(flows) ? flows : [];
  if (has("--json")) return emit(JSON.stringify(list.map(f => ({
    id: f.id, name: f.name, type: f.type, nodes: (graphOf(f).nodes || []).length, deployed: f.deployed,
  })), null, 2));
  const rows = list.map(f => {
    const n = (graphOf(f).nodes || []).length;
    return `${String(f.type || "?").padEnd(10)} ${String(f.name).padEnd(40)} ${f.id}  nodes=${String(n).padStart(3)}  deployed=${f.deployed}`;
  });
  emit(rows.join("\n") + `\n\n${list.length} flows`);
}

async function cmdNodes(want) {
  const f = await findFlow(want);
  const g = graphOf(f);
  const nodes = g.nodes || [];
  const edges = g.edges || [];
  const lines = [`FLOW: ${f.name}  (${f.type})  id=${f.id}  nodes=${nodes.length}  edges=${edges.length}`, ""];
  nodes.forEach((n, i) => {
    const d = n.data || {};
    const label = d.label || n.label || n.id;
    const kind = d.name || n.type || "";
    lines.push(`[${String(i).padStart(2, "0")}] ${label}`);
    lines.push(`     kind=${kind}  id=${n.id}  size=${JSON.stringify(n).length}`);
  });
  if (edges.length) {
    lines.push("", "EDGES");
    for (const e of edges) lines.push(`  ${e.source} -> ${e.target}${e.sourceHandle ? `  (${e.sourceHandle})` : ""}`);
  }
  emit(lines.join("\n"));
}

async function cmdPrompts(want) {
  const f = await findFlow(want);
  const nodes = graphOf(f).nodes || [];
  const found = [];
  for (const n of nodes) {
    const d = n.data || {};
    const label = d.label || n.label || n.id;
    for (const [path, val] of walk(d.inputs ?? d)) {
      const isPromptish = /prompt|message|content|system|instruction|template/i.test(path);
      if (!isPromptish) continue;
      const text = decode(val);
      // Short strings here are labels and enum values, not prompts.
      if (text.length < 80) continue;
      found.push({ node: label, path, chars: text.length, text });
    }
  }
  if (has("--json")) return emit(JSON.stringify(found, null, 2));
  if (!found.length) return emit(`No prompts found in "${f.name}". If you expected some, run \`nodes\` first: a flow whose logic lives in custom functions keeps its instructions in code, not in prompt fields.`);
  const out = [`FLOW: ${f.name}   ${found.length} prompt field(s)`, ""];
  for (const p of found) {
    out.push("=".repeat(100), `### ${p.node}`, `    ${p.path}  (${p.chars} chars)`, "", p.text, "");
  }
  emit(out.join("\n"));
}

async function cmdCode(want) {
  const f = await findFlow(want);
  const nodes = graphOf(f).nodes || [];
  const only = flag("--node");
  const out = [];
  for (const n of nodes) {
    const d = n.data || {};
    const label = d.label || n.label || n.id;
    if (only && !label.toLowerCase().includes(only.toLowerCase())) continue;
    const inputs = d.inputs ?? d;

    // A custom-function node declares the state it reads as named input variables, then runs
    // a JS body against them. Showing the declarations first turns the body from orphaned
    // code into something with a data contract you can actually reason about.
    const receives = [];
    for (const [path, val] of walk(inputs)) {
      if (!/InputVariables\/\d+\/variableName/i.test(path)) continue;
      const idx = path.match(/InputVariables\/(\d+)\//)?.[1];
      const valuePath = path.replace(/variableName$/, "variableValue");
      const bound = walk(inputs).find(([p]) => p === valuePath)?.[1];
      receives.push(`  ${String(val).padEnd(28)} <- ${decode(bound || "").replace(/\s+/g, " ").slice(0, 80)}`);
    }

    // The JS body itself. Match the code key, never the declarations that share its prefix.
    for (const [path, val] of walk(inputs)) {
      if (!/javascript|functionBody|(^|\/)code$/i.test(path)) continue;
      if (/InputVariables/i.test(path)) continue;
      if (typeof val !== "string" || val.length < 40) continue;
      out.push("=".repeat(100), `### ${label}`, `    ${path}  (${val.length} chars)`);
      if (receives.length) out.push("", "  receives:", ...receives);
      out.push("", unescape(val), "");
    }
  }
  emit(out.length ? out.join("\n") : `No custom-function code found in "${f.name}"${only ? ` for node matching "${only}"` : ""}. Run \`nodes\` to see which nodes exist.`);
}

async function cmdVars(want) {
  const f = await findFlow(want);
  const nodes = graphOf(f).nodes || [];
  const refs = new Map();
  for (const n of nodes) {
    const d = n.data || {};
    const label = d.label || n.label || n.id;
    const blob = JSON.stringify(d);
    for (const m of blob.matchAll(/\{\{\s*([^}]+?)\s*\}\}/g)) {
      const key = m[1].trim();
      if (!refs.has(key)) refs.set(key, new Set());
      refs.get(key).add(label);
    }
  }
  const rows = [...refs.entries()].sort((a, b) => a[0].localeCompare(b[0]))
    .map(([k, v]) => `${k.padEnd(48)} ${[...v].join(", ")}`);
  emit(rows.length
    ? `Template references in "${f.name}" (the flow's real data contract):\n\n` + rows.join("\n")
    : `No {{ }} references in "${f.name}".`);
}

async function cmdFlow(want) {
  const f = await findFlow(want);
  emit(JSON.stringify({ ...f, flowData: graphOf(f) }, null, 2));
}

async function cmdGet(path) {
  if (!path) die("get needs an API path, for example /api/v1/nodes");
  emit(JSON.stringify(await api(path.startsWith("/") ? path : "/" + path), null, 2));
}

// Flows are edited in a GUI, so "what changed" is a real question with no built-in answer.
//
// Compare what a reader cares about, not what the canvas happens to store. Node ids,
// x/y positions, selection state and credential ids differ between any two instances
// of the same flow, so diffing raw node JSON marks every node changed and reports byte
// counts that mean nothing. Answering "did prod drift from dev" is the main reason this
// command exists, so it compares data.inputs per key with uuids normalised and names
// the fields that actually moved.
const DIFF_NOISE = /^(id|position|positionAbsolute|selected|dragging|width|height|zIndex|handleBounds)$/;
const denoise = (v) => (JSON.stringify(v, (k, val) => (DIFF_NOISE.test(k) ? undefined : val)) ?? "")
  .replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/g, "<uuid>");

function cmdDiff(a, b) {
  if (!a || !b) die("diff needs two saved export files.");
  const load = (p) => { const j = JSON.parse(readFileSync(p, "utf8")); return j.flowData && typeof j.flowData === "string" ? { ...j, flowData: JSON.parse(j.flowData) } : j; };
  const nodesOf = (x) => {
    const m = new Map();
    for (const n of (x.flowData?.nodes) || x.nodes || []) {
      const label = n.data?.label || n.label || n.id;
      // Repeated labels (Sticky Note, Condition 0) would silently collide and hide a node.
      let key = label, i = 2;
      while (m.has(key)) key = `${label} #${i++}`;
      m.set(key, { name: n.data?.name, inputs: n.data?.inputs ?? {} });
    }
    return m;
  };
  const na = nodesOf(load(a)), nb = nodesOf(load(b));
  const out = [];
  for (const k of nb.keys()) if (!na.has(k)) out.push(`+ ADDED    ${k}`);
  for (const k of na.keys()) if (!nb.has(k)) out.push(`- REMOVED  ${k}`);
  for (const k of na.keys()) {
    if (!nb.has(k)) continue;
    const A = na.get(k), B = nb.get(k);
    if (denoise(A) === denoise(B)) continue;
    const fields = [...new Set([...Object.keys(A.inputs), ...Object.keys(B.inputs)])]
      .filter((f) => denoise(A.inputs[f]) !== denoise(B.inputs[f]));
    out.push(`~ CHANGED  ${k}${fields.length ? `   fields: ${fields.join(", ")}` : "   (node type changed)"}`);
    for (const f of fields) {
      // Prompts run to thousands of characters, so show the first line that differs.
      const al = String(A.inputs[f] ?? "").split("\n"), bl = String(B.inputs[f] ?? "").split("\n");
      const at = al.findIndex((l, i) => l !== bl[i]);
      if (at >= 0) out.push(`             ${f}: first change at line ${at + 1}\n               A: ${(al[at] ?? "").slice(0, 150)}\n               B: ${(bl[at] ?? "").slice(0, 150)}`);
    }
  }
  emit(out.length ? out.join("\n") : "No semantic differences: same nodes, same inputs. Only ids and canvas positions differ.");
}

// ── dispatch ────────────────────────────────────────────────────────────────

const target = positional[0];
switch (cmd) {
  case "flows":   await cmdFlows(); break;
  case "nodes":   await cmdNodes(target); break;
  case "prompts": await cmdPrompts(target); break;
  case "code":    await cmdCode(target); break;
  case "vars":    await cmdVars(target); break;
  case "flow":    await cmdFlow(target); break;
  case "get":     await cmdGet(target); break;
  case "diff":    cmdDiff(positional[0], positional[1]); break;
  default:
    console.log(readFileSync(new URL(import.meta.url)).toString().split("\n").slice(1, 30).map(l => l.replace(/^\/\/ ?/, "")).join("\n"));
    process.exit(cmd ? 1 : 0);
}
