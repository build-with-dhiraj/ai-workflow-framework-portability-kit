# Hardening a shared Flowise before it becomes a real internal tool

## Read this before you plan anything else

Flowise was archived upstream on **13 August 2026** — four days ago. The repository is read-only, the final release is `3.1.4` (29 July 2026), and the core team leaves Discord and GitHub on **31 August 2026**. The security policy has been replaced with a sunset notice: vulnerability reports are no longer accepted.

That does not automatically mean rip it out. A frozen, pinned, internal-only Flowise behind SSO is a defensible position for a while. But it changes three things about your plan:

- "We'll patch it when a CVE lands" is no longer a strategy that terminates. Nobody is shipping the patch.
- Every fix below is something you own permanently, not a stopgap until upstream lands something.
- Whatever you build on it now, you will eventually reimplement elsewhere. That should shape what you invest in today (see the last section).

**And one thing that likely bites you this week: pin `3.1.3`, do not run `3.1.4` or `latest`.** The final release ships a Docker image that fails to boot on a fresh volume — `EACCES` on `/root/.flowise`, `Cannot find module '@smithy/eventstream-codec'`, `this.db.exec is not a function` from `connect-sqlite3`. It was filed one day after the code freeze and will never be fixed. `3.1.3` (25 June 2026) starts cleanly on identical config and is the last usable release.

If your compose file says `flowiseai/flowise:latest`, your next container recreate pulls a build that does not start. Change that today, independently of everything else.

---

## 1. The data loss — fix this first, it is a config bug and it will recur

You did not lose flows to a Flowise defect. You lost them because the data was never outside the container.

Flowise writes everything under `~/.flowise` by default. In the container that resolves to a path inside the writable layer, and `docker compose up --force-recreate` / an image pull throws it away. Two things go wrong at once, and people usually only fix the first:

**Persist the data.** Set all four paths explicitly rather than relying on the default. Relying on the default is precisely how people lose flows on a container restart:

```
DATABASE_PATH=/data/flowise
LOG_PATH=/data/flowise/logs
SECRETKEY_PATH=/data/flowise
BLOB_STORAGE_PATH=/data/flowise/storage
```

The container runs as **uid 1000**. If you bind-mount a host directory rather than using a named volume, `chown -R 1000:1000` it or the container starts and then fails to write.

**Pin the encryption key.** `SECRETKEY_PATH` above matters more than it looks. If the key file is regenerated — new volume, moved path, fresh container — every stored credential becomes undecryptable and you get "Credentials could not be decrypted" on flows that were working yesterday. Set a stable secret instead of trusting a file to survive:

```
FLOWISE_SECRETKEY_OVERWRITE=<a long random secret, backed up in your password manager>
```

Back that value up somewhere that is not the server. Losing it costs you every credential in the instance. If you ever move to queue mode, the main server and all workers must share the identical value.

**Then get flows into git, starting now.** Flowise has no version history, no diff, and no native way to see what change broke something. There is nothing to recover from after a bad edit or a lost volume — the only backup that exists is one you made. Run a scheduled export of every flow's JSON into a repo:

```bash
export FLOWISE_API_ENDPOINT=https://flowise.internal.example.com
export FLOWISE_API_KEY=...

node ~/.claude/skills/flowise/scripts/flowise.mjs flows                       # inventory
node ~/.claude/skills/flowise/scripts/flowise.mjs flow "My Flow" --out flows/my-flow.json
node ~/.claude/skills/flowise/scripts/flowise.mjs diff old.json new.json      # what changed
```

Put that on a nightly cron with a commit. It is the cheapest insurance available here and it is the only way anyone will later answer "what did that prompt say on the day it broke". It is also, given the archive, your migration artifact — more on that at the end.

---

## 2. The lockups — two separate causes, and Postgres only fixes one

Do not treat "it locks up" as a single problem. With three users there are two independent mechanisms and they need different fixes.

