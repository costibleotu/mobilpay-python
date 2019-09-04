### Dependencies

---

##### In order to run the sdk you need to install the following dependencies

- ```python ^3.5.x```
- ```pip install pycrypto```
- ```pip install pyopenssl```


#### Implementation
    See ```server/main.py``` and ```server/main_local``` for implementation


###### Optional

- ```brew install libffi```

- Then reinstall ```cryptography``` or ```boxsdk``` with pip:

- ```pip install cryptography --force-reinstall```

~~~~python

#CLIENT SIDE
payment_url = 'http://sandboxsecure.mobilpay.ro'

# path to your public certificate that contains the public key
x509_filePath = "path_to_cert/public_cert.cer"

obj_pm_req_card = Card()

obj_pm_req_card.set_signature("signature_from_xml")

obj_pm_req_card.set_payment_type("card")

obj_pm_req_card.set_order_id("order_id")

obj_pm_req_card.set_confirm_url("confirm_url")

obj_pm_req_card.set_return_url("return_url")

obj_pm_req_card.set_invoice(Invoice())

obj_pm_req_card.get_invoice().set_currency("RON")

obj_pm_req_card.get_invoice().set_amount("0.10")

obj_pm_req_card.get_invoice().set_token_id("fmndiusnvdfiu")

obj_pm_req_card.get_invoice().set_details("Plata online cu cardul")

billing_address = Address("billing")

billing_address.set_type("person")
billing_address.set_first_name("Netopia")
billing_address.set_last_name("Man")
billing_address.set_address("Acasa Bucuresti")
billing_address.set_email("contact@netopia.com")
billing_address.set_mobile_phone("8989989")

obj_pm_req_card.get_invoice().set_billing_address(billing_address)

shipping_address = Address("shipping")

shipping_address.set_type("person")
shipping_address.set_first_name("Netopia")
shipping_address.set_last_name("House")
shipping_address.set_address("Acasa Bucuresti")
shipping_address.set_email("contact@netopia.com")
shipping_address.set_mobile_phone("8989989")

obj_pm_req_card.get_invoice().set_shipping_address(shipping_address)

obj_pm_req_card.encrypt(x509_filePath)

# encoded data and env_key
data = obj_pm_req_card.get_enc_data()
env_key = obj_pm_req_card.get_env_key()


# SERVER SIDE
error_code = 0
error_type = BaseRequest.CONFIRM_ERROR_TYPE_NONE
error_message = ""
if request.method == "POST":
    # calea catre cheia privata
    private_key_path = "path_to_private_key/private.key"

    # get the envelope key and data from the request
    result = request.form.to_dict()
    env_key = result["env_key"]
    env_data = result["data"]

    # env_key si data trebuie parsate pentru ca vin din url, se face cu function unquote din urllib
    obj_pm_request = Request().factory_from_encrypted(
        unquote(env_key), unquote(env_data), private_key_path)

    notify = obj_pm_request.get_notify()

    if env_key is not None and len(env_key) > 0 and env_data is not None and len(env_data) > 0:
        try:
            if int(notify.errorCode) == 0:
                """
                orice action este insotit de un cod de eroare si de un mesaj de eroare. Acestea pot fi citite
                folosind error_code = obj_pm_req.get_notify().errorCode
                respectiv error_message = obj_pm_req.get_notify()errorMessage
                pentru a identifica ID-ul comenzii pentru care primim rezultatul platii folosim
                order_id = obj_pm_req.get_order_id()
                """
                if notify.action == "confirmed":
                    """ 
                    cand action este confirmed avem certitudinea ca banii au plecat din contul posesorului de
                    card si facem update al starii comenzii si livrarea produsului
                    update DB, SET status = "confirmed/captured"
                    """
                    error_message = notify.errorMessage
                elif notify.action == "confirmed_pending":
                    """ 
                    cand action este confirmed_pending inseamna ca tranzactia este in curs de verificare
                    antifrauda. Nu facem livrare/expediere. In urma trecerii de aceasta verificare se va primi o
                    noua notificare pentru o actiune de confirmare sau anulare.
                    update DB, SET status = "pending"
                    """
                    error_message = notify.errorMessage
                elif notify.action == "paid_pending":
                    """
                    cand action este paid_pending inseamna ca tranzactia este in curs de verificare. 
                    Nu facem livrare/expediere. In urma trecerii de aceasta verificare se va primi o noua 
                    notificare pentru o actiune de confirmare sau anulare.
                    update DB, SET status = "pending"
                    """
                    error_message = notify.errorMessage
                elif notify.action == "paid":
                    """cand action este paid inseamna ca tranzactia este in curs de procesare.
                    Nu facem livrare/expediere. In urma trecerii de aceasta procesare se va primi o noua
                    notificare pentru o actiune de confirmare sau anulare.
                    update DB, SET status = 'open/preauthorized'"""
                    error_message = notify.errorMessage
                elif notify.action == "canceled":
                    """cand action este canceled inseamna ca tranzactia este anulata. Nu facem livrare/expediere.
                    update DB, SET status = 'canceled'"""
                    error_message = notify.errorMessage
                elif notify.action == "credit":
                    """
                    cand action este credit inseamna ca banii sunt returnati posesorului de card.
                    Daca s-a facut deja livrare, aceasta trebuie oprita sau facut un reverse.
                    update DB, SET status = 'refunded'
                    """
                    error_message = notify.errorMessage
                else:
                    error_type = Request.CONFIRM_ERROR_TYPE_PERMANENT
                    error_code = Request.ERROR_CONFIRM_INVALID_ACTION
                    error_message = 'mobilpay_refference_action paramaters is invalid'
            else:
                """  # update DB, SET status = "rejected"""
                error_message = notify.errorMessage
                # error_type = Request.CONFIRM_ERROR_TYPE_TEMPORARY not sure here
                # error_code = notify.errorCode
        except Exception as e:
            error_type = Request.CONFIRM_ERROR_TYPE_TEMPORARY
            error_code = int(e)
            error_message = 'mobilpay_refference_action paramaters is invalid'
    else:
        error_type = Request.CONFIRM_ERROR_TYPE_PERMANENT
        error_code = Request.ERROR_CONFIRM_INVALID_POST_PARAMETERS
        error_message = 'mobilpay.ro posted invalid parameters'
else:
    error_type = Request.CONFIRM_ERROR_TYPE_PERMANENT
    error_code = Request.ERROR_CONFIRM_INVALID_POST_METHOD
    error_message = 'invalid request method for payment confirmation'

crc = Document()
crc_text = crc.createElement("crc")
crc_value = crc.createTextNode(error_message)

if error_code != 0:
    crc_text.setAttribute("error_type", str(error_type))
    crc_text.setAttribute("error_code", str(error_code))

crc_text.appendChild(crc_value)
crc.appendChild(crc_text)

return crc.toprettyxml(indent="\t", newl="\n", encoding="utf-8")
~~~~