ABSOLUTE_ZERO_C = -273.15
KELVIN_OFFSET = 273.15


def c_to_f(c: float) -> float:
    """Градусы Цельсия -> градусы Фаренгейта."""
    return c * 9 / 5 + 32


def f_to_c(f: float) -> float:
    """Градусы Фаренгейта -> градусы Цельсия."""
    return (f - 32) * 5 / 9


def c_to_k(c: float) -> float:
    """Цельсий -> Кельвин. Ниже абсолютного нуля (−273.15 °C) — ValueError."""
    if c < ABSOLUTE_ZERO_C:
        raise ValueError("temperature below absolute zero")
    return c + KELVIN_OFFSET
