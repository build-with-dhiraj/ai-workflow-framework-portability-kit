# Hardening self-hosted Flowise for a team

## Short version

Five changes, in this order. Everything else can wait.

1. **Move off SQLite to Postgres.** This is the lock-up. SQLite allows one writer at a time across the whole file, and Flowise writes on every chat message, not just every save.
2. **Find out why you lost flows — today, before anything else.** In almost every case it's a missing or misdirected volume mount, which means you are still one `docker compose up` away from losing them again. Then add real backups; Postgres by itself is not a backup.
3. **Pin the image tag and back up the encryption key.** `:latest` means an unplanned pull runs untested schema migrations. Losing `encryption.key` means every stored credential in every flow becomes undecryptable while the flows themselves look fine.
4. **Decide your SSO story deliberately.** Real per-user identity, workspaces and RBAC in Flowise are Enterprise-licensed. The open-source route is an identity-aware proxy in front, which gates the UI but leaves Flowise with one shared identity. Pick knowingly, and carve out the prediction API or you'll break your integrations.
5. **Lock down the code-execution nodes before you widen access.** Anyone who can open the Flowise UI can run arbitrary server-side JS inside the container via Custom Tool / Custom Function nodes. That's tolerable for one person; it's a real risk once SSO puts it in front of a directory.

Explicitly *not* yet: queue mode, Redis, S3 storage, multiple replicas, Kubernetes. Triggers for each are at the end.

---

## Before you read further: two constraints from your own codebase

I found a live Flowise integration in `~/dev/jove-code/jove-ai-agent`. If the instance you're describing is the same one (or will become it), two of the recommendations above have hard constraints attached.

**Flow IDs are hardcoded downstream.** `~/dev/jove-code/jove-ai-agent/app-manifest.yaml` pins specific chatflow UUIDs:

```yaml
FLOWISE_AI_MODE_FLOW_ID: "f9304162-f9a1-4610-9831-7303bb27ee5c"
FLOWISE_AI_COPILOT_FLOW_ID: "6070befe-7be4-4dce-b71d-ce34d9a20ff2"
FLOWISE_SUPER_AGENT_FLOW_ID: "7feab331-7d14-4a01-acac-4b585fb61406"
FLOWISE_PLAYLIST_AGENT_FLOW_ID: "fe20a92c-9245-484b-88a9-155cbb1889cc"
```

Migrating by export/import can assign **new** UUIDs on import. If it does, every one of those breaks silently. Verify ID preservation on a throwaway instance first, and if IDs change, plan to update the manifest and the Vault-backed config in the same change window. This is the single most likely way the migration bites you.

**The prediction API is called machine-to-machine, including SSE.** `~/dev/jove-code/jove-ai-agent/src/jove_ai_agent_service/clients/flowise.py`:

```python
self.prediction_url = f"{self.url}/api/v1/prediction/{self.agent_flow_id}"
...
"Authorization": f"Bearer {self.api_key}",
"Accept": "text/event-stream",
```

Three consequences for the SSO work:
- `/api/v1/prediction/*` must be **excluded** from any interactive SSO redirect. An OIDC proxy that 302s an unauthenticated request to a login page turns this client's POST into a broken HTML response, not an error it can interpret.
- That excluded path must then be protected by the Flowise API key it already sends, so the exclusion isn't a hole.
- The proxy must **not buffer** responses on that path, or streaming dies. On nginx that means `proxy_buffering off;` plus `proxy_read_timeout` above your `FLOWISE_TIMEOUT_SECONDS` of 180.

Also: this client sends `overrideConfig: {"sessionId": ...}`. If you tighten override config on those chatflows (a reasonable hardening step), leave `sessionId` permitted or you break session continuity.

---

## 1. SQLite is why it locks up

### Why

SQLite serialises writes with a lock over the entire database file. In default rollback-journal mode, a writer also blocks readers. Flowise doesn't just write when you click Save — it writes a row per chat message, per upsert, and (on recent versions) per execution step of an agentflow. Three people using it at once means near-continuous writes against a single-writer database, and the symptom is exactly what you describe: the UI hangs, and logs show `SQLITE_BUSY: database is locked`.

It gets worse if the database file sits on a bind mount rather than a Docker named volume, and worse again on Docker Desktop's filesystem shim or anything network-backed, where SQLite's locking is unreliable rather than merely slow.

There's no tuning that fixes this. It's the storage engine's design.

### The stopgap you can do in five minutes

If you can't migrate this week, switch the existing file to WAL mode. Writers stop blocking readers, which removes most of the perceived freezing:

