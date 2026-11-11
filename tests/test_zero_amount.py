import datetime
import xml.etree.ElementTree as ET

import pytest

from sepaxml import SepaDD, SepaTransfer
from sepaxml.utils import decimal_str_to_int
from tests.utils import validate_xml


@pytest.mark.parametrize("amount, expected", [
    ("0.00", 0), ("00.00", 0), ("0.01", 1), ("0.10", 10),
    ("1.00", 100), ("10.12", 1012), ("999999999.99", 99999999999),
])
def test_decimal_str_to_int(amount, expected):
    assert decimal_str_to_int(amount) == expected


@pytest.mark.parametrize("schema", [
    "pain.001.001.03", "pain.001.001.09", "pain.001.001.10", "pain.001.001.11",
    "pain.008.001.02", "pain.008.001.08", "pain.008.001.09", "pain.008.001.10",
])
@pytest.mark.parametrize("batch", [False, True])
@pytest.mark.parametrize("amounts", [(0,), (0, 1012)])
def test_export_zero_amount(schema, batch, amounts):
    config = {
        "name": "TestCreditor", "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A", "currency": "EUR", "batch": batch,
    }
    is_debit = schema.startswith("pain.008")
    if is_debit:
        config["creditor_id"] = "DE26ZZZ00000000000"
    payment_class = SepaDD if is_debit else SepaTransfer
    sepa = payment_class(config, schema=schema)
    for amount in amounts:
        payment = {
            "name": "TestDebtor", "IBAN": "NL50BANK1234567890",
            "BIC": "BANKNL2A", "amount": amount, "description": "Synthetic test",
        }
        if is_debit:
            payment.update(type="RCUR", mandate_id="TEST-MANDATE",
                           mandate_date=datetime.date(2026, 1, 1),
                           collection_date=datetime.date(2026, 11, 20))
        else:
            payment["execution_date"] = datetime.date(2026, 11, 20)
        sepa.add_payment(payment)

    xmlout = sepa.export()
    validate_xml(xmlout, schema)
    ns = {"p": "urn:iso:std:iso:20022:tech:xsd:" + schema}
    root = ET.fromstring(xmlout)
    header = root.find(".//p:GrpHdr", ns)
    assert header.find("p:NbOfTxs", ns).text == str(len(amounts))
    assert header.find("p:CtrlSum", ns).text == ("10.12" if len(amounts) > 1 else "0.00")
    assert [node.text for node in root.findall(".//p:InstdAmt", ns)] == [
        "0.00" if amount == 0 else "10.12" for amount in amounts
    ]
