#!/usr/bin/env node
// BFS Jira issuelinks to depth 3 with JoVE prune rules.
// Live: JIRA_EMAIL + JIRA_API_TOKEN (aliases: ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN).
// Offline: --selftest
// ponytail: no SDK; REST + fixture. Slack hops stay with the agent.
import { Buffer } from "node:buffer";

const DEPTH = 3;
const SITE = process.env.JIRA_BASE || "https://your-org.atlassian.net";
const MEGA_EPICS = new Set(["JVA-29512"]);
const SKIP_LINK = /gantt|polaris|polar datapoint|polar merge|polar work|tested by/i;
const FOLLOW_LINK =
  /relates|blocks|duplicate|cloner|action item|escalate|resolve|problem\/incident|work item split|parent-child|is child of|is parent of/i;

const email = process.env.JIRA_EMAIL || process.env.ATLASSIAN_EMAIL;
const token = process.env.JIRA_API_TOKEN || process.env.ATLASSIAN_API_TOKEN;

function usage() {
  console.error("Usage: node walk.mjs --seed JVA-31344");
  console.error("       node walk.mjs --selftest");
  process.exit(2);
}

function parseArgs(argv) {
  if (argv.includes("--selftest")) return { selftest: true };
  const i = argv.indexOf("--seed");
  if (i < 0 || !argv[i + 1]) usage();
  return { seed: argv[i + 1].toUpperCase() };
}

function linkTypeName(link) {
  return link?.type?.name || link?.type || "";
}

function otherKey(link, here) {
  const inward = link.inwardIssue?.key;
  const outward = link.outwardIssue?.key;
  if (inward && inward !== here) return inward;
  if (outward && outward !== here) return outward;
  return null;
}

function shouldFollow(typeName) {
  if (!typeName) return false;
  if (SKIP_LINK.test(typeName)) return false;
  return FOLLOW_LINK.test(typeName);
}

function isMegaEpic(issue) {
  const key = issue.key;
  if (MEGA_EPICS.has(key)) return true;
  if (issue.issuetype === "Epic" && MEGA_EPICS.has(key)) return true;
  const epic = issue.epicLink || issue.parent;
  return Boolean(epic && MEGA_EPICS.has(epic));
}

export function walkGraph(seed, fetchIssue) {
  const hops = { 0: [], 1: [], 2: [], 3: [] };
  const skipped = [];
  const edges = [];
  const seen = new Set();
  const queue = [{ key: seed, hop: 0, via: null }];

  while (queue.length) {
    const { key, hop, via } = queue.shift();
    if (seen.has(key)) continue;
    if (hop > DEPTH) continue;
    seen.add(key);

    const issue = fetchIssue(key);
    if (!issue) {
      skipped.push({ key, reason: "fetch-failed" });
      continue;
    }
    const node = {
      key: issue.key,
      summary: issue.summary || "",
      issuetype: issue.issuetype || "",
      status: issue.status || "",
      via,
    };
    hops[hop].push(node);

    const leaf = hop === DEPTH || issue.issuetype === "Epic" || MEGA_EPICS.has(issue.key);
    if (leaf && hop < DEPTH && (issue.issuetype === "Epic" || MEGA_EPICS.has(issue.key))) {
      skipped.push({ key: issue.key, reason: "mega-epic-or-epic-leaf" });
    }
    if (leaf) continue;

    for (const link of issue.issuelinks || []) {
      const typeName = linkTypeName(link);
      const dest = otherKey(link, issue.key);
      if (!dest) continue;
      if (!shouldFollow(typeName)) {
        skipped.push({ key: dest, reason: `skip-link:${typeName}` });
        continue;
      }
      if (isMegaEpic({ key: dest, epicLink: dest }) && MEGA_EPICS.has(dest)) {
        if (!seen.has(dest) && hop + 1 <= DEPTH) {
          queue.push({ key: dest, hop: hop + 1, via: typeName });
        }
        continue;
      }
      edges.push({ from: issue.key, to: dest, hop: hop + 1, linkType: typeName });
      if (!seen.has(dest)) queue.push({ key: dest, hop: hop + 1, via: typeName });
    }
  }

  return { seed, hops, skipped, edges };
}