```bash
docker compose stop flowise
docker compose run --rm --entrypoint sh flowise -c \
  'apk add --no-cache sqlite >/dev/null 2>&1; sqlite3 /root/.flowise/database.sqlite "PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;"'
docker compose start flowise
```

The setting persists in the file. Ceiling: still one writer at a time, so it buys headroom, not a fix — and WAL needs working shared memory on the filesystem, so it will fail on an NFS/SMB mount. Treat it as a bridge to Postgres, not a destination.

While you're in there, check whether the file is already damaged, because that changes the migration plan:

```bash
sqlite3 /path/on/host/database.sqlite "PRAGMA integrity_check;"
```

Anything other than `ok` means your export may be incomplete, and you need to know that before you decommission anything.

### Migrating to Postgres

Flowise ships no SQLite-to-Postgres data migration. Two options:

**Export/import (recommended for your size).** Stand up an empty Postgres, let Flowise create its own schema via its TypeORM migrations on first boot, then import. In the UI: Settings → Export, which covers chatflows, agentflows, tools, variables, assistants, document store and chat messages depending on version. Import into the new instance.

**`pgloader` on the raw file.** Only worth it at hundreds of flows. Flowise's TypeORM schema differs per database driver — UUID handling, JSON vs text columns, booleans stored as integers, timestamp types — so you'll spend the afternoon fixing type casts and you still have to run migrations afterward. Don't, unless export/import demonstrably loses something you need.

Assume credentials do **not** survive cleanly. Credential values are encrypted at rest with a key that lives outside the database, so plan to re-enter them by hand and treat it as a pleasant surprise if you don't have to. Budget for it in the change window; it's usually 20 minutes of pasting API keys.

Runbook, in order:

1. `PRAGMA integrity_check` on the current file. Stop if it isn't `ok`.
2. Copy the whole `.flowise` directory off the host to somewhere safe. This includes `encryption.key`.
3. Export everything from the UI. Save the JSON in a repo or a shared drive, not on the host.
4. Bring up Postgres and a **second, throwaway** Flowise container pointed at it, on a different port.
5. Import. Then check: do the chatflow IDs match the UUIDs in `app-manifest.yaml`? Do credentials decrypt, or do they need re-entry?
6. Re-enter credentials as needed. Run each flow once from the UI. Then hit `/api/v1/prediction/{flow_id}` with curl and the API key, both streaming and not, to prove the machine path works.
7. Cut over. Leave the old container **stopped, not deleted**, and the old volume intact, for at least two weeks.
8. Only then remove the SQLite volume.

---

## 2. Why you lost flows, and how to know

Don't guess at this. Run the checks — the answer determines whether you're currently safe.

```bash
# Is the data directory actually a volume, or the container's own filesystem?
docker inspect <flowise-container> --format '{{json .Mounts}}' | python3 -m json.tool

# Where does Flowise think its data lives?
docker compose config | grep -Ei 'DATABASE_PATH|SECRETKEY_PATH|APIKEY_PATH|LOG_PATH|BLOB_STORAGE'

# Did it die uncleanly? Exit 137 = SIGKILL, i.e. killed mid-write.
docker inspect <flowise-container> --format '{{.State.ExitCode}} {{.State.OOMKilled}}'
```

The four causes, in descending order of likelihood:

**No volume at all.** The most common by far. Everything lived in the container's writable layer. `docker restart` preserves that layer, but `docker compose up -d` after an image change, `docker compose pull`, `--force-recreate`, or `docker rm` all destroy it. If the mount list doesn't show your data path, this is your answer, and everything currently in there is one command away from gone. Fix it before you do anything else.

**Volume mounted, `DATABASE_PATH` pointing elsewhere.** The classic near-miss: you mount `/root/.flowise` but set `DATABASE_PATH=/opt/flowise/db`. The volume is real, empty, and useless.

**Unclean kill mid-write.** Compose sends SIGTERM and waits 10 seconds by default, then SIGKILL. Killed during a write, SQLite rolls back to the last committed state — so the flows saved just before the restart vanish while older ones survive. That partial-loss pattern matches "we lost *some* flows" well. Raise `stop_grace_period`.

**Lost encryption key.** This one masquerades as data loss. The flows are all there, but every credential inside them is undecryptable, so every flow errors on run. If `SECRETKEY_PATH` wasn't on a persistent volume, or you set `FLOWISE_SECRETKEY_OVERWRITE` inconsistently between restarts, this is what you get. Worth ruling out explicitly, because the fix is completely different.

### Backups

Postgres stops the corruption class of loss. It does nothing about someone deleting the wrong flow. You need both parts — the database *and* the key — or a restore doesn't produce a working system.

