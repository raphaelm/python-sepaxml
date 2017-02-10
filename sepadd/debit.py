import datetime
import xml.etree.ElementTree as ET
from collections import OrderedDict
from xml.sax.saxutils import escape

from sepadd.utils import (decimal_str_to_int, int_to_decimal_str, make_id,
                          make_msg_id)


class SepaDD(object):
    """
    This class creates a Sepa Direct Debit XML File.
    """

    def __init__(self, config, schema="pain.008.002.02"):
        """
        Constructor. Checks the config, prepares the document and
        builds the header.
        @param param: The config dict.
        @raise exception: When the config file is invalid.
        """
        self._config = None                    # Will contain the config file.
        self._xml = None                       # Will contain the final XML file.
        self._batches = OrderedDict()          # Will contain the SEPA batches.
        self._batch_totals = OrderedDict()     # Will contain the total amount to debit per batch for checksum total.
        self.schema = schema

        config_result = self.check_config(config)
        if config_result:
            self._config = config

        self._prepare_document()
        self._create_header()

    def check_config(self, config):
        """
        Check the config file for required fields and validity.
        @param config: The config dict.
        @return: True if valid, error string if invalid paramaters where
        encountered.
        """
        validation = ""
        required = ["name", "IBAN", "BIC", "batch", "creditor_id", "currency"]

        for config_item in required:
            if config_item not in config:
                validation += config_item.upper() + "_MISSING "

        if not validation:
            return True
        else:
            raise Exception("Config file did not validate. " + validation)

    def check_payment(self, payment):
        """
        Check the config file for required fields and validity.
        @param payment: The payment dict
        @return: True if valid, error string if invalid paramaters where
        encountered.
        """
        validation = ""

        if not isinstance(payment['amount'], int):
            validation += "AMOUNT_NOT_INTEGER "

        if not isinstance(payment['mandate_date'], datetime.date):
            validation += "MANDATE_DATE_INVALID_OR_NOT_DATETIME_INSTANCE"
        payment['mandate_date'] = str(payment['mandate_date'])

        if not isinstance(payment['collection_date'], datetime.date):
            validation += "COLLECTION_DATE_INVALID_OR_NOT_DATETIME_INSTANCE"
        payment['collection_date'] = str(payment['collection_date'])

        if validation == "":
            return True
        else:
            raise Exception('Payment did not validate: ' + validation)

    def add_payment(self, payment):
        """
        Function to add payments
        @param payment: The payment dict
        @raise exception: when payment is invalid
        """
        # Validate the payment
        self.check_payment(payment)

        # Get the CstmrDrctDbtInitnNode
        if not self._config['batch']:
            # Start building the non batch payment
            PmtInf_nodes = self._create_PmtInf_node()
            PmtInf_nodes['PmtInfIdNode'].text = make_id(self._config['name'])
            PmtInf_nodes['PmtMtdNode'].text = "DD"
            PmtInf_nodes['BtchBookgNode'].text = "false"
            PmtInf_nodes['NbOfTxsNode'].text = "1"
            PmtInf_nodes['CtrlSumNode'].text = int_to_decimal_str(
                                               payment['amount'])
            PmtInf_nodes['Cd_SvcLvl_Node'].text = "SEPA"
            PmtInf_nodes['Cd_LclInstrm_Node'].text = "CORE"
            PmtInf_nodes['SeqTpNode'].text = payment['type']
            PmtInf_nodes['ReqdColltnDtNode'].text = payment['collection_date']
            PmtInf_nodes['Nm_Cdtr_Node'].text = escape(self._config['name'])
            PmtInf_nodes['IBAN_CdtrAcct_Node'].text = self._config['IBAN']

            if 'BIC' in self._config:
                PmtInf_nodes['BIC_CdtrAgt_Node'].text = self._config['BIC']

            PmtInf_nodes['ChrgBrNode'].text = "SLEV"
            PmtInf_nodes['Nm_CdtrSchmeId_Node'].text = escape(
                                                       self._config['name'])
            PmtInf_nodes['Id_Othr_Node'].text = self._config['creditor_id']
            PmtInf_nodes['PrtryNode'].text = "SEPA"

        if 'BIC' in payment:
            bic = True
        else:
            bic = False

        TX_nodes = self._create_TX_node(bic)
        TX_nodes['InstdAmtNode'].set("Ccy", self._config['currency'])
        TX_nodes['InstdAmtNode'].text = int_to_decimal_str(payment['amount'])

        TX_nodes['MndtIdNode'].text = payment['mandate_id']
        TX_nodes['DtOfSgntrNode'].text = payment['mandate_date']
        if bic:
            TX_nodes['BIC_DbtrAgt_Node'].text = payment['BIC']

        TX_nodes['Nm_Dbtr_Node'].text = escape(payment['name'])
        TX_nodes['IBAN_DbtrAcct_Node'].text = payment['IBAN']
        TX_nodes['UstrdNode'].text = escape(payment['description'])
        TX_nodes['EndToEndIdNode'].text = make_id(self._config['name'])

        if self._config['batch']:
            self._add_batch(TX_nodes, payment)
        else:
            self._add_non_batch(TX_nodes, PmtInf_nodes)

    def export(self):
        """
        Method to output the xml as string. It will finalize the batches and
        then calculate the checksums (amount sum and transaction count),
        fill these into the group header and output the XML.
        """
        self._finalize_batch()

        ctrl_sum_total = 0
        nb_of_txs_total = 0

        for ctrl_sum in self._xml.iter('CtrlSum'):
            if ctrl_sum.text is None:
                continue
            ctrl_sum_total += decimal_str_to_int(ctrl_sum.text)

        for nb_of_txs in self._xml.iter('NbOfTxs'):
            if nb_of_txs.text is None:
                continue
            nb_of_txs_total += int(nb_of_txs.text)

        CstmrDrctDbtInitn_node = self._xml.find('CstmrDrctDbtInitn')
        GrpHdr_node = CstmrDrctDbtInitn_node.find('GrpHdr')
        CtrlSum_node = GrpHdr_node.find('CtrlSum')
        NbOfTxs_node = GrpHdr_node.find('NbOfTxs')
        CtrlSum_node.text = int_to_decimal_str(ctrl_sum_total)
        NbOfTxs_node.text = str(nb_of_txs_total)

        # Prepending the XML version is hacky, but cElementTree only offers this
        # automatically if you write to a file, which we don't necessarily want.
        return b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + ET.tostring(
               self._xml, "utf-8")

    def _prepare_document(self):
        """
        Build the main document node and set xml namespaces.
        """
        self._xml = ET.Element("Document")
        self._xml.set("xmlns",
                      "urn:iso:std:iso:20022:tech:xsd:" + self.schema)
        self._xml.set("xmlns:xsi",
                      "http://www.w3.org/2001/XMLSchema-intance")
        ET.register_namespace("",
                              "urn:iso:std:iso:20022:tech:xsd:" + self.schema)
        ET.register_namespace("xsi",
                              "http://www.w3.org/2001/XMLSchema-intance")
        CstmrDrctDbtInitn_node = ET.Element("CstmrDrctDbtInitn")
        self._xml.append(CstmrDrctDbtInitn_node)

    def _create_header(self):
        """
        Function to create the GroupHeader (GrpHdr) in the
        CstmrDrctDbtInit Node
        """
        # Retrieve the node to which we will append the group header.
        CstmrDrctDbtInitn_node = self._xml.find('CstmrDrctDbtInitn')

        # Create the header nodes.
        GrpHdr_node = ET.Element("GrpHdr")
        MsgId_node = ET.Element("MsgId")
        CreDtTm_node = ET.Element("CreDtTm")
        NbOfTxs_node = ET.Element("NbOfTxs")
        CtrlSum_node = ET.Element("CtrlSum")
        InitgPty_node = ET.Element("InitgPty")
        Nm_node = ET.Element("Nm")

        # Add data to some header nodes.
        MsgId_node.text = make_msg_id()
        CreDtTm_node.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        Nm_node.text = self._config['name']

        # Append the nodes
        InitgPty_node.append(Nm_node)
        GrpHdr_node.append(MsgId_node)
        GrpHdr_node.append(CreDtTm_node)
        GrpHdr_node.append(NbOfTxs_node)
        GrpHdr_node.append(CtrlSum_node)
        GrpHdr_node.append(InitgPty_node)

        # Append the header to its parent
        CstmrDrctDbtInitn_node.append(GrpHdr_node)

    def _create_PmtInf_node(self):
        """
        Method to create the blank payment information nodes as a dict.
        """
        ED = dict()  # ED is element dict
        ED['PmtInfNode'] = ET.Element("PmtInf")
        ED['PmtInfIdNode'] = ET.Element("PmtInfId")
        ED['PmtMtdNode'] = ET.Element("PmtMtd")
        ED['BtchBookgNode'] = ET.Element("BtchBookg")
        ED['NbOfTxsNode'] = ET.Element("NbOfTxs")
        ED['CtrlSumNode'] = ET.Element("CtrlSum")
        ED['PmtTpInfNode'] = ET.Element("PmtTpInf")
        ED['SvcLvlNode'] = ET.Element("SvcLvl")
        ED['Cd_SvcLvl_Node'] = ET.Element("Cd")
        ED['LclInstrmNode'] = ET.Element("LclInstrm")
        ED['Cd_LclInstrm_Node'] = ET.Element("Cd")
        ED['SeqTpNode'] = ET.Element("SeqTp")
        ED['ReqdColltnDtNode'] = ET.Element("ReqdColltnDt")
        ED['CdtrNode'] = ET.Element("Cdtr")
        ED['Nm_Cdtr_Node'] = ET.Element("Nm")
        ED['CdtrAcctNode'] = ET.Element("CdtrAcct")
        ED['Id_CdtrAcct_Node'] = ET.Element("Id")
        ED['IBAN_CdtrAcct_Node'] = ET.Element("IBAN")
        ED['CdtrAgtNode'] = ET.Element("CdtrAgt")
        ED['FinInstnId_CdtrAgt_Node'] = ET.Element("FinInstnId")
        if 'BIC' in self._config:
            ED['BIC_CdtrAgt_Node'] = ET.Element("BIC")
        ED['ChrgBrNode'] = ET.Element("ChrgBr")
        ED['CdtrSchmeIdNode'] = ET.Element("CdtrSchmeId")
        ED['Nm_CdtrSchmeId_Node'] = ET.Element("Nm")
        ED['Id_CdtrSchmeId_Node'] = ET.Element("Id")
        ED['PrvtIdNode'] = ET.Element("PrvtId")
        ED['OthrNode'] = ET.Element("Othr")
        ED['Id_Othr_Node'] = ET.Element("Id")
        ED['SchmeNmNode'] = ET.Element("SchmeNm")
        ED['PrtryNode'] = ET.Element("Prtry")
        return ED

    def _create_TX_node(self, bic=True):
        """
        Method to create the blank transaction nodes as a dict. If bic is True,
        the BIC node will also be created.
        """
        ED = dict()
        ED['DrctDbtTxInfNode'] = ET.Element("DrctDbtTxInf")
        ED['PmtIdNode'] = ET.Element("PmtId")
        ED['EndToEndIdNode'] = ET.Element("EndToEndId")
        ED['InstdAmtNode'] = ET.Element("InstdAmt")
        ED['DrctDbtTxNode'] = ET.Element("DrctDbtTx")
        ED['MndtRltdInfNode'] = ET.Element("MndtRltdInf")
        ED['MndtIdNode'] = ET.Element("MndtId")
        ED['DtOfSgntrNode'] = ET.Element("DtOfSgntr")
        ED['DbtrAgtNode'] = ET.Element("DbtrAgt")
        ED['FinInstnId_DbtrAgt_Node'] = ET.Element("FinInstnId")
        if bic:
            ED['BIC_DbtrAgt_Node'] = ET.Element("BIC")
        ED['DbtrNode'] = ET.Element("Dbtr")
        ED['Nm_Dbtr_Node'] = ET.Element("Nm")
        ED['DbtrAcctNode'] = ET.Element("DbtrAcct")
        ED['Id_DbtrAcct_Node'] = ET.Element("Id")
        ED['IBAN_DbtrAcct_Node'] = ET.Element("IBAN")
        ED['RmtInfNode'] = ET.Element("RmtInf")
        ED['UstrdNode'] = ET.Element("Ustrd")
        return ED

    def _add_non_batch(self, TX_nodes, PmtInf_nodes):
        """
        Method to add a transaction as non batch, will fold the transaction
        together with the payment info node and append to the main xml.
        """
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['PmtInfIdNode'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['PmtMtdNode'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['BtchBookgNode'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['NbOfTxsNode'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CtrlSumNode'])

        PmtInf_nodes['SvcLvlNode'].append(PmtInf_nodes['Cd_SvcLvl_Node'])
        PmtInf_nodes['LclInstrmNode'].append(PmtInf_nodes['Cd_LclInstrm_Node'])
        PmtInf_nodes['PmtTpInfNode'].append(PmtInf_nodes['SvcLvlNode'])
        PmtInf_nodes['PmtTpInfNode'].append(PmtInf_nodes['LclInstrmNode'])
        PmtInf_nodes['PmtTpInfNode'].append(PmtInf_nodes['SeqTpNode'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['PmtTpInfNode'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['ReqdColltnDtNode'])

        PmtInf_nodes['CdtrNode'].append(PmtInf_nodes['Nm_Cdtr_Node'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CdtrNode'])

        PmtInf_nodes['Id_CdtrAcct_Node'].append(
                                         PmtInf_nodes['IBAN_CdtrAcct_Node'])
        PmtInf_nodes['CdtrAcctNode'].append(PmtInf_nodes['Id_CdtrAcct_Node'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CdtrAcctNode'])

        if 'BIC' in self._config:
            PmtInf_nodes['FinInstnId_CdtrAgt_Node'].append(
                        PmtInf_nodes['BIC_CdtrAgt_Node'])
        PmtInf_nodes['CdtrAgtNode'].append(
                                    PmtInf_nodes['FinInstnId_CdtrAgt_Node'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CdtrAgtNode'])

        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['ChrgBrNode'])

        if self.schema == 'pain.008.001.02':
            PmtInf_nodes['CdtrSchmeIdNode'].append(PmtInf_nodes['Nm_CdtrSchmeId_Node'])
        PmtInf_nodes['OthrNode'].append(PmtInf_nodes['Id_Othr_Node'])
        PmtInf_nodes['SchmeNmNode'].append(PmtInf_nodes['PrtryNode'])
        PmtInf_nodes['OthrNode'].append(PmtInf_nodes['SchmeNmNode'])
        PmtInf_nodes['PrvtIdNode'].append(PmtInf_nodes['OthrNode'])
        PmtInf_nodes['Id_CdtrSchmeId_Node'].append(PmtInf_nodes['PrvtIdNode'])
        PmtInf_nodes['CdtrSchmeIdNode'].append(
                                        PmtInf_nodes['Id_CdtrSchmeId_Node'])
        PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CdtrSchmeIdNode'])

        TX_nodes['PmtIdNode'].append(TX_nodes['EndToEndIdNode'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['PmtIdNode'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['InstdAmtNode'])

        TX_nodes['MndtRltdInfNode'].append(TX_nodes['MndtIdNode'])
        TX_nodes['MndtRltdInfNode'].append(TX_nodes['DtOfSgntrNode'])
        TX_nodes['DrctDbtTxNode'].append(TX_nodes['MndtRltdInfNode'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['DrctDbtTxNode'])

        if TX_nodes['BIC_DbtrAgt_Node'].text is not None:
            TX_nodes['FinInstnId_DbtrAgt_Node'].append(
                                                TX_nodes['BIC_DbtrAgt_Node'])
        TX_nodes['DbtrAgtNode'].append(TX_nodes['FinInstnId_DbtrAgt_Node'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['DbtrAgtNode'])

        TX_nodes['DbtrNode'].append(TX_nodes['Nm_Dbtr_Node'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['DbtrNode'])

        TX_nodes['Id_DbtrAcct_Node'].append(TX_nodes['IBAN_DbtrAcct_Node'])
        TX_nodes['DbtrAcctNode'].append(TX_nodes['Id_DbtrAcct_Node'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['DbtrAcctNode'])

        TX_nodes['RmtInfNode'].append(TX_nodes['UstrdNode'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['RmtInfNode'])
        PmtInf_nodes['PmtInfNode'].append(TX_nodes['DrctDbtTxInfNode'])
        CstmrDrctDbtInitn_node = self._xml.find('CstmrDrctDbtInitn')
        CstmrDrctDbtInitn_node.append(PmtInf_nodes['PmtInfNode'])

    def _add_batch(self, TX_nodes, payment):
        """
        Method to add a payment as a batch. The transaction details are already
        present. Will fold the nodes accordingly and the call the
        _add_to_batch_list function to store the batch.
        """
        TX_nodes['PmtIdNode'].append(TX_nodes['EndToEndIdNode'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['PmtIdNode'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['InstdAmtNode'])

        TX_nodes['MndtRltdInfNode'].append(TX_nodes['MndtIdNode'])
        TX_nodes['MndtRltdInfNode'].append(TX_nodes['DtOfSgntrNode'])
        TX_nodes['DrctDbtTxNode'].append(TX_nodes['MndtRltdInfNode'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['DrctDbtTxNode'])

        if TX_nodes['BIC_DbtrAgt_Node'].text is not None:
            TX_nodes['FinInstnId_DbtrAgt_Node'].append(
                                                TX_nodes['BIC_DbtrAgt_Node'])
        TX_nodes['DbtrAgtNode'].append(TX_nodes['FinInstnId_DbtrAgt_Node'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['DbtrAgtNode'])

        TX_nodes['DbtrNode'].append(TX_nodes['Nm_Dbtr_Node'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['DbtrNode'])

        TX_nodes['Id_DbtrAcct_Node'].append(TX_nodes['IBAN_DbtrAcct_Node'])
        TX_nodes['DbtrAcctNode'].append(TX_nodes['Id_DbtrAcct_Node'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['DbtrAcctNode'])

        TX_nodes['RmtInfNode'].append(TX_nodes['UstrdNode'])
        TX_nodes['DrctDbtTxInfNode'].append(TX_nodes['RmtInfNode'])
        self._add_to_batch_list(TX_nodes, payment)

    def _add_to_batch_list(self, TX, payment):
        """
        Method to add a transaction to the batch list. The correct batch will
        be determined by the payment dict and the batch will be created if
        not existant. This will also add the payment amount to the respective
        batch total.
        """
        batch_key = payment['type'] + "::" + payment['collection_date']
        if batch_key in self._batches.keys():
            self._batches[batch_key].append(TX['DrctDbtTxInfNode'])
        else:
            self._batches[batch_key] = []
            self._batches[batch_key].append(TX['DrctDbtTxInfNode'])

        if batch_key in self._batch_totals:
            self._batch_totals[batch_key] += payment['amount']
        else:
            self._batch_totals[batch_key] = payment['amount']

    def _finalize_batch(self):
        """
        Method to finalize the batch, this will iterate over the _batches dict
        and create a PmtInf node for each batch. The correct information (from
        the batch_key and batch_totals) will be inserted and the batch
        transaction nodes will be folded. Finally, the batches will be added to
        the main XML.
        """
        for batch_meta, batch_nodes in self._batches.items():
            batch_meta_split = batch_meta.split("::")
            PmtInf_nodes = self._create_PmtInf_node()
            PmtInf_nodes['PmtInfIdNode'].text = make_id(self._config['name'])
            PmtInf_nodes['PmtMtdNode'].text = "DD"
            PmtInf_nodes['BtchBookgNode'].text = "true"
            PmtInf_nodes['Cd_SvcLvl_Node'].text = "SEPA"
            PmtInf_nodes['Cd_LclInstrm_Node'].text = "CORE"
            PmtInf_nodes['SeqTpNode'].text = batch_meta_split[0]
            PmtInf_nodes['ReqdColltnDtNode'].text = batch_meta_split[1]
            PmtInf_nodes['Nm_Cdtr_Node'].text = escape(self._config['name'])
            PmtInf_nodes['IBAN_CdtrAcct_Node'].text = self._config['IBAN']

            if 'BIC' in self._config:
                PmtInf_nodes['BIC_CdtrAgt_Node'].text = self._config['BIC']

            PmtInf_nodes['ChrgBrNode'].text = "SLEV"
            PmtInf_nodes['Nm_CdtrSchmeId_Node'].text = escape(self._config['name'])
            PmtInf_nodes['Id_Othr_Node'].text = self._config['creditor_id']
            PmtInf_nodes['PrtryNode'].text = "SEPA"

            PmtInf_nodes['NbOfTxsNode'].text = str(len(batch_nodes))
            PmtInf_nodes['CtrlSumNode'].text = int_to_decimal_str(self._batch_totals[batch_meta])

            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['PmtInfIdNode'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['PmtMtdNode'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['BtchBookgNode'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['NbOfTxsNode'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CtrlSumNode'])

            PmtInf_nodes['SvcLvlNode'].append(PmtInf_nodes['Cd_SvcLvl_Node'])
            PmtInf_nodes['LclInstrmNode'].append(
                                          PmtInf_nodes['Cd_LclInstrm_Node'])
            PmtInf_nodes['PmtTpInfNode'].append(PmtInf_nodes['SvcLvlNode'])
            PmtInf_nodes['PmtTpInfNode'].append(PmtInf_nodes['LclInstrmNode'])
            PmtInf_nodes['PmtTpInfNode'].append(PmtInf_nodes['SeqTpNode'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['PmtTpInfNode'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['ReqdColltnDtNode'])

            PmtInf_nodes['CdtrNode'].append(PmtInf_nodes['Nm_Cdtr_Node'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CdtrNode'])

            PmtInf_nodes['Id_CdtrAcct_Node'].append(
                                            PmtInf_nodes['IBAN_CdtrAcct_Node'])
            PmtInf_nodes['CdtrAcctNode'].append(
                                         PmtInf_nodes['Id_CdtrAcct_Node'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CdtrAcctNode'])

            if 'BIC' in self._config:
                PmtInf_nodes['FinInstnId_CdtrAgt_Node'].append(
                                            PmtInf_nodes['BIC_CdtrAgt_Node'])
            PmtInf_nodes['CdtrAgtNode'].append(
                                       PmtInf_nodes['FinInstnId_CdtrAgt_Node'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CdtrAgtNode'])

            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['ChrgBrNode'])

            if self.schema == 'pain.008.001.02':
                PmtInf_nodes['CdtrSchmeIdNode'].append(PmtInf_nodes['Nm_CdtrSchmeId_Node'])
            PmtInf_nodes['OthrNode'].append(PmtInf_nodes['Id_Othr_Node'])
            PmtInf_nodes['SchmeNmNode'].append(PmtInf_nodes['PrtryNode'])
            PmtInf_nodes['OthrNode'].append(PmtInf_nodes['SchmeNmNode'])
            PmtInf_nodes['PrvtIdNode'].append(PmtInf_nodes['OthrNode'])
            PmtInf_nodes['Id_CdtrSchmeId_Node'].append(
                                                PmtInf_nodes['PrvtIdNode'])
            PmtInf_nodes['CdtrSchmeIdNode'].append(
                                           PmtInf_nodes['Id_CdtrSchmeId_Node'])
            PmtInf_nodes['PmtInfNode'].append(PmtInf_nodes['CdtrSchmeIdNode'])

            for txnode in batch_nodes:
                PmtInf_nodes['PmtInfNode'].append(txnode)

            CstmrDrctDbtInitn_node = self._xml.find('CstmrDrctDbtInitn')
            CstmrDrctDbtInitn_node.append(PmtInf_nodes['PmtInfNode'])
