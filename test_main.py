import pytest

from main import ABSOLUTE_ZERO_C, c_to_f, c_to_k, f_to_c


# ---------- c_to_f ----------

@pytest.mark.parametrize(
    "celsius, fahrenheit",
    [
        (0, 32),        # замерзание воды
        (100, 212),     # кипение воды
        (-40, -40),     # точка, где шкалы совпадают
        (37, 98.6),     # температура тела
        (-273.15, -459.67),  # абсолютный ноль
    ],
)
def test_c_to_f_known_points(celsius, fahrenheit):
    assert c_to_f(celsius) == pytest.approx(fahrenheit)


def test_c_to_f_accepts_fractional_values():
    assert c_to_f(36.6) == pytest.approx(97.88)


# ---------- f_to_c ----------

@pytest.mark.parametrize(
    "fahrenheit, celsius",
    [
        (32, 0),
        (212, 100),
        (-40, -40),
        (98.6, 37),
        (-459.67, -273.15),
    ],
)
def test_f_to_c_known_points(fahrenheit, celsius):
    assert f_to_c(fahrenheit) == pytest.approx(celsius)


@pytest.mark.parametrize("celsius", [-100, -40, 0, 36.6, 100, 1000])
def test_c_to_f_and_f_to_c_are_inverse(celsius):
    assert f_to_c(c_to_f(celsius)) == pytest.approx(celsius)


# ---------- c_to_k ----------

@pytest.mark.parametrize(
    "celsius, kelvin",
    [
        (0, 273.15),
        (100, 373.15),
        (-100, 173.15),
        (25, 298.15),
    ],
)
def test_c_to_k_known_points(celsius, kelvin):
    assert c_to_k(celsius) == pytest.approx(kelvin)


def test_c_to_k_absolute_zero_is_allowed_and_equals_zero_kelvin():
    assert c_to_k(ABSOLUTE_ZERO_C) == pytest.approx(0.0)


@pytest.mark.parametrize("celsius", [-273.16, -274, -300, -1000])
def test_c_to_k_below_absolute_zero_raises(celsius):
    with pytest.raises(ValueError, match="below absolute zero"):
        c_to_k(celsius)
