# Running, upgrading and eventually leaving Flowise

## The situation, and the dates that matter

Workday acquired Flowise on 14 August 2025. Eleven and a half months later the project was
sunset: code freeze 29 July 2026, repository archived 13 August 2026, core team leaves Discord
and GitHub 31 August 2026. Final release `3.1.4`, 29 July 2026.

Three externally-imposed deadlines nobody upstream will handle:

| Date | What breaks | Who is affected |
|---|---|---|
| 26 Aug 2026 | OpenAI retires the Assistants API | Any flow using the `openAIAssistant` node |
| 31 Aug 2026 | Maintainers leave; Discord support ends | Everyone, for support |
| 16 Oct 2026 | Google retires the `gemini-2.5-pro`/`flash`/`flash-lite` defaults | Flows on the default Gemini models |

Check the first one directly rather than assuming. `flowise.mjs get /api/v1/chatflows` and grep
node names for `openAIAssistant`; the Custom Assistant path (`type: CUSTOM`) is unaffected.

## Which version to run

**Pin `3.1.3`.** `3.1.4` ships a Docker image that fails to start on a fresh volume, with
`Package subpath './utils/uuid' is not defined by "exports" in @langchain/core`,
`Cannot find module '@smithy/eventstream-codec'`, and `this.db.exec is not a function` from
`connect-sqlite3`. It reproduces on clean config, so it is not a migration problem, and it was
filed one day after the code freeze. `3.1.3` starts cleanly on identical config.

Version boundaries worth knowing when reading someone else's instance:

| Version | Date | What it means |
|---|---|---|
| `2.0.0` | Jul 2024 | Sequential Agents, i.e. Agentflow V1, on LangGraph |
| `2.1.0` | Sep 2024 | Streaming moved to SSE. Embeds below this break |
| `2.1.4` | Nov 2024 | `overrideConfig` disabled by default, per property |
| `2.2.5` | Feb 2025 | Queue mode, BullMQ and Redis |
| `3.0.0` | May 2025 | Agentflow V2, new engine, Executions. Export format becomes incompatible with older versions |
| `3.0.1` | May 2025 | Auth rewritten to Passport plus JWT cookies. Commercial licence carve-out appears |
| `3.0.11` | Nov 2025 | Read/Write File tools removed permanently |
| `3.1.0` | Mar 2026 | `HTTP_SECURITY_CHECK` on by default. LangChain v1. Node 24 required |
| `3.1.3` | Jun 2026 | Last usable release |
| `3.1.4` | Jul 2026 | Final, and broken in Docker |

## Symptom to cause

| Symptom | Cause | What to do |
|---|---|---|
| `overrideConfig` silently ignored | Disabled by default since `2.1.4` | Enable each property in the flow's Security tab |
| HTTP node fails against internal hostnames or `localhost` | `HTTP_SECURITY_CHECK=true` default since `3.1.0` | Curate `HTTP_DENY_LIST`, or disable the check knowing it is an SSRF guard |
| `Package subpath './utils/uuid' is not defined` | LangChain v1 migration at `3.1.0` | Rebuild dependencies cleanly; custom code importing LangChain internals needs updating |
| `NodeVM Execution Error: VMError: Cannot find module` | Module not allowlisted for the sandbox | Add to `TOOL_FUNCTION_EXTERNAL_DEP`, not `ALLOW_BUILTIN_DEP=true` |
| "Credentials could not be decrypted" | Encryption key regenerated or its path moved | Set `FLOWISE_SECRETKEY_OVERWRITE` to a stable value and keep it stable |
| Import of an export file fails, "Transaction is not started yet" | Export format changed at `3.0.0` and is not backward compatible | Match versions; there is no converter |
| Rate limiting misfires behind a load balancer | `NUMBER_OF_PROXIES` wrong | Start at 0, restart, call `/api/v1/ip`, compare to your real IP, increment until they match |
| Enterprise UI menus return 403 on a self-hosted instance | Evaluations, Datasets, Evaluators, Roles, Login Activity and Logs are licence-gated | Not a bug. They are visible but gated without an enterprise licence |

## Memory, which is the operational issue

This is the best-corroborated problem in the project's history: seven independent reporters
across twenty months and multiple versions, on both Agentflow V1 and V2, SQLite and Postgres,
Docker, Fargate and Kubernetes.

The mechanism was diagnosed by a user rather than a maintainer: graphs are added to a pool keyed
by session id and never evicted, and the pool is not a cache, because nodes must be reprocessed
per request to resolve `{{ }}` interpolation. So every request rebuilds the graph and the pool
grows. Reported effects include roughly 150MB leaked per Custom MCP node added, several GB never
released after a large vector upsert, worker memory never returned after a job completes in
queue mode, and 8 to 12GB consumed by opening the admin chat-messages panel on a large history.

Practical mitigations, all of them workarounds:

- Restart on a schedule. Several teams run a cron that recycles the container, and this is the
  most commonly reported fix.
- Give workers generous limits, 8 to 16GB, and expect to restart pods.
- Avoid opening the admin Chat Messages panel on instances with large histories.
- One user solved it properly by patching his own fork and abandoning `{{ }}` interpolation in
  favour of state variables. That works, and it means becoming a Flowise maintainer.

## Security posture, which changed materially

Treat an internet-exposed Flowise instance as unmaintained software with public exploits.

