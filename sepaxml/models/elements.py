import collections
import sys
import xml.etree.cElementTree as ET
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal

from drafthorse.utils import validate_xml

from sepaxml.validation import is_valid_xml, ValidationError
from . import NS_UDT
from .container import Container
from .fields import Field


class BaseElementMeta(type):
    @classmethod
    def __prepare__(self, name, bases):
        return collections.OrderedDict()

    def __new__(mcls, name, bases, attrs):
        cls = super(BaseElementMeta, mcls).__new__(mcls, name, bases, attrs)
        fields = list(cls._fields) if hasattr(cls, '_fields') else []
        for attr, obj in attrs.items():
            if isinstance(obj, Field):
                if sys.version_info < (3, 6):
                    obj.__set_name__(cls, attr)
                fields.append(obj)
        cls._fields = fields
        return cls


class Element(metaclass=BaseElementMeta):
    def __init__(self, **kwargs):
        self.required = kwargs.get('required', False)
        self._data = OrderedDict([
            (f.name, f.initialize() if f.default or f.required else None) for f in self._fields
        ])
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _etree_node(self):
        node = ET.Element(self.get_tag())
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'attributes'):
            for k, v in self.Meta.attributes.items():
                node.set(k, v)
        return node

    def to_etree(self):
        node = self._etree_node()
        for k, v in self._data.items():
            if v is not None:
                v.append_to(node)
        return node

    def get_tag(self):
        return "{%s}%s" % (self.Meta.namespace, self.Meta.tag)

    def append_to(self, node):
        el = self.to_etree()
        if self.required or list(el) or el.text:
            node.append(el)

    def serialize(self):
        xml = b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + ET.tostring(self.to_etree(), "utf-8")
        if not is_valid_xml(xml, "camt.052.001.02"):
            raise ValidationError(
                "The output SEPA file contains validation errors. This is likely due to an illegal value in one of "
                "your input fields."
            )
        return xml

    def from_etree(self, root):
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'namespace') and root.tag != "{%s}%s" % (
                self.Meta.namespace, self.Meta.tag):
            raise TypeError("Invalid XML, found tag {} where {} was expected".format(root.tag, "{%s}%s" % (
                self.Meta.namespace, self.Meta.tag)))
        field_index = {}
        for field in self._fields:
            element = getattr(self, field.name)
            field_index[element.get_tag()] = (field.name, element)
        for child in root:
            if child.tag == ET.Comment:
                continue
            if child.tag in field_index:
                name, childel = field_index[child.tag]
                if isinstance(getattr(self, name), Container):
                    getattr(self, name).add_from_etree(child)
                else:
                    getattr(self, name).from_etree(child)
            else:
                raise TypeError("Unknown element {}".format(child.tag))
        return self

    @classmethod
    def parse(cls, xmlinput):
        from lxml import etree
        root = etree.fromstring(xmlinput)
        return cls().from_etree(root)


class StringElement(Element):
    def __init__(self, namespace, tag, text=""):
        super().__init__()
        self.namespace = namespace
        self.tag = tag
        self.text = text

    def __repr__(self):
        return '<{}: {}>'.format(type(self).__name__, str(self))

    def __str__(self):
        return self.text

    def get_tag(self):
        return "{%s}%s" % (self.namespace, self.tag)

    def to_etree(self):
        node = self._etree_node()
        node.text = self.text
        return node

    def from_etree(self, root):
        self.text = root.text
        return self


class DecimalElement(StringElement):
    def __init__(self, namespace, tag, value=None):
        super().__init__(namespace, tag)
        self.value = value

    def to_etree(self):
        node = self._etree_node()
        node.text = str(self.value) if self.value is not None else ""
        return node

    def __str__(self):
        return self.value

    def from_etree(self, root):
        self.value = Decimal(root.text)
        return self


class CurrencyElement(StringElement):
    def __init__(self, namespace, tag, amount="", currency="EUR"):
        super().__init__(namespace, tag)
        self.amount = amount
        self.currency = currency

    def to_etree(self):
        node = self._etree_node()
        node.text = str(self.amount)
        node.attrib["Ccy"] = self.currency
        return node

    def from_etree(self, root):
        self.amount = Decimal(root.text)
        self.currency = root.attrib['Ccy']
        return self

    def __str__(self):
        return "{} {}".format(self.amount, self.currency)


class DateTimeElement(StringElement):
    def __init__(self, namespace, tag, value=None):
        super().__init__(namespace, tag)
        self.value = value
        self.format = format

    def to_etree(self):
        t = self._etree_node()
        if self.value:
            t.text = self.value.strftime("%Y-%m-%dT%H:%M:%S.%f")
        return t

    def from_etree(self, root):
        self.value = datetime.strptime(root.text, '%Y-%m-%dT%H:%M:%S.%f').date()
        return self

    def __str__(self):
        return "{}".format(self.value)
