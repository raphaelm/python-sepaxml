import datetime

import pytest

from sepaxml import SepaDD
from tests.utils import clean_ids, validate_xml


@pytest.fixture
def sdd_with_ultimate_creditor():
    return SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "ultimate_creditor": {
            "name": "Ultimate Creditor Company",
            "BIC_or_BEI": "ABCDEFGH",
            "id": "UC123456789",
            "id_scheme_name": "CUST"
        }
    }, schema="pain.008.001.02")


@pytest.fixture
def sdd_with_ultimate_creditor_minimal():
    return SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "ultimate_creditor": {
            "name": "Ultimate Creditor Company",
            "id": "UC123456789"
        }
    }, schema="pain.008.001.02")


def test_ultimate_creditor_full(sdd_with_ultimate_creditor):
    """Test that ultimate creditor with all fields is correctly added to the XML"""
    sdd_with_ultimate_creditor.add_payment({
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date(2017, 1, 20),
        "mandate_id": "1234",
        "mandate_date": datetime.date(2017, 1, 20),
        "description": "Test transaction"
    })

    xmlout = sdd_with_ultimate_creditor.export(validate=False)
    xmlpretty = clean_ids(xmlout)

    # Check that UltmtCdtr node exists
    assert b'<UltmtCdtr>' in xmlpretty
    assert b'<Nm>Ultimate Creditor Company</Nm>' in xmlpretty
    
    # Check BIC or BEI
    assert b'<BICOrBEI>ABCDEFGH</BICOrBEI>' in xmlpretty
    
    # Check ID and scheme
    assert b'<Id>UC123456789</Id>' in xmlpretty
    assert b'<Prtry>CUST</Prtry>' in xmlpretty
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_ultimate_creditor_minimal(sdd_with_ultimate_creditor_minimal):
    """Test that ultimate creditor with minimal fields is correctly added to the XML"""
    sdd_with_ultimate_creditor_minimal.add_payment({
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date(2017, 1, 20),
        "mandate_id": "1234",
        "mandate_date": datetime.date(2017, 1, 20),
        "description": "Test transaction"
    })

    xmlout = sdd_with_ultimate_creditor_minimal.export(validate=False)
    xmlpretty = clean_ids(xmlout)

    # Check that UltmtCdtr node exists
    assert b'<UltmtCdtr>' in xmlpretty
    assert b'<Nm>Ultimate Creditor Company</Nm>' in xmlpretty
    
    # Check ID
    assert b'<Id>UC123456789</Id>' in xmlpretty
    
    # Check BIC or BEI is not present
    assert b'<BICOrBEI>' not in xmlpretty
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_ultimate_creditor_with_newer_schema():
    """Test ultimate creditor with pain.008.001.08 schema"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "ultimate_creditor": {
            "name": "Ultimate Creditor Company",
            "id": "UC123456789",
            "id_scheme_name": "CUST"
        }
    }, schema="pain.008.001.08")

    sdd.add_payment({
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date(2017, 1, 20),
        "mandate_id": "1234",
        "mandate_date": datetime.date(2017, 1, 20),
        "description": "Test transaction"
    })

    xmlout = sdd.export(validate=False)
    xmlpretty = clean_ids(xmlout)

    # Check that UltmtCdtr node exists
    assert b'<UltmtCdtr>' in xmlpretty
    assert b'<Nm>Ultimate Creditor Company</Nm>' in xmlpretty
    assert b'<Id>UC123456789</Id>' in xmlpretty
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.08")


def test_without_ultimate_creditor():
    """Test that XML without ultimate creditor does not contain UltmtCdtr node"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR"
    }, schema="pain.008.001.02")

    sdd.add_payment({
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date(2017, 1, 20),
        "mandate_id": "1234",
        "mandate_date": datetime.date(2017, 1, 20),
        "description": "Test transaction"
    })

    xmlout = sdd.export(validate=False)
    xmlpretty = clean_ids(xmlout)

    # Check that UltmtCdtr node does not exist
    assert b'<UltmtCdtr>' not in xmlpretty
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")
