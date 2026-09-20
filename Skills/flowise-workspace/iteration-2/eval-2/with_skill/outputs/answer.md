# Hardening self-hosted Flowise for a small team

## Read this before the checklist

**Flowise was archived on 13 August 2026 — four days ago. It is read-only.** Final release is
`3.1.4` (29 July 2026), and the core team leaves Discord and GitHub on **31 August 2026**. The
security policy has been replaced with a sunset notice: vulnerability reports are no longer
accepted.

That changes the shape of your question. "Make this a real internal tool" no longer means
"configure it properly and keep it updated" — there are no more updates. It means **you become the
maintainer of this software**, permanently, starting now. Everything below is written for that
reality rather than around it.

Two immediate consequences before any config:

- **Do not "upgrade to latest."** Pin `3.1.3` (25 June 2026). `3.1.4` ships a Docker image that
  fails to start on a fresh volume — `EACCES` on `/root/.flowise`,
  `Cannot find module '@smithy/eventstream-codec'`, `this.db.exec is not a function` from
  `connect-sqlite3`, and `Package subpath './utils/uuid' is not defined by "exports" in
  @langchain/core`. It reproduces on clean config, so it isn't a migration problem, and it was
  filed one day after the code freeze. It will never be fixed. `3.1.3` starts cleanly on identical
  config.
- **There is a hard deadline nine days out.** On **26 August 2026** OpenAI retires the Assistants
  API. Any flow using the `openAIAssistant` node stops working, and nobody upstream will patch it.
  This is checkable in one command (below), so check rather than assume.

## The answer, ordered by what will hurt you first

| # | Change | Fixes | Urgency |
|---|---|---|---|
| 1 | Pin the image to `3.1.3` and make `~/.flowise` genuinely persistent | The lost flows | Today |
| 2 | Set `FLOWISE_SECRETKEY_OVERWRITE` **and** `SECRETKEY_PATH`, and back the key up | Silent credential loss on restart | Today |
| 3 | Move `DATABASE_TYPE` to `postgres` | The lock-ups | This week |
| 4 | Scheduled JSON export of every flow into git | No version history, no rollback, no exit | This week |
| 5 | Grep your flows for the `openAIAssistant` node | 26 Aug breakage | This week |
| 6 | SSO at the reverse proxy, **plus** an API key per flow | Access control | Before you open it up |
| 7 | Confirm no public ingress | Six published RCE paths, unpatchable | Before you open it up |

Items 1, 2 and 7 are the ones where doing nothing has a bad ending. Item 3 is what you actually
asked about and is the least dangerous of the set.

## 1. The lost flows are a persistence bug, and it's the urgent one

Flowise stores everything under `~/.flowise` by default. If that path wasn't on a volume — or was
on a volume the container couldn't write — a restart lands on a fresh directory and the flows are
simply gone. Two specifics that catch people:

- **Containers run as uid 1000.** A bind mount needs `chown -R 1000:1000` or writes fail, sometimes
  partially and quietly.
- **Set the paths explicitly** rather than relying on the default. `DATABASE_PATH`, `LOG_PATH`,
  `SECRETKEY_PATH` and `BLOB_STORAGE_PATH`. Relying on the default is specifically how people lose
  flows on a container restart.

Named Docker volumes sidestep the ownership problem entirely, which is why the compose below uses
them instead of bind mounts.

## 2. The encryption key has two halves, and everyone sets only one

`FLOWISE_SECRETKEY_OVERWRITE` supplies the key. `SECRETKEY_PATH` decides where the key file is read
from and written to. **They are not alternatives.** Leave the path on its container default and a
restart can land on a fresh ephemeral file, which produces `Credentials could not be decrypted`
even though the override was set correctly the whole time. Treat them as one setting with two
halves, both pointed at persisted storage, and back the key value up somewhere that isn't the
container.

Since you already lost data in a restart, **check now whether your stored credentials still
decrypt** — open a flow with an API-key credential and run it. If the key was regenerated during
that incident, credentials need recreating, and you'd rather discover that deliberately than
mid-demo.

## 3. SQLite is the right call for one person and the wrong one for three

`DATABASE_TYPE` accepts `sqlite`, `mysql`, `postgres`, and — undocumented but implemented —
`mariadb`. SQLite is the default and is genuinely fine for one person evaluating the tool. It is
also exactly where the concurrency and durability complaints cluster. Three concurrent users is the
point at which you move to Postgres. That directly addresses the lock-ups.

