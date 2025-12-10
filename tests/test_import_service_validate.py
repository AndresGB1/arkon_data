import pandas as pd

from app.services.import_service import validate_row


def test_validate_row_ok_returns_none():
    row = pd.Series({
        "id": "abc",
        "programa": "CDMX WiFi",
        "alcaldia": "Coyoacan",
        "latitud": "19.3",
        "longitud": "-99.1",
    })

    assert validate_row(row) is None


def test_validate_row_out_of_range_latitude():
    row = pd.Series({
        "id": "abc",
        "programa": "CDMX WiFi",
        "alcaldia": "Coyoacan",
        "latitud": "123.0",
        "longitud": "-99.1",
    })

    assert validate_row(row) == "Latitud fuera de rango: 123.0"
