import os
from unittest.mock import patch

from watcherr.config import WatcherrConfig, configure


def test_default_config():
    config = WatcherrConfig()
    assert config.bot_token == ""
    assert config.enabled is True
    assert config.rate_limit_seconds == 60


def test_configure_explicit():
    config = configure(
        bot_token="123:ABC",
        chat_id="-100",
        service_name="test-svc",
        environment="test",
        rate_limit_seconds=30,
        enabled=True,
    )
    assert config.bot_token == "123:ABC"
    assert config.chat_id == "-100"
    assert config.service_name == "test-svc"


def test_configure_from_env():
    env = {
        "WATCHERR_BOT_TOKEN": "env-token",
        "WATCHERR_CHAT_ID": "-200",
        "WATCHERR_SERVICE_NAME": "env-svc",
        "WATCHERR_ENVIRONMENT": "staging",
        "WATCHERR_RATE_LIMIT": "120",
        "WATCHERR_ENABLED": "false",
    }
    with patch.dict(os.environ, env, clear=False):
        config = configure()

    assert config.bot_token == "env-token"
    assert config.chat_id == "-200"
    assert config.service_name == "env-svc"
    assert config.environment == "staging"
    assert config.rate_limit_seconds == 120
    assert config.enabled is False
