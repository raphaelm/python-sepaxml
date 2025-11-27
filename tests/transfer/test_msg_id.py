import datetime

import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


def test_custom_msg_id_transfer():
    """Test that custom msg_id is correctly set in transfer XML"""
    custom_msg_id = "CUSTOM-TRANSFER-MSG-ID-123"
    
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR",
        "msg_id": custom_msg_id
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

    # Check that custom msg_id is present
    assert f'<MsgId>{custom_msg_id}</MsgId>'.encode() in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.03")


def test_msg_id_truncated_to_35_chars_transfer():
    """Test that msg_id longer than 35 characters is truncated in transfers"""
    long_msg_id = "T" * 50  # 50 characters
    expected_msg_id = "T" * 35  # Should be truncated to 35
    
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR",
        "msg_id": long_msg_id
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

    # Check that msg_id is truncated to 35 characters
    assert f'<MsgId>{expected_msg_id}</MsgId>'.encode() in xmlout
    assert f'<MsgId>{long_msg_id}</MsgId>'.encode() not in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.03")


def test_default_msg_id_transfer():
    """Test that default msg_id is generated when not provided in transfers"""
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
    validate_xml(xmlout, "pain.001.001.03")


def test_msg_id_with_newer_transfer_schema():
    """Test custom msg_id with pain.001.001.09 schema"""
    custom_msg_id = "TRANSFER-2023-MSG"
    
    strf = SepaTransfer({
        "name": "TestDebtor",
        "IBAN": "NL50BANK1234567890",
        "batch": True,
        "currency": "EUR",
        "msg_id": custom_msg_id
    }, schema="pain.001.001.09")

    strf.add_payment({
        "name": "Test Creditor",
        "IBAN": "NL50BANK9876543210",
        "amount": 1012,
        "execution_date": datetime.date(2017, 1, 20),
        "description": "Test transfer"
    })

    xmlout = strf.export(validate=False)

    # Check that custom msg_id is present
    assert f'<MsgId>{custom_msg_id}</MsgId>'.encode() in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.001.001.09")
