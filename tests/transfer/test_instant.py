import datetime

import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


@pytest.fixture
def strf_instant():
    return SepaTransfer({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "instant": True,
        "currency": "EUR"
    }, schema="pain.001.001.03")


# Identical to tests/transfer/test_00100103.py's SAMPLE_RESULT, but with the
# SEPA Instant local instrument (LclInstrm/Cd=INST) emitted directly after
# SvcLvl inside PmtTpInf -- the ISO 20022 PaymentTypeInformation sequence is
# InstrPrty?, SvcLvl?, LclInstrm?, CtgyPurp?.
SAMPLE_RESULT = b"""
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>20180724040432-d24ce3b3e284</MsgId>
      <CreDtTm>2018-07-24T16:04:32</CreDtTm>
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>60.12</CtrlSum>
      <InitgPty>
        <Nm>TestCreditor</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>TestCreditor-90102652f82a</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>60.12</CtrlSum>
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
          <EndToEndId>NOTPROVIDED</EndToEndId>
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
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>NOTPROVIDED</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="EUR">50.00</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId>
            <BIC>BANKNL2A</BIC>
          </FinInstnId>
        </CdtrAgt>
        <Cdtr>
          <Nm>Test du Test</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>NL50BANK1234567890</IBAN>
          </Id>
        </CdtrAcct>
        <RmtInf>
          <Ustrd>Test transaction2</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
"""


def test_instant_batch_emits_inst_after_svclvl(strf_instant):
    payment1 = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction1"
    }
    payment2 = {
        "name": "Test du Test",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 5000,
        "execution_date": datetime.date.today(),
        "description": "Test transaction2"
    }

    strf_instant.add_payment(payment1)
    strf_instant.add_payment(payment2)
    xmlout = strf_instant.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())


def test_instant_non_batch_emits_inst_after_svclvl():
    strf = SepaTransfer({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": False,
        "instant": True,
        "currency": "EUR"
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction1"
    })

    xmlout = strf.export()
    # export() output is not pretty-printed, so the elements are adjacent:
    # asserting the compact substring pins both presence and SvcLvl->LclInstrm order.
    assert b"<PmtTpInf><SvcLvl><Cd>SEPA</Cd></SvcLvl><LclInstrm><Cd>INST</Cd></LclInstrm></PmtTpInf>" in xmlout
    validate_xml(xmlout, "pain.001.001.03")


def test_no_instant_flag_emits_no_lclinstrm():
    """Without the flag, the transfer is a plain SEPA transfer -- no INST."""
    strf = SepaTransfer({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR"
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction1"
    })

    xmlout = strf.export()
    assert b"LclInstrm" not in xmlout
    assert b"INST" not in xmlout
    validate_xml(xmlout, "pain.001.001.03")


def test_instant_false_emits_no_lclinstrm():
    """instant=False is the verified plain-SEPA fallback -- no INST node."""
    strf = SepaTransfer({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "instant": False,
        "currency": "EUR"
    }, schema="pain.001.001.03")

    strf.add_payment({
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction1"
    })

    xmlout = strf.export()
    assert b"LclInstrm" not in xmlout
    assert b"INST" not in xmlout
    validate_xml(xmlout, "pain.001.001.03")
