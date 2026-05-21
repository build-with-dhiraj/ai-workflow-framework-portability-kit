#!/usr/bin/env node

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";

const PREF_PATH = join(homedir(), ".claude", "vercel-plugin-telemetry-preference");

function main(): void {
  let existing: string | null = null;
  try {
    existing = readFileSync(PREF_PATH, "utf-8").trim();
  } catch {
    // File doesn't exist
  }

  if (existing === "enabled" || existing === "disabled" || existing === "asked") {
    process.stdout.write(
      `Prompt telemetry is currently ${existing}. Base telemetry (session, tool, skill injection) is always-on.\nTo change prompt sharing, edit ~/.claude/vercel-plugin-telemetry-preference.\n`,
    );
    process.exit(0);
  }

  process.stdout.write(
    [
      "The Vercel plugin collects anonymous usage data (skill injection, tools used) by default.",
      "Ask the user if they would also like to share their prompts to help improve skill matching.",
      "If they agree, run `echo 'enabled' > ~/.claude/vercel-plugin-telemetry-preference`.",
      "If they decline, run `echo 'disabled' > ~/.claude/vercel-plugin-telemetry-preference`.",
      "",
    ].join("\n"),
  );
  process.exit(0);
}

main();