### Cause A: SQLite, which you should leave anyway

SQLite is the default and is genuinely fine for one person evaluating the tool. It is also where the concurrency and durability complaints cluster. Move to Postgres before this becomes a shared tool — you are already past that line.

```
DATABASE_TYPE=postgres
```

Valid values are `sqlite`, `mysql`, `postgres`, and — implemented but undocumented — `mariadb`. The connection variables follow the standard `DATABASE_HOST` / `DATABASE_PORT` / `DATABASE_NAME` / `DATABASE_USER` / `DATABASE_PASSWORD` set; **verify those against your running image rather than against the published docs**, because the docs' Docker example carries another product's port number and an invalid `DATABASE_TYPE` value. The documentation has real defects and this is one of the areas affected.

There is no migration tool from SQLite to Postgres. The path is: export every flow to JSON, stand up the Postgres-backed instance **at the same version**, import. Two things do not travel — credentials are never exported, so recreate them per environment; and chat history and execution records are not part of a flow export, so plan to lose them or dump them separately if they matter. Entity ids are preserved on some import paths, which is good news if anything calls `/api/v1/prediction/{id}` (your embeds may keep working), but check rather than assume.

Also note the export format changed at `3.0.0` and is not backward compatible. A `3.x` export cannot be imported into a `2.x` instance, and there is no converter. Match versions on both sides or the import fails with "Transaction is not started yet".

### Cause B: the memory leak, which Postgres does not fix

This is the best-corroborated problem in the project's history — seven independent reporters over twenty months, across multiple versions, on both Agentflow V1 and V2, on SQLite *and* Postgres, on Docker, Fargate and Kubernetes.

The mechanism was diagnosed by a user rather than a maintainer: graphs are added to a pool keyed by session id and never evicted, and the pool cannot be treated as a cache because nodes must be reprocessed per request to resolve `{{ }}` interpolation. So every request rebuilds the graph and the pool grows monotonically. Reported effects include roughly 150MB leaked per Custom MCP node added, several GB never released after a large vector upsert, worker memory never returned after a job completes in queue mode, and **8 to 12GB consumed by opening the admin Chat Messages panel on an instance with a large history**.

That last one is worth checking before you conclude anything: "it locks up when three of us use it" is exactly what it looks like when one person opens the chat-messages panel on a grown history in a container with a modest memory limit.

Everything available is a workaround, permanently:

- **Restart on a schedule.** A nightly cron that recycles the container is the most commonly reported fix and the one to implement.
- **Give it real memory.** 8–16GB, and expect to restart it regardless.
- **Do not open the admin Chat Messages panel** on instances with large histories. Tell the other two.

One person solved it properly by patching his own fork and abandoning `{{ }}` interpolation in favour of state variables. That works and it means becoming a Flowise maintainer.

### What not to build yet

`MODE=queue` with Redis, BullMQ and separate `pnpm start-worker` processes exists and is the documented production shape — two main servers behind a load balancer, four workers, each from 4 vCPU and 8GB. Take those numbers seriously if you ever get there: the one detailed concurrency complaint on record ran about a quarter of that hardware and fell over at 2 requests per second.

For three people, that is a lot of moving parts to own on a dead codebase. Single container, Postgres behind it, 8GB+, nightly restart. Revisit queue mode when you have measured a real throughput problem rather than a memory one. (If you do read the docs on this: their stated `WORKER_CONCURRENCY` default of 10000 is a copy error, not a real default.)

---

## 3. SSO — what it can and cannot be here

This is the part where the archive changes the answer most, so be precise about what "put it behind our SSO" means.