```bash
#!/bin/sh
# /usr/local/bin/flowise-backup.sh — cron nightly
set -eu
DEST=/backups/flowise/$(date +%F)
mkdir -p "$DEST"
cd /opt/flowise

# Database
docker compose exec -T postgres pg_dump -U flowise -Fc flowise > "$DEST/flowise.dump"

# Encryption key + local blob storage. Without the key the dump is half a backup.
docker run --rm -v flowise_data:/d:ro -v "$DEST":/out alpine \
  tar czf /out/flowise_data.tgz -C /d .

find /backups/flowise -maxdepth 1 -type d -mtime +30 -exec rm -rf {} +
```

Two rules that matter more than the script: **restore it once, to a scratch instance, and confirm a flow runs** — an untested backup is a belief, not a backup. And store the key material somewhere separate from the dumps, ideally Vault, which you're already using for `JOVE_FLOWISE_API_KEY`.

Ban `docker compose down -v` from your runbooks and shell history. The `-v` deletes named volumes.

---

## 3. Pin the image, own the key

```
image: flowiseai/flowise:latest    # ← how a Tuesday becomes an incident
```

Flowise runs schema migrations on boot. With `:latest`, any pull silently upgrades you across versions and migrates your database, with no staging step and no rollback — old image against new schema generally doesn't start. Pin an exact version. Upgrade deliberately: back up, bump the tag, boot a scratch instance against a restored copy, then promote.

For the encryption key, pick one approach and be explicit about it:

- Keep `encryption.key` at `SECRETKEY_PATH` on the persistent volume, and back it up (the script above does).
- Or inject it with `FLOWISE_SECRETKEY_OVERWRITE` from Vault, which is the better fit for your stack — the key stops living on a host you might rebuild.

Do not do both inconsistently, and never let it be generated fresh into an ephemeral path. There's no recovery from a lost key beyond re-entering every credential in every flow.

---

## 4. SSO: know which thing you're buying

Be clear about the fork in the road, because the two paths give very different things.

**Flowise Enterprise (licensed).** Native SAML/OIDC SSO, organisations, workspaces, RBAC, per-user identity. This is the only path where Flowise itself knows *who* did something — needed for per-user flow ownership, an audit trail, and keeping three people out of each other's work. Requires a `LICENSE_KEY`.

**Identity-aware proxy (open source).** oauth2-proxy, Authelia, Cloudflare Access, or nginx with an OIDC module in front. Your SSO controls who reaches the app. Inside, Flowise still sees a single shared identity — no per-user attribution, no per-user permissions, no audit of who edited what.

The proxy route is the right lazy default *if* you accept the shared-identity ceiling. Say the ceiling out loud when you propose it, so nobody assumes they bought an audit trail they didn't.

Non-negotiables either way:

- **Exclude `/api/v1/prediction/*` from the interactive redirect**, protected by the Flowise API key. Otherwise `jove-ai-agent` gets a login page where it expects JSON or SSE. Audit the rest of the API surface you actually use (`/api/v1/vector/upsert/*` if you do document ingestion) and treat it the same way.
- **No response buffering on those paths**, or streaming breaks. Read timeout above 180s to match `FLOWISE_TIMEOUT_SECONDS`.
- **Set the JWT and session secrets explicitly** rather than letting them default or regenerate — otherwise everyone gets logged out on each restart. Check the names your version uses (roughly `JWT_AUTH_TOKEN_SECRET`, `JWT_REFRESH_TOKEN_SECRET`, `EXPRESS_SESSION_SECRET`, `TOKEN_HASH_SECRET`).
- **Don't publish port 3000 to the world.** Bind it to loopback or an internal network so the proxy is the only way in. An open 3000 makes the whole SSO exercise decorative.
- **Set `CORS_ORIGINS`** to your actual origin, and `IFRAME_ORIGINS` if you embed the chat widget anywhere.

One workflow note while you're here: Flowise has no locking on flow edits. Two people editing the same chatflow is last-write-wins, silently. With three of you, either split ownership by flow or accept occasional clobbering — the real fix is Enterprise workspaces.

---

## 5. Lock down code execution before you widen access

Custom Tool and Custom Function nodes execute JavaScript server-side, inside the container, with the container's network position and credentials. Read/write-file nodes touch the container filesystem. For one trusted person that's a feature. Once SSO fronts it and "three of us" becomes "anyone in the directory who asks", it's a lateral-movement path into your cluster.

Cheap, high-value, do it in the same change:

