# encoding: utf-8
import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


@pytest.fixture
def strf():
    return SepaTransfer({
        "name": "Miller & Son Ltd",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR"
    })


SAMPLE_RESULT = b"""
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>20180724041136-3b840ce62087</MsgId>
      <CreDtTm>2018-07-24T16:11:36</CreDtTm>
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>20.24</CtrlSum>
      <InitgPty>
        <Nm>Miller &amp; Son Ltd</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>MillerSonLtd-67c22f433a9e</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>20.24</CtrlSum>
      <Dbtr>
        <Nm>Miller &amp; Son Ltd</Nm>
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
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>af755a40cb692551ed9f9d55f7179525</EndToEndId>
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


def test_two_debits(strf):
    payment1 = {
        "endtoend_id": "ebd75e7e649375d91b33dc11ae44c0e1",
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "description": "Test transaction1"
    }
    payment2 = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "description": "Test transaction1",
        "endtoend_id": "af755a40cb692551ed9f9d55f7179525"
    }

    strf.add_payment(payment1)
    strf.add_payment(payment2)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())
