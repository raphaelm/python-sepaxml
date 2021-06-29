import xml.etree.ElementTree as ET
from collections import OrderedDict

from utils import decimal_str_to_int, int_to_decimal_str, make_msg_id, make_id
from validation import try_valid_xml


class SepaPaymentInitn:

    def __init__(self, config, schema, clean=True):
        """
        Constructor. Checks the config, prepares the document and
        builds the header.
        @param param: The config dict.
        @raise exception: When the config file is invalid.
        """
        self._config = None  # Will contain the config file.
        self._xml = None  # Will contain the final XML file.
        self._batches = OrderedDict()  # Will contain the SEPA batches.
        self._batch_totals = OrderedDict()  # Will contain the total amount to debit per batch for checksum total.
        self.schema = schema
        self.msg_id = make_msg_id()
        self.clean = clean

        config_result = self.check_config(config)
        if config_result:
            self._config = config
            if self.clean:
                from text_unidecode import unidecode

                self._config['name'] = unidecode(self._config['name'])[:70]
                self._config["unique_id"] = make_id(self._config['name'])

        self._prepare_document()
        self._create_header()
        self._PmtInf_Nodes()

    def _prepare_document(self):
        """
        Build the main document node and set xml namespaces.
        """
        self._xml = ET.Element("CBIPaymentRequest")
        self._xml.set("xsi:schemaLocation",
                      "urn:CBI:xsd:CBIPaymentRequest.00.04.00 " + self.schema + ".xsd")
        self._xml.set("xmlns",
                      "urn:CBI:xsd:" + self.schema)
        self._xml.set("xmlns:xsi",
                      "http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace("",
                              "urn:CBI:xsd:" + self.schema)
        ET.register_namespace("xsi",
                              "http://www.w3.org/2001/XMLSchema-instance")
        n1 = ET.Element(self.root_el_g)
        self._xml.append(n1)
        n2 = ET.Element(self.root_el_p)
        self._xml.append(n2)

    def _create_header(self):
        raise NotImplementedError()

    def _PmtInf_Nodes(self):
        raise NotImplementedError()

    def _finalize_batch(self):
        raise NotImplementedError()

    def export(self, validate=True):
        """
        Method to output the xml as string. It will finalize the batches and
        then calculate the checksums (amount sum and transaction count),
        fill these into the group header and output the XML.
        """
        self._finalize_batch()

        ctrl_sum_total = 0
        nb_of_txs_total = 0

        for ctrl_sum in self._xml.iter('InstdAmt'):
            if ctrl_sum.text is None:
                continue
            ctrl_sum_total += decimal_str_to_int(ctrl_sum.text)

        for nb_of_txs in self._xml.iter('CdtTrfTxInf'):
            nb_of_txs_total += 1
            PmtIdNode = nb_of_txs.find('PmtId')
            InstrId_Node = PmtIdNode.find('InstrId')
            InstrId_Node.text = str(nb_of_txs_total)

        GrpHdr_node = self._xml.find('GrpHdr')
        CtrlSum_node = GrpHdr_node.find('CtrlSum')
        NbOfTxs_node = GrpHdr_node.find('NbOfTxs')
        CtrlSum_node.text = int_to_decimal_str(ctrl_sum_total)
        NbOfTxs_node.text = str(nb_of_txs_total)

        # Prepending the XML version is hacky, but cElementTree only offers this
        # automatically if you write to a file, which we don't necessarily want.
        out = b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + ET.tostring(
            self._xml, "utf-8")
        if validate:
            try_valid_xml(out, self.schema)
        return out
