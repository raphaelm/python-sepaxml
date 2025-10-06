import datetime

import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


@pytest.fixture
def strf():
    return SepaTransfer(
        {
            "name": "TestCreditor",
            "IBAN": "NL50BANK1234567890",
            "BIC": "BANKNL2A",
            "batch": False,
            "currency": "EUR",
        },
        schema="pain.001.001.03",
    )


SAMPLE_RESULT_INSTANT = b"""
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>20180724041334-4db42f0dd97e</MsgId>
      <CreDtTm>2018-07-24T16:13:34</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10.12</CtrlSum>
      <InitgPty>
        <Nm>TestCreditor</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>TestCreditor-8748725a0019</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>false</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10.12</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>INST</Cd>
        </LclInstrm>
      </PmtTpInf>
      <ReqdExctnDt>2018-07-24</ReqdExctnDt>
      <Dbtr>
        <Nm>TestCreditor</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>NL50BANK1234567890</IBAN>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BIC>BANKNL2A</BIC>
        </FinInstnId>
      </DbtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>ebd75e7e649375d91b33dc11ae44c0e1</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="EUR">10.12</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId>
            <BIC>BANKNL2A</BIC>
          </FinInstnId>
        </CdtrAgt>
        <Cdtr>
          <Nm>Test von Testenstein</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>NL50BANK1234567890</IBAN>
          </Id>
        </CdtrAcct>
        <RmtInf>
          <Ustrd>Test transaction1</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
"""


def test_instant_payment_non_batch(strf):
    payment = {
        "endtoend_id": "ebd75e7e649375d91b33dc11ae44c0e1",
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction1",
        "instant": True,
    }

    strf.add_payment(payment)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    print(xmlpretty.decode())
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT_INSTANT.strip())


def test_instant_payment_batch():
    strf_batch = SepaTransfer(
        {
            "name": "TestCreditor",
            "IBAN": "NL50BANK1234567890",
            "BIC": "BANKNL2A",
            "batch": True,
            "currency": "EUR",
        },
        schema="pain.001.001.03",
    )

    payment1 = {
        "endtoend_id": "ebd75e7e649375d91b33dc11ae44c0e1",
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction1",
        "instant": True,
    }
    payment2 = {
        "endtoend_id": "af755a40cb692551ed9f9d55f7179525",
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction2",
        "instant": True,
    }

    strf_batch.add_payment(payment1)
    strf_batch.add_payment(payment2)
    xmlout = strf_batch.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    xmlstr = xmlpretty.decode()
    print(xmlstr)

    # Verify that LclInstrm with INST code is present
    assert "<LclInstrm>" in xmlstr
    assert "<Cd>INST</Cd>" in xmlstr

    # Verify batch has correct number of transactions
    assert "<NbOfTxs>2</NbOfTxs>" in xmlstr


def test_mixed_instant_and_normal_batch():
    """Test that instant and non-instant payments create separate batches"""
    strf_batch = SepaTransfer(
        {
            "name": "TestCreditor",
            "IBAN": "NL50BANK1234567890",
            "BIC": "BANKNL2A",
            "batch": True,
            "currency": "EUR",
        },
        schema="pain.001.001.03",
    )

    payment_instant = {
        "endtoend_id": "instant001",
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Instant payment",
        "instant": True,
    }
    payment_normal = {
        "endtoend_id": "normal001",
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 2024,
        "execution_date": datetime.date.today(),
        "description": "Normal payment",
        "instant": False,
    }

    strf_batch.add_payment(payment_instant)
    strf_batch.add_payment(payment_normal)
    xmlout = strf_batch.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    xmlstr = xmlpretty.decode()
    print(xmlstr)

    # Should have 2 separate PmtInf blocks (one for instant, one for normal)
    assert xmlstr.count("<PmtInf>") == 2
    assert xmlstr.count("</PmtInf>") == 2

    # One should have LclInstrm with INST, the other should not
    assert xmlstr.count("<LclInstrm>") == 1
    assert xmlstr.count("<Cd>INST</Cd>") == 1

    # Each batch should have 1 transaction
    assert xmlstr.count("<NbOfTxs>1</NbOfTxs>") == 2

    # Verify total in header is sum of both
    assert "<CtrlSum>30.36</CtrlSum>" in xmlstr


def test_domestic_instant_payment():
    strf_domestic = SepaTransfer(
        {
            "name": "TestCreditor",
            "IBAN": "NL50BANK1234567890",
            "BIC": "BANKNL2A",
            "batch": False,
            "currency": "EUR",
            "domestic": True,
        },
        schema="pain.001.001.03",
    )

    payment = {
        "endtoend_id": "ebd75e7e649375d91b33dc11ae44c0e1",
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction1",
        "instant": True,
    }

    strf_domestic.add_payment(payment)
    xmlout = strf_domestic.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    xmlstr = xmlpretty.decode()
    print(xmlstr)

    # Verify that LclInstrm with INST code is present even for domestic
    assert "<LclInstrm>" in xmlstr
    assert "<Cd>INST</Cd>" in xmlstr
    # Verify that SvcLvl is not present for domestic
    assert "<SvcLvl>" not in xmlstr
