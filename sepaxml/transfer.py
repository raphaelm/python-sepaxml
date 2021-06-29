import datetime
import xml.etree.ElementTree as ET

from shared import SepaPaymentInitn
from utils import int_to_decimal_str


class SepaTransfer(SepaPaymentInitn):
    """
    This class creates a Sepa transfer XML File.
    """
    root_el_g = "GrpHdr"
    root_el_p = "PmtInf"

    def __init__(self, config, schema="CBIPaymentRequest.00.04.00", clean=True):
        super().__init__(config, schema, clean)

    def check_config(self, config):
        """
        Check the config file for required fields and validity.
        @param config: The config dict.
        @return: True if valid, error string if invalid paramaters where
        encountered.
        """
        validation = ""
        required = ["name", "currency", "IBAN"]

        if 'execution_date' in config:
            if not isinstance(config['execution_date'], datetime.date):
                validation += "EXECUTION_DATE_INVALID_OR_NOT_DATETIME_INSTANCE"
            config['execution_date'] = config['execution_date'].isoformat()

        for config_item in required:
            if config_item not in config:
                validation += config_item.upper() + "_MISSING "

        if not validation:
            return True
        else:
            raise Exception("Config file did not validate. " + validation)

    def check_payment(self, payment):
        """
        Check the payment for required fields and validity.
        @param payment: The payment dict
        @return: True if valid, error string if invalid paramaters where
        encountered.
        """
        validation = ""
        required = ["name", "IBAN", "amount", "execution_date"]

        for config_item in required:
            if config_item not in payment:
                validation += config_item.upper() + "_MISSING "

        # if (("description" in payment) or ("document" in payment)):
        #     validation += "DESCRIPTION_OR_DOCUMENT_REQUIRED"

        if not isinstance(payment['amount'], int):
            validation += "AMOUNT_NOT_INTEGER "

        if 'document' in payment:
            for invoices in payment["document"]:
                if 'invoice_date' in invoices:
                    if not isinstance(invoices["invoice_date"], datetime.date):
                        validation += "INVOICE_DATE_INVALID_OR_NOT_DATETIME_INSTANCE"
                    invoices["invoice_date"] = invoices["invoice_date"].isoformat()

        if 'execution_date' in payment:
            if not isinstance(payment['execution_date'], datetime.date):
                validation += "EXECUTION_DATE_INVALID_OR_NOT_DATETIME_INSTANCE"
            payment['execution_date'] = payment['execution_date'].isoformat()

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

        if self.clean:
            from text_unidecode import unidecode

            payment['name'] = unidecode(payment['name'])[:70]
            if ("description" in payment):
                payment['description'] = unidecode(payment['description'])[:140]

        if 'BIC' in self._config:
            CdtTrfTxInf_nodes = self._create_CdtTrfTxInf_node(payment)
            CdtTrfTxInf_nodes['BIC_CdtrAgt_Node'].text = self._config['BIC']
        else:
            CdtTrfTxInf_nodes = self._create_CdtTrfTxInf_node(payment, bic = False)

        CdtTrfTxInf_nodes['Nm_Cdtr_Node'].text = self._config['name']
        CdtTrfTxInf_nodes['InstdAmtNode'].set("Ccy", self._config['currency'])
        CdtTrfTxInf_nodes['InstdAmtNode'].text = int_to_decimal_str(payment['amount'])
        CdtTrfTxInf_nodes['Cd_CtgyPurp'].text = "SUPP"
        CdtTrfTxInf_nodes['IBAN_CdtrAcct_Node'].text = self._config['IBAN']
        CdtTrfTxInf_nodes['EndToEnd_PmtId_Node'].text = payment.get('endtoend_id', 'NOTPROVIDED')

        if ("description" in payment):
            CdtTrfTxInf_nodes['UstrdNode'].text = payment['description']

        if self._config['batch']:
            self._add_batch(CdtTrfTxInf_nodes, payment)
        else:
            CdtTrfTxInf_nodes['InstrId_Node'].text = "1"
            self._add_non_batch(CdtTrfTxInf_nodes)

    def _create_header(self):
        """
        Function to create the GroupHeader (GrpHdr) and PmtInf
        """
        # Create the header nodes.
        MsgId_node = ET.Element("MsgId")
        CreDtTm_node = ET.Element("CreDtTm")
        NbOfTxs_node = ET.Element("NbOfTxs")
        CtrlSum_node = ET.Element("CtrlSum")
        InitgPty_node = ET.Element("InitgPty")
        Nm_node = ET.Element("Nm")
        Id_Othr_node = ET.Element("Id")
        Id_InitgPty_node = ET.Element("Id")
        Issr_node = ET.Element("Issr")
        Othr_node = ET.Element("Othr")
        OrgId_node = ET.Element("OrgId")

        # Add data to some header nodes.
        MsgId_node.text = self._config['unique_id']
        CreDtTm_node.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        Nm_node.text = self._config['name']
        Id_Othr_node.text = self._config['Organisation_id']
        Issr_node.text = 'CBI'

        # Append the nodes
        InitgPty_node.append(Nm_node)
        Othr_node.append(Id_Othr_node)
        Othr_node.append(Issr_node)
        OrgId_node.append(Othr_node)
        Id_InitgPty_node.append(OrgId_node)
        InitgPty_node.append(Id_InitgPty_node)
        GrpHdr_node = self._xml.find('GrpHdr')
        GrpHdr_node.append(MsgId_node)
        GrpHdr_node.append(CreDtTm_node)
        GrpHdr_node.append(NbOfTxs_node)
        GrpHdr_node.append(CtrlSum_node)
        GrpHdr_node.append(InitgPty_node)

    def _PmtInf_Nodes(self):
        # creating pmtinf nodes

        PmtInfIdNode = ET.Element("PmtInfId")
        PmtMtdNode = ET.Element("PmtMtd")
        BtchBookgNode = ET.Element("BtchBookg")
        NbOfTxsNode = ET.Element("NbOfTxs")
        PmtTpInfNode = ET.Element("PmtTpInf")
        if not self._config.get('domestic', False):
            SvcLvlNode = ET.Element("SvcLvl")
            Cd_SvcLvl_Node = ET.Element("Cd")
        ReqdExctnDtNode = ET.Element("ReqdExctnDt")

        DbtrNode = ET.Element("Dbtr")
        Nm_Dbtr_Node = ET.Element("Nm")
        DbtrAcctNode = ET.Element("DbtrAcct")
        Id_DbtrAcct_Node = ET.Element("Id")
        IBAN_DbtrAcct_Node = ET.Element("IBAN")
        DbtrAgtNode = ET.Element("DbtrAgt")
        FinInstnId_DbtrAgt_Node = ET.Element("FinInstnId")
        ClrSysMmbId_Node = ET.Element("ClrSysMmbId")
        MmbId_Node = ET.Element("MmbId")
        if 'BIC' in self._config:
            BIC_DbtrAgt_Node = ET.Element("BIC")
        ChrgBrNode = ET.Element("ChrgBr")

        PmtInfIdNode.text = self._config['unique_id']
        PmtMtdNode.text = "TRA"
        if not self._config.get('domestic', False):
            Cd_SvcLvl_Node.text = "SEPA"
        ReqdExctnDtNode.text = self._config['execution_date']

        Nm_Dbtr_Node.text = self._config['name']
        IBAN_DbtrAcct_Node.text = self._config['IBAN']
        if 'BIC' in self._config:
            BIC_DbtrAgt_Node.text = self._config['BIC']

        ChrgBrNode.text = "SLEV"
        MmbId_Node.text = self._config['bank code']
        if self._config['batch']:
            BtchBookgNode.text = "true"
        else:
            BtchBookgNode.text = "false"


        PmtInfnode = self._xml.find('PmtInf')
        PmtInfnode.append(PmtInfIdNode)
        PmtInfnode.append(PmtMtdNode)
        PmtInfnode.append(BtchBookgNode)

        if not self._config.get('domestic', False):
            SvcLvlNode.append(Cd_SvcLvl_Node)
            PmtTpInfNode.append(SvcLvlNode)
            PmtInfnode.append(PmtTpInfNode)
        PmtInfnode.append(ReqdExctnDtNode)

        DbtrNode.append(Nm_Dbtr_Node)
        PmtInfnode.append(DbtrNode)

        Id_DbtrAcct_Node.append(IBAN_DbtrAcct_Node)
        DbtrAcctNode.append(Id_DbtrAcct_Node)
        PmtInfnode.append(DbtrAcctNode)

        if 'BIC' in self._config:
            FinInstnId_DbtrAgt_Node.append(BIC_DbtrAgt_Node)
        ClrSysMmbId_Node.append(MmbId_Node)
        FinInstnId_DbtrAgt_Node.append(ClrSysMmbId_Node)
        DbtrAgtNode.append(FinInstnId_DbtrAgt_Node)
        PmtInfnode.append(DbtrAgtNode)

        PmtInfnode.append(ChrgBrNode)

    def _create_CdtTrfTxInf_node(self, payment, bic=True):
        """
        Method to create the blank transaction nodes as a dict. If bic is True,
        the BIC node will also be created.
        """
        ED = dict()
        ED['CdtTrfTxInfNode'] = ET.Element("CdtTrfTxInf")
        ED['PmtIdNode'] = ET.Element("PmtId")
        ED['PmtTpInfNode'] = ET.Element("PmtTpInf")
        ED['CtgyPurpNode'] = ET.Element("CtgyPurp")
        ED['Cd_CtgyPurp'] = ET.Element("Cd")
        ED['EndToEnd_PmtId_Node'] = ET.Element("EndToEndId")
        ED['InstrId_Node'] = ET.Element("InstrId")
        ED['AmtNode'] = ET.Element("Amt")
        ED['InstdAmtNode'] = ET.Element("InstdAmt")
        ED['CdtrNode'] = ET.Element("Cdtr")
        ED['Nm_Cdtr_Node'] = ET.Element("Nm")

        ED['CdtrAgtNode'] = ET.Element("CdtrAgt")
        ED['FinInstnId_CdtrAgt_Node'] = ET.Element("FinInstnId")
        if bic:
            ED['BIC_CdtrAgt_Node'] = ET.Element("BIC")
        ED['CdtrAcctNode'] = ET.Element("CdtrAcct")
        ED['Id_CdtrAcct_Node'] = ET.Element("Id")
        ED['IBAN_CdtrAcct_Node'] = ET.Element("IBAN")
        ED['RmtInfNode'] = ET.Element("RmtInf")
        if ("description" in payment):
            ED['UstrdNode'] = ET.Element("Ustrd")
        return ED

    def _add_non_batch(self, CdtTrfTxInf_nodes):
        """
        Method to add a transaction as non batch, will fold the transaction
        together with the payment info node and append to the main xml.
        """

        CdtTrfTxInf_nodes['PmtIdNode'].append(CdtTrfTxInf_nodes['InstrId_Node'])
        CdtTrfTxInf_nodes['PmtIdNode'].append(CdtTrfTxInf_nodes['EndToEnd_PmtId_Node'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['PmtIdNode'])
        CdtTrfTxInf_nodes['CtgyPurpNode'].append(CdtTrfTxInf_nodes['Cd_CtgyPurp'])
        CdtTrfTxInf_nodes['PmtTpInfNode'].append(CdtTrfTxInf_nodes['CtgyPurpNode'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['PmtTpInfNode'])
        CdtTrfTxInf_nodes['AmtNode'].append(CdtTrfTxInf_nodes['InstdAmtNode'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['AmtNode'])

        if 'BIC_CdtrAgt_Node' in CdtTrfTxInf_nodes and CdtTrfTxInf_nodes['BIC_CdtrAgt_Node'].text is not None:
            CdtTrfTxInf_nodes['FinInstnId_CdtrAgt_Node'].append(
                CdtTrfTxInf_nodes['BIC_CdtrAgt_Node'])
            CdtTrfTxInf_nodes['CdtrAgtNode'].append(CdtTrfTxInf_nodes['FinInstnId_CdtrAgt_Node'])
            CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['CdtrAgtNode'])

        CdtTrfTxInf_nodes['CdtrNode'].append(CdtTrfTxInf_nodes['Nm_Cdtr_Node'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['CdtrNode'])

        CdtTrfTxInf_nodes['Id_CdtrAcct_Node'].append(CdtTrfTxInf_nodes['IBAN_CdtrAcct_Node'])
        CdtTrfTxInf_nodes['CdtrAcctNode'].append(CdtTrfTxInf_nodes['Id_CdtrAcct_Node'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['CdtrAcctNode'])

        if('UstrdNode' in CdtTrfTxInf_nodes):
            CdtTrfTxInf_nodes['RmtInfNode'].append(CdtTrfTxInf_nodes['UstrdNode'])
            CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['RmtInfNode'])
        else:
            for x in self.strd_data(payment):
                CdtTrfTxInf_nodes['RmtInfNode'].append(x['StrdNode'])
            CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['RmtInfNode'])
        PmtInfnode = self._xml.find('PmtInf')
        PmtInfnode.append(CdtTrfTxInf_nodes['CdtTrfTxInfNode'])

    def _add_batch(self, CdtTrfTxInf_nodes, payment):
        """
        Method to add a payment as a batch. The transaction details are already
        present. Will fold the nodes accordingly and the call the
        _add_to_batch_list function to store the batch.
        """
        CdtTrfTxInf_nodes['PmtIdNode'].append(CdtTrfTxInf_nodes['InstrId_Node'])
        CdtTrfTxInf_nodes['PmtIdNode'].append(CdtTrfTxInf_nodes['EndToEnd_PmtId_Node'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['PmtIdNode'])
        CdtTrfTxInf_nodes['CtgyPurpNode'].append(CdtTrfTxInf_nodes['Cd_CtgyPurp'])
        CdtTrfTxInf_nodes['PmtTpInfNode'].append(CdtTrfTxInf_nodes['CtgyPurpNode'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['PmtTpInfNode'])
        CdtTrfTxInf_nodes['AmtNode'].append(CdtTrfTxInf_nodes['InstdAmtNode'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['AmtNode'])

        if 'BIC_CdtrAgt_Node' in CdtTrfTxInf_nodes and CdtTrfTxInf_nodes['BIC_CdtrAgt_Node'].text is not None:
            CdtTrfTxInf_nodes['FinInstnId_CdtrAgt_Node'].append(
                CdtTrfTxInf_nodes['BIC_CdtrAgt_Node'])
            CdtTrfTxInf_nodes['CdtrAgtNode'].append(CdtTrfTxInf_nodes['FinInstnId_CdtrAgt_Node'])
            CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['CdtrAgtNode'])

        CdtTrfTxInf_nodes['CdtrNode'].append(CdtTrfTxInf_nodes['Nm_Cdtr_Node'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['CdtrNode'])

        CdtTrfTxInf_nodes['Id_CdtrAcct_Node'].append(CdtTrfTxInf_nodes['IBAN_CdtrAcct_Node'])
        CdtTrfTxInf_nodes['CdtrAcctNode'].append(CdtTrfTxInf_nodes['Id_CdtrAcct_Node'])
        CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['CdtrAcctNode'])

        if('UstrdNode' in CdtTrfTxInf_nodes):
            CdtTrfTxInf_nodes['RmtInfNode'].append(CdtTrfTxInf_nodes['UstrdNode'])
            CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['RmtInfNode'])
        else:
            for x in self.strd_data(payment):
                CdtTrfTxInf_nodes['RmtInfNode'].append(x['StrdNode'])
            CdtTrfTxInf_nodes['CdtTrfTxInfNode'].append(CdtTrfTxInf_nodes['RmtInfNode'])
        self._add_to_batch_list(CdtTrfTxInf_nodes, payment)

    def _add_to_batch_list(self, CdtTrfTxInf_nodes, payment):
        """
        Method to add a transaction to the batch list. The correct batch will
        be determined by the payment dict and the batch will be created if
        not existant. This will also add the payment amount to the respective
        batch total.
        """
        batch_key = payment.get('execution_date', None)
        if batch_key in self._batches.keys():
            self._batches[batch_key].append(CdtTrfTxInf_nodes['CdtTrfTxInfNode'])
        else:
            self._batches[batch_key] = []
            self._batches[batch_key].append(CdtTrfTxInf_nodes['CdtTrfTxInfNode'])

        if batch_key in self._batch_totals:
            self._batch_totals[batch_key] += payment['amount']
        else:
            self._batch_totals[batch_key] = payment['amount']

    def _finalize_batch(self):
        """
        Method to finalize the batch, this will iterate over the _batches dict
        and create a CdtTrfTxInf_nodes for each batch. The correct information (from
        the batch_key and batch_totals) will be inserted and the batch
        transaction nodes will be folded. Finally, the batches will be added to
        the main XML.
        """
        for batch_meta, batch_nodes in self._batches.items():
            for x in batch_nodes:
                PmtInfNode = self._xml.find('PmtInf')
                PmtInfNode.append(x)

    def _create_strd_nodes(self):

        ED = dict()
        ED['Nb_Node'] = ET.Element('Nb')
        ED['Cd_Node'] = ET.Element('Cd')
        ED['CdtNoteAmt_Node'] = ET.Element('CdtNoteAmt')
        ED['RltdDt_Node'] = ET.Element('RltdDt')
        ED['StrdNode'] = ET.Element("Strd")
        ED['CdOrPrtryNode'] = ET.Element("CdOrPrtry")
        ED['TpNode'] = ET.Element("Tp")
        ED['RfrdDocInfNode'] = ET.Element("RfrdDocInf")
        ED['RfrdDocAmtNode'] = ET.Element("RfrdDocAmt")

        return ED

    def strd_data(self, payment):

        lst =  list()
        for batches in payment['document']:
            # adding data to TX_Nodes
            strd_node = self._create_strd_nodes()
            strd_node['Nb_Node'].text = batches["invoice_number"]
            strd_node['Cd_Node'].text = batches["type"]
            strd_node['CdtNoteAmt_Node'].set("Ccy", self._config["currency"])
            strd_node['CdtNoteAmt_Node'].text = batches["invoice_amount"]
            strd_node['RltdDt_Node'].text = batches["invoice_date"]

            #appending the strd node for each batches
            strd_node['CdOrPrtryNode'].append(strd_node['Cd_Node'])
            strd_node['TpNode'].append(strd_node['CdOrPrtryNode'])
            strd_node['RfrdDocInfNode'].append(strd_node['TpNode'])
            strd_node['RfrdDocInfNode'].append(strd_node['Nb_Node'])
            strd_node['RfrdDocInfNode'].append(strd_node['RltdDt_Node'])
            strd_node['StrdNode'].append(strd_node['RfrdDocInfNode'])
            strd_node['RfrdDocAmtNode'].append(strd_node['CdtNoteAmt_Node'])
            strd_node['StrdNode'].append(strd_node['RfrdDocAmtNode'])
            lst.append(strd_node)
            del strd_node
        return lst
