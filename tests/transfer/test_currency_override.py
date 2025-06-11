# encoding: utf-8

import datetime

import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


@pytest.fixture
def strf_eur():
    return SepaTransfer({
        "name": "Miller & Son Ltd",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR"
    }, schema="pain.001.001.03")


SAMPLE_RESULT = b"""
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>20180724041136-3b840ce62087</MsgId>
      <CreDtTm>2018-07-24T16:11:36</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10.12</CtrlSum>
      <InitgPty>
        <Nm>Miller &amp; Son Ltd</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>MillerSonLtd-67c22f433a9e</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10.12</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
      </PmtTpInf>
      <ReqdExctnDt>2018-07-24</ReqdExctnDt>
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
          <EndToEndId>test123</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="GBP">10.12</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId>
            <BIC>BANKNL2A</BIC>
          </FinInstnId>
        </CdtrAgt>
        <Cdtr>
          <Nm>This is a test</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>NL50BANK1234567890</IBAN>
          </Id>
        </CdtrAcct>
        <RmtInf>
          <Ustrd>Test transaction</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
"""


def test_payment_overrides_currency(strf_eur):
    """Test that payment currency overrides config currency"""
    payment = {
        "name": "This is a test",
        "IBAN": "NL50BANK1234567890", 
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction",
        "endtoend_id": "test123",
        "currency": "GBP"  # Override the EUR config currency
    }

    strf_eur.add_payment(payment)
    xmlout = strf_eur.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())