**But set your expectations honestly: Postgres will not fix all of it.** There is a
well-corroborated memory problem in Flowise, independent of database choice — seven independent
reporters over twenty months, across multiple versions, on Agentflow V1 and V2, on SQLite *and*
Postgres, on Docker, Fargate and Kubernetes. The mechanism was diagnosed by a user, not a
maintainer: graphs are added to a pool keyed by session id and never evicted, and the pool can't act
as a cache because nodes must be reprocessed per request to resolve `{{ }}` interpolation. So every
request rebuilds the graph and the pool grows.

Reported magnitudes, so you can recognise it: roughly 150MB leaked per Custom MCP node added,
several GB never released after a large vector upsert, worker memory never returned after a job
completes in queue mode, and **8–12GB consumed by opening the admin Chat Messages panel on a large
history**. That last one is worth telling all three of you: don't open that panel on a busy
instance.

The mitigations are all workarounds, and the honest one is a scheduled container restart. Several
teams do exactly this and report it as the most effective fix.

> **Sequencing matters here.** A restart cron is what lost your flows last week. Fix persistence
> (§1) and the secret key (§2) *first*, verify a manual restart preserves everything, and only then
> automate the restart. Otherwise you've automated the data loss.

### What I am deliberately not recommending

The documented production shape is two main servers behind a load balancer plus four workers in
`MODE=queue` with Redis and BullMQ, each from 4 vCPU and 8GB. **You have three users. Skip it.** One
container against Postgres with a nightly recycle covers three people comfortably. Queue mode adds
Redis, worker processes, three BullMQ queues, and a stream path fed through Redis pub/sub that has a
history of fragility — including a fix shipped and reverted in the same release. That's a lot of new
failure surface bought against load you don't have.

Take the topology seriously *when* you have the traffic: the one detailed concurrency complaint on
record ran roughly a quarter of that hardware and fell over at 2 requests per second. If you do go
to queue mode later, set `WORKER_CONCURRENCY` deliberately — the documentation gives its default as
`10000`, which is a copy error rather than a real number, and the effective default is unbounded for
practical purposes. Combined with the memory behaviour above, a worker that accepts everything
offered grows until the pod is killed, and it presents as a memory leak rather than as a concurrency
setting. Pick a number your worker memory can hold, in the low tens, and scale by adding workers.

### The migration itself

There is no automatic SQLite → Postgres migration. The path is manual:

1. **Export every flow's JSON from the current instance first** (see §4). Do this before you touch
   anything.
2. Stand up Postgres, point a `3.1.3` instance at it, import the flows.
3. **Recreate credentials by hand.** They are deliberately not included in exports.
4. Check for id collisions — entity ids are preserved on some import paths, so an imported flow can
   keep its id and collide. Check rather than assume.
5. Accept that **chat history and executions do not come across.** For three internal users that's
   almost certainly fine, but it should be a decision rather than a surprise.

If you ever import between instances, match versions: the export format changed at `3.0.0` and is
not backward compatible. A failed import reporting `Transaction is not started yet` is that, and
there is no converter.

## 4. Flows are not a git artifact, so make them one

There is no version history in the product, no diff, and no native way to see which change broke
something. Flows are edited in a GUI, so once three people are editing, "who changed this and when"
becomes unanswerable by default. The community workaround is exporting JSON into a repo and
committing it, which people describe as messy — do it anyway. It is the cheapest insurance
available and the only way anyone can later establish what a prompt said on a given date.

The skill ships a dependency-free client that does this without you writing anything:

```bash
export FLOWISE_API_ENDPOINT=https://flowise.internal.example.com
export FLOWISE_API_KEY=...

node scripts/flowise.mjs flows                              # inventory: type, node count, id
node scripts/flowise.mjs flow "My Flow" --out flows/my-flow.json
node scripts/flowise.mjs diff old.json new.json             # what actually changed
```

Put the export on a schedule (cron, or a CI job) and commit the output. `diff` is built for exactly
the question you'll have: it normalises away node ids, credential ids and canvas coordinates — which
otherwise mark every node as changed and tell you nothing — and names the fields that actually
moved. "No semantic differences" becomes a real answer.

Add ordinary Postgres backups alongside it. Once you're on Postgres, the flows live in the database,
so your DB backup covers them; the exports are for readability, review and diffing, and they cover
the case where the database is fine but someone edited a prompt.

**One caveat about what an export is.** It preserves the *design*, not a runnable artifact. There is
no code export — requests for "export this flow as LangChain code" run from June 2023 to July 2026
and were never shipped, and a request for a headless runner that could execute an exported flow
without the full server was filed fifteen days before the code freeze, with source citations showing
the executor is deeply coupled to the server runtime. Never actioned. A community tool,
`flowise-to-langchain`, converts flow JSON to TypeScript or Python and is lightly tested. So treat
your exports as the specification you would reimplement from — which is a reason to keep them
current now, not when you need them.

