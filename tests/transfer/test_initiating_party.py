import datetime

import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


def test_custom_initiating_party_transfer():
    """Test that custom initiating_party is correctly set in transfer XML"""
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR",
        "initiating_party": "Custom Transfer Party"
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test Creditor",
        "IBAN": "NL50BANK9876543210",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date(2017, 1, 20),
        "description": "Test transfer"
    })

    xmlout = strf.export(validate=False)

    # Check that custom initiating_party is present in InitgPty
    assert b'<InitgPty>' in xmlout
    assert b'<Nm>Custom Transfer Party</Nm>' in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.03")


def test_custom_initiating_party_id_transfer():
    """Test that custom initiating_party_id is correctly set in transfer XML"""
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR",
        "initiating_party_id": "TRANSFER-ID-987654"
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test Creditor",
        "IBAN": "NL50BANK9876543210",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date(2017, 1, 20),
        "description": "Test transfer"
    })

    xmlout = strf.export(validate=False)

    # Check that custom initiating_party_id is present in InitgPty
    assert b'<InitgPty>' in xmlout
    
    # Extract the InitgPty section
    import re
    initgpty_match = re.search(rb'<InitgPty>.*?</InitgPty>', xmlout, re.DOTALL)
    assert initgpty_match is not None
    initgpty_section = initgpty_match.group(0)
    
    # Check that custom ID is present (within the nested structure)
    assert b'<Id>TRANSFER-ID-987654</Id>' in initgpty_section
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.03")


def test_custom_initiating_party_and_id_transfer():
    """Test that both custom initiating_party and initiating_party_id are set in transfers"""
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR",
        "initiating_party": "Custom Transfer Party",
        "initiating_party_id": "TRANSFER-ID-2023"
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test Creditor",
        "IBAN": "NL50BANK9876543210",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date(2017, 1, 20),
        "description": "Test transfer"
    })

    xmlout = strf.export(validate=False)

    # Check that both custom values are present
    assert b'<InitgPty>' in xmlout
    assert b'<Nm>Custom Transfer Party</Nm>' in xmlout
    
    import re
    initgpty_match = re.search(rb'<InitgPty>.*?</InitgPty>', xmlout, re.DOTALL)
    assert initgpty_match is not None
    initgpty_section = initgpty_match.group(0)
    
    assert b'<Id>TRANSFER-ID-2023</Id>' in initgpty_section
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.03")


def test_default_initiating_party_transfer():
    """Test that default initiating_party uses the name field in transfers"""
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR"
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test Creditor",
        "IBAN": "NL50BANK9876543210",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date(2017, 1, 20),
        "description": "Test transfer"
    })

    xmlout = strf.export(validate=False)

    # Check that default name is used
    assert b'<InitgPty>' in xmlout
    assert b'<Nm>TestDebtor</Nm>' in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.03")


def test_initiating_party_transfer_newer_schema():
    """Test custom initiating party with pain.001.001.09 schema"""
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "batch": True,
        "currency": "EUR",
        "initiating_party": "Modern Transfer Party",
        "initiating_party_id": "MTP-2023-001"
    }, schema="pain.001.001.09")

    strf.add_payment({
        "name": "Test Creditor",
        "IBAN": "NL50BANK9876543210",
        "amount": 1012,
        "execution_date": datetime.date(2017, 1, 20),
        "description": "Test transfer"
    })

    xmlout = strf.export(validate=False)

    # Check that custom values are present
    assert b'<Nm>Modern Transfer Party</Nm>' in xmlout
    
    import re
    initgpty_match = re.search(rb'<InitgPty>.*?</InitgPty>', xmlout, re.DOTALL)
    assert initgpty_match is not None
    initgpty_section = initgpty_match.group(0)
    
    assert b'<Id>MTP-2023-001</Id>' in initgpty_section
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.09")


def test_empty_initiating_party_not_used_transfer():
    """Test that empty initiating_party falls back to name in transfers"""
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR",
        "initiating_party": ""  # Empty string should fallback to name
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test Creditor",
        "IBAN": "NL50BANK9876543210",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date(2017, 1, 20),
        "description": "Test transfer"
    })

    xmlout = strf.export(validate=False)

    # Check that default name is used instead of empty string
    assert b'<Nm>TestDebtor</Nm>' in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.03")


def test_initiating_party_without_id_in_transfer():
    """Test that InitgPty can have only Nm without Id in transfers"""
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR",
        "initiating_party": "Party Without ID"
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test Creditor",
        "IBAN": "NL50BANK9876543210",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date(2017, 1, 20),
        "description": "Test transfer"
    })

    xmlout = strf.export(validate=False)

    # Check that InitgPty has name but check structure
    assert b'<Nm>Party Without ID</Nm>' in xmlout
    
    # Validate against schema - InitgPty with only Nm should be valid
    validate_xml(xmlout, "pain.001.001.03")
