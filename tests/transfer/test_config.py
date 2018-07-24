import pytest

from sepaxml import SepaTransfer


def test_valid_config():
    return SepaTransfer({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR"
    })


def test_invalid_config():
    with pytest.raises(Exception):
        return SepaTransfer({
            "name": "TestCreditor",
            "BIC": "BANKNL2A",
            "batch": True,
            "currency": "EUR"
        })
