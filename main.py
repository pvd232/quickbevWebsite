from flask import Flask, jsonify, Response, request, redirect, url_for, render_template
import requests
from models import app, instantiate_db_connection
from service import *
import json
import time
import uuid
import stripe
import os
from werkzeug.utils import secure_filename
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask
import jwt
import calendar
from pushjack_http2_mod import APNSHTTP2Client, APNSAuthToken
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import MultiDict

merchant_menu_upload_folder = os.getcwd() + "/files"
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}
app.config['UPLOAD_FOLDER'] = merchant_menu_upload_folder

stripe.api_key = "sk_test_51I0xFxFseFjpsgWvh9b1munh6nIea6f5Z8bYlIDfmKyNq6zzrgg8iqeKEHwmRi5PqIelVkx4XWcYHAYc1omtD7wz00JiwbEKzj"
secret = '3327aa0ee1f61998369e815c17b1dc5eaf7e728bca14f6fe557af366ee6e20f9'
# theme color RGB = rgb(134,130,230), hex = #8682E6
# nice seafoam color #19cca3
# TODO: need to finish the add_business function by adding the new business address and returning the unique identifier to main.py so i can dynamically set the files path of the new image using the UUID of the business address


def send_apn(device_token, action):
    apn_key = ''
    team_id = '6YGH9XK378'
    # converted authkey to private key that can be properly encoded as RSA key by jwt.encode method using advice here https://github.com/lcobucci/jwt/issues/244
    with open(os.getcwd()+"/private_key.pem") as f:
        apn_token = f.read()
        f.close()
    token = APNSAuthToken(
        token=apn_token,
        team_id=team_id,
        key_id="9KCZ66FCHF")

    client = APNSHTTP2Client(
        token=token,
        bundle_id='com.theQuickCompany.QuickBev')

    if action == "email":
        client.send(
            ids=[device_token],
            title="Email verified",
            message="Email verification complete. Lets get this party started",
            category="email"
        )
    elif action == "order_complete":
        pass


def send_fcm(device_token):
    from pushjack_http2_mod import GCMClient

    client = GCMClient(
        api_key='AAAATofs8JE:APA91bFkb9kmo-sZuDwJIs4PNAh-6oxnN4XoR5RhTAB06qWJ9VMi3vFBTtgi6kIXGLwJfTUmzph-UTnKpXmZcyQ59uFSAOY1saTLdiobNmspqIU7uSQsM0nlPCM-VRH8A8QSNJvzuCxt')

    registration_id = device_token
    alert = 'new_order'
    notification = {'title': 'Title', 'body': 'Body', 'icon': 'icon'}

    # Send to single device.
    # NOTE: Keyword arguments are optional.
    res = client.send(registration_id,
                      alert,
                      notification=notification,
                      collapse_key='collapse_key',
                      delay_while_idle=True,
                      time_to_live=604800)

    # Send to multiple devices by passing a list of ids.
    # client.send([registration_id], alert, **options)


@app.route("/")
def my_index():
    return render_template("index.html", flask_token="Hello world")


@app.errorhandler(404)
def not_found(e):
    return render_template('index.html')


@app.route("/b")
def b():
    # test_service = Test_Service()
    # test_service.test_connection()
    instantiate_db_connection()
    return Response(status=200)