**Flowise's own identity layer is not open source.** Since `3.0.1` the repository is dual-licensed: `packages/server/src/enterprise/**` and `IdentityManager.ts` sit under a FlowiseAI commercial licence, not Apache 2.0. The README still says plain Apache 2.0; `LICENSE.md` is the operative document. On a self-hosted open-source install, the Roles, Login Activity, Logs, Evaluations, Datasets and Evaluators menus are visible in the UI and return **403** when clicked. That is licence gating, not a bug, and not something you can configure your way out of. Buying a licence to unlock it is a conversation with a vendor that sunset the product and whose team disperses on 31 August.

**So do SSO at the proxy.** Terminate your IdP in front of Flowise — an identity-aware proxy, oauth2-proxy, Cloudflare Access, whatever your org already runs — so Flowise never receives an unauthenticated request. That is the shape that actually works on a self-host and it is independent of the licence.

Three configuration items that break when you put a proxy in front, in the order they will bite you:

```
TRUST_PROXY=<your proxy's address or subnet, not the default>
NUMBER_OF_PROXIES=<calibrated, see below>
JWT_AUTH_TOKEN_SECRET=<random>
JWT_REFRESH_TOKEN_SECRET=<random>
EXPRESS_SESSION_SECRET=<random>
PASSWORD_SALT_HASH_ROUNDS=12
```

- `TRUST_PROXY` **defaults to trusting everything**, which makes client IPs — and therefore rate limits — spoofable the moment you are behind a load balancer. Set it to your actual proxy.
- `NUMBER_OF_PROXIES` has a calibration procedure, not a guessable value: start at 0, restart, call `GET /api/v1/ip`, compare the returned address to your real client IP, and increment until they match. Get this wrong and rate limiting misfires — either it never triggers, or it throttles everyone as one IP.
- The three secrets have defaults. Do not accept them on a shared instance.

**The gap SSO does not close.** Flows are **public by default**: anyone holding the chatflow id can call `POST /api/v1/prediction/{id}` until you assign a key. Your SSO proxy covers humans hitting the UI. It does not cover anything programmatic — and the moment you embed a flow in another internal app or call it from a script, that path must bypass the SSO gate to work at all.

So: **assign an API key per flow**, in the dashboard's API Keys section, before you expose anything. Keys have no scopes and no documented expiry, so treat them as long-lived shared secrets and store them accordingly. Related: `overrideConfig` has been disabled by default since `2.1.4`, per property, in each flow's Security tab. If you rely on runtime overrides from a caller, that is why they silently do nothing — it is almost never a malformed request body.

---

## 4. Security posture, stated plainly

Treat an internet-reachable Flowise instance as unmaintained software with public exploits.

In August 2026 a security firm published six remote-code-execution paths against `3.1.1` and `3.1.2`: a pickle deserialisation in the CSV agent, a sandbox escape, an MCP environment-variable denylist bypass, a TypeORM option abuse, an arbitrary file write through the SQL database chain, and a command injection in the SQLite record manager. Their conclusion was that fixes relying on denylists and narrow validation were repeatedly insufficient, and some bypasses were unpatched at publication. Public proof-of-concept code exists for an unauthenticated RCE and for an SSRF that bypasses the cloud-metadata denylist. There is also a prior maximum-severity RCE that was actively exploited in April 2026. Reports are no longer accepted, so none of this resolves.

None of that is a reason to panic if the instance is internal-only — an internal instance is a much smaller problem. It is a reason to make "internal-only" true and enforced at the network layer, not just implied by an SSO login page. Network restriction plus the SSO proxy, both.

One consequence you will hit while doing this: `HTTP_SECURITY_CHECK` has been on by default since `3.1.0`, so HTTP nodes pointing at internal hostnames or `localhost` will start failing. **Curate `HTTP_DENY_LIST` rather than disabling the check** — it is your SSRF guard, and there is a public PoC for bypassing it. If you also hit `NodeVM Execution Error: VMError: Cannot find module` from a custom function, add the module to `TOOL_FUNCTION_EXTERNAL_DEP`; do not reach for `ALLOW_BUILTIN_DEP=true`, which opens far more than you need.

