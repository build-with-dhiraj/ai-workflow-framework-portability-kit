---
name: github-actions
description: Set up GitHub Actions CI/CD workflows. Triggers on "add CI", "run tests on PR", "GitHub Actions", "branch protection", "scheduled workflow".
---

# GitHub Actions CI/CD

Dispatch to: `devops-automator` agent.

Reference: https://github.com/actions/starter-workflows

---

## 1. Workflow Anatomy

```yaml
name: CI
on: <trigger>        # when to run
jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4   # reusable action
      - run: npm test               # shell command
```

Key fields: `on`, `jobs.<id>.runs-on`, `steps[].uses`, `steps[].run`, `steps[].with`, `steps[].env`.

---

## 2. Key Triggers

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 9 * * 1'   # Mondays 9am UTC
  workflow_dispatch:        # manual "Run workflow" button
```

---

## 3. TypeScript / Node.js CI (primary stack)

`.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [20.x, 22.x]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm           # built-in cache — no extra step needed

      - run: npm ci
      - run: npm run typecheck --if-present
      - run: npm run lint --if-present
      - run: npm test --if-present
      - run: npm run build --if-present
```

`setup-node@v4` with `cache: npm` handles `node_modules` caching automatically. Saves ~60% of install time.

---

## 4. Python CI (automation stack)

`.github/workflows/python-ci.yml`

```yaml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install flake8 pytest

      - name: Lint
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Test
        run: pytest
```

`setup-python@v5` with `cache: pip` caches the pip download cache. Saves ~70% of install time.

---

## 5. Secrets

Add in: GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

Reference in steps:

```yaml
- name: Deploy
  env:
    API_KEY: ${{ secrets.MY_API_KEY }}
  run: ./deploy.sh
```

Or pass to an action:

```yaml
- uses: some-action@v1
  with:
    token: ${{ secrets.GITHUB_TOKEN }}   # built-in, always available
```

Never echo secrets. GitHub redacts them in logs but avoid `echo ${{ secrets.X }}`.

---

## 6. Manual Caching (when built-in cache isn't available)

```yaml
- name: Cache node_modules
  uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

Use this for monorepos or custom install paths. For standard npm/pip/yarn, prefer the built-in `cache:` param in `setup-node`/`setup-python`.

---

## 7. Branch Protection Rules

After CI is green: GitHub repo → Settings → Branches → Add rule → branch name: `main`.

Check:
- "Require a pull request before merging"
- "Require status checks to pass before merging" → search for and add your job name (e.g., `ci (20.x, ubuntu-latest)`)
- "Require branches to be up to date before merging"

Status check names match `jobs.<id>` in the workflow, suffixed with matrix values.

---

## 8. Reusable Workflows

Define once in `.github/workflows/shared-ci.yml`:

```yaml
on:
  workflow_call:
    inputs:
      node-version:
        required: false
        type: string
        default: '20.x'
    secrets:
      SLACK_WEBHOOK:
        required: false

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci && npm test
```

Call from another workflow:

```yaml
jobs:
  run-ci:
    uses: ./.github/workflows/shared-ci.yml
    with:
      node-version: '22.x'
    secrets:
      SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 9. Slack Failure Notifications

```yaml
      - name: Notify Slack on failure
        if: failure()
        uses: slackapi/slack-github-action@v2
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
          webhook-type: incoming-webhook
          payload: |
            {
              "text": "CI failed on `${{ github.repository }}` branch `${{ github.ref_name }}`",
              "attachments": [{
                "color": "danger",
                "text": "Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
              }]
            }
```

Add `SLACK_WEBHOOK_URL` as a repo secret (Incoming Webhook URL from Slack app settings).

---

## 10. Matrix Strategy

```yaml
strategy:
  fail-fast: false       # don't cancel other matrix jobs on first failure
  matrix:
    node-version: [18.x, 20.x, 22.x]
    os: [ubuntu-latest, windows-latest]
  exclude:
    - os: windows-latest
      node-version: 18.x
```

Each combination becomes a separate job. Status checks are named per combination.

---

## Checklist

- [ ] Workflow file in `.github/workflows/`
- [ ] `actions/checkout@v4` as first step
- [ ] Built-in cache via `setup-node`/`setup-python` `cache:` param
- [ ] Secrets added to repo settings, referenced via `${{ secrets.X }}`
- [ ] Branch protection rules require status checks to pass
- [ ] Slack notification step added with `if: failure()`
- [ ] Matrix covers supported versions (Node 20/22, Python 3.11/3.12)
