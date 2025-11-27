import datetime
import re

import pytest

from sepaxml import SepaDD
from tests.utils import clean_ids, validate_xml


def test_custom_initiating_party():
    """Test that custom initiating_party is correctly set in the XML"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "initiating_party": "Custom Initiating Party Name"
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

    # Check that custom initiating_party is present in InitgPty
    assert b'<InitgPty>' in xmlout
    assert b'<Nm>Custom Initiating Party Name</Nm>' in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_custom_initiating_party_id():
    """Test that custom initiating_party_id is correctly set in the XML"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "initiating_party_id": "CUSTOM-ID-123456"
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

    # Check that custom initiating_party_id is present in InitgPty
    assert b'<InitgPty>' in xmlout
    
    # The ID should be in the InitgPty section
    import re
    # Extract the InitgPty section
    initgpty_match = re.search(rb'<InitgPty>.*?</InitgPty>', xmlout, re.DOTALL)
    assert initgpty_match is not None
    initgpty_section = initgpty_match.group(0)
    
    # Check that custom ID is present
    assert b'<Id>CUSTOM-ID-123456</Id>' in initgpty_section
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_custom_initiating_party_and_id():
    """Test that both custom initiating_party and initiating_party_id are correctly set"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "initiating_party": "Custom Initiating Party",
        "initiating_party_id": "CUSTOM-ID-789"
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

    # Check that both custom values are present
    assert b'<InitgPty>' in xmlout
    assert b'<Nm>Custom Initiating Party</Nm>' in xmlout
    
    import re
    # Extract the InitgPty section
    initgpty_match = re.search(rb'<InitgPty>.*?</InitgPty>', xmlout, re.DOTALL)
    assert initgpty_match is not None
    initgpty_section = initgpty_match.group(0)
    
    assert b'<Id>CUSTOM-ID-789</Id>' in initgpty_section
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_default_initiating_party():
    """Test that default initiating_party uses the name field"""
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

    # Check that default name is used
    assert b'<InitgPty>' in xmlout
    assert b'<Nm>TestCreditor</Nm>' in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_default_initiating_party_id():
    """Test that default initiating_party_id uses the creditor_id field"""
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

    # Check that default creditor_id is used
    import re
    # Extract the InitgPty section
    initgpty_match = re.search(rb'<InitgPty>.*?</InitgPty>', xmlout, re.DOTALL)
    assert initgpty_match is not None
    initgpty_section = initgpty_match.group(0)
    
    assert b'<Id>DE26ZZZ00000000000</Id>' in initgpty_section
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_initiating_party_with_newer_schema():
    """Test custom initiating party with pain.008.001.08 schema"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "initiating_party": "Custom Party 2023",
        "initiating_party_id": "CP-2023-001"
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

    # Check that custom values are present
    assert b'<Nm>Custom Party 2023</Nm>' in xmlout
    
    import re
    initgpty_match = re.search(rb'<InitgPty>.*?</InitgPty>', xmlout, re.DOTALL)
    assert initgpty_match is not None
    initgpty_section = initgpty_match.group(0)
    
    assert b'<Id>CP-2023-001</Id>' in initgpty_section
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.08")


def test_empty_initiating_party_not_used():
    """Test that empty initiating_party falls back to name"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "initiating_party": ""  # Empty string should fallback to name
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

    # Check that default name is used instead of empty string
    assert b'<Nm>TestCreditor</Nm>' in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")
