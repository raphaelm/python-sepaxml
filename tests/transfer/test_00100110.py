import datetime

import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


@pytest.fixture
def strf():
    return SepaTransfer({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "currency": "EUR"
    }, schema="pain.001.001.10")


SAMPLE_RESULT = b"""
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.10" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
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
      </PmtTpInf>
      <ReqdExctnDt>
        <Dt>2018-07-24</Dt>
      </ReqdExctnDt>
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
          <BICFI>BANKNL2A</BICFI>
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
            <BICFI>BANKNL2A</BICFI>
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
            <BICFI>BANKNL2A</BICFI>
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


def test_two_debits(strf):
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

    strf.add_payment(payment1)
    strf.add_payment(payment2)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.10")
    assert clean_ids(xmlpretty.strip()).decode() == clean_ids(SAMPLE_RESULT.strip()).decode()
