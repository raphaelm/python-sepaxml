# encoding: utf-8

import datetime

import pytest

from sepaxml import SepaDD
from tests.utils import clean_ids, validate_xml



@pytest.fixture
def sdd():
    return SepaDD({
        "name": "Miller & Son Ltd",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR"
    }, schema="pain.008.001.02")


SAMPLE_RESULT = b"""
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrDrctDbtInitn>
    <GrpHdr>
      <MsgId>20012017014921-ba2dab283fdd</MsgId>
      <CreDtTm>2017-01-20T13:49:21</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10.12</CtrlSum>
      <InitgPty>
        <Nm>Miller &amp; Son Ltd</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>DE26ZZZ00000000000</Id>
            </Othr>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>MillerSonLtd-ecd6a2f680ce</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10.12</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>CORE</Cd>
        </LclInstrm>
        <SeqTp>FRST</SeqTp>
      </PmtTpInf>
      <ReqdColltnDt>2017-01-20</ReqdColltnDt>
      <Cdtr>
        <Nm>Miller &amp; Son Ltd</Nm>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>NL50BANK1234567890</IBAN>
        </Id>
      </CdtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BIC>BANKNL2A</BIC>
        </FinInstnId>
      </CdtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtrSchmeId>
        <Id>
          <PrvtId>
            <Othr>
              <Id>DE26ZZZ00000000000</Id>
              <SchmeNm>
                <Prtry>SEPA</Prtry>
              </SchmeNm>
            </Othr>
          </PrvtId>
        </Id>
      </CdtrSchmeId>
      <DrctDbtTxInf>
        <PmtId>
          <EndToEndId>MillerSonLtd-1234567890ab</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="GBP">10.12</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>1234</MndtId>
            <DtOfSgntr>2017-01-20</DtOfSgntr>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId>
            <BIC>BANKNL2A</BIC>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>This is a test</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>NL50BANK1234567890</IBAN>
          </Id>
        </DbtrAcct>
        <RmtInf>
          <Ustrd>Test transaction</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>
"""


def test_payment_overrides_currency(sdd):
    """Test that payment currency overrides config currency"""
    payment = {
        "name": "This is a test",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction",
        "currency": "GBP"  # Override the EUR config currency
    }

    sdd.add_payment(payment)
    xmlout = sdd.export()
    xmlpretty = validate_xml(xmlout, "pain.008.001.02")
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())