## 5. Check the 26 August deadline today

```bash
node scripts/flowise.mjs get /api/v1/chatflows | grep -c openAIAssistant
```

Any hit is a flow that breaks in nine days when OpenAI retires the Assistants API. The Custom
Assistant path (`type: CUSTOM`) is unaffected — only the `openAIAssistant` node.

While you're in there, note a second date: **16 October 2026**, when Google retires the
`gemini-2.5-pro`, `flash` and `flash-lite` defaults. Any flow sitting on a default Gemini model
needs its model pinned to something that will still exist. Neither of these will be handled
upstream.

## 6. SSO: put it in front, not inside

This is the item where the archive changes the answer most, so two separate points.

**Flowise's built-in auth and SSO live under a commercial licence, not Apache 2.0.** Since `3.0.1`
the repo is dual-licensed: `packages/server/src/enterprise/**` and `IdentityManager.ts` sit under a
FlowiseAI commercial licence, and `IdentityManager.ts` is load-bearing for auth and route mounting.
The README still says plain Apache 2.0; `LICENSE.md` is the operative document. On a self-hosted
open-source instance the enterprise surfaces — Roles, Login Activity, Logs, Evaluations, Datasets,
Evaluators — are visible in the UI and return 403. **That is gating, not a bug**, and it's a common
false bug report. `GET /api/v1/settings` returns `PLATFORM_TYPE`, which tells you which side of that
line your instance is on.

So the built-in route means buying a commercial licence for a product whose maintainers walk away on
31 August 2026. That may still be the right call if you need in-app roles specifically, but name the
bet before you make it.

**The pragmatic route: terminate SSO at the reverse proxy.** oauth2-proxy, your IdP's forward-auth,
Cloudflare Access, or an internal ALB with OIDC — anything that is still maintained. Flowise binds
to loopback and only ever sees authenticated traffic. For three internal users this is less work
than the enterprise path, it's the same pattern you'll reuse for the next internal tool, and the
component doing your authentication is software that still receives security fixes. Given §7, that
last point is the whole argument.

**Then the part people miss: SSO on the UI does not protect your flows.** Flows are **public by
default** — anyone holding the chatflow id can `POST /api/v1/prediction/{chatflowId}` until you
assign a key. The prediction API is a separate door from the UI login, and a proxy that only guards
the UI leaves it open. **Assign an API key per flow** in the dashboard's API Keys section. Keys have
no scopes and no documented expiry, so treat them as long-lived shared secrets and keep them
server-side (proxy predictions through your own backend rather than calling from a browser).

Set these rather than accepting defaults, whichever route you take:

| Setting | Why |
|---|---|
| `JWT_AUTH_TOKEN_SECRET`, `JWT_REFRESH_TOKEN_SECRET`, `EXPRESS_SESSION_SECRET` | Defaults are not secrets |
| `PASSWORD_SALT_HASH_ROUNDS` | Raise from 10 to 12 or more |
| `TRUST_PROXY` | Defaults to trusting everything, which makes client IPs — and therefore rate limits — spoofable behind a proxy |
| `NUMBER_OF_PROXIES` | Must match your real proxy depth or rate limiting misfires |
| `CORS_ORIGINS`, `IFRAME_ORIGINS` | A missing `Access-Control-Allow-Origin` in the browser is this, not a widget setting |

`NUMBER_OF_PROXIES` becomes relevant *because* you're adding a proxy, and it has an exact
calibration procedure rather than a guess: set it to 0, restart, call `GET /api/v1/ip`, compare what
the server reports to your real IP, and increment until they match.

## 7. The security posture is the real gate on "internal tool"

Treat an internet-exposed Flowise instance as unmaintained software with public exploits — because
that is now literally what it is.

In August 2026 a security firm published six remote code execution paths against `3.1.1` and
`3.1.2`: a pickle deserialisation in the CSV agent, a sandbox escape, an MCP environment-variable
denylist bypass, a TypeORM option abuse, an arbitrary file write through the SQL database chain, and
a command injection in the SQLite record manager. Their stated conclusion was that fixes relying on
denylists and narrow validation were repeatedly insufficient, and some bypasses were unpatched at
publication. Public proof-of-concept code exists for an unauthenticated RCE and for an SSRF that
bypasses the cloud-metadata denylist. A prior maximum-severity RCE was actively exploited in April
2026. Reports are no longer accepted — a researcher who filed an unauthenticated data-exposure issue
this month closed it himself on discovering that.

Stated plainly rather than alarmingly: **an internal-only instance is a much smaller problem, and
that is the configuration you should choose.** No public ingress, network-restricted, SSO in front.
What is no longer available is the strategy "we'll patch when a CVE lands" — that sentence no longer
terminates.

