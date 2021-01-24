import datetime

import pytest

from sepaxml import SepaTransfer
from tests.utils import clean_ids, validate_xml


@pytest.fixture
def strf():
    return SepaTransfer({
        "name": "TestCreditor",
        "IBAN": "CH4912345123456789012",
        "batch": True,
        "domestic": True,
        "currency": "CHF"
    }, schema="pain.001.001.03")


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
      <ReqdExctnDt>2018-07-24</ReqdExctnDt>
      <Dbtr>
        <Nm>TestCreditor</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>CH4912345123456789012</IBAN>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId/>
      </DbtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>NOTPROVIDED</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="CHF">10.12</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId/>
        </CdtrAgt>
        <Cdtr>
          <Nm>Test von Testenstein</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>CH4912345123456789012</IBAN>
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
          <InstdAmt Ccy="CHF">50.00</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId/>
        </CdtrAgt>
        <Cdtr>
          <Nm>Test du Test</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>CH6911111222222222222</IBAN>
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


def test_two_domestic_debits(strf):
    payment1 = {
        "name": "Test von Testenstein",
        "IBAN": "CH4912345123456789012",
        "amount": 1012,
        "execution_date": datetime.date.today(),
        "description": "Test transaction1"
    }
    payment2 = {
        "name": "Test du Test",
        "IBAN": "CH6911111222222222222",
        "amount": 5000,
        "execution_date": datetime.date.today(),
        "description": "Test transaction2"
    }

    strf.add_payment(payment1)
    strf.add_payment(payment2)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())
