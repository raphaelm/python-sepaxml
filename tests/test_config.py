import pytest

from sepadd import SepaDD


def test_valid_config():
    return SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "000000",
        "currency": "EUR"
    })


def test_invalid_config():
    with pytest.raises(Exception):
        return SepaDD({
            "name": "TestCreditor",
            "BIC": "BANKNL2A",
            "batch": True,
            "creditor_id": "000000",
            "currency": "EUR"
        })
