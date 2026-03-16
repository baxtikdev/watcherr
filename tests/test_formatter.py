from watcherr.formatter import _detect_language, _escape_html, format_message


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
    assert 'class="language-python"' in result


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


def test_detect_language_python():
    assert _detect_language("Traceback (most recent call last):") == "python"
    assert _detect_language('File "app.py", line 10, in main') == "python"


def test_detect_language_java():
    text = 'Exception in thread "main"\n\tat com.example.Main.run(Main.java:42)'
    assert _detect_language(text) == "java"


def test_detect_language_javascript():
    text = "TypeError: undefined\n    at Object.<anonymous> (/app/index.js:5:1)"
    assert _detect_language(text) == "javascript"


def test_detect_language_go():
    text = "goroutine 1 [running]:\npanic: runtime error"
    assert _detect_language(text) == "go"


def test_detect_language_json():
    assert _detect_language('{"error": "not found"}') == "json"
    assert _detect_language('[{"code": 400}]') == "json"


def test_detect_language_default():
    assert _detect_language("some unknown error text") == "python"
