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
      <MsgId>20240730112717-6ee4a6dd7e67</MsgId>
      <CreDtTm>2024-07-30T11:27:17</CreDtTm>
      <NbOfTxs>4</NbOfTxs>
      <CtrlSum>306.65</CtrlSum>
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
      <PmtInfId>MillerSonLtd-a9f5ba6196ee</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>4</NbOfTxs>
      <CtrlSum>306.65</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>CORE</Cd>
        </LclInstrm>
        <SeqTp>RCUR</SeqTp>
      </PmtTpInf>
      <ReqdColltnDt>2024-07-30</ReqdColltnDt>
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
          <EndToEndId>MillerSonLtd-2f15d22210fb</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">66.66</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>PLOP</MndtId>
            <DtOfSgntr>2024-07-30</DtOfSgntr>
            <AmdmntInd>true</AmdmntInd>
            <AmdmntInfDtls>
              <OrgnlDbtrAcct>
                <Id>
                  <Othr>
                    <Id>SMNDA</Id>
                  </Othr>
                </Id>
              </OrgnlDbtrAcct>
            </AmdmntInfDtls>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId>
            <BIC>AGRIFRPP872</BIC>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>Mr Changing Banks</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>FR7617206000000012345678982</IBAN>
          </Id>
        </DbtrAcct>
        <RmtInf>
          <Ustrd>New IBAN with new BIC</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
      <DrctDbtTxInf>
        <PmtId>
          <EndToEndId>MillerSonLtd-9e35edfe8055</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">99.99</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>BLOP</MndtId>
            <DtOfSgntr>2024-07-30</DtOfSgntr>
            <AmdmntInd>true</AmdmntInd>
            <AmdmntInfDtls>
              <OrgnlDbtrAcct>
                <Id>
                  <Othr>
                    <Id>SMNDA</Id>
                  </Othr>
                </Id>
              </OrgnlDbtrAcct>
            </AmdmntInfDtls>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId>
            <BIC>AGRIFRPP866</BIC>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>Ms Changes Accounts</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>FR7616606000000012345678838</IBAN>
          </Id>
        </DbtrAcct>
        <RmtInf>
          <Ustrd>New IBAN with same BIC</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
      <DrctDbtTxInf>
        <PmtId>
          <EndToEndId>MillerSonLtd-841102ac9726</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">50.00</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>OOPS</MndtId>
            <DtOfSgntr>2024-07-30</DtOfSgntr>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId>
            <BIC>AGRIFRPP866</BIC>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>Mr Mistake</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>FR7616606000000000888888849</IBAN>
          </Id>
        </DbtrAcct>
        <RmtInf>
          <Ustrd>New IBAN is the same as previous one</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
      <DrctDbtTxInf>
        <PmtId>
          <EndToEndId>MillerSonLtd-056d67ec1a38</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">90.00</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>WOOSH</MndtId>
            <DtOfSgntr>2024-07-30</DtOfSgntr>
            <AmdmntInd>true</AmdmntInd>
            <AmdmntInfDtls>
              <OrgnlDbtrAcct>
                <Id>
                  <Othr>
                    <Id>SMNDA</Id>
                  </Othr>
                </Id>
              </OrgnlDbtrAcct>
            </AmdmntInfDtls>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId>
            <BIC>BCDMFRPPXXX</BIC>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>Ms Efficiency</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>FR7641439000000000444444460</IBAN>
          </Id>
        </DbtrAcct>
        <RmtInf>
          <Ustrd>Joker value SMNDA instead</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>
"""


def test_four_debits(sdd):
    payment1 = {
        "name": "Mr Changing Banks",
        "IBAN": "FR7617206000000012345678982",
        "BIC": "AGRIFRPP872",
        "previous_IBAN": "FR7616989000000012345678895",
        "amount": 6666,
        "type": "RCUR",
        "collection_date": datetime.date.today(),
        "mandate_id": "PLOP",
        "mandate_date": datetime.date.today(),
        "description": "New IBAN with new BIC",
    }
    payment2 = {
        "name": "Ms Changes Accounts",
        "IBAN": "FR7616606000000012345678838",
        "BIC": "AGRIFRPP866",
        "previous_IBAN": "FR7616606000000099999999953",
        "amount": 9999,
        "type": "RCUR",
        "collection_date": datetime.date.today(),
        "mandate_id": "BLOP",
        "mandate_date": datetime.date.today(),
        "description": "New IBAN with same BIC",
    }
    payment3 = {
        "name": "Mr Mistake",
        "IBAN": "FR7616606000000000888888849",
        "BIC": "AGRIFRPP866",
        "previous_IBAN": "FR7616606000000000888888849",
        "amount": 5000,
        "type": "RCUR",
        "collection_date": datetime.date.today(),
        "mandate_id": "OOPS",
        "mandate_date": datetime.date.today(),
        "description": "New IBAN is the same as previous one",
    }
    payment4 = {
        "name": "Ms Efficiency",
        "IBAN": "FR7641439000000000444444460",
        "BIC": "BCDMFRPPXXX",
        "previous_IBAN": "SMNDA",
        "amount": 9000,
        "type": "RCUR",
        "collection_date": datetime.date.today(),
        "mandate_id": "WOOSH",
        "mandate_date": datetime.date.today(),
        "description": "Joker value SMNDA instead",
    }
    sdd.add_payment(payment1)
    sdd.add_payment(payment2)
    sdd.add_payment(payment3)
    sdd.add_payment(payment4)
    xmlout = sdd.export()
    xmlpretty = validate_xml(xmlout, "pain.008.001.02")
    with open('xmlexport.xml', 'w') as f:
        f.write(xmlpretty.decode())
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())
