import pandas as pd

from app.utils.file_reader import parse_decimal


def test_parse_decimal_accepts_comma_decimal():
    assert parse_decimal("19,4321") == 19.4321


def test_parse_decimal_returns_none_for_invalid():
    assert parse_decimal("nope") is None
    assert parse_decimal(None) is None
