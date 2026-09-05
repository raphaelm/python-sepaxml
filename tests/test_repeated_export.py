import datetime
from decimal import Decimal
from xml.etree import ElementTree as ET

import pytest

from sepaxml import SepaDD, SepaTransfer


@pytest.mark.parametrize("batch", [True, False])
@pytest.mark.parametrize("payment_class,schema,transaction_tag", [
    (SepaDD, "pain.008.001.02", "DrctDbtTxInf"),
    (SepaTransfer, "pain.001.001.03", "CdtTrfTxInf"),
])
def test_repeated_export_preserves_payments(batch, payment_class, schema, transaction_tag):
    document = payment_class({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": batch,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
    }, schema=schema)
    payment = {
        "name": "Test Debtor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "RCUR",
        "execution_date": datetime.date(2026, 1, 5),
        "collection_date": datetime.date(2026, 1, 5),
        "mandate_id": "1234",
        "mandate_date": datetime.date(2025, 1, 5),
        "description": "Test transaction",
    }
    document.add_payment(payment.copy())
    document.add_payment(dict(payment, amount=5000))
    namespace = {"s": "urn:iso:std:iso:20022:tech:xsd:" + schema}

    def check_export(expected_count, expected_sum, pretty_print=False):
        xml = ET.fromstring(document.export(pretty_print=pretty_print))
        header = xml.find(".//s:GrpHdr", namespace)
        assert header.find("s:NbOfTxs", namespace).text == str(expected_count)
        assert header.find("s:CtrlSum", namespace).text == expected_sum
        assert len(xml.findall(".//s:" + transaction_tag, namespace)) == expected_count
        batches = xml.findall(".//s:PmtInf", namespace)
        assert sum(int(b.find("s:NbOfTxs", namespace).text) for b in batches) == expected_count
        assert sum(Decimal(b.find("s:CtrlSum", namespace).text) for b in batches) == Decimal(expected_sum)

    check_export(2, "60.12")
    check_export(2, "60.12", pretty_print=True)
    check_export(2, "60.12")

    document.add_payment(dict(payment, amount=123))
    check_export(3, "61.35")
    check_export(3, "61.35")
