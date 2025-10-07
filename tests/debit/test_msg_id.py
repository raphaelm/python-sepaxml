import datetime

import pytest

from sepaxml import SepaDD
from tests.utils import clean_ids, validate_xml


def test_custom_msg_id():
    """Test that custom msg_id is correctly set in the XML"""
    custom_msg_id = "CUSTOM-MSG-ID-123456789"
    
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "msg_id": custom_msg_id
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

    # Check that custom msg_id is present
    assert f'<MsgId>{custom_msg_id}</MsgId>'.encode() in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_msg_id_truncated_to_35_chars():
    """Test that msg_id longer than 35 characters is truncated"""
    long_msg_id = "A" * 50  # 50 characters
    expected_msg_id = "A" * 35  # Should be truncated to 35
    
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "msg_id": long_msg_id
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

    # Check that msg_id is truncated to 35 characters
    assert f'<MsgId>{expected_msg_id}</MsgId>'.encode() in xmlout
    assert f'<MsgId>{long_msg_id}</MsgId>'.encode() not in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_default_msg_id():
    """Test that default msg_id is generated when not provided"""
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

    # Check that MsgId node exists and is not empty
    assert b'<MsgId>' in xmlout
    assert b'</MsgId>' in xmlout
    
    # Extract the MsgId value
    import re
    msg_id_match = re.search(rb'<MsgId>([^<]+)</MsgId>', xmlout)
    assert msg_id_match is not None
    msg_id = msg_id_match.group(1).decode('utf-8')
    
    # Check that msg_id follows the expected format (timestamp-random)
    assert '-' in msg_id
    assert len(msg_id) > 0
    assert len(msg_id) <= 35
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_msg_id_with_newer_schema():
    """Test custom msg_id with pain.008.001.08 schema"""
    custom_msg_id = "CUSTOM-MSG-ID-2023"
    
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "msg_id": custom_msg_id
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

    # Check that custom msg_id is present
    assert f'<MsgId>{custom_msg_id}</MsgId>'.encode() in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.08")
