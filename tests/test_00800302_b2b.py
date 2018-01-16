# encoding: utf-8

import datetime

import pytest

from sepadd import SepaDD

from .utils import clean_ids
from .utils import validate_xml


@pytest.fixture
def sdd():
    return SepaDD({
        "name": "TestCreditor",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR",
        "instrument": "B2B"
    }, schema="pain.008.003.02")


SAMPLE_RESULT = b"""
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.003.02" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrDrctDbtInitn>
    <GrpHdr>
      <MsgId>20012017014921-ba2dab283fdd</MsgId>
      <CreDtTm>2017-01-20T13:49:21</CreDtTm>
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>60.12</CtrlSum>
      <InitgPty>
        <Nm>TestCreditor</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>TestCreditor-ecd6a2f680ce</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10.12</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>B2B</Cd>
        </LclInstrm>
        <SeqTp>FRST</SeqTp>
      </PmtTpInf>
      <ReqdColltnDt>2017-01-20</ReqdColltnDt>
      <Cdtr>
        <Nm>TestCreditor</Nm>
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
          <EndToEndId>TestCreditor-4431989789fb</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">10.12</InstdAmt>
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
          <Nm>Test von Testenstein</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>NL50BANK1234567890</IBAN>
          </Id>
        </DbtrAcct>
        <RmtInf>
          <Ustrd>Test transaction1</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
    </PmtInf>
    <PmtInf>
      <PmtInfId>TestCreditor-d547a1b3882f</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>50.00</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>B2B</Cd>
        </LclInstrm>
        <SeqTp>RCUR</SeqTp>
      </PmtTpInf>
      <ReqdColltnDt>2017-01-20</ReqdColltnDt>
      <Cdtr>
        <Nm>TestCreditor</Nm>
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
          <EndToEndId>TestCreditor-7e989083e265</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">50.00</InstdAmt>
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
          <Nm>Test du Test</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>NL50BANK1234567890</IBAN>
          </Id>
        </DbtrAcct>
        <RmtInf>
          <Ustrd>Test transaction2</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>
"""


def test_two_debits(sdd):
    payment1 = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction1"
    }
    payment2 = {
        "name": "Test du Test",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 5000,
        "type": "RCUR",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction2"
    }

    sdd.add_payment(payment1)
    sdd.add_payment(payment2)
    xmlout = sdd.export()
    xmlpretty = validate_xml(xmlout, "pain.008.003.02")
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())
