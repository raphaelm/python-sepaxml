# encoding: utf-8

import datetime
from unittest import mock

import pytest

from sepaxml import SepaDD
from tests.utils import validate_xml


@pytest.fixture
def freeze_random():
    import random

    with mock.patch("sepaxml.utils.random", random.Random(123456)):
        yield


@pytest.fixture
def now():
    return datetime.datetime(2021, 10, 2, 20, 17, 35, tzinfo=datetime.timezone.utc)


@pytest.fixture
def today(now):
    return now.date()


@pytest.fixture
def freeze_time(now):
    import time

    def _strftime(pattern):
        return time.strftime(pattern, now.timetuple())

    _time = mock.Mock(time=time.time, strftime=_strftime)
    with mock.patch("sepaxml.utils.time", _time):
        yield


@pytest.fixture
def freeze_datetime(now):
    _datetime = mock.Mock(
        date=datetime.date,
        datetime=mock.Mock(now=mock.Mock(return_value=now)),
    )
    with mock.patch("sepaxml.debit.datetime", _datetime):
        yield


@pytest.fixture
def sdd():
    return SepaDD({
        "name": "Miller & Son Ltd",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "batch": True,
        "creditor_id": "DE26ZZZ00000000000",
        "currency": "EUR"
    }, schema="pain.008.003.02")


SAMPLE_RESULT = b"""
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.003.02" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CstmrDrctDbtInitn>
    <GrpHdr>
      <MsgId>20211002081735-9050218037f5</MsgId>
      <CreDtTm>2021-10-02T20:17:35</CreDtTm>
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
      <PmtInfId>MillerSonLtd-04cb151eee51</PmtInfId>
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
      <ReqdColltnDt>2021-10-02</ReqdColltnDt>
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
            <DtOfSgntr>2021-10-02</DtOfSgntr>
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
      <PmtInfId>MillerSonLtd-323224a9eab8</PmtInfId>
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
      <ReqdColltnDt>2021-10-02</ReqdColltnDt>
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
            <DtOfSgntr>2021-10-02</DtOfSgntr>
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

@pytest.mark.usefixtures("freeze_random", "freeze_time", "freeze_datetime")
def test_two_debits(sdd, today):
    payment1 = {
        "name": "Test & Co.",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "type": "FRST",
        "collection_date": today,
        "mandate_id": "1234",
        "mandate_date": today,
        "description": "Test transaction1",
        "endtoend_id": "ebd75e7e649375d91b33dc11ae44c0e1"
    }
    payment2 = {
        "name": "Test du Test",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 5000,
        "type": "RCUR",
        "collection_date": today,
        "mandate_id": "1234",
        "mandate_date": today,
        "description": u"Testgrüße <html>",
        "endtoend_id": "af755a40cb692551ed9f9d55f7179525"
    }

    sdd.add_payment(payment1)
    sdd.add_payment(payment2)
    xmlout = sdd.export()
    xmlpretty = validate_xml(xmlout, "pain.008.003.02")
    assert xmlpretty.strip() == SAMPLE_RESULT.strip()
