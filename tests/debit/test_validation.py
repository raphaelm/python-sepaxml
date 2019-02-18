import datetime

import pytest

from sepaxml import SepaDD
from sepaxml.validation import ValidationError


def test_name_too_long():
    sdd = SepaDD({
        "name": "TestCreditor",
        "BIC": "BANKNL2A",
        "IBAN": "NL50BANK1234567890",
        "batch": True,
        "creditor_id": "000000",
        "currency": "EUR"
    })
    payment1 = {
        "name": "Test von Testenstein Test von Testenstein Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction1"
    }
    sdd.add_payment(payment1)
    with pytest.raises(ValidationError):
        sdd.export()
    sdd.export(validate=False)


def test_invalid_mandate():
    sdd = SepaDD({
        "name": "TestCreditor",
        "BIC": "BANKNL2A",
        "IBAN": "NL50BANK1234567890",
        "batch": True,
        "creditor_id": "000000",
        "currency": "EUR"
    })
    payment1 = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234ÄOÜ",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction1"
    }
    sdd.add_payment(payment1)
    with pytest.raises(ValidationError):
        sdd.export()
    sdd.export(validate=False)
