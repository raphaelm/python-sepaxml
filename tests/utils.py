import os
import re

from lxml import etree


def validate_xml(xmlout):
    with open(os.path.join(os.path.dirname(__file__), 'pain.008.001.02.xsd'), 'rb') as schema_file:
        schema_xml = schema_file.read()
    schema_root = etree.XML(schema_xml)
    schema = etree.XMLSchema(schema_root)
    parser = etree.XMLParser(schema=schema)
    xml_root = etree.fromstring(xmlout, parser)
    return etree.tostring(xml_root, pretty_print=True)


def clean_ids(xmlout):
    pat1 = re.compile(b'-[0-9a-f]{12}')
    pat2 = re.compile(b'<MsgId>[^<]*</MsgId>')
    pat3 = re.compile(b'\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d')
    pat4 = re.compile(b'\d\d\d\d-\d\d-\d\d')
    return pat4.sub(b'0000-00-00', pat3.sub(b'0000-00-00T00:00:00', pat2.sub(b'<MsgId></MsgId>', pat1.sub(b'-000000000000', xmlout))))
