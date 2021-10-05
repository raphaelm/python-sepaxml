# encoding: utf-8

import datetime
from unittest import mock

import pytest

from sepaxml import SepaTransfer
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
def freeze_datetime(now):
    _datetime = mock.Mock(
        date=datetime.date,
        datetime=mock.Mock(now=mock.Mock(return_value=now)),
    )
    with mock.patch("sepaxml.transfer.datetime", _datetime), mock.patch(
        "sepaxml.utils.datetime", _datetime
    ):
        yield


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
      <MsgId>20211002081735-9050218037f5</MsgId>
      <CreDtTm>2021-10-02T20:17:35</CreDtTm>
      <NbOfTxs>2</NbOfTxs>
      <CtrlSum>30.60</CtrlSum>
      <InitgPty>
        <Nm>Miller &amp; Son Ltd</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>MillerSonLtd-04cb151eee51</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10.12</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
      </PmtTpInf>
      <ReqdExctnDt>2021-10-02</ReqdExctnDt>
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
    </PmtInf>
    <PmtInf>
      <PmtInfId>MillerSonLtd-323224a9eab8</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>20.48</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
      </PmtTpInf>
      <ReqdExctnDt>2021-10-03</ReqdExctnDt>
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
          <EndToEndId>af755a40cb692551ed9f9d55f7179525</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="EUR">20.48</InstdAmt>
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
          <Ustrd>Test transaction2</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
"""


@pytest.mark.usefixtures("freeze_random", "freeze_datetime")
def test_two_debits(strf, today):
    payment1 = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 1012,
        "execution_date": today,
        "description": "Test transaction1",
        "endtoend_id": "ebd75e7e649375d91b33dc11ae44c0e1",
    }
    payment2 = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 2048,
        "execution_date": today + datetime.timedelta(days=1),
        "description": "Test transaction2",
        "endtoend_id": "af755a40cb692551ed9f9d55f7179525",
    }

    strf.add_payment(payment1)
    strf.add_payment(payment2)
    xmlout = strf.export()
    xmlpretty = validate_xml(xmlout, "pain.001.001.03")
    assert xmlpretty.strip() == SAMPLE_RESULT.strip()
