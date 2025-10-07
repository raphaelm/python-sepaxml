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
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>60.12</CtrlSum>
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
          <EndToEndId>ebd75e7e649375d91b33dc11ae44c0e1</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">10.12</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>1234</MndtId>
            <DtOfSgntr>2017-01-20</DtOfSgntr>
            <AmdmntInd>false</AmdmntInd>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId>
            <BIC>BANKNL2A</BIC>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>Test &amp; Co.</Nm>
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
      <PmtInfId>MillerSonLtd-d547a1b3882f</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>50.00</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>CORE</Cd>
        </LclInstrm>
        <SeqTp>RCUR</SeqTp>
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
          <EndToEndId>af755a40cb692551ed9f9d55f7179525</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">50.00</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>1234</MndtId>
            <DtOfSgntr>2017-01-20</DtOfSgntr>
            <AmdmntInd>false</AmdmntInd>
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
          <Ustrd>Testgrusse &lt;html&gt;</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>
"""


def test_two_debits(sdd):
    payment1 = {
        "name": "Test & Co.",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction1",
        "endtoend_id": "ebd75e7e649375d91b33dc11ae44c0e1"
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
        "description": u"Testgrüße <html>",
        "endtoend_id": "af755a40cb692551ed9f9d55f7179525"
    }

    sdd.add_payment(payment1)
    sdd.add_payment(payment2)
    xmlout = sdd.export()
    xmlpretty = validate_xml(xmlout, "pain.008.001.02")
    assert clean_ids(xmlpretty.strip()) == clean_ids(SAMPLE_RESULT.strip())


def test_endtoend_id_truncated_to_35_chars(sdd):
    """Test that endtoend_id longer than 35 characters is truncated"""
    long_endtoend_id = "A" * 50  # 50 characters
    expected_endtoend_id = "A" * 35  # Should be truncated to 35
    
    payment = {
        "name": "Test Customer",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1000,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction",
        "endtoend_id": long_endtoend_id
    }
    
    sdd.add_payment(payment)
    xmlout = sdd.export(validate=False)
    
    # Check that endtoend_id is truncated to 35 characters
    assert f'<EndToEndId>{expected_endtoend_id}</EndToEndId>'.encode() in xmlout
    assert f'<EndToEndId>{long_endtoend_id}</EndToEndId>'.encode() not in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_endtoend_id_exactly_35_chars(sdd):
    """Test that endtoend_id with exactly 35 characters is not truncated"""
    exact_endtoend_id = "B" * 35  # Exactly 35 characters
    
    payment = {
        "name": "Test Customer",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1000,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction",
        "endtoend_id": exact_endtoend_id
    }
    
    sdd.add_payment(payment)
    xmlout = sdd.export(validate=False)
    
    # Check that endtoend_id is preserved
    assert f'<EndToEndId>{exact_endtoend_id}</EndToEndId>'.encode() in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_endtoend_id_less_than_35_chars(sdd):
    """Test that endtoend_id with less than 35 characters is preserved"""
    short_endtoend_id = "SHORT-ID-123"  # Less than 35 characters
    
    payment = {
        "name": "Test Customer",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1000,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction",
        "endtoend_id": short_endtoend_id
    }
    
    sdd.add_payment(payment)
    xmlout = sdd.export(validate=False)
    
    # Check that endtoend_id is preserved
    assert f'<EndToEndId>{short_endtoend_id}</EndToEndId>'.encode() in xmlout
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")


def test_endtoend_id_with_special_chars_truncated(sdd):
    """Test that endtoend_id with special characters is truncated correctly"""
    long_endtoend_id = "ABC-123-XYZ-456-DEF-789-GHI-012-JKL-345-MNO"  # More than 35 chars
    expected_endtoend_id = long_endtoend_id[:35]  # First 35 characters
    
    payment = {
        "name": "Test Customer",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1000,
        "type": "FRST",
        "collection_date": datetime.date.today(),
        "mandate_id": "1234",
        "mandate_date": datetime.date.today(),
        "description": "Test transaction",
        "endtoend_id": long_endtoend_id
    }
    
    sdd.add_payment(payment)
    xmlout = sdd.export(validate=False)
    
    # Check that endtoend_id is truncated to 35 characters
    assert f'<EndToEndId>{expected_endtoend_id}</EndToEndId>'.encode() in xmlout
    assert len(expected_endtoend_id) == 35
    
    # Validate against schema
    validate_xml(xmlout, "pain.008.001.02")