- Restrict what custom functions can import. `TOOL_FUNCTION_BUILTIN_DEP` and `TOOL_FUNCTION_EXTERNAL_DEP` are allowlists — keep them minimal rather than permissive.
- Run the container as a non-root user. Never mount the Docker socket into it.
- Restrict egress. This container should reach your model providers and its own Postgres, not your internal admin APIs. In your k8s setup that's a NetworkPolicy.
- Don't attach a cloud instance role or Vault scope broader than the flows need. Anything the container can reach, a Custom Function can reach.
- If your version supports `DISABLED_NODES`, disable the node types you don't use.
- Set `DISABLE_FLOWISE_TELEMETRY=true` for an internal tool.

---

## Reference compose

Verify the env var names against your version before applying — see the caveat below.

```yaml
services:
  flowise:
    image: flowiseai/flowise:3.0.6        # pin exactly; never :latest
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      PORT: 3000
      DATABASE_TYPE: postgres
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_NAME: flowise
      DATABASE_USER: flowise
      DATABASE_PASSWORD: ${POSTGRES_PASSWORD}
      DATABASE_SSL: "false"               # true (+ cert) if Postgres is remote

      # Encryption key: file on the volume, OR inject from Vault. Not both.
      SECRETKEY_PATH: /root/.flowise
      # FLOWISE_SECRETKEY_OVERWRITE: ${FLOWISE_ENCRYPTION_KEY}

      APIKEY_STORAGE_TYPE: db             # keeps API keys in Postgres, not a JSON file
      BLOB_STORAGE_PATH: /root/.flowise/storage
      LOG_PATH: /root/.flowise/logs
      LOG_LEVEL: info

      CORS_ORIGINS: https://flowise.internal.example.com
      DISABLE_FLOWISE_TELEMETRY: "true"
      TOOL_FUNCTION_BUILTIN_DEP: crypto   # allowlist; keep it tiny
      TOOL_FUNCTION_EXTERNAL_DEP: ""

      JWT_AUTH_TOKEN_SECRET: ${JWT_AUTH_TOKEN_SECRET}
      JWT_REFRESH_TOKEN_SECRET: ${JWT_REFRESH_TOKEN_SECRET}
      EXPRESS_SESSION_SECRET: ${EXPRESS_SESSION_SECRET}
    volumes:
      - flowise_data:/root/.flowise       # key + blobs + logs
    ports:
      - "127.0.0.1:3000:3000"             # proxy only; not world-facing
    stop_grace_period: 60s

  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: flowise
      POSTGRES_USER: flowise
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U flowise -d flowise"]
      interval: 10s
      timeout: 5s
      retries: 10
    stop_grace_period: 60s

volumes:
  flowise_data:
  pg_data:
```

A single Postgres container with its own volume is genuinely fine for three users. Use managed Postgres instead only if you already run it — then you inherit its backups and PITR, which is a real gain over the cron script.

---

## What you don't need yet

Each of these is correct at some scale and premature at yours. The trigger is what matters:

| Thing | Add it when |
|---|---|
| Queue mode + Redis (`MODE=queue`, worker process) | After Postgres, requests still stall behind each other — meaning long agentflow runs are blocking the event loop, not the database. Also required before you run more than one replica. |
| S3 / GCS storage (`STORAGE_TYPE`) | You move to more than one replica. Local blob storage isn't shared, so uploads land on whichever pod answered and vanish from the others. |
| Multiple replicas | Real concurrent load, and only after queue mode plus shared storage. Two replicas over local storage is a bug, not redundancy. |
| Separate staging instance | Before your first version upgrade. A restored backup on a scratch container covers it initially. |
| Kubernetes / autoscaling | You already have the cluster, so if this instance moves there, inherit the platform's secrets, network policy and backups rather than standing up a parallel story. Don't migrate for scale reasons at three users. |

Diagnostic order matters: fix the database first, then measure. If lock-ups survive Postgres, that's real evidence for queue mode. Adding Redis and a worker now would just mean two things changed at once and you learn nothing from either.

---

## Verify against your version

Flowise's environment variables have shifted meaningfully across 1.x → 2.x → 3.x, and the auth model changed outright. Check your actual version before applying any of the above:

```bash
docker compose exec flowise flowise --version
docker compose images flowise
```

Then confirm these specific ones against the env-var reference in the docs for *your* version, or `packages/server/.env.example` in the repo at that tag:

- `APIKEY_STORAGE_TYPE` — newer versions only.
- `DISABLED_NODES` — availability varies.
- The JWT/session secret names — these arrived with the 2.x auth rework, and 1.x instead used a single shared `FLOWISE_USERNAME`/`FLOWISE_PASSWORD`.
- Whether SSO and workspaces are available on your license tier. If you're on 1.x, native SSO does not exist at all and the proxy route is your only option.
- Whether export/import preserves chatflow UUIDs — the one thing you must test empirically rather than read about, because your `jove-ai-agent` manifest depends on it.
