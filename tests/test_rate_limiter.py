import time

from watcherr.rate_limiter import RateLimiter


def test_first_message_allowed():
    limiter = RateLimiter(window_seconds=60)
    assert limiter.should_send("error: something") is True


def test_duplicate_blocked():
    limiter = RateLimiter(window_seconds=60)
    assert limiter.should_send("error: same") is True
    assert limiter.should_send("error: same") is False


def test_different_messages_allowed():
    limiter = RateLimiter(window_seconds=60)
    assert limiter.should_send("error A") is True
    assert limiter.should_send("error B") is True


def test_expired_message_allowed_again():
    limiter = RateLimiter(window_seconds=0)
    assert limiter.should_send("error: expire") is True
    time.sleep(0.01)
    assert limiter.should_send("error: expire") is True
