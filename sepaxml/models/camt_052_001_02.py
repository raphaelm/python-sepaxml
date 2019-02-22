import xml.etree.cElementTree as ET

from .elements import Element
from .fields import (
    DateTimeField, Field, StringField, DecimalField
)

NS = "urn:iso:std:iso:20022:tech:xsd:camt.052.001.02"


class MsgPgntn(Element):
    page_number = DecimalField(NS, "PgNb")  # TODO: should be integer
    LastPgInd = StringField(NS, "LastPgInd")  # TODO: should be bool

    class Meta:
        namespace = NS
        tag = "GrpHdr"


class Othr(Element):
    id = StringField(NS, "Id")
    issuer = StringField(NS, "Issr")

    class Meta:
        namespace = NS
        tag = "Othr"


class OrgId(Element):
    other = Field(Othr, required=True)

    class Meta:
        namespace = NS
        tag = "OrgId"


class Id(Element):
    orgid = Field(OrgId, required=True)

    class Meta:
        namespace = NS
        tag = "Id"


class MsgRcpt(Element):
    id = Field(Id, required=True)

    class Meta:
        namespace = NS
        tag = "MsgRcpt"


class GrpHdr(Element):
    message_id = StringField(NS, "MsgId")
    creation_datetime = DateTimeField(NS, "CreDtTm")
    recipient = Field(MsgPgntn, required=False)
    pagination = Field(MsgPgntn, required=False)
    complete = DateTimeField(NS, "CompleteDateTime")

    class Meta:
        namespace = NS
        tag = "GrpHdr"


class Account(Element):
    

class Rpt(Element):
    id = StringField(NS, "Id", required=True)
    legal_sequence_number = StringField(NS, "LglSeqNb", required=False)
    creation_datetime = DateTimeField(NS, "CreDtTm")
    account = Field(Account, required=True)

    class Meta:
        namespace = NS
        tag = "Rpt"

class BkToCstmrAcctRprt(Element):
    header = Field(GrpHdr, required=True)
    report = Field(Rpt, required=True)

    class Meta:
        namespace = NS
        tag = "BkToCstmrAcctRpt"


class Document(Element):
    report = Field(BkToCstmrAcctRprt, required=True)

    def __init__(self):
        super().__init__()
        ET.register_namespace("xmlns", NS)

    class Meta:
        namespace = NS
        tag = "Document"