In August 2026 a security firm published six remote code execution paths against `3.1.1` and
`3.1.2`, covering a pickle deserialisation in the CSV agent, a sandbox escape, an MCP
environment-variable denylist bypass, a TypeORM option abuse, an arbitrary file write through
the SQL database chain, and a command injection in the SQLite record manager. Their stated
conclusion was that fixes relying on denylists and narrow validation were repeatedly
insufficient, and some bypasses were unpatched at publication. Public proof-of-concept code
exists for an unauthenticated RCE and for an SSRF that bypasses the cloud-metadata denylist.
There is also a prior maximum-severity RCE that was actively exploited in April 2026.

The security policy was replaced with a sunset notice, so reports are no longer accepted. A
researcher who filed an unauthenticated data-exposure issue in August closed it himself on
discovering that.

What that implies, stated plainly rather than alarmingly: an instance reachable from the
internet should be put behind authentication and network restriction, or taken off the public
internet. An internal-only instance is a much smaller problem. Either way, "we will patch when
a CVE lands" is no longer a strategy that terminates.

## Deployment shape

**Database.** `DATABASE_TYPE` accepts `sqlite`, `mysql`, `postgres` and, undocumented but
implemented, `mariadb`. SQLite is the default and is genuinely fine for one person evaluating
it. Move to Postgres before it becomes a shared tool: SQLite is where the concurrency and
durability complaints cluster.

**Persistence.** Data lives under `~/.flowise` by default, and containers run as uid 1000, so a
bind mount needs `chown -R 1000:1000`. Set `DATABASE_PATH`, `LOG_PATH`, `SECRETKEY_PATH` and
`BLOB_STORAGE_PATH` explicitly rather than relying on the default, which is how people lose
flows on a container restart.

**Encryption key.** Set `FLOWISE_SECRETKEY_OVERWRITE` to a stable secret and back it up. Losing it
means every stored credential becomes undecryptable, and in queue mode the main server and all
workers must share it.

Set `SECRETKEY_PATH` alongside it, and this is the half people miss. They are not alternatives:
the override supplies the key, `SECRETKEY_PATH` decides where the key file is read from and written
to. Leave the path on its default inside a container and a restart can land on a fresh ephemeral
file, which produces "Credentials could not be decrypted" even though the override was set
correctly the whole time. Treat them as one setting with two halves, both pointed at persisted
storage.

**Concurrency.** `MODE=queue` with Redis and BullMQ, plus separate worker processes started with
`pnpm start-worker`. Three queues derive from `QUEUE_NAME`: prediction, upsertion and schedule.
The documented production shape is two main servers behind a load balancer and four workers,
each from 4 vCPU and 8GB. Take that seriously; the one detailed concurrency complaint on record
ran roughly a quarter of that hardware and fell over at 2 requests per second.

Set `WORKER_CONCURRENCY` deliberately. The documentation gives its default as `10000`, which is a
copy error rather than a real number, and the effective default is high enough to be unbounded for
practical purposes. Combined with the memory behaviour below, a worker that accepts everything
offered will grow until the pod is killed, and the symptom presents as a memory leak rather than as
a concurrency setting. Pick a number your worker memory can actually hold, in the low tens per
worker, and scale by adding workers instead of raising it.

**Storage.** `STORAGE_TYPE` is `local`, `s3`, `gcs` or `azure`. S3 supports `S3_ENDPOINT_URL`
and `S3_FORCE_PATH_STYLE`, so MinIO works.

**Auth.** Flows are **public by default**: anyone with the chatflow id can call it. Assign an API
key per flow. For the application itself, set `JWT_AUTH_TOKEN_SECRET`, `JWT_REFRESH_TOKEN_SECRET`
and `EXPRESS_SESSION_SECRET` rather than accepting defaults, and raise
`PASSWORD_SALT_HASH_ROUNDS` from 10 to 12 or more. `TRUST_PROXY` defaults to trusting everything,
which makes client IPs and therefore rate limits spoofable behind a load balancer.

## Treat flows as things you will one day need to leave

Two structural facts drove most pre-sunset departures, and both still apply:

**Flows are not a git artifact.** There is no version history in the product, no diff, and no
native way to see what change broke something. The community workaround is exporting JSON into a
repo and committing it by hand, which people describe as messy and error-prone. Do it anyway: a
scheduled export of every flow into version control is the cheapest insurance available, and it
is the only way a future reader can answer what a prompt said on a given date.

**There is no code export.** Requests for "export this flow as LangChain code" run from June 2023
to July 2026 and were never shipped, which is precisely why several teams left. A community tool,
`flowise-to-langchain`, converts flow JSON into TypeScript or Python and is lightly tested. A
request for a headless runner that could execute an exported flow without the full server was
filed fifteen days before the code freeze, with source citations showing the executor is deeply
coupled to the server runtime. It was never actioned.

The realistic reading: exporting your flows preserves the *design*, not a runnable artifact.
Porting means reimplementation, and the flow JSON is the specification you reimplement from. That
is a reason to keep exports current now rather than when you need them.

**On forking as a continuity plan.** The sunset announcement recommends it. Two things temper
that. The auth layer, `IdentityManager.ts` and `enterprise/**`, is under a commercial licence
rather than Apache 2.0, and a request to relicense went unanswered. And as of late August 2026 no
serious community fork had emerged, only personal copies. Forking means owning dependency
updates, security patches and model API churn indefinitely, with the contributor base dispersed.
It is a real option for a team that will genuinely staff it, and a comforting fiction otherwise.
