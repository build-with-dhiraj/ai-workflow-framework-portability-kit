---
name: python-pipelines
description: Build Python automation pipelines, scheduled jobs, async task orchestration, or ETL workflows. Triggers on "build a pipeline", "schedule this script", "task queue".
dispatch_to: data-engineer
---

# Python Pipelines — Prefect Orchestration

Prefect adds scheduling, retry logic, observability, and failure notifications to Python scripts without rewriting them. It wins over Celery (no broker needed) and cron (no visibility, no retries) for API-dependent pipelines.

## Decision Guide: Prefect vs Celery vs cron

| Need | Prefect | Celery | cron |
|---|---|---|---|
| Retry with backoff on API failures | Yes | Yes | No |
| UI to inspect run history | Yes | Flower (limited) | No |
| No message broker required | Yes | No (Redis/RabbitMQ) | Yes |
| Dependency between tasks | Yes | Limited | No |
| Slack alert on failure | Yes (automations) | Manual | Manual |
| Setup complexity | Low | High | Zero |

**Default to Prefect** when pipelines call LLM/external APIs and need failure visibility. Use cron only for fire-and-forget shell scripts with no retry requirement.

## Core Pattern: @flow + @task

```python
from prefect import flow, task
from prefect.logging import get_run_logger

@task(
    retries=3,
    retry_delay_seconds=60,
    log_prints=True,
)
def fetch_articles(source_url: str) -> list[dict]:
    logger = get_run_logger()
    logger.info(f"Fetching from {source_url}")
    # ... fetch logic
    return articles

@task(log_prints=True)
def process_with_llm(article: dict, api_key: str) -> str:
    # ... LLM call
    return summary

@flow(name="UPSC Daily Processing", log_prints=True)
def upsc_pipeline(source_url: str):
    articles = fetch_articles(source_url)
    summaries = process_with_llm.map(articles)  # concurrent map
    return summaries
```

Rules:
- `@task` wraps atomic units of work (one API call, one DB write)
- `@flow` orchestrates tasks — it is the entry point
- Tasks are retried independently; if one fails, others continue unless there is a dependency

## Scheduling

```python
# Option 1: serve() — simplest, runs in a local process
if __name__ == "__main__":
    upsc_pipeline.serve(
        name="upsc-daily",
        cron="0 6 * * *",          # 6 AM daily
        parameters={"source_url": "https://example.com/upsc"},
    )

# Option 2: interval schedule
from datetime import timedelta
upsc_pipeline.serve(
    name="upsc-hourly",
    interval=timedelta(hours=1),
)

# Option 3: RRule for complex schedules (every weekday)
from prefect.schedules import RRuleSchedule
import rrule
schedule = RRuleSchedule(rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR")
```

Run `prefect server start` locally and open `http://localhost:4200` to see all runs.

## Retry Logic + Exponential Backoff

```python
from prefect import task
from prefect.tasks import exponential_backoff

@task(
    retries=4,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    # delays: 2s, 4s, 8s, 16s
    retry_jitter_factor=0.5,   # add randomness to avoid thundering herd
)
def call_llm_api(prompt: str, api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
```

Rate-limited APIs (Anthropic, OpenAI) should use `retries=4` + exponential backoff as the default. Do not set retries on tasks that write to a DB without idempotency — duplicate writes are worse than failures.

## Logging and Observability

Prefect captures all `print()` and `logger` output in the UI per task run. Add structured context:

```python
from prefect import task
from prefect.logging import get_run_logger

@task
def process_article(article_id: str):
    logger = get_run_logger()
    logger.info("processing started", extra={"article_id": article_id})
    # ...
    logger.info("processing complete", extra={"article_id": article_id, "tokens": 412})
```

Slack failure notification via Prefect automations (requires Prefect Cloud) or via a hook:

```python
from prefect import flow
from prefect.blocks.notifications import SlackWebhook

@flow(name="ask-ai-daily")
def ask_ai_daily():
    try:
        run_pipeline()
    except Exception as e:
        # Fallback: call Slack MCP directly if not on Prefect Cloud
        # or use SlackWebhook block
        slack = SlackWebhook.load("slack-alerts")
        slack.notify(f"ask-ai-daily FAILED: {e}")
        raise
```

For Slack MCP integration (preferred — no secrets in code):
After flow failure, use `mcp__c6399901__slack_send_message` to post to your alerts channel. Wire this in a `flow.on_failure` hook.

## Async Concurrent Tasks

```python
import asyncio
from prefect import flow, task

@task
async def fetch_one(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

@flow
async def fetch_all(urls: list[str]):
    # Run all fetches concurrently
    results = await asyncio.gather(*[fetch_one(url) for url in urls])
    return results

# Or use Prefect's built-in .map() for parallel task submission:
@flow
def parallel_pipeline(article_ids: list[str]):
    # .map() submits all tasks concurrently, collects results
    summaries = process_article.map(article_ids)
    return summaries
```

Use `.map()` for CPU/IO-bound work over a list. Use `asyncio.gather()` inside a single async task for fine-grained concurrency within one step.

## Secret Management

Never put API keys in flow parameters or code. Use Prefect Blocks:

```python
from prefect.blocks.system import Secret

# Store once (CLI or UI):
# prefect block create secret --name anthropic-api-key --value sk-...

@task
def call_api():
    api_key = Secret.load("anthropic-api-key").get()
    # use api_key
```

For local dev, `.env` + `python-dotenv` is fine. In production, Prefect Blocks store secrets encrypted in the Prefect server DB.

## Deployment: Local vs Docker vs Prefect Cloud

| Mode | When | Command |
|---|---|---|
| `flow.serve()` | Dev + simple prod (single machine) | `python pipeline.py` |
| Docker worker | Multi-pipeline, isolated envs | `prefect worker start --pool docker-pool` |
| Prefect Cloud | Team visibility, managed infra | Sign up at app.prefect.cloud |

For `ask-ai-daily-automation` and UPSC pipelines: start with `flow.serve()` on the same machine running the scripts today. Migrate to Docker only when you need environment isolation between pipelines.

```bash
# Install
pip install prefect

# Start local UI
prefect server start

# In another terminal, run your pipeline (registers it as a deployment)
python upsc_pipeline.py
```

Open `http://localhost:4200` — all runs, logs, and retries are visible there.
