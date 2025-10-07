import datetime

import pytest

from sepaxml import SepaDD
from tests.utils import clean_ids, validate_xml


def test_amendment_indicator_present():
    """Test that AmdmntInd node is present in the XML and set to false"""
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

    # Check that AmdmntInd node exists and is set to false
    assert b'<AmdmntInd>false</AmdmntInd>' in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_amendment_indicator_in_batch():
    """Test that AmdmntInd is present for batch transactions"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR"
    }, schema="pain.008.001.02")

    # Add multiple payments
    for i in range(3):
        sdd.add_payment({
            "name": f"Test Person {i}",
            "IBAN": "NL50BANK1234567890",
            "BIC": "BANKNL2A",
            "amount": 1000 + i,
            "type": "FRST",
            "collection_date": datetime.date(2017, 1, 20),
            "mandate_id": f"mandate-{i}",
            "mandate_date": datetime.date(2017, 1, 20),
            "description": f"Test transaction {i}"
        })

    xmlout = sdd.export(validate=False)

    # Count occurrences of AmdmntInd (should be 3, one for each payment)
    amdmnt_count = xmlout.count(b'<AmdmntInd>false</AmdmntInd>')
    assert amdmnt_count == 3
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_amendment_indicator_non_batch():
    """Test that AmdmntInd is present for non-batch transactions"""
    sdd = SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": False,
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

    # Check that AmdmntInd node exists and is set to false
    assert b'<AmdmntInd>false</AmdmntInd>' in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_amendment_indicator_newer_schemas():
    """Test that AmdmntInd works with newer schemas"""
    schemas = ["pain.008.001.08", "pain.008.001.09", "pain.008.001.10"]
    
    for schema in schemas:
        sdd = SepaDD({
            "name": "TestCreditor",
            "IBAN": "NL50BANK1234567890",
            "batch": True,
            "creditor_id": "DE26ZZZ00000000000",
            "currency": "EUR"
        }, schema=schema)

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

        # Check that AmdmntInd node exists
        assert b'<AmdmntInd>false</AmdmntInd>' in xmlout, f"AmdmntInd not found in {schema}"
        
        # Validate against schema
        validate_xml(xmlout, schema)


def test_amendment_indicator_location_in_mandate_info():
    """Test that AmdmntInd is in the correct location within MndtRltdInf"""
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

    # Check that AmdmntInd is within MndtRltdInf section
    import re
    mandate_sections = re.findall(rb'<MndtRltdInf>.*?</MndtRltdInf>', xmlout, re.DOTALL)
    
    assert len(mandate_sections) > 0, "MndtRltdInf section not found"
    
    for mandate_section in mandate_sections:
        assert b'<AmdmntInd>false</AmdmntInd>' in mandate_section, "AmdmntInd not in MndtRltdInf section"
        # Check order: MndtId, DtOfSgntr, AmdmntInd
        assert mandate_section.index(b'<MndtId>') < mandate_section.index(b'<DtOfSgntr>')
        assert mandate_section.index(b'<DtOfSgntr>') < mandate_section.index(b'<AmdmntInd>')
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")
