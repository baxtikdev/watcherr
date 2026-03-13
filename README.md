# watcherr

Lightweight error alerting via Telegram for Python apps.

## Install

```bash
pip install watcherr
```

Optional integrations:

```bash
pip install watcherr[fastapi]
pip install watcherr[django]
pip install watcherr[flask]
pip install watcherr[sanic]
pip install watcherr[litestar]
pip install watcherr[aiohttp]
pip install watcherr[celery]
pip install watcherr[dramatiq]
pip install watcherr[rq]
pip install watcherr[huey]
pip install watcherr[apscheduler]
pip install watcherr[playwright]
pip install watcherr[all]
```

## Setup

### 1. Get chat ID

```bash
WATCHERR_BOT_TOKEN=<your-token> watcherr
```

Send `/start` to the bot — it will reply with your `chat_id`.

### 2. Configure

Via code:

```python
import watcherr

watcherr.configure(
    bot_token="123456:ABC-DEF",
    chat_id="-1001234567890",
    service_name="my-api",
)
```

Or via `.env`:

```
WATCHERR_BOT_TOKEN=123456:ABC-DEF
WATCHERR_CHAT_ID=-1001234567890
WATCHERR_SERVICE_NAME=my-api
WATCHERR_ENVIRONMENT=production
```

## Usage

```python
import watcherr

watcherr.send_alert("Database connection failed", exc=exception)
watcherr.send_warning("Slow query", table="users", duration="5s")
watcherr.send_info("Deployed", version="1.2.0")
watcherr.send_photo("screenshot.png", caption="Login page broken", exc=exception)
```

### Logging handler

```python
import logging
from watcherr.logging_handler import WatcherrHandler

logging.getLogger("myapp").addHandler(WatcherrHandler())
```

## Web Framework Integrations

### FastAPI

```python
from watcherr.integrations.fastapi_middleware import WatcherrMiddleware

app.add_middleware(WatcherrMiddleware)
```

### Django

```python
# settings.py
MIDDLEWARE = [
    "watcherr.integrations.django_middleware.WatcherrMiddleware",
    # ... other middleware
]
```

### Flask

```python
from watcherr.integrations.flask import init_app

init_app(app)
```

### Sanic

```python
from watcherr.integrations.sanic_middleware import init_app

init_app(app)
```

### Litestar

```python
from litestar import Litestar
from watcherr.integrations.litestar_middleware import create_exception_handler

app = Litestar(
    exception_handlers={Exception: create_exception_handler()},
)
```

### aiohttp

```python
from aiohttp import web
from watcherr.integrations.aiohttp_middleware import watcherr_middleware

app = web.Application(middlewares=[watcherr_middleware()])
```

### Generic ASGI

```python
from watcherr.integrations.asgi import WatcherrASGIMiddleware

app = WatcherrASGIMiddleware(app)
```

### Generic WSGI

```python
from watcherr.integrations.wsgi import WatcherrWSGIMiddleware

app = WatcherrWSGIMiddleware(app)
```

## Task Queue Integrations

### Celery

```python
from watcherr.integrations.celery_signals import setup_celery_alerts

setup_celery_alerts()
```

### Dramatiq

```python
import dramatiq
from watcherr.integrations.dramatiq_middleware import WatcherrMiddleware

dramatiq.get_broker().add_middleware(WatcherrMiddleware())
```

### RQ (Redis Queue)

```python
from rq import Worker
from watcherr.integrations.rq_handler import watcherr_exception_handler

worker = Worker(queues, exception_handlers=[watcherr_exception_handler])
```

### Huey

```python
from huey import RedisHuey
from watcherr.integrations.huey_signals import setup_huey_alerts

huey = RedisHuey("my-app")
setup_huey_alerts(huey)
```

### APScheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler
from watcherr.integrations.apscheduler_listener import setup_apscheduler_alerts

scheduler = BackgroundScheduler()
setup_apscheduler_alerts(scheduler)
```

## Playwright Integration

### Context manager (sync)

```python
from watcherr.integrations.playwright import WatcherrPlaywright

with WatcherrPlaywright(page, name="login-test"):
    page.goto("https://example.com")
    page.click("#submit")
# On exception: screenshot + alert sent to Telegram
```

### Context manager (async)

```python
from watcherr.integrations.playwright import AsyncWatcherrPlaywright

async with AsyncWatcherrPlaywright(page, name="checkout-flow"):
    await page.goto("https://example.com/checkout")
    await page.click("#pay")
```

### Pytest plugin

```python
# conftest.py
pytest_plugins = ["watcherr.integrations.playwright_pytest"]

# Failed tests with a `page` fixture automatically send screenshot + alert
```

## Config options

| Env variable | Default | Description |
|---|---|---|
| `WATCHERR_BOT_TOKEN` | — | Telegram bot token |
| `WATCHERR_CHAT_ID` | — | Telegram chat/group ID |
| `WATCHERR_SERVICE_NAME` | `app` | Service name in alert title |
| `WATCHERR_ENVIRONMENT` | `production` | Environment label |
| `WATCHERR_RATE_LIMIT` | `60` | Dedup window in seconds |
| `WATCHERR_ENABLED` | `true` | Enable/disable sending |