@app.route('/apn-token/<string:customer_id>/<string:session_token>', methods=["POST"])
def apn_token(customer_id, session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    else:
        device_token = request.headers.get("DeviceToken")
        Customer_Service().update_device_token(device_token, customer_id)
        return Response(status=200)


@app.route('/fcm_token/<string:business_id>/<string:session_token>', methods=["POST"])
def fcm_token(business_id, session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    else:
        device_token = json.loads(request.data)
        Business_Service().update_device_token(
            device_token, business_id)
        return Response(status=200)


@app.route("/test")
def test():
    return Response(status=200)


@app.route('/login', methods=['GET'])
def login():
    # grab the username and password values from a custom header that was sent as a part of the request from the frontend
    email = request.headers.get('email')
    password = request.headers.get('password')
    response = {"msg": "customer not found"}
    headers = {}
    customer_service = Customer_Service()
    customer = customer_service.authenticate_customer(email, password)

    if customer:
        serialized_customer = customer.dto_serialize()
        jwt_token = jwt.encode(
            {"sub": serialized_customer["id"]}, key=secret, algorithm="HS256")
        headers["authorization-token"] = jwt_token
        return Response(status=200, response=json.dumps(serialized_customer), headers=headers)
    else:
        return Response(status=404, response=json.dumps(response))


@app.route('/drink/<string:session_token>', methods=['GET'])
def inventory(session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    drink_list = []
    response = {}
    headers = {}
    drinks = Drink_Service().get_drinks()
    client_etag = json.loads(request.headers.get("If-None-Match"))

    if client_etag:
        if not ETag_Service().validate_etag(client_etag):
            for drink in drinks:
                drinkDTO = {}
                drinkDTO['drink'] = drink.dto_serialize()
                drink_list.append(drinkDTO)
            response['drinks'] = drink_list

            etag = ETag_Service().get_etag("drink")
            headers["e-tag-id"] = etag.id
            headers["e-tag-category"] = etag.category
    else:
        etag = ETag_Service().get_etag("drink")
        headers["e-tag-id"] = etag.id
        headers["e-tag-category"] = etag.category

    return Response(status=200, response=json.dumps(response), headers=headers)


@app.route('/order/<string:session_token>', methods=['POST', 'GET', 'OPTIONS', 'PUT'])
def orders(session_token):
    headers = {}
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    response = {}

    if request.method == 'PUT':
        order_to_update = json.loads(request.data)
        if order_to_update["rejected"] == True:
            # 1. send push notification to device
            device_token = Customer_Service().get_device_token(
                order_to_update["customer_id"])
            # send_apn(device_token, 'order_rejected')
            # 2. refund customer
            pass
        elif order_to_update["completed"] == True:
            # 1. send push notification to device saying the order is ready
            # device_token = Customer_Service.get_device_token(order_to_update.customer_id)
            # send_apn(device_token, 'order_completed')
            device_token = Customer_Service().get_device_token(
                order_to_update["customer_id"])
            # send_apn(device_token, "order_ready")

        Order_Service().update_order(order_to_update)
        return Response(status=200)
    elif request.method == 'POST':
        new_order = request.json
        Order_Service().create_order(new_order)
        business_device_token = Business_Service().get_device_token(new_order.business_id)
        send_fcm(business_device_token)
        response['msg'] = 'order_received'
        return Response(status=200, response=json.dumps(response))
    elif request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Allow-Credentials"] = "true"

        headers["Access-Control-Expose-Headers"] = "*"

        return Response(status=200, headers=headers)
    elif request.method == "GET":
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Allow-Credentials"] = "true"

        headers["Access-Control-Expose-Headers"] = "*"
        # for tablet get request
        business_id = request.headers.get('business')
        if business_id:
            orders = [x.dto_serialize()
                      for x in Order_Service().get_business_orders(business_id)]

        else:
            username = base64.b64decode(
                request.headers.get(
                    "Authorization").split(" ")[1]).decode("utf-8").split(":")[0]

            filter_orders_by = request.headers.get('Filterby')
            orders = []
            if filter_orders_by == 'merchant':
                orders = [x.dto_serialize()
                          for x in Order_Service().get_merchant_orders(username=username)]
                if len(orders) == 0:
                    # dummy data to populate orders table if the merchant has no orders
                    dummy_order = Order_Domain()
                    orders.append(dummy_order.dto_serialize())

            elif filter_orders_by == 'customer':
                orders = Order_Service().get_merchant_orders(username=username)
        response['orders'] = orders

    return Response(status=200, response=json.dumps(response), headers=headers)


def send_confirmation_email(jwt_token, customer):
    host = request.headers.get('Host')
    button_url = f"https://{host}/verify-email/{jwt_token}"

    logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

    verify_button = f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin-right: auto; margin-top:5vh; margin-left:auto; margin-bottom:2vh;   border-collapse:separate;line-height:100%;"><tr><td><div><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://www.activecampaign.com" style="height:40px;v-text-anchor:middle;width:130px;" arcsize="5%" strokecolor="#8682E6" fillcolor="#8682E6;width: 130;"><w:anchorlock/><center style="color:#ffffff;font-family:Helvetica, sans-serif;font-size:18px; font-weight: 600;">Click here!</center></v:roundrect><![endif]--><a href={button_url} style="display: inline-block; mso-hide:all; background-color: #8682E6; color: #FFFFFF; border:1px solid #8682E6; border-radius: 6px; line-height: 220%; width: 200px; font-family: Helvetica, sans-serif; font-size:18px; font-weight:600; text-align: center; text-decoration: none; -webkit-text-size-adjust:none;" target="_blank">Verify email</a></a></div></td></tr></table>'
    mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey {customer.first_name},</p><p style="margin-top: 15px;margin-bottom: 15px;">Welcome to QuickBev!</p><p style="margin-top: 15px;margin-bottom: 15px;">Please click the link below to verify your account.</p><br /><p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div><div style="width:100%; height:3vh;">{verify_button}</div>'
    mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"><img src="{logo}" style="width:50%; height:12%; margin-right:auto; margin-left:auto" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

    sender_address = 'confirmation@quickbev.us'
    email = customer.id

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = email

    message['Subject'] = 'Welcome to Quickbev'  # The subject line

    mail_content = mail_body
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    s = smtplib.SMTP('smtp.mailgun.org', 587)
    # this password was generated ay the domain settings page on mailgun. its a really shitty confusing service.
    s.login('postmaster@quickbev.us',
            '77bf9d60999ee72f1f72f98dd1a57152-1f1bd6a9-a4533d5f')
    s.sendmail(message['From'], message['To'], message.as_string())
    s.quit()


def send_password_reset_email(jwt_token, customer):
    host = request.headers.get('Host')
    # host = "quickbev.uc.r.appspot.com"

    button_url = f"https://{host}/reset-password/{jwt_token}"

    logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

    verify_button = f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin-right: auto; margin-top:5vh; margin-left:auto;   border-collapse:separate;line-height:100%;"><tr><td><div><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://www.activecampaign.com" style="height:40px;v-text-anchor:middle;width:130px;" arcsize="5%" strokecolor="#8682E6" fillcolor="#8682E6;width: 130;"><w:anchorlock/><center style="color:#ffffff;font-family:Helvetica, sans-serif;font-size:18px; font-weight: 600;">Click here!</center></v:roundrect><![endif]--><a href={button_url} style="display: inline-block; mso-hide:all; background-color: #8682E6; color: #FFFFFF; border:1px solid #8682E6; border-radius: 6px; line-height: 220%; width: 200px; font-family: Helvetica, sans-serif; font-size:18px; font-weight:600; text-align: center; text-decoration: none; -webkit-text-size-adjust:none;" target="_blank">Reset passsword</a></a></div></td></tr></table>'
    mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey {customer.first_name},</p><p style="margin-top: 15px;margin-bottom: 15px;">Having trouble logging in?</p><p style="margin-top: 15px;margin-bottom: 15px;">No worries. Click the button below to reset your password.</p><br /><p style="margin-top: 15px;margin-bottom: 15px;">Keep calm and carry on,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div><div style="width:100%">{verify_button}</div>'
    mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:45vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="display: flex; width:100%; text-align:center;"><img src="" style="width:50%; height:12%" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:10vh;"></tr></div></div></div>'

    sender_address = 'postmaster@sandbox471ef3a89bf64e819540bc75206062f2.mailgun.org'
    email = customer.id

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = email

    message['Subject'] = 'Order From'  # The subject line

    mail_content = mail_body
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    s = smtplib.SMTP('smtp.mailgun.org', 587)
    s.login('postmaster@sandbox471ef3a89bf64e819540bc75206062f2.mailgun.org',
            '44603d9d0e3864edd01989602e0db876-e49cc42c-7570439d')
    s.sendmail(message['From'], message['To'], message.as_string())
    s.quit()


@app.route('/email')
def email():
    test_customer_json = {"id": "patardriscoll@gmail.com", "first_name": "peter", "last_name": "driscoll",
                          "password": "iqo", "has_registered": False, "email_verified": False, "stripe_id": "abc"}
    test_customer = Customer_Domain(customer_json=test_customer_json)
    send_confirmation_email(jwt_token=jwt.encode(
        {"sub": test_customer.id}, key=secret, algorithm="HS256"), customer=test_customer)
    return Response(status=200)


@app.route('/guest-device-token', methods=['POST'])
def guest_device_token():
    headers = {}
    device_token = request.headers.get("DeviceToken")
    Customer_Service().add_guest_device_token(device_token)
    jwt_token = jwt.encode(
        {"sub": device_token}, key=secret, algorithm="HS256")
    headers["authorization-token"] = jwt_token
    return Response(status=200, headers=headers)


@app.route('/customer', methods=['POST', 'GET', 'OPTIONS', 'PUT'])
def customer():
    response = {}
    headers = {}
    if request.method == 'OPTIONS':
        session_token = request.args.get('sessionToken')
        if not jwt.decode(session_token, secret, algorithms=["HS256"]):
            return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Allow-Credentials"] = "true"

        headers["Access-Control-Expose-Headers"] = "*"

        return Response(status=200, headers=headers)
    if request.method == 'POST':
        requested_new_customer = json.loads(
            request.data)
        generated_new_customer = Customer_Service().register_new_customer(
            requested_new_customer)
        device_token = request.headers.get("DeviceToken")

        # generate a secure JSON token using the user's unverified email address. then i embed this token in the url for the verify account link sent in the email. i then parse this string when the user navigates to the page, securely verifying their email by using the
        if generated_new_customer:
            print('generated cust', generated_new_customer.dto_serialize())
            Customer_Service().update_device_token(
                device_token, generated_new_customer.id)
            jwt_token = jwt.encode(
                {"sub": generated_new_customer.id}, key=secret, algorithm="HS256")
            # send the hashed user ID as a crypted key embedded in the activation link for security
            headers["authorization-token"] = jwt_token
            send_confirmation_email(
                jwt_token=jwt_token, customer=generated_new_customer)
            if generated_new_customer.has_registered == True:
                status = 201
            else:
                status = 200
            return Response(response=json.dumps(generated_new_customer.dto_serialize()), status=status, headers=headers)
        else:
            return Response(status=400)
    elif request.method == 'PUT':
        customer = Customer_Domain(customer_json=json.loads(
            request.data))
        jwt_token = jwt.encode(
            {"sub": customer.id}, key=secret, algorithm="HS256")
        send_confirmation_email(
            jwt_token=jwt_token, customer=customer)
        return Response(status=200)
        return Response(status=200, headers=headers)
    elif request.method == "GET":
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Allow-Credentials"] = "true"

        headers["Access-Control-Expose-Headers"] = "*"

        merchant_id = base64.b64decode(
            request.headers.get(
                "Authorization").split(" ")[1]).decode("utf-8")
        customers = [x.dto_serialize() for x in Customer_Service(
        ).get_customers(merchant_id=merchant_id)]

        if len(customers) < 1:
            dummy_customer = Customer_Domain()
            customers.append(dummy_customer.dto_serialize())
        response = {"customers": customers}
        return Response(status=200, response=json.dumps(response), headers=headers)


# strongly typed url argument ;)
@app.route("/verify-email/<string:session_token>")
def verify_email(session_token):
    status = jwt.decode(session_token, secret, algorithms=["HS256"])
    if not status:
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    # verify the hashed username that was embedded in the verification link
    customer_id = status["sub"]
    if Customer_Service().update_email_verification(customer_id):
        Customer_Service().get_device_token(customer_id)
        device_token = Customer_Service().get_device_token(customer_id)
        send_apn(device_token, "email")
        response = {"msg": "successfully registered"}
        return Response(response=json.dumps(response), status=200)
    else:
        response = {"msg": "customer not found"}
        return Response(response=json.dumps(response), status=400)


@app.route('/reset-password/<string:customer_id>', methods=['POST', 'GET'])
def reset_password(customer_id):
    if request.method == 'GET':
        customer = Customer_Service().get_customer(customer_id)
        if customer:
            jwt_token = jwt.encode(
                {"sub": customer_id}, key=secret, algorithm="HS256")
            send_password_reset_email(
                jwt_token=jwt_token, customer=customer)
        return Response(status=200)
    elif request.method == 'POST':
        jwt_token = customer_id
        if jwt.decode(jwt_token, secret, algorithms=["HS256"]):
            new_password = json.loads(request.data)
            Customer_Service().update_password(customer_id, new_password)
            return Response(status=200, response=json.dumps({"msg": "password reset"}))
        else:
            return Response(status=400, response=json.dumps({"msg": "error"}))


@app.route('/business/<string:session_token>', methods=['GET', 'OPTIONS'])
def business(session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    response = {}
    headers = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Allow-Credentials"] = "true"

        headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Origin"
        headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Credentials"
        headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Headers"
        return Response(status=200, headers=headers)
    elif request.method == 'GET':
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "authorization"
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Credentials"] = 'true'
        headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Origin"
        headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Credentials"
        headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Headers"

        business_list = []
        if request.headers.get('merchantId'):
            print('request.headers.get(merchantId)',request.headers.get('merchantId'))
            merchant_id = request.headers.get('merchantId')
            merchant_businesses = [x.dto_serialize(
            ) for x in Business_Service().get_merchant_business(merchant_id)]

            if len(merchant_businesses) < 1:
                dummy_business = Business_Domain()
                merchant_businesses.append(dummy_business.dto_serialize())
            response["businesses"] = merchant_businesses
            if merchant_businesses:
                return Response(status=200, response=json.dumps(response), headers=headers)
            else:
                response["msg"] = "businesses for the requested merchant_id were not found"
                return Response(status=404, response=json.dumps(response), headers=headers)

        businesss = Business_Service().get_businesses()
        client_etag = json.loads(request.headers.get("If-None-Match"))

        if client_etag:
            if not ETag_Service().validate_etag(client_etag):
                for business in businesss:
                    # turn into dictionaries
                    businessDTO = {}
                    businessDTO['business'] = business.dto_serialize()
                    business_list.append(businessDTO)
                    response['businesses'] = business_list

                etag = ETag_Service().get_etag("business")
                headers["e-tag-category"] = etag.category
                headers["e-tag-id"] = str(etag.id)
        else:
            etag = ETag_Service().get_etag("business")
            headers["e-tag-category"] = etag.category
            headers["e-tag-id"] = str(etag.id)
        return Response(status=200, response=json.dumps(response), headers=headers)


@app.route('/tabs', methods=['POST', 'GET'])
def tabs():
    if request.method == 'POST':
        response = {}
        new_tab = request.json['tab']
        tab_service = Tab_Service()
        if tab_service.post_tab(new_tab):
            response['msg'] = 'tab posted'
            return Response(status=200, response=json.dumps(response))
        else:
            response['msg'] = 'something broke'
            return Response(status=500, response=json.dumps(response))


@app.route('/create-ephemeral-keys/<string:session_token>', methods=['POST'])
def ephemeral_keys(session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    request_data = json.loads(request.data)
    order_service = Order_Service()
    key, header = order_service.create_stripe_ephemeral_key(request_data)
    if key and header:
        return Response(status=200, response=json.dumps(key), headers=header)
    else:
        return Response(status=200, response=json.dumps(key))


@app.route('/create-payment-intent/<string:session_token>', methods=['POST'])
def create_payment_intent(session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    response = {}
    request_data = json.loads(request.data)
    order_service = Order_Service()
    client_secret = order_service.stripe_payment_intent(request_data)
    response["secret"] = client_secret
    return Response(status=200, response=json.dumps(response))


@app.route('/business_phone_number', methods=['GET'])
def business_phone_number():
    business_phone_number = request.args.get('business_phone_number')
    business_phone_number_status = Business_Service(
    ).get_business_phone_number(business_phone_number)
    if business_phone_number_status == False:
        return Response(status=400)
    else:
        # if the business phone exists then the business id will be returned
        return Response(status=200, response=json.dumps(business_phone_number_status.dto_serialize()))


@app.route('/create-account', methods=['POST', 'OPTIONS'])
def create_account():
    response = {"msg": ""}
    headers = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')

        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    elif request.method == 'POST':
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Expose-Headers"] = "*"
        # check if the post request has the file part
        requested_merchant = json.loads(request.form.get("merchant"))
        requested_business = json.loads(request.form.get("business"))

        merchant_service = Merchant_Service()
        business_service = Business_Service()

        new_merchant = merchant_service.add_merchant(requested_merchant)
        new_business = business_service.add_business(requested_business)
        if new_merchant and new_business:
            headers["jwt_token"] = jwt.encode(
            {"sub": request}, key=secret, algorithm="HS256")
            response['confirmed_new_business'] = new_business.dto_serialize()

            if 'file' not in request.files:
                response["msg"] = "No file part in request"
                return Response(status=200, response=json.dumps(response), headers=headers)

            file = request.files['file']
            # merchant does not select file
            if file.filename == '':
                response["msg"] = "No file file uploaded"
                return Response(status=200, response=json.dumps(response), headers=headers)
            # if file and allowed_file(file.filename):
            if file:
                Google_Cloud_Storage_API().upload_menu_file(file, new_business.id)
                response["msg"] = "File successfully uploaded!"
                return Response(status=200, response=json.dumps(response), headers=headers)
            # elif file and not allowed_file(file.filename):
            #     response["msg"] = "File not allowed"
            #     return Response(status=415, response=json.dumps(response), headers=headers)
        response["msg"] = "An unknown internal server error occured"
        return Response(status=500, response=json.dumps(response), headers=headers)

# dont need this anymore because i no longer generate a new stripe ID when the user hits the redirect_url. felt cute, will probably delete later
# @app.route('/create-account-redirect', methods=['POST'])
# def create_account_redirect():
#     response = {"msg": ""}
#     headers = {}
#     business_service = Business_Service()
#     request_json = json.loads(request.data)
#     print('request_json',request_json)
#     business_to_update = request_json["business"]
#     print('business_to_update',business_to_update)
#     if business_service.update_business(business_to_update):
        # headers["jwt_token"] = jwt.encode(
        #     {"sub": business_to_update["id"]}, key=secret, algorithm="HS256")
#         response["msg"] = "Business sucessfully updated"
#         return Response(status=200, response=json.dumps(response), headers=headers)
#     else:
#         response["msg"] = "Failed to update business"
#         return Response(status=500, response=json.dumps(response))


@app.route('/merchant_employee_stripe_account', methods=['GET'])
def merchant_employee_stripe_account():
    headers = {}
    merchant_employee_id = request.args.get('merchant_employee_id')
    stripe_id = Merchant_Employee_Service().get_stripe_account(merchant_employee_id)
    account_links = stripe.AccountLink.create(
        account=stripe_id,
        refresh_url='https://quickbev.uc.r.appspot.com/merchant-employee-payout-setup-callback',
        return_url='https://quickbev.uc.r.appspot.com/merchant-employee-payout-setup-complete',
        type='account_onboarding',
    )
    headers["stripe_id"] = stripe_id
    headers["Access-Control-Allow-Origin"] = request.origin
    headers["Access-Control-Expose-Headers"] = "*"

    response = Response(status=200, response=json.dumps(
        account_links), headers=headers)
    return response


@app.route('/merchant_employee', methods=['POST', 'GET'])
def merchant_employee():
    if request.method == 'POST':
        request_json = json.loads(request.data)
        new_merchant_employee = Merchant_Employee_Service().add_merchant_employee(request_json)
        return Response(status=200, response=json.dumps(new_merchant_employee.dto_serialize()))
    # check to see if the merchant username already exists during account creation
    elif request.method == 'GET':
        merchant_employee_username = request.args.get('username')
        merchant_employee_username_status = Merchant_Employee_Service(
        ).authenticate_username(merchant_employee_username)
        if merchant_employee_username_status == True:
            return Response(status=400)
        else:
            return Response(status=200)


@app.route('/merchant_employee/validate_pin_number', methods=['POST', 'GET'])
def validate_pin_number():
    if request.method == 'GET':
        merchant_employee_pin_number = request.args.get('pin_number')
        business_id = request.args.get('business_id')
        merchant_employee_pin_number_status = Merchant_Employee_Service(
        ).validate_pin_number(business_id, merchant_employee_pin_number)
        if merchant_employee_pin_number_status == True:
            return Response(status=200)
        else:
            return Response(status=400)


@app.route('/authenticate_business/<string:session_token>', methods=['POST'])
def authenticate_business(session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=404, response=json.dumps({"msg": "Inconsistent request"}))
    business_id = json.loads(request.data)['business_id']
    business_status = Business_Service().authenticate_business(business_id)
    if business_status == True:
        return Response(status=200)
    else:
        return Response(status=400)


@app.route('/merchant_employee_login', methods=['POST', 'OPTIONS'])
def merchant_employee_login():
    headers = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')

        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    elif request.method == 'POST':
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Expose-Headers"] = "*"
        # check if the post request has the file part
    request_data = json.loads(request.data)

    merchant_employee_service = Merchant_Employee_Service()
    new_merchant_employee = merchant_employee_service.authenticate_merchant_employee(
        email=request_data['email'], password=request_data['password'])
    if new_merchant_employee != False:
        headers["jwt_token"] = jwt.encode(
            {"sub": new_merchant_employee.id}, key=secret, algorithm="HS256")

        return Response(status=200, response=json.dumps(new_merchant_employee.dto_serialize()), headers=headers)
    else:
        return Response(status=400)


@app.route('/merchant_employee/pin_number', methods=['POST'])
def authenticate_pin_number():
    headers = {}
    data = json.loads(request.data)
    pin_number = data['pin_number']
    merchant_employee_id = data['email']

    login_status = data['logged_in']
    new_merchant_employee = Merchant_Employee_Service().authenticate_pin_number(
        merchant_employee_id, pin_number, login_status)
    if new_merchant_employee != False:
        # have to reset the pin number otherwise it will be the hashed version
        new_merchant_employee.pin_number = pin_number
        print('new_merchant_employee', new_merchant_employee.dto_serialize())
        headers["jwt_token"] = jwt.encode(
            {"sub": new_merchant_employee.id}, key=secret, algorithm="HS256")
        return Response(status=200, response=json.dumps(new_merchant_employee.dto_serialize()), headers=headers)
    else:
        return Response(status=400)


@app.route('/merchant_employee/reset_pin_number', methods=['POST'])
def reset_pin_number():
    headers = {}
    data = json.loads(request.data)
    pin_number = data['pin_number']
    merchant_employee_id = data['email']

    new_merchant_employee = Merchant_Employee_Service(
    ).reset_pin_number(merchant_employee_id, pin_number)
    if new_merchant_employee != False:
        new_merchant_employee.pin_number = pin_number
        return Response(status=200, response=json.dumps(new_merchant_employee.dto_serialize()))
    else:
        return Response(status=400)


@app.route('/merchant', methods=['GET', 'OPTIONS'])
def authenticate_merchant():
    headers = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "*"

        return Response(status=200, headers=headers)
    if request.method == "GET":
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Expose-Headers"] = "*"

        username = request.headers.get('email')
        password = request.headers.get('password')

        response = {"msg": "customer not found"}
        merchant = Merchant_Service().authenticate_merchant(username, password)
        # if the merchant exists it will return False, if it doesn't it will return True
        if merchant:
            headers["jwt_token"] = jwt.encode(
                {"sub": merchant.id}, key=secret, algorithm="HS256")

            return Response(status=200, response=json.dumps(merchant.dto_serialize()), headers=headers)
        else:
            return Response(status=204, response=json.dumps(response), headers=headers)


@app.route('/create-stripe-account', methods=['GET', 'OPTIONS'])
def create_stripe_account():
    headers = {}
    callback_stripe_id = request.args.get('stripe')
    account_links = ''
    if callback_stripe_id:
        account_links = stripe.AccountLink.create(
            account=callback_stripe_id,
            refresh_url='https://quickbev.uc.r.appspot.com/payout-setup-callback',
            return_url='https://quickbev.uc.r.appspot.com/home',
            type='account_onboarding',
        )
        headers["stripe_id"] = callback_stripe_id
    else:
        new_account = Merchant_Service().create_stripe_account()
        account_links = stripe.AccountLink.create(
            account=new_account.id,
            refresh_url='https://quickbev.uc.r.appspot.com/payout-setup-callback',
            return_url='https://quickbev.uc.r.appspot.com/home',
            type='account_onboarding',
        )
        headers["stripe_id"] = new_account.id

    headers["Access-Control-Allow-Origin"] = request.origin
    headers["Access-Control-Expose-Headers"] = "*"
    response = Response(status=200, response=json.dumps(
        account_links), headers=headers)
    return response


@app.route('/validate-merchant-stripe-account', methods=['GET'])
def validate_merchant_stripe_account():
    print('hey')
    callback_stripe_id = request.args.get('stripe')
    print('callback_stripe_id',callback_stripe_id)
    merchant_stripe_status = Merchant_Service(
    ).authenticate_merchant_stripe(callback_stripe_id)
    print('merchant_stripe_status', merchant_stripe_status)
    if merchant_stripe_status:
        response = Response(status=200)
    else:
        response = Response(status=400)
    return response


@app.route('/menu', methods=['POST', 'GET'])
def add_menu():
    headers = {}
    response = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "*"

        return Response(status=200, headers=headers)

    if request.method == 'POST':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Expose-Headers"] = "*"

        drink_names = json.loads(request.form.get("drinkName"))
        drink_descriptions = json.loads(request.form.get("drinkDescription"))
        drink_prices = json.loads(request.form.get("drinkPrice"))
        drink_file_names = json.loads(request.form.get("selectedFile"))
        business_id = json.loads(request.form.get("businessId"))

        new_drinks = [{"name": x} for x in drink_names]
        for i in range(len(new_drinks)):
            drink = new_drinks[i]
            drink["description"] = drink_descriptions[i]
            drink["price"] = float(drink_prices[i])
            drink["has_image"] = drink_file_names[i]

        added_drinks = Drink_Service().add_drinks(business_id, new_drinks)

        files = request.files
        drinks_with_images = [
            x for x in added_drinks if x.has_image == True]
        if 'selectedFile' in files:
            multi_dict_files = MultiDict(files).getlist('selectedFile')
            for i in range(len(multi_dict_files)):
                file = multi_dict_files[i]
                file_type = file.filename.split('.')[1]
                if file_type != 'jpg':
                    file.filename = file.filename.split('.')[0] + '.jpg'
                drink = drinks_with_images[i]
                drink.file = file
                Google_Cloud_Storage_API().upload_drink_image_file(drink)
                response["msg"] = "File successfully uploaded!"
            return Response(status=200, response=json.dumps(response), headers=headers)
        drink_descriptions = json.loads(request.form.get("drinkDescription"))
        drink_descriptions = json.loads(request.form.get("drinkDescription"))

        response = Response(status=200, headers=headers)
        return response
    else:
        business_id = request.args.get('businessId')
        menu = Business_Service().get_menu(business_id)
        if menu:
            menu = [x.dto_serialize() for x in menu]
            response = Response(status=200, response=json.dumps(menu))
        else:
            response = Response(status=404)
        return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