Two related settings you'll meet while doing this:

- `HTTP_SECURITY_CHECK` is on by default since `3.1.0`. If HTTP nodes fail against internal
  hostnames or `localhost`, that's why. Curate `HTTP_DENY_LIST` rather than switching the check off
  blindly — it is your SSRF guard, and there's a public PoC against the metadata denylist.
- If a custom function node throws `NodeVM Execution Error: VMError: Cannot find module`, add the
  module to `TOOL_FUNCTION_EXTERNAL_DEP`. Do **not** reach for `ALLOW_BUILTIN_DEP=true` — one of the
  six published paths is a sandbox escape.

## The config

```yaml
# docker-compose.yml
services:
  flowise:
    image: flowiseai/flowise:3.1.3        # pinned: NOT latest, NOT 3.1.4
    restart: unless-stopped
    depends_on: [db]
    ports: ["127.0.0.1:3000:3000"]        # loopback only — the proxy terminates SSO
    environment:
      DATABASE_TYPE: postgres
      DATABASE_HOST: db
      DATABASE_PORT: 5432
      DATABASE_NAME: flowise
      DATABASE_USER: flowise
      DATABASE_PASSWORD: ${PG_PASSWORD}

      # persistence — the half that lost your flows
      SECRETKEY_PATH: /data/secret        # must be persisted, see below
      BLOB_STORAGE_PATH: /data/storage
      LOG_PATH: /data/logs
      # DATABASE_PATH is sqlite-only and drops out once you're on Postgres

      # the other half: supplies the key. Both, always, or credentials break on restart.
      FLOWISE_SECRETKEY_OVERWRITE: ${FLOWISE_SECRETKEY}   # back this up outside the container

      JWT_AUTH_TOKEN_SECRET: ${JWT_AUTH_SECRET}
      JWT_REFRESH_TOKEN_SECRET: ${JWT_REFRESH_SECRET}
      EXPRESS_SESSION_SECRET: ${SESSION_SECRET}
      PASSWORD_SALT_HASH_ROUNDS: 12

      NUMBER_OF_PROXIES: 1                # calibrate via GET /api/v1/ip, don't guess
      CORS_ORIGINS: https://flowise.internal.example.com
    volumes:
      - flowise-data:/data                # named volume: avoids the uid-1000 chown trap

  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: flowise
      POSTGRES_USER: flowise
      POSTGRES_PASSWORD: ${PG_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  flowise-data:
  pgdata:
```

If you use bind mounts instead of named volumes, `chown -R 1000:1000` the host directories first.

Then, in order: export flows from the old instance → bring this up → import → recreate credentials
→ assign an API key per flow → verify a manual `docker compose restart` preserves flows *and*
decrypts credentials → only then add the nightly restart cron and the scheduled export job.

## The decision you're actually making

You're adopting archived software as an internal tool, four days after it was archived. That can be
a perfectly reasonable choice — but it's a choice, and it has three honest versions:

1. **Run it pinned, internal-only, with current exports and a named exit trigger.** Cheapest, and
   correct for a tool three people use to build internal flows. The exit trigger is the thing people
   skip: decide in advance what makes you leave (a flow becomes customer-facing; a fourth model API
   deprecation lands; someone wants it exposed beyond the VPN).
2. **Fork and staff it.** The sunset announcement recommends this. Two things temper it: the auth
   layer you'd need for SSO — `IdentityManager.ts` and `enterprise/**` — is under the commercial
   licence, and a request to relicense went unanswered; and as of late August 2026 no serious
   community fork has emerged, only personal copies. It is a real option for a team that will
   genuinely staff dependency updates, security patches and model API churn indefinitely, and a
   comforting fiction otherwise.
3. **Treat the flows as specs and reimplement the two or three that matter** directly against the
   model APIs. This is what several teams did pre-sunset, specifically because there was never a
   code export. Your exported JSON is the specification.

Option 1 with current exports keeps option 3 open at all times, which is the main reason §4 isn't
optional. Nothing here requires you to decide today — but the exports do need to start today,
because they're what makes the decision reversible later.

---

**One thing I could not check.** Everything above is about Flowise's behaviour, not your instance. I
haven't seen your compose file, your version, or your flows. Before acting, confirm three things
against the real thing: `GET /api/v1/version` (which release you're actually on), `GET
/api/v1/settings` (open source vs enterprise), and the `openAIAssistant` grep in §5. If your running
version is below `3.1.0`, the `HTTP_SECURITY_CHECK` and Node 24 notes apply on the way up rather
than now.
