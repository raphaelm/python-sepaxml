import datetime
import xml.etree.ElementTree as ET

import pytest

from sepaxml import SepaDD
from tests.utils import validate_xml


@pytest.fixture
def sdd():
    return SepaDD(
        {
            "name": "TestCreditor",
            "IBAN": "NL50BANK1234567890",
            "BIC": "BANKNL2A",
            "batch": True,
            "creditor_id": "DE26ZZZ00000000000",
            "currency": "EUR",
        }
    )


def test_structured_reference(sdd):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "structured_reference": "617094556122022",
    }

    sdd.add_payment(payment)
    xmlout = sdd.export()
    xmlpretty = validate_xml(xmlout, "pain.008.001.02")
    xml = ET.fromstring(xmlpretty)

    # Define namespace map for findall
    ns = {"doc": "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02"}

    # Check that the structured reference nodes exist and have correct values
    strd_nodes = xml.findall(".//doc:Strd", ns)
    assert len(strd_nodes) == 1

    ref_nodes = xml.findall(".//doc:Ref", ns)
    assert len(ref_nodes) == 1
    assert ref_nodes[0].text == "617094556122022"

    cd_nodes = xml.findall(".//doc:Cd", ns)
    assert len(cd_nodes) >= 1
    assert "SCOR" in [node.text for node in cd_nodes]

    # Check that no Ustrd node exists in RmtInf
    ustrd_nodes = xml.findall(".//doc:Ustrd", ns)
    assert len(ustrd_nodes) == 0


def test_unstructured_reference(sdd):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction",
    }

    sdd.add_payment(payment)
    xmlout = sdd.export()
    xmlpretty = validate_xml(xmlout, "pain.008.001.02")
    xml = ET.fromstring(xmlpretty)

    # Define namespace map for findall
    ns = {"doc": "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02"}

    # Check that the unstructured reference node exists
    ustrd_nodes = xml.findall(".//doc:Ustrd", ns)
    assert len(ustrd_nodes) == 1
    assert ustrd_nodes[0].text == "Test transaction"

    # Check that no structured reference nodes exist
    strd_nodes = xml.findall(".//doc:Strd", ns)
    assert len(strd_nodes) == 0


def test_missing_references(sdd):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
    }

    with pytest.raises(Exception) as excinfo:
        sdd.add_payment(payment)

    assert "DESCRIPTION_MISSING" in str(excinfo.value)


def test_both_references(sdd):
    payment = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction",
        "structured_reference": "617094556122022",
    }

    with pytest.raises(Exception) as excinfo:
        sdd.add_payment(payment)

    assert "CANNOT_HAVE_BOTH_DESCRIPTION_AND_STRUCTURED_REFERENCE" in str(excinfo.value)
