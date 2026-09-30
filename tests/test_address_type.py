import datetime
import xml.etree.ElementTree as ET

import pytest

from sepaxml import SepaDD, SepaTransfer
from sepaxml.validation import ValidationError
from tests.utils import validate_xml

SCHEMAS = [
    (SepaTransfer, "pain.001.001.03"),
    (SepaTransfer, "pain.001.001.09"),
    (SepaTransfer, "pain.001.001.10"),
    (SepaTransfer, "pain.001.001.11"),
    (SepaDD, "pain.008.001.02"),
    (SepaDD, "pain.008.001.08"),
    (SepaDD, "pain.008.001.09"),
    (SepaDD, "pain.008.001.10"),
]
LEGACY_AND_CHOICE_SCHEMAS = [SCHEMAS[0], SCHEMAS[1], SCHEMAS[4], SCHEMAS[5]]


def make_document(payment_class, schema, batch, address):
    config = {
        "name": "Test sender",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": batch,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "address": dict(address),
    }
    payment = {
        "name": "Test receiver",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 5000,
        "type": "RCUR",
        "execution_date": datetime.date(2026, 10, 1),
        "collection_date": datetime.date(2026, 10, 1),
        "mandate_id": "TEST",
        "mandate_date": datetime.date(2026, 9, 1),
        "description": "Synthetic test",
        "address": dict(address),
    }
    document = payment_class(config, schema=schema)
    document.add_payment(payment)
    return document


def validated_addresses(document):
    output = document.export()
    validate_xml(output, document.schema)
    namespaces = {"s": "urn:iso:std:iso:20022:tech:xsd:" + document.schema}
    addresses = ET.fromstring(output).findall(".//s:PstlAdr", namespaces)
    assert addresses
    return addresses, namespaces


@pytest.mark.parametrize("payment_class,schema", SCHEMAS)
@pytest.mark.parametrize("batch", [False, True])
def test_address_type_matches_schema(payment_class, schema, batch):
    address = {
        "address_type": "PBOX",
        "department": "Finance",
        "street_name": "Test Street",
        "country": "NL",
        "lines": ["Line one", "Line two"],
    }
    document = make_document(payment_class, schema, batch, address)
    addresses, namespaces = validated_addresses(document)
    if batch:
        assert len(addresses) == 2
    for node in addresses:
        assert [child.tag.rsplit("}", 1)[-1] for child in node] == [
            "AdrTp", "Dept", "StrtNm", "Ctry", "AdrLine", "AdrLine",
        ]
        assert node.find("s:Dept", namespaces).text == "Finance"
        assert node.find("s:StrtNm", namespaces).text == "Test Street"
        assert node.find("s:Ctry", namespaces).text == "NL"
        assert [line.text for line in node.findall("s:AdrLine", namespaces)] == ["Line one", "Line two"]
        address_type = node.find("s:AdrTp", namespaces)
        if schema in ("pain.001.001.03", "pain.008.001.02"):
            assert address_type.text == "PBOX"
            assert len(address_type) == 0
        else:
            assert address_type.text is None
            assert len(address_type) == 1
            assert address_type.find("s:Cd", namespaces).text == "PBOX"


@pytest.mark.parametrize("payment_class,schema", LEGACY_AND_CHOICE_SCHEMAS)
@pytest.mark.parametrize("batch", [False, True])
@pytest.mark.parametrize("type_fields", [{}, {"address_type": None}, {"address_type": ""}])
def test_missing_address_type_is_omitted(payment_class, schema, batch, type_fields):
    address = {"country": "NL", "lines": ["Line one", "Line two"]}
    address.update(type_fields)
    addresses, namespaces = validated_addresses(make_document(payment_class, schema, batch, address))
    for node in addresses:
        assert node.find("s:AdrTp", namespaces) is None
        assert node.find("s:Ctry", namespaces).text == "NL"
        assert [line.text for line in node.findall("s:AdrLine", namespaces)] == ["Line one", "Line two"]


@pytest.mark.parametrize("payment_class,schema", LEGACY_AND_CHOICE_SCHEMAS)
def test_invalid_address_type_is_rejected(payment_class, schema):
    document = make_document(payment_class, schema, True, {"address_type": "INVALID", "country": "NL"})
    with pytest.raises(ValidationError):
        document.export()


@pytest.mark.parametrize("payment_class,schema", [
    (SepaTransfer, "pain.001.001.99"),
    (SepaDD, "pain.008.001.99"),
])
def test_unbundled_schema_keeps_address_type_text(payment_class, schema):
    document = make_document(payment_class, schema, True, {"address_type": "ADDR", "country": "NL"})
    namespaces = {"s": "urn:iso:std:iso:20022:tech:xsd:" + schema}
    nodes = ET.fromstring(document.export(validate=False)).findall(".//s:AdrTp", namespaces)
    assert len(nodes) == 2
    for node in nodes:
        assert node.text == "ADDR"
        assert len(node) == 0
