from xml.dom.minidom import parseString

from mobilPay.payment.request.card import Card
from mobilPay.util.encrypt_data import Crypto


class Request:

    PAYMENT_TYPE_SMS = 'sms'
    PAYMENT_TYPE_CARD = 'card'
    PAYMENT_TYPE_TRANSFER = "transfer"
    PAYMENT_TYPE_INTERNET = "homePay"
    PAYMENT_TYPE_BITCOIN = "bitcoin"

    CONFIRM_ERROR_TYPE_NONE = 0
    CONFIRM_ERROR_TYPE_TEMPORARY = 1
    CONFIRM_ERROR_TYPE_PERMANENT = 2

    ERROR_LOAD_X509_CERTIFICATE = 1
    ERROR_ENCRYPT_DATA = 2

    ERROR_PREPARE_MANDATORY_PROPERTIES_UNSET = 1

    ERROR_FACTORY_BY_XML_ORDER_ELEM_NOT_FOUND = 1
    ERROR_FACTORY_BY_XML_ORDER_TYPE_ATTR_NOT_FOUND = 2
    ERROR_FACTORY_BY_XML_INVALID_TYPE = 3

    ERROR_LOAD_FROM_XML_ORDER_ID_ATTR_MISSING = 0x30000001
    ERROR_LOAD_FROM_XML_SIGNATURE_ELEM_MISSING = 0x30000002

    ERROR_CONFIRM_LOAD_PRIVATE_KEY = 0x300000f0
    ERROR_CONFIRM_FAILED_DECODING_DATA = 0x300000f1
    ERROR_CONFIRM_FAILED_DECODING_ENVELOPE_KEY = 0x300000f2
    ERROR_CONFIRM_FAILED_DECRYPT_DATA = 0x300000f3
    ERROR_CONFIRM_INVALID_POST_METHOD = 0x300000f4
    ERROR_CONFIRM_INVALID_POST_PARAMETERS = 0x300000f5
    ERROR_CONFIRM_INVALID_ACTION = 0x300000f6

    CONFIRM_ERROR_TYPE_NONE = 0
    CONFIRM_ERROR_TYPE_TEMPORARY = 1
    CONFIRM_ERROR_TYPE_PERMANENT = 2

    # def __init__(self):
    #     super().__init__()
    #     root_order = document.getElementsByTagName("order")
    #
    #     if len(root_order) != 1:
    #         raise Exception(
    #             "factory_from_xml -> order element not found" + str(self.ERROR_FACTORY_BY_XML_ORDER_ELEM_NOT_FOUND))
    #
    #     order = root_order[0]
    #
    #     attr = order.getAttribute("type")
    #     if attr is None or len(str(attr)) == 0:
    #         raise Exception("factory_from_xml -> invalid payment request type={} ".format(attr) + str(
    #             self.ERROR_FACTORY_BY_XML_ORDER_ELEM_NOT_FOUND))
    #     payment_type = attr
    #     self.load_xml_type(document, payment_type)

    def factory_from_encrypted(self, env_key, enc_data, private_key_file_path, private_key_password=None):
        private_key = None
        if private_key_password is None:
            private_key = Crypto.get_private_key(private_key_file_path)
        else:
            private_key = Crypto.get_private_key(private_key_file_path, private_key_password)

        if private_key is False:
            raise Exception("Error loading private key" + str(self.ERROR_CONFIRM_LOAD_PRIVATE_KEY))

        # src_data = base64.b64decode(enc_data)
        src_data = enc_data
        if src_data is False:
            raise Exception("Failed decoding data" + str(self.ERROR_CONFIRM_FAILED_DECODING_DATA))

        # src_env_key = base64.b64decode(enc_data)
        src_env_key = env_key
        if src_env_key is False:
            raise Exception(" Failed decoding envelope key" + str(self.ERROR_CONFIRM_FAILED_DECODING_ENVELOPE_KEY))

        result = Crypto.decrypt(src_data, private_key, src_env_key)
        if result is False:
            raise Exception("Failed decrypting data" + str(self.ERROR_CONFIRM_FAILED_DECRYPT_DATA))

        xml_data = parseString(result.decode("utf-8"))

        root_order = xml_data.getElementsByTagName("order")

        if len(root_order) != 1:
            raise Exception(
                "factory_from_xml -> order element not found" + str(self.ERROR_FACTORY_BY_XML_ORDER_ELEM_NOT_FOUND))

        order = root_order[0]

        attr = order.getAttribute("type")
        if attr is None or len(str(attr)) == 0:
            raise Exception("factory_from_xml -> invalid payment request type={} ".format(attr) + str(
                self.ERROR_FACTORY_BY_XML_ORDER_ELEM_NOT_FOUND))

        if attr == self.PAYMENT_TYPE_CARD:
            obj_pm_req = Card(order)
            return obj_pm_req
        # elif attr == self.PAYMENT_TYPE_SMS:
        #     obj_pm_req = SMS()
        # TODO add other payment types
        else:
            raise Exception("factory_from_xml -> invalid payment request type={} ".format(attr) + str(
                self.ERROR_FACTORY_BY_XML_INVALID_TYPE))