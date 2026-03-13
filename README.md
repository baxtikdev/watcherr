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
pip install watcherr[celery]
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
```

### Logging handler

```python
import logging
from watcherr.logging_handler import WatcherrHandler

logging.getLogger("myapp").addHandler(WatcherrHandler())
```

### FastAPI middleware

```python
from watcherr.integrations.fastapi_middleware import WatcherrMiddleware

app.add_middleware(WatcherrMiddleware)
```

### Django middleware

```python
# settings.py
MIDDLEWARE = [
    "watcherr.integrations.django_middleware.WatcherrMiddleware",
    # ... other middleware
]
```

### Celery signals

```python
from watcherr.integrations.celery_signals import setup_celery_alerts

setup_celery_alerts()
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