const FIXTURE = {
  "JVA-31344": {
    key: "JVA-31344",
    summary: "Authors cannot download PDFs",
    issuetype: "Expedited",
    status: "Closed",
    issuelinks: [
      { type: { name: "Relates" }, outwardIssue: { key: "JVA-31632" } },
      { type: { name: "Relates" }, outwardIssue: { key: "JVA-25045" } },
      { type: { name: "Gantt End to Start" }, outwardIssue: { key: "JVA-99999" } },
      { type: { name: "Relates" }, outwardIssue: { key: "JVA-29512" } },
    ],
  },
  "JVA-31632": {
    key: "JVA-31632",
    summary: "PDF attach + privilege matrix",
    issuetype: "Story",
    status: "To Do (ENG)",
    issuelinks: [{ type: { name: "Relates" }, outwardIssue: { key: "JVA-31344" } }],
  },
  "JVA-25045": {
    key: "JVA-25045",
    summary: "Standard Access notice copy",
    issuetype: "Task",
    status: "Done",
    issuelinks: [
      { type: { name: "Relates" }, outwardIssue: { key: "JVA-19543" } },
      { type: { name: "Relates" }, outwardIssue: { key: "JVA-25851" } },
    ],
  },
  "JVA-19543": {
    key: "JVA-19543",
    summary: "Delayed paywall text only",
    issuetype: "Story",
    status: "Done",
    issuelinks: [{ type: { name: "Relates" }, outwardIssue: { key: "JVA-19765" } }],
  },
  "JVA-25851": {
    key: "JVA-25851",
    summary: "Survey in publication email",
    issuetype: "Expedited",
    status: "Done",
    issuelinks: [],
  },
  "JVA-19765": {
    key: "JVA-19765",
    summary: "www clone of 19543",
    issuetype: "Story",
    status: "Closed",
    issuelinks: [],
  },
  "JVA-29512": {
    key: "JVA-29512",
    summary: "JoVE Labs V2",
    issuetype: "Epic",
    status: "In Progress",
    issuelinks: [{ type: { name: "Relates" }, outwardIssue: { key: "JVA-29997" } }],
  },
  "JVA-29997": {
    key: "JVA-29997",
    summary: "should never be reached from the epic",
    issuetype: "Story",
    status: "Done",
    issuelinks: [],
  },
};

function selftest() {
  const { hops, skipped, edges } = walkGraph("JVA-31344", (k) => FIXTURE[k]);
  const keys = (n) => hops[n].map((x) => x.key).sort();
  const fail = (msg) => {
    console.error("✗ walk selftest:", msg);
    process.exit(1);
  };
  if (keys(0).join() !== "JVA-31344") fail("seed missing");
  if (!keys(1).includes("JVA-25045") || !keys(1).includes("JVA-31632")) fail("hop 1");
  if (!keys(1).includes("JVA-29512")) fail("mega-epic should appear as a leaf");
  if (keys(1).includes("JVA-99999")) fail("Gantt link was followed");
  if (!keys(2).includes("JVA-19543") || !keys(2).includes("JVA-25851")) fail("hop 2");
  if (!keys(3).includes("JVA-19765")) fail("hop 3");
  if (Object.values(hops).flat().some((n) => n.key === "JVA-29997")) fail("epic children leaked");
  if (!skipped.some((s) => /Gantt/.test(s.reason))) fail("gantt skip unrecorded");
  if (!edges.some((e) => e.to === "JVA-19543")) fail("edge missing");
  console.log("✓ walk selftest — depth 3, Gantt skipped, mega-epic is a leaf");
}

async function fetchLive(key) {
  const auth = Buffer.from(`${email}:${token}`).toString("base64");
  const url = `${SITE}/rest/api/3/issue/${encodeURIComponent(key)}?fields=summary,issuetype,status,issuelinks,parent,customfield_10014`;
  const res = await fetch(url, { headers: { Authorization: `Basic ${auth}`, Accept: "application/json" } });
  if (!res.ok) return null;
  const j = await res.json();
  const f = j.fields || {};
  return {
    key: j.key,
    summary: f.summary,
    issuetype: f.issuetype?.name,
    status: f.status?.name,
    parent: f.parent?.key,
    epicLink: f.customfield_10014,
    issuelinks: f.issuelinks || [],
  };
}

async function live(seed) {
  if (!email || !token) {
    console.error("walk.mjs: no JIRA_EMAIL/JIRA_API_TOKEN (or ATLASSIAN_*). BFS via getJiraIssue issuelinks. Same FOLLOW/SKIP/mega-epic rules. Do not shorten the walk.");
    process.exit(2);
  }
  const cache = new Map();
  const seen = new Set();
  const queue = [{ key: seed, hop: 0 }];
  while (queue.length) {
    const { key, hop } = queue.shift();
    if (seen.has(key) || hop > DEPTH) continue;
    seen.add(key);
    const issue = await fetchLive(key);
    cache.set(key, issue);
    if (!issue || hop === DEPTH || issue.issuetype === "Epic" || MEGA_EPICS.has(issue.key)) continue;
    for (const link of issue.issuelinks || []) {
      const dest = otherKey(link, issue.key);
      if (!dest || !shouldFollow(linkTypeName(link))) continue;
      if (!seen.has(dest)) queue.push({ key: dest, hop: hop + 1 });
    }
  }
  console.log(JSON.stringify(walkGraph(seed, (k) => cache.get(k) ?? null), null, 2));
}

const args = parseArgs(process.argv.slice(2));
if (args.selftest) selftest();
else live(args.seed).catch((e) => {
  console.error(e.message);
  process.exit(1);
});