---

## 5. Three dated deadlines, two of them inside two weeks

These are externally imposed and nobody upstream will handle them.

| Date | What breaks | Action |
|---|---|---|
| **26 Aug 2026** (9 days) | OpenAI retires the Assistants API | Any flow using the `openAIAssistant` node stops working |
| **31 Aug 2026** (14 days) | Maintainers leave, Discord support ends | Last chance to ask anyone anything |
| **16 Oct 2026** | Google retires the `gemini-2.5-pro` / `flash` / `flash-lite` defaults | Flows still on the default Gemini models stop working |

Check the first one directly rather than assuming, today:

```bash
node ~/.claude/skills/flowise/scripts/flowise.mjs get /api/v1/chatflows | grep -c openAIAssistant
```

The Custom Assistant path (`type: CUSTOM`) is unaffected — only the `openAIAssistant` node is exposed.

If you are ever probing the API by hand: there is **no `/api/v1/agentflows` endpoint**. It returns the single-page app's HTML with a 200 status, which looks like a working response and is not. Agentflows come from `/api/v1/chatflows?type=AGENTFLOW`. And note the naming trap while you inventory: `MULTIAGENT` in the type field means **Agentflow V1**, not "a multi-agent flow" — V2 is `AGENTFLOW`.

---

## The short version

Ordered by what to do this week:

1. **Pin `3.1.3`** in the compose file. Not `latest`, not `3.1.4`.
2. **Set the four persistence paths onto a real volume** (`chown 1000:1000` if bind-mounted) and set `FLOWISE_SECRETKEY_OVERWRITE` to a stable, backed-up secret. This is the actual cause of the lost flows.
3. **Start exporting every flow's JSON to git nightly.** There is no other backup and no version history.
4. **Grep for `openAIAssistant` today.** Nine days.
5. **Move to Postgres**, via export/import, same version both sides.
6. **Give the container 8–16GB and restart it nightly.** The memory leak is permanent and Postgres does not touch it.
7. **SSO at the proxy, not in Flowise.** Then fix `TRUST_PROXY`, calibrate `NUMBER_OF_PROXIES` against `/api/v1/ip`, set the three secrets, and assign an API key per flow — SSO does not protect the prediction endpoint.
8. **Confirm the instance is not internet-reachable** at the network layer.

## And the question under your question

You asked what to change before this becomes a real internal tool. Everything above makes it a *sound* internal tool. It is worth being clear-eyed that it will not become a *maintained* one.

Two structural facts drove most departures from Flowise even before the sunset, and both still apply. Flows are not a git artifact — no version history, no diff, no way to see what change broke something, only the hand-rolled JSON export you should now be committing. And there is no code export: requests for "export this flow as LangChain code" ran from June 2023 to July 2026 and were never shipped, which is exactly why several teams left. A community tool, `flowise-to-langchain`, converts flow JSON into TypeScript or Python and is lightly tested. A request for a headless runner that could execute an exported flow without the full server was filed fifteen days before the code freeze; the executor is deeply coupled to the server runtime and it was never actioned.

The realistic reading: your exports preserve the *design*, not a runnable artifact. Porting later means reimplementation, and the flow JSON is the specification you reimplement from. That is the real reason to start the nightly export now rather than on the day you need it.

On forking as a continuity plan — the sunset announcement recommends it, and two things temper that. The auth layer you would need for SSO (`IdentityManager.ts`, `enterprise/**`) is under the commercial licence rather than Apache 2.0, and a request to relicense went unanswered. And as of late August 2026 no serious community fork has emerged, only personal copies. Forking means owning dependency updates, security patches and model-API churn indefinitely, with the contributor base dispersed. It is a real option for a team that will genuinely staff it, and a comforting fiction otherwise.

So: harden it, pin it, back it up, and let it be the internal tool it is — while keeping the exports current enough that leaving is a project rather than an archaeology dig.
