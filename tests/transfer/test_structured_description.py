import datetime
import xml.etree.ElementTree as ET

import pytest

from sepaxml import SepaTransfer
from tests.utils import validate_xml


@pytest.fixture
def strf():
    return SepaTransfer(
        {
            "name": "TestCreditor",
            "IBAN": "NL50BANK1234567890",
            "BIC": "BANKNL2A",
            "batch": True,
            "currency": "EUR",
        },
        schema="pain.001.001.03",
    )


def test_structured_description(strf):
    # Using a valid BBA structured description: 000/0000/00196 (base 0000000001, check digit 96)
    # Check digit = 97 - (1 % 97) = 96
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "structured_description": "000/0000/00196",
        "structured_description_type": "BBA",
    }

    strf.add_payment(payment)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    xml = ET.fromstring(xmlpretty)

    # Define namespace map for findall
    ns = {"doc": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"}

    # Check that the structured description nodes exist and have correct values
    strd_nodes = xml.findall(".//doc:Strd", ns)
    assert len(strd_nodes) == 1

    ref_nodes = xml.findall(".//doc:Ref", ns)
    assert len(ref_nodes) == 1
    # Should be cleaned (formatting removed)
    assert ref_nodes[0].text == "000000000196"

    cd_nodes = xml.findall(".//doc:Cd", ns)
    assert len(cd_nodes) >= 1
    assert "SCOR" in [node.text for node in cd_nodes]

    # Check that no Ustrd node exists
    ustrd_nodes = xml.findall(".//doc:Ustrd", ns)
    assert len(ustrd_nodes) == 0


def test_unstructured_description(strf):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction",
    }

    strf.add_payment(payment)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    xml = ET.fromstring(xmlpretty)

    # Define namespace map for findall
    ns = {"doc": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"}

    # Check that the unstructured description node exists
    ustrd_nodes = xml.findall(".//doc:Ustrd", ns)
    assert len(ustrd_nodes) == 1
    assert ustrd_nodes[0].text == "Test transaction"

    # Check that no structured description nodes exist
    strd_nodes = xml.findall(".//doc:Strd", ns)
    assert len(strd_nodes) == 0


def test_missing_descriptions(strf):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
    }

    with pytest.raises(Exception) as excinfo:
        strf.add_payment(payment)

    assert "DESCRIPTION_MISSING" in str(excinfo.value)


def test_both_descriptions(strf):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction",
        "structured_description": "000/0001/00096",
    }

    with pytest.raises(Exception) as excinfo:
        strf.add_payment(payment)

    assert "CANNOT_HAVE_BOTH_DESCRIPTION_AND_STRUCTURED_DESCRIPTION" in str(excinfo.value)


def test_invalid_structured_description_format(strf):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "structured_description": "617094556122022",  # Invalid: too many digits
        "structured_description_type": "BBA",
    }

    with pytest.raises(Exception) as excinfo:
        strf.add_payment(payment)

    assert "STRUCTURED_DESCRIPTION_INVALID" in str(excinfo.value)


def test_invalid_structured_description_checksum(strf):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "structured_description": "000/0001/00099",  # Invalid checksum (should be 96)
        "structured_description_type": "BBA",
    }

    with pytest.raises(Exception) as excinfo:
        strf.add_payment(payment)

    assert "STRUCTURED_DESCRIPTION_INVALID_CHECKSUM" in str(excinfo.value)


def test_iso11649_structured_description(strf):
    # Using a valid ISO 11649 RF creditor reference: RF56TEST123
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "structured_description": "RF56TEST123",
        "structured_description_type": "ISO",
    }

    strf.add_payment(payment)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    xml = ET.fromstring(xmlpretty)

    # Define namespace map for findall
    ns = {"doc": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"}

    # Check that the structured description nodes exist and have correct values
    strd_nodes = xml.findall(".//doc:Strd", ns)
    assert len(strd_nodes) == 1

    ref_nodes = xml.findall(".//doc:Ref", ns)
    assert len(ref_nodes) == 1
    # Should be cleaned (spaces removed, uppercase)
    assert ref_nodes[0].text == "RF56TEST123"


def test_invalid_iso11649_description(strf):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "structured_description": "RF99TEST123",  # Invalid checksum (should be 56)
        "structured_description_type": "ISO",
    }

    with pytest.raises(Exception) as excinfo:
        strf.add_payment(payment)

    assert "STRUCTURED_DESCRIPTION_INVALID_CHECKSUM" in str(excinfo.value)
