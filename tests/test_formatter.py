from watcherr.formatter import _escape_html, format_message


def test_format_error_message():
    result = format_message(
        level="error",
        message="Something broke",
        service_name="api",
        environment="prod",
    )
    assert "ERROR" in result
    assert "api" in result
    assert "prod" in result
    assert "Something broke" in result


def test_format_with_exception():
    try:
        raise ValueError("test error")
    except ValueError as e:
        result = format_message(
            level="error",
            message="Caught",
            service_name="worker",
            environment="staging",
            exc=e,
        )
    assert "ValueError" in result
    assert "test error" in result


def test_format_with_extra():
    result = format_message(
        level="warning",
        message="Slow query",
        service_name="db",
        environment="prod",
        extra={"table": "users", "duration": "5s"},
    )
    assert "table" in result
    assert "users" in result


def test_escape_html():
    assert _escape_html("<script>") == "&lt;script&gt;"
    assert _escape_html("a & b") == "a &amp; b"
