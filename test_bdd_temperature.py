import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from main import c_to_f, c_to_k, f_to_c

scenarios("../features/temperature.feature")


@pytest.fixture
def context():
    """Общее состояние сценария: входное значение, результат или ошибка."""
    return {}


# ---------- Given ----------

@given(parsers.parse("the temperature is {value} degrees Celsius"))
def given_celsius(context, value):
    context["value"] = float(value)


@given(parsers.parse("the temperature is {value} degrees Fahrenheit"))
def given_fahrenheit(context, value):
    context["value"] = float(value)


# ---------- When ----------

@when("I convert it to Fahrenheit")
def when_to_fahrenheit(context):
    context["result"] = c_to_f(context["value"])


@when("I convert it to Celsius")
def when_to_celsius(context):
    context["result"] = f_to_c(context["value"])


@when("I convert it to Kelvin")
def when_to_kelvin(context):
    context["result"] = c_to_k(context["value"])


@when("I try to convert it to Kelvin")
def when_try_to_kelvin(context):
    try:
        context["result"] = c_to_k(context["value"])
    except ValueError as exc:
        context["error"] = exc


# ---------- Then ----------

@then(parsers.parse("the result is {expected}"))
def then_result_is(context, expected):
    assert context["result"] == pytest.approx(float(expected), abs=1e-9)


@then(parsers.parse('the conversion fails with error "{message}"'))
def then_conversion_fails(context, message):
    assert "result" not in context
    assert isinstance(context.get("error"), ValueError)
    assert str(context["error"]) == message
