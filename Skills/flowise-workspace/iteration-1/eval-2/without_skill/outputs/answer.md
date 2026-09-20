# Hardening self-hosted Flowise for a small team

Short version: you have three separate problems that feel like one, and they need fixing in a specific order. Plus a fourth one you haven't hit yet that will hurt more than the other three combined.

1. **The lost flows are not SQLite's fault.** That's almost certainly a missing volume mount. One-line fix, do it today.
2. **The lock-ups are SQLite's fault.** Move to Postgres. Half a day.
3. **The encryption key is your real single point of failure.** If you migrate the database without carrying the key across, every stored credential becomes unrecoverable garbage. This is the one that bites people during exactly the migration you're about to do.
4. **SSO in Flowise is a paid Enterprise feature.** The free path is an auth proxy in front, which works but does *not* give you per-user identity inside Flowise. Know which one you're buying before you promise anything to whoever asked for SSO.

Details below, in the order I'd do them.

---

## 1. Fix the data loss first — it's a volume, not a database problem

A container restart doesn't wipe SQLite. Recreating a container wipes anything not on a volume. If `docker compose up --force-recreate`, an image pull, or a `docker rm` was involved last week, that's your culprit — the database file was living in the container's writable layer and went away with it.

Check where the data actually is:

```bash
docker exec <container> sh -c 'ls -la /root/.flowise'
docker inspect <container> --format '{{json .Mounts}}' | python3 -m json.tool
```

If nothing is mounted at `/root/.flowise`, that's the bug. The official image keeps everything there — the SQLite file, the encryption key, uploaded files, and logs. Mount it:

```yaml
volumes:
  - ./flowise-data:/root/.flowise
```

I'd use a bind mount rather than a named volume, purely because backups become `tar` instead of a Docker volume dance.

Then verify it properly, because "it seems fine" is what you had last week:

```bash
docker compose down && docker compose up -d   # flows must still be there
```

**Also check your vector stores.** If any flow uses an in-memory vector store, or a local file-based one (Chroma/FAISS on disk), that data has the same lifecycle problem and the same fix. In-memory ones simply don't survive a restart at all, by design — if a flow depends on documents staying upserted, it needs a real vector store.

## 2. The lock-ups are SQLite — move to Postgres

This one is genuinely SQLite and there's no tuning that fixes it. SQLite allows exactly one writer at a time across the whole database. Flowise writes constantly: saving a flow, every chat message, execution traces, upsert history, leads. Three people working simultaneously means writers queueing behind a database-level lock, which surfaces as the UI hanging or `SQLITE_BUSY`. WAL mode raises the ceiling slightly, but it doesn't give you concurrent writers, and Flowise doesn't expose those pragmas anyway. Three concurrent users is past where SQLite is the right answer.

Postgres is a first-class supported backend — `DATABASE_TYPE=postgres` plus host/port/name/user/password. Config is in the compose file below.

**There is no supported SQLite→Postgres migration.** Don't try to copy rows across; the TypeORM column types don't line up cleanly and you'll produce a subtly broken database. Do it by export/import instead:

1. Back up the whole `.flowise` directory to somewhere off the host. Before anything else.
2. Grab the existing encryption key (see next section) — this is the step people skip.
3. Stand up Postgres and a **second** Flowise container on a different port, pointed at it. Leave the old one running.
4. Export your flows from the old instance (Settings → Export, or export each chatflow/agentflow as JSON) and import into the new one.
5. Verify every flow actually runs on the new instance — not just that it renders in the editor.
6. Cut over. Keep the old container **stopped, not deleted**, for a week or two.

Chat history won't come across with the flow JSON. That's fine — it's the biggest table and the least valuable. Only go hunting for it if someone specifically needs those transcripts.

## 3. Pin down the encryption key before you migrate anything

Flowise encrypts every stored credential — your OpenAI keys, database passwords, whatever else your flows hold — with a key at `/root/.flowise/encryption.key`, auto-generated on first boot. A fresh instance generates a *different* key. Import your credentials onto an instance with a different key and they decrypt to nothing.

This is why a Postgres backup on its own is not a complete backup. The database holds the ciphertext; the key lives in a file.

Read the existing key out of the old container and carry it forward explicitly:

```bash
docker exec <container> cat /root/.flowise/encryption.key
```

Set that exact value as `FLOWISE_SECRETKEY_OVERWRITE` on the new instance. Existing credentials keep working. Store the value in whatever secret store you already use — 1Password, Vault, SOPS, your CI secrets — not just in a file on one host.

Once you're on Enterprise or a newer build, the same logic applies to `TOKEN_HASH_SECRET`, `EXPRESS_SESSION_SECRET`, `JWT_AUTH_TOKEN_SECRET`, and `JWT_REFRESH_TOKEN_SECRET`. Generate each with `openssl rand -hex 32`, set them explicitly, and keep them stable — if they're unset and regenerate on restart, everyone gets logged out on every deploy.

## 4. Backups you have actually restored

You've already learned the expensive version of this lesson, so keep it small and real:

- `pg_dump` nightly to somewhere off the host.
- The encryption key, stored separately from the dump.
- The `.flowise` directory (uploaded files, blob storage).

Then restore one, once, into a scratch container and confirm a flow runs. An untested backup isn't a backup. Fifteen minutes now, and it's the only thing on this list that pays for itself twice.

## 5. SSO — be precise about what you're getting

Here's the licensing reality, because it changes the plan:

Flowise is open-core. The Community Edition is Apache 2.0 and fully self-hostable, but **SSO, RBAC, workspaces, organizations, and audit logs live in a separately licensed enterprise directory**. The docs are explicit: SSO is Enterprise-only, and so are workspaces. Enterprise SSO covers Microsoft Entra ID, Google, and Auth0 over OIDC, is configured in the UI by an Organization Admin, and requires users be invited into Flowise before they can sign in. Self-hosted Enterprise needs `LICENSE_URL` and `FLOWISE_EE_LICENSE_KEY`, which you get from their sales/support.

So you have two paths.

**Path A — buy Enterprise.** You get real per-user identity inside Flowise, RBAC, workspaces, and an audit trail. Worth it specifically if you need to answer "who changed this flow" or "who can see these credentials." With three people sharing credentials that hold live API keys, you will eventually need both.

**Path B — auth proxy in front.** oauth2-proxy, Authelia, Pomerium, Cloudflare Access, or your existing ingress if it speaks OIDC. Free, roughly an hour of work, and it genuinely does gate the UI behind your IdP. Three caveats, and the second one is the one people get wrong:

- **Everyone inside is still the same Flowise user.** No attribution, no per-flow permissions. Anyone who can get through the proxy can read and use every stored credential. The proxy is a front door, not a permission system.
- **The prediction API must bypass the proxy** or every embedded chatbot, webhook, and integration you have breaks the moment SSO goes live. `/api/v1/prediction/*` and the public chatbot endpoints need to be excluded and protected by Flowise API keys instead. Get this wrong in one direction and your integrations die; get it wrong in the other and you've left the API open while everyone believes the app is behind SSO.
- **Set `NUMBER_OF_PROXIES=1`** so Flowise's rate limiting sees the real client IP instead of the proxy's, and **bind the container port to `127.0.0.1`** so nobody can reach it around the proxy.

My recommendation: **do Path B now** — it unblocks the SSO deadline and it's reversible. Treat Enterprise as a decision you make once you know whether you need attribution, which you'll know within a month of three people sharing one login. Either way, say out loud to whoever asked for SSO that Path B does not scope access to credentials. Don't let "it's behind SSO now" become an assumption the organisation builds on.

## 6. The compose file

```yaml
services:
  flowise:
    image: flowiseai/flowise:<pin-your-current-version>   # never :latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"        # proxy is the only way in
    environment:
      DATABASE_TYPE: postgres
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_NAME: flowise
      DATABASE_USER: flowise
      DATABASE_PASSWORD: ${DB_PASSWORD}
      FLOWISE_SECRETKEY_OVERWRITE: ${FLOWISE_SECRET_KEY}  # the OLD key, from your secret store
      SECRETKEY_PATH: /root/.flowise
      BLOB_STORAGE_PATH: /root/.flowise/storage
      LOG_PATH: /root/.flowise/logs
      LOG_LEVEL: info
      NUMBER_OF_PROXIES: 1
      DISABLE_FLOWISE_TELEMETRY: true
    volumes:
      - ./flowise-data:/root/.flowise
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: flowise
      POSTGRES_USER: flowise
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U flowise"]
      interval: 10s
      retries: 5

volumes:
  pgdata:
```

Two things worth noticing in there.

**Pin the image tag.** `latest` plus a schema migration plus no backup is precisely how last week happened. Flowise moves fast and has shipped breaking migrations. Upgrades become: back up, bump the tag, verify, and you have a tag to roll back to.

**Add `CORS_ORIGINS` and `IFRAME_ORIGINS`** if you're embedding chatbots anywhere — they default permissively.

## 7. Order of operations

They interact, so sequence matters:

1. Back up `.flowise` off the host. **Before touching anything.**
2. Add the volume mount. Restart. Confirm data survives `down && up`.
3. Extract the encryption key, put it in your secret store, set `FLOWISE_SECRETKEY_OVERWRITE`.
4. Stand up Postgres plus a second Flowise on another port. Export, import, verify flows *run*.
5. Cut over. Keep the old container stopped, not deleted.
6. Put the auth proxy in front, with the `/api/v1/prediction/*` carve-out.
7. Nightly `pg_dump` plus the key. Restore it once to prove it works.

Steps 1 and 2 are today and stop the bleeding. The rest is a comfortable afternoon.

## 8. What not to build

You're three people. Skip these until something actually measures as the bottleneck:

- **Queue mode** (`MODE=queue` + Redis + worker containers). That's for prediction throughput, not for three people editing flows. Your bottleneck is a write lock, and Postgres fixes it.
- **Postgres HA, replicas, connection pooling.** One Postgres container with a volume and a nightly dump is correct at this size.
- **Kubernetes.** Compose on one host is the right shape here.
- **Migrating chat history.** Biggest table, least value.
- **S3/GCS blob storage.** `STORAGE_TYPE=s3` exists and is a fine future move, but a mounted directory with a backup is fine now.

Add any of them when you have a specific number showing you need it.

---

### Sources

- [SSO | FlowiseAI](https://docs.flowiseai.com/configuration/sso)
- [Workspaces | FlowiseAI](https://docs.flowiseai.com/using-flowise/workspaces)
- [Environment Variables | FlowiseAI](https://docs.flowiseai.com/configuration/environment-variables)
- [Flowise docker/.env.example](https://github.com/FlowiseAI/Flowise/blob/main/docker/.env.example)
- [Get Started | FlowiseAI](https://docs.flowiseai.com/getting-started)

One caveat worth stating: env var names and edition gating have moved between Flowise 1.x, 2.x, and 3.x. Check your running version against your image tag and diff against your version's `docker/.env.example` before applying the config above verbatim.
