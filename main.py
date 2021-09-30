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
from pushjack_http2_mod import APNSHTTP2Client, APNSHTTP2SandboxClient, APNSAuthToken
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import MultiDict

merchant_menu_upload_folder = os.getcwd() + "/files"
app.config['UPLOAD_FOLDER'] = merchant_menu_upload_folder

stripe.api_key = "sk_test_51I0xFxFseFjpsgWvh9b1munh6nIea6f5Z8bYlIDfmKyNq6zzrgg8iqeKEHwmRi5PqIelVkx4XWcYHAYc1omtD7wz00JiwbEKzj"
secret = '3327aa0ee1f61998369e815c17b1dc5eaf7e728bca14f6fe557af366ee6e20f9'
# theme color RGB = rgb(134,130,230), hex = #8682E6
# nice seafoam color #19cca3


def send_apn(device_token, action, env):
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
    if env == "production":
        client = APNSHTTP2Client(
            token=token,
            bundle_id='com.theQuickCompany.QuickBev')
    elif env == "sandbox":
        client = APNSHTTP2SandboxClient(
            token=token,
            bundle_id='com.theQuickCompany.QuickBev')

    if action == "email":
        client.send(
            ids=[device_token],
            title="Email Verified",
            message="Email verification complete. Lets get this party started",
            category=action
        )
    elif action == "order_completed":
        client.send(
            ids=[device_token],
            title="Order Completed",
            message="Your order is ready for pickup!",
            category=action
        )
    elif action == "order_refunded":
        client.send(
            ids=[device_token],
            title="Order Refunded",
            message="Items in your order are out of stock. We refunded you.",
            category=action
        )


def send_fcm(device_token, new_order):
    from pushjack_http2_mod import GCMClient

    client = GCMClient(
        api_key='AAAATofs8JE:APA91bFkb9kmo-sZuDwJIs4PNAh-6oxnN4XoR5RhTAB06qWJ9VMi3vFBTtgi6kIXGLwJfTUmzph-UTnKpXmZcyQ59uFSAOY1saTLdiobNmspqIU7uSQsM0nlPCM-VRH8A8QSNJvzuCxt')

    registration_id = device_token
    alert = 'new_order'

    notification = {
        'title': new_order["customer"]['first_name'], 'body': new_order["customer"]['last_name']}
    # Send to single device.
    # NOTE: Keyword arguments are optional.
    res = client.send(registration_id,
                      alert,
                      notification=notification,
                      time_to_live=604800)

    # Send to multiple devices by passing a list of ids.
    # client.send([registration_id], alert, **options)


@app.route("/")
def my_index():

    return render_template("index.html", flask_token="Hello world")


@app.errorhandler(404)
def not_found(e):
    return render_template('index.html')

# @app.route("/c")
# def c():
#     a = db.session.query(Business).all()
#     for biz in a:
#         print("biz", biz.serialize)
#         print("biz schedule", biz.schedule)
#     return Response(status=200)

@app.route("/b")
def b():
    # test_service = Test_Service()
    # test_service.test_connection()
    instantiate_db_connection()
    return Response(status=200)

@app.route("/c")
def c():
    order_id = request.args.get("order_id")
    Order_Service().get_order(order_id)
    device_token = Customer_Service().get_device_token('c')
    send_apn(device_token, 'order_completed', 'sandbox')
    return Response(status=200)
    
@app.route('/test_token', methods=["GET"])
def test_token():
    fcm_token = 'cdCW0jutR2aIZ_k869mOrM:APA91bGp_eetQsBkM9-CnLlEZBAwM8N2fWEhDV4PDch6EsVZGM0G8NATrKx-CYfSyxM_RbfjTh42nWJxopSesywc3WCqEz4Z_JZTpSQLnuVY-x_Er7Z7KVj5VwVGCb4gjcKwdQQNRKlB'
    customer = {"first_name": "peter", "last_name": "driscoll"}
    new_order = {"customer": customer}
    send_fcm(fcm_token, new_order)


@app.route('/apn-token/<string:customer_id>/<string:session_token>', methods=["POST"])
def apn_token(customer_id, session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    else:
        device_token = request.headers.get("DeviceToken")
        Customer_Service().update_device_token(device_token, customer_id)
        return Response(status=200)


@app.route('/fcm_token/<string:session_token>', methods=["POST"])
def fcm_token(business_id, session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    else:
        business_id = request.headers.get('business_id')
        device_token = json.loads(request.data)
        print('device_token', device_token)
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
            print("could not validate drinkEtag")
            for drink in drinks:
                drinkDTO = {}
                drinkDTO['drink'] = drink.dto_serialize()
                drink_list.append(drinkDTO)
            response['drinks'] = drink_list

            etag = ETag_Service().get_etag("drink")
            headers["e-tag-id"] = str(etag.id)
            headers["e-tag-category"] = etag.category
        else:
            print('drink Etag exists but it was validated')
    else:
        print('no client drink Etag')
        etag = ETag_Service().get_etag("drink")
        headers["e-tag-id"] = str(etag.id)
        headers["e-tag-category"] = etag.category

    return Response(status=200, response=json.dumps(response), headers=headers)


@app.route('/order/<string:session_token>', methods=['POST', 'GET', 'OPTIONS', 'PUT'])
def orders(session_token):
    headers = {}
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    response = {}
    headers["Access-Control-Allow-Origin"] = request.origin
    headers["Access-Control-Allow-Headers"] = request.headers.get(
        'Access-Control-Request-Headers')
    headers["Access-Control-Allow-Credentials"] = "true"

    headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Origin"
    headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Credentials"
    headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Headers"
    if request.method == 'PUT':
        order_to_update = json.loads(request.data)
        if order_to_update["refunded"] == True:
            # 1. send push notification to device
            device_token = Customer_Service().get_device_token(
                order_to_update["customer_id"])
            send_apn(device_token, 'order_refunded')
            Order_Service().refund_stripe_order(order_to_update)
        elif order_to_update["completed"] == True:
            # 1. send push notification to device saying the order is ready
            # device_token = Customer_Service.get_device_token(order_to_update.customer_id)
            device_token = Customer_Service().get_device_token(
                order_to_update["customer_id"])
            send_apn(device_token, 'order_completed', 'sandbox')
            # send_apn(device_token, "order_ready")

        Order_Service().update_order(order_to_update)
        return Response(status=200)
    elif request.method == 'POST':
        new_order = request.json
        updated_order = Order_Service().create_order(new_order)
        print("updated_order.dto_serialize()", updated_order.dto_serialize())
        business_device_token = Business_Service(
        ).get_device_token(new_order["business_id"])

        send_fcm(business_device_token, new_order)
        response['order'] = updated_order.dto_serialize()
        return Response(status=200, response=json.dumps(response))
    elif request.method == 'OPTIONS':
        return Response(status=200, headers=headers)
    elif request.method == "GET":
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

            # elif filter_orders_by == 'customer':
            #     orders = Order_Service().get_merchant_orders(username=username)
        response['orders'] = orders

        return Response(status=200, response=json.dumps(response), headers=headers)


def send_info_email(jwt_token, email_type, user=None):
    # host = request.headers.get('Host')
    # host = '192.168.1.192:3000'

    if email_type == "quick_pass_link":
        host = '192.168.1.192:3000'
        button_url = f"https://{host}/bouncer-quick-pass/{jwt_token}/{user.business_id}"

        logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

        queue_page_button = f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin-right: auto; margin-top:5vh; margin-left:auto; margin-bottom:2vh;   border-collapse:separate;line-height:100%;"><tr><td><div><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://www.activecampaign.com" style="height:40px;v-text-anchor:middle;width:130px;" arcsize="5%" strokecolor="#8682E6" fillcolor="#8682E6;width: 130;"><w:anchorlock/><center style="color:#ffffff;font-family:Helvetica, sans-serif;font-size:18px; font-weight: 600;">QuickPass Page</center></v:roundrect><![endif]--><a href={button_url} style="display: inline-block; mso-hide:all; background-color: #8682E6; color: #FFFFFF; border:1px solid #8682E6; border-radius: 6px; line-height: 220%; width: 200px; font-family: Helvetica, sans-serif; font-size:18px; font-weight:600; text-align: center; text-decoration: none; -webkit-text-size-adjust:none;" target="_blank">QuickPass page</a></a></div></td></tr></table>'
        mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey {user.first_name.capitalize()},</p><p style="margin-top: 15px;margin-bottom: 15px;">Click the button below to access the QuickPass page.</p><p style="margin-top: 15px;margin-bottom: 15px;">Please click the button below to verify your account.</p><br /><p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div><div style="width:100%; height:3vh;">{queue_page_button}</div>'
        mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"><img src="{logo}" style="width:50%; height:12%; margin-right:auto; margin-left:auto" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

        sender_address = 'confirmation@quickbev.us'
        email = user.id

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = user.id

        message['Subject'] = 'QuickPass Page Link'  # The subject line

        mail_content = mail_body
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'html'))
        s = smtplib.SMTP('smtp.mailgun.org', 587)
        # this password was generated ay the domain settings page on mailgun. its a really shitty confusing service.
        s.login('postmaster@quickbev.us',
                '77bf9d60999ee72f1f72f98dd1a57152-1f1bd6a9-a4533d5f')
        s.sendmail(message['From'], message['To'], message.as_string())
        s.quit()


def send_confirmation_email(jwt_token, email_type, user=None, business=None, stripe_account_status=None, bouncer_id=None):
    host = request.headers.get('Host')
    if email_type == "customer_confirmation":
        button_url = f"https://{host}/verify-email/{jwt_token}"

        logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

        verify_button = f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin-right: auto; margin-top:5vh; margin-left:auto; margin-bottom:2vh;   border-collapse:separate;line-height:100%;"><tr><td><div><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://www.activecampaign.com" style="height:40px;v-text-anchor:middle;width:130px;" arcsize="5%" strokecolor="#8682E6" fillcolor="#8682E6;width: 130;"><w:anchorlock/><center style="color:#ffffff;font-family:Helvetica, sans-serif;font-size:18px; font-weight: 600;">Click here!</center></v:roundrect><![endif]--><a href={button_url} style="display: inline-block; mso-hide:all; background-color: #8682E6; color: #FFFFFF; border:1px solid #8682E6; border-radius: 6px; line-height: 220%; width: 200px; font-family: Helvetica, sans-serif; font-size:18px; font-weight:600; text-align: center; text-decoration: none; -webkit-text-size-adjust:none;" target="_blank">Verify email</a></a></div></td></tr></table>'
        mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey {user.first_name.capitalize()},</p><p style="margin-top: 15px;margin-bottom: 15px;">Welcome to QuickBev!</p><p style="margin-top: 15px;margin-bottom: 15px;">Please click the button below to verify your account.</p><br /><p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div><div style="width:100%; height:3vh;">{verify_button}</div>'
        mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"><img src="{logo}" style="width:50%; height:12%; margin-right:auto; margin-left:auto" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

        sender_address = 'confirmation@quickbev.us'
        email = user.id

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

    elif email_type == "merchant_confirmation":
        logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

        mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey {user.first_name},</p><p style="margin-top: 15px;margin-bottom: 15px;">Welcome to QuickBev!</p><p style="margin-top: 15px;margin-bottom: 15px;">Below is the id of the business you just registered. You should write this down, it will be important for setting up your account.</p> <br /> <p>You will receive an email confirmation shortly with the shipping details for your tablet.</p> <br />Business Id: {business.id}</p><p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div>'
        mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"><img src="{logo}" style="width:50%; height:12%; margin-right:auto; margin-left:auto" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

        sender_address = 'confirmation@quickbev.us'
        email = user.id

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

    elif email_type == "staged_merchant_employee_confirmation":
        logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

        mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hello,</p><p style="margin-top: 15px;margin-bottom: 15px;">Welcome to QuickBev!</p><p style="margin-top: 15px;margin-bottom: 15px;">This email has been registered with Quickbev as a merchant employee. The Merchant who registered you is listed below.</p><br /><p>Merchant Name: {user.first_name} {user.last_name}</p><p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div>'
        mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"><img src="{logo}" style="width:50%; height:12%; margin-right:auto; margin-left:auto" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

        sender_address = 'confirmation@quickbev.us'
        email = user.id

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = email

        message['Subject'] = 'New Business Confirmation'  # The subject line

        mail_content = mail_body
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'html'))
        s = smtplib.SMTP('smtp.mailgun.org', 587)
        # this password was generated ay the domain settings page on mailgun. its a really shitty confusing service.
        s.login('postmaster@quickbev.us',
                '77bf9d60999ee72f1f72f98dd1a57152-1f1bd6a9-a4533d5f')
        s.sendmail(message['From'], message['To'], message.as_string())
        s.quit()
    elif email_type == "staged_bouncer_confirmation":
        host = '192.168.1.192:3000'
        logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"
        # button_url = f"https://{host}/bouncer/get-info/{jwt_token}"
        button_url = f"http://{host}/bouncer-email-confirmed/{jwt_token}"

        verify_button = f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin-right: auto; margin-top:5vh; margin-left:auto; margin-bottom:2vh;   border-collapse:separate;line-height:100%;"><tr><td><div><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://www.activecampaign.com" style="height:40px;v-text-anchor:middle;width:130px;" arcsize="5%" strokecolor="#8682E6" fillcolor="#8682E6;width: 130;"><w:anchorlock/></v:roundrect><![endif]--><a href={button_url} style="display: inline-block; mso-hide:all; background-color: #8682E6; color: #FFFFFF; border:1px solid #8682E6; border-radius: 6px; line-height: 220%; width: 200px; font-family: Helvetica, sans-serif; font-size:18px; font-weight:600; text-align: center; text-decoration: none; -webkit-text-size-adjust:none;" target="_blank">Verify email</a></a></div></td></tr></table>'
        mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hello,</p><p style="margin-top: 15px;margin-bottom: 15px;">Welcome to QuickBev!</p><p style="margin-top: 15px;margin-bottom: 15px;">This email has been registered with Quickbev as a bouncer. The Merchant who registered you is listed below.</p><p>Merchant Name: {user.first_name} {user.last_name}</p> <p> Please click the button below to confirm your email. You will then receive another email with a link to the QuickPass Page.<p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div><div style="width:100%; height:3vh;">{verify_button}</div>'
        mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"><img src="{logo}" style="width:50%; height:12%; margin-right:auto; margin-left:auto" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

        sender_address = 'confirmation@quickbev.us'
        email = bouncer_id
        print('email staged bouncer', email)

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = email

        # The subject line
        message['Subject'] = 'New Bouncer Email Confirmation'

        mail_content = mail_body
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'html'))
        s = smtplib.SMTP('smtp.mailgun.org', 587)
        # this password was generated ay the domain settings page on mailgun. its a really shitty confusing service.
        s.login('postmaster@quickbev.us',
                '77bf9d60999ee72f1f72f98dd1a57152-1f1bd6a9-a4533d5f')
        s.sendmail(message['From'], message['To'], message.as_string())
        s.quit()
    elif email_type == "business_confirmation":
        logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

        mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey {user.first_name.capitalize()},</p><p style="margin-top: 15px;margin-bottom: 15px;">Welcome to QuickBev!</p><p style="margin-top: 15px;margin-bottom: 15px;">Below is the id of the business you just registered. You should write this down, it will be important later.</p><br />Business Id: {business.id}</p> <br /> <p>You will receive an email confirmation shortly with the shipping details for your tablet.<p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div>'
        mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"><img src="{logo}" style="width:50%; height:12%; margin-right:auto; margin-left:auto" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

        sender_address = 'confirmation@quickbev.us'
        email = user.id

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = email

        message['Subject'] = 'New Business Confirmation'  # The subject line

        mail_content = mail_body
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'html'))
        s = smtplib.SMTP('smtp.mailgun.org', 587)
        # this password was generated ay the domain settings page on mailgun. its a really shitty confusing service.
        s.login('postmaster@quickbev.us',
                '77bf9d60999ee72f1f72f98dd1a57152-1f1bd6a9-a4533d5f')
        s.sendmail(message['From'], message['To'], message.as_string())
        s.quit()

    elif email_type == "merchant_sign_up_notification":
        logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

        mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey Peter and Blaise,</p><p style="margin-top: 15px;margin-bottom: 15px;">A new merchant just signed up!</p><p style="margin-top: 15px;margin-bottom: 15px;">Below is their name, business name, business address, business id, and stripe account status.</p><br />Merchant name: {user.first_name} {user.last_name}<br /> Business name: {business.name}<br /> Business address: {business.address}<br /> Business id: {business.id}<br /> Stripe account status: {stripe_account_status} </p><p style="margin-top: 15px; margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px; margin-bottom: 15px;">—The QuickBev Team</div>'
        mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

        sender_address = 'confirmation@quickbev.us'
        recipients = ['patardriscoll@gmail.com', 'bbucey@utexas.edu']

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = ", ".join(recipients)

        message['Subject'] = 'New Merchant'  # The subject line

        mail_content = mail_body
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'html'))
        s = smtplib.SMTP('smtp.mailgun.org', 587)
        # this password was generated ay the domain settings page on mailgun. its a really shitty confusing service.
        s.login('postmaster@quickbev.us',
                '77bf9d60999ee72f1f72f98dd1a57152-1f1bd6a9-a4533d5f')
        s.sendmail(message['From'], message['To'], message.as_string())
        s.quit()

    elif email_type == "add_business_notification":
        logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

        mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey Peter and Blaise,</p><p style="margin-top: 15px;margin-bottom: 15px;">A merchant just signed up a new business!</p><p style="margin-top: 15px;margin-bottom: 15px;">Below is their name, business name, business address, business id, and stripe account status.</p><br />Merchant name: {user.first_name} {user.last_name}<br /> Business name: {business.name}<br /> Business address {business.address}<br /> Business id {business.id} Stripe account status: {stripe_account_status} </p><p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div>'
        mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:50vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="width:100%; text-align:center; justify-content:center"><img src="{logo}" style="width:50%; height:12%; margin-right:auto; margin-left:auto" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:5vh;"></tr></div></div></div>'

        sender_address = 'confirmation@quickbev.us'
        recipients = ['patardriscoll@gmail.com', 'bbucey@utexas.edu']

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = ", ".join(recipients)

        message['Subject'] = 'New Business'  # The subject line

        mail_content = mail_body
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'html'))
        s = smtplib.SMTP('smtp.mailgun.org', 587)
        # this password was generated ay the domain settings page on mailgun. its a really shitty confusing service.
        s.login('postmaster@quickbev.us',
                '77bf9d60999ee72f1f72f98dd1a57152-1f1bd6a9-a4533d5f')
        s.sendmail(message['From'], message['To'], message.as_string())
        s.quit()


def send_password_reset_email(jwt_token, entity):
    host = request.headers.get('Host')
    # host = "quickbev.us.com"

    button_url = f"https://{host}/reset-password/{jwt_token}"

    logo = "https://storage.googleapis.com/my-new-quickbev-bucket/landscape-logo-purple.png"

    verify_button = f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin-right: auto; margin-top:5vh; margin-left:auto;   border-collapse:separate;line-height:100%;"><tr><td><div><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://www.activecampaign.com" style="height:40px;v-text-anchor:middle;width:130px;" arcsize="5%" strokecolor="#8682E6" fillcolor="#8682E6;width: 130;"><w:anchorlock/><center style="color:#ffffff;font-family:Helvetica, sans-serif;font-size:18px; font-weight: 600;">Click here!</center></v:roundrect><![endif]--><a href={button_url} style="display: inline-block; mso-hide:all; background-color: #8682E6; color: #FFFFFF; border:1px solid #8682E6; border-radius: 6px; line-height: 220%; width: 200px; font-family: Helvetica, sans-serif; font-size:18px; font-weight:600; text-align: center; text-decoration: none; -webkit-text-size-adjust:none;" target="_blank">Reset passsword</a></a></div></td></tr></table>'
    mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey {entity.first_name.capitalize()},</p><p style="margin-top: 15px;margin-bottom: 15px;">Having trouble logging in?</p><p style="margin-top: 15px;margin-bottom: 15px;">No worries. Click the button below to reset your password.</p><br /><p style="margin-top: 15px;margin-bottom: 15px;">Keep calm and carry on,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div><div style="width:100%">{verify_button}</div>'
    mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:5vh;"></tr><div style="width:calc(100% - 30px); height:45vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="display: flex; width:100%; text-align:center;"><img src="" style="width:50%; height:12%" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:10vh;"></tr></div></div></div>'

    sender_address = 'confirmation@quickbev.us'
    email = entity.id

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = email

    message['Subject'] = 'Reset Your Password'  # The subject line

    mail_content = mail_body
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    s = smtplib.SMTP('smtp.mailgun.org', 587)
    s.login('postmaster@sandbox471ef3a89bf64e819540bc75206062f2.mailgun.org',
            '44603d9d0e3864edd01989602e0db876-e49cc42c-7570439d')
    s.sendmail(message['From'], message['To'], message.as_string())
    s.quit()


# @app.route('/email')
# def email():
#     test_customer_json = {"id": "patardriscoll@gmail.com", "first_name": "peter", "last_name": "driscoll",
#                           "password": "iqo", "has_registered": False, "email_verified": False, "stripe_id": "abc"}
#     test_customer = Customer_Domain(customer_json=test_customer_json)
#     send_confirmation_email(jwt_token=jwt.encode(
#         {"sub": test_customer.id}, key=secret, algorithm="HS256"), customer=test_customer)
#     return Response(status=200)


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
        session_token = request.args.get('session_token')
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
            Customer_Service().update_device_token(
                device_token, generated_new_customer.id)
            jwt_token = jwt.encode(
                {"sub": generated_new_customer.id}, key=secret, algorithm="HS256")
            # send the hashed user ID as a crypted key embedded in the activation link for security
            headers["authorization-token"] = jwt_token
            send_confirmation_email(
                jwt_token=jwt_token, email_type="customer_confirmation", user=generated_new_customer)
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
            jwt_token=jwt_token, email_type="customer_confirmation", user=customer)
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


@app.route("/customer/device_token", methods=["GET"])
def update_device_token():
    device_token = request.headers.get("device_token")
    customer_id = request.headers.get("customer_id")
    if device_token and customer_id:
        Customer_Service().update_device_token(device_token, customer_id)
    return Response(status=200)



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
        send_apn(device_token, "email", 'sandbox')
        response = {"msg": "successfully registered"}
        return Response(response=json.dumps(response), status=200)
    else:
        response = {"msg": "customer not found"}
        return Response(response=json.dumps(response), status=400)


@app.route('/reset-password/<string:entity_id>', methods=['POST', 'GET', 'OPTIONS'])
def reset_password(entity_id):
    if request.method == 'OPTIONS':
        headers = {}
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    if request.method == 'GET':
        entity_type = request.headers.get("entity")
        entity = ""
        if entity_type == "customer":
            entity = Customer_Service().get_customer(entity_id)
        elif entity_type == "merchant":
            entity = Merchant_Service().get_merchant(entity_id)
        if entity:
            jwt_token = jwt.encode(
                {"sub": entity_id}, key=secret, algorithm="HS256")
            send_password_reset_email(
                jwt_token=jwt_token, entity=entity)
            return Response(status=200)
    elif request.method == 'POST':
        jwt_token = entity_id
        if jwt.decode(jwt_token, secret, algorithms=["HS256"]):
            new_password = json.loads(request.data)
            Customer_Service().update_password(entity_id, new_password)
            return Response(status=200, response=json.dumps({"msg": "password reset"}))
        else:
            return Response(status=400, response=json.dumps({"msg": "error"}))


@app.route('/business/<string:session_token>', methods=['GET', 'POST', 'OPTIONS'])
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
        if request.headers.get('merchant-id'):
            merchant_id = request.headers.get('merchant-id')
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
        else:
            businesses = Business_Service().get_businesses()
            client_etag = json.loads(request.headers.get("If-None-Match"))
            if client_etag:
                if not ETag_Service().validate_etag(client_etag):
                    for business in businesses:
                        # turn into dictionaries
                        businessDTO = {}
                        businessDTO['business'] = business.dto_serialize()
                        business_list.append(businessDTO)
                    response['businesses'] = business_list

                    etag = ETag_Service().get_etag("business")
                    headers["e-tag-category"] = etag.category
                    headers["e-tag-id"] = str(etag.id)
                else:
                    print('client etag exists but it was validated')
            else:
                print('no client etag')
                etag = ETag_Service().get_etag("business")
                headers["e-tag-category"] = etag.category
                headers["e-tag-id"] = str(etag.id)
            return Response(status=200, response=json.dumps(response), headers=headers)

    elif request.method == 'POST':
        requested_business = json.loads(request.form.get("business"))
        new_business = Business_Service().add_business(requested_business)
        merchant = Merchant_Service().get_merchant(new_business.merchant_id)
        if new_business:
            ETag_Service().update_etag("business")
            headers["jwt_token"] = jwt.encode(
                {"sub": new_business.merchant_id}, key=secret, algorithm="HS256")
            send_confirmation_email(
                jwt_token=headers["jwt_token"], email_type="business_confirmation", user=merchant, business=new_business)
            stripe_account_status = Merchant_Service(
            ).authenticate_merchant_stripe(merchant.stripe_id)
            send_confirmation_email(
                jwt_token=headers["jwt_token"], email_type="add_business_notification", user=merchant, business=new_business, stripe_account_status=stripe_account_status)
            response['confirmed_new_business'] = new_business.dto_serialize()
            if 'file' not in request.files:
                response["msg"] = "No file part in request"
                return Response(status=200, response=json.dumps(response), headers=headers)

            file = request.files['file']
            # merchant does not select file
            if file.filename == '':
                response["msg"] = "No file file uploaded"
                return Response(status=200, response=json.dumps(response), headers=headers)

            if file:
                Google_Cloud_Storage_API().upload_menu_file(file, new_business.id)
                response["msg"] = "File successfully uploaded!"
                return Response(status=200, response=json.dumps(response), headers=headers)
        response["msg"] = "An unknown internal server error occured"
        return Response(status=500, response=json.dumps(response), headers=headers)


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
    client_secret = Order_Service().create_stripe_payment_intent(request_data)
    response["secret"] = client_secret["secret"]
    response["payment_intent_id"] = client_secret["payment_intent_id"]
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

        new_merchant = Merchant_Service().add_merchant(requested_merchant)
        new_business = Business_Service().add_business(requested_business)
        if new_merchant and new_business:
            ETag_Service().update_etag("business")
            headers["jwt_token"] = jwt.encode(
                {"sub": new_merchant.id}, key=secret, algorithm="HS256")
            send_confirmation_email(
                jwt_token=headers["jwt_token"], email_type="merchant_confirmation", user=new_merchant, business=new_business)
            stripe_account_status = Merchant_Service(
            ).authenticate_merchant_stripe(new_merchant.stripe_id)
            send_confirmation_email(
                jwt_token=headers["jwt_token"], email_type="merchant_sign_up_notification", user=new_merchant, business=new_business, stripe_account_status=stripe_account_status)
            response['confirmed_new_business'] = new_business.dto_serialize()
            response['confirmed_new_merchant'] = new_merchant.dto_serialize()
            if 'file' not in request.files:
                response["msg"] = "No file part in request"
                return Response(status=200, response=json.dumps(response), headers=headers)

            file = request.files['file']
            # merchant does not select file
            if file.filename == '':
                response["msg"] = "No file file uploaded"
                return Response(status=200, response=json.dumps(response), headers=headers)

            if file:
                Google_Cloud_Storage_API().upload_menu_file(file, new_business.id)
                response["msg"] = "File successfully uploaded!"
                return Response(status=200, response=json.dumps(response), headers=headers)

        response["msg"] = "An unknown internal server error occured"
        return Response(status=500, response=json.dumps(response), headers=headers)


@app.route('/merchant_employee_stripe_account', methods=['GET', 'OPTIONS'])
def merchant_employee_stripe_account():
    headers = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')

        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    merchant_employee_id = request.args.get('merchant_employee_id')
    stripe_id = Merchant_Employee_Service().get_stripe_account(merchant_employee_id)
    account_links = stripe.AccountLink.create(
        account=stripe_id,
        refresh_url='http://192.168.1.192:3000/merchant-employee-payout-setup-callback',
        return_url='http://192.168.1.192:3000/merchant-employee-payout-setup-complete',
        # refresh_url='https://quickbev.us/merchant-employee-payout-setup-callback',
        # return_url='https://quickbev.us/merchant-employee-payout-setup-complete',
        type='account_onboarding',
    )
    headers["stripe_id"] = stripe_id
    headers["Access-Control-Allow-Origin"] = request.origin
    headers["Access-Control-Expose-Headers"] = "*"

    response = Response(status=200, response=json.dumps(
        account_links), headers=headers)
    return response


@app.route('/merchant_employee/stripe_id', methods=['GET'])
def merchant_employee_stripe_id_authenticate():
    merchant_employee_stripe_id = request.headers.get("stripe-id")
    status = Merchant_Employee_Service().authenticate_merchant_employee_stripe(
        merchant_employee_stripe_id)
    if status:
        return Response(status=200)
    else:
        return Response(status=400)


@app.route('/merchant_employee/<string:session_token>', methods=['POST', 'OPTIONS', 'GET'])
def merchant_employee(session_token):
    headers = {}
    response = {}
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    elif request.method == 'POST':
        request_json = json.loads(request.data)
        requested_new_merchant_employee = request_json['merchant']
        quick_pass_initial_values = request_json['quick_pass_initial_values']
        new_merchant_employee = Merchant_Employee_Service(
        ).add_merchant_employee(requested_new_merchant_employee)
        Quick_Pass_Service().set_business_quick_pass(quick_pass_initial_values)
        return Response(status=200, response=json.dumps(new_merchant_employee.dto_serialize()))
    elif request.method == 'GET':
        merchant_id = request.headers.get('merchant_id')
        merchant_employees = [x.dto_serialize(
        ) for x in Merchant_Employee_Service().get_merchant_employees(merchant_id)]
        if len(merchant_employees) < 1:
            dummy_merchant_employee = Merchant_Employee_Domain()
            merchant_employees.append(dummy_merchant_employee.dto_serialize())
        response["merchant_employees"] = merchant_employees
        return Response(status=200, response=json.dumps(response))


@app.route('/merchant_employee', methods=['POST', 'GET', 'OPTIONS'])
def validate_merchant_employee():
    headers = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    # check to see if the merchant username already exists during account creation
    if request.method == 'GET':
        merchant_employee_username = request.args.get('merchant_employee_id')
        merchant_employee_username_status = Merchant_Employee_Service(
        ).authenticate_username(merchant_employee_username)
        print('merchant_employee_username_status',
              merchant_employee_username_status)
        # the requested username is already assigned to a merchant employee
        if merchant_employee_username_status == 0:
            return Response(status=400)
        # the requested username is not assigned to a staged merchant employee or a real merchant employee thus is available. this will be used for a merchant to register a staged merchant employee
        elif merchant_employee_username_status == 1:
            return Response(status=200)
        # the requested username is already assigned to a staged merchant employee but not a real merchant employee. this will be used by the tablet to confirm the merchant employee has been pre-authorized. it will return a jwt_token
        elif merchant_employee_username_status == 2:
            jwt_token = jwt.encode(
                {"sub": merchant_employee_username}, key=secret, algorithm="HS256")
            headers["jwt_token"] = jwt_token
            return Response(status=204, headers=headers)


@app.route('/bouncer/<string:session_token>', methods=['POST', 'OPTIONS', 'GET'])
def bouncer(session_token):
    headers = {}
    response = {}
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    elif request.method == 'POST':
        # request_json = json.loads(request.data)
        # requested_new_bouncer = request_json['merchant']
        # new_bouncer = Bouncer_Service(
        # ).add_bouncer(requested_new_bouncer)
        status = jwt.decode(session_token, secret, algorithms=["HS256"])
        if not status:
            return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
        # verify the hashed username that was embedded in the verification link
        bouncer_id = status["sub"]
        print('bouncer_id',bouncer_id)

        new_bouncer = Bouncer_Service(
        ).add_bouncer(bouncer_id)
        jwt_token = jwt.encode(
        {"sub": bouncer_id}, key=secret, algorithm="HS256")

        send_info_email(jwt_token=jwt_token,
                    email_type="quick_pass_link", user=new_bouncer)
        return Response(status=200, response=json.dumps(new_bouncer.dto_serialize()))
    elif request.method == 'GET':
        merchant_id = request.headers.get('merchant_id')
        bouncers = [x.dto_serialize(
        ) for x in Bouncer_Service().get_bouncers(merchant_id)]
        if len(bouncers) < 1:
            dummy_bouncer = Bouncer_Domain()
            bouncers.append(dummy_bouncer.dto_serialize())
        response["bouncers"] = bouncers
        return Response(status=200, response=json.dumps(response))


@app.route('/bouncer', methods=['POST', 'GET', 'OPTIONS'])
def validate_bouncer():
    headers = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    # check to see if the merchant username already exists during account creation
    if request.method == 'GET':
        bouncer_username = request.args.get('bouncer_id')
        bouncer_username_status = Bouncer_Service(
        ).authenticate_username(bouncer_username)
        print('bouncer_username_status',
              bouncer_username_status)
        # the requested username is already assigned to a merchant employee
        if bouncer_username_status == 0:
            return Response(status=400)
        # the requested username is not assigned to a staged merchant employee or a real merchant employee thus is available. this will be used for a merchant to register a staged merchant employee
        elif bouncer_username_status == 1:
            return Response(status=200)
        # the requested username is already assigned to a staged merchant employee but not a real merchant employee. this will be used by the tablet to confirm the merchant employee has been pre-authorized. it will return a jwt_token
        elif bouncer_username_status == 2:
            jwt_token = jwt.encode(
                {"sub": bouncer_username}, key=secret, algorithm="HS256")
            headers["jwt_token"] = jwt_token
            return Response(status=204, headers=headers)


@app.route('/bouncer/staging/<string:session_token>', methods=['POST', 'PUT', 'GET', 'OPTIONS'])
def add_staged_bouncer(session_token):
    headers = {}
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')

        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    elif request.method == "POST":
        bouncer = json.loads(request.data)
        print('bouncer', bouncer)
        merchant_id = bouncer["merchant_id"]
        merchant = Merchant_Service().get_merchant(merchant_id)
        new_staged_bouncer = Bouncer_Service().add_staged_bouncer(
            bouncer)
        jwt_token = jwt.encode(
            {"sub": bouncer["id"]}, key=secret, algorithm="HS256")
        send_confirmation_email(
            jwt_token=jwt_token, email_type="staged_bouncer_confirmation", user=new_staged_bouncer, bouncer_id=new_staged_bouncer.id)
        return Response(status=200)

    elif request.method == "PUT":
        data = json.loads(request.data)
        bouncer_id = data["bouncer_id"]
        Bouncer_Service().remove_staged_bouncer(bouncer_id)
        return Response(status=200)


@app.route('/merchant_employee/staging/<string:session_token>', methods=['POST', 'PUT', 'GET', 'OPTIONS'])
def add_staged_merchant_employee(session_token):
    headers = {}
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')

        headers["Access-Control-Expose-Headers"] = "*"
        return Response(status=200, headers=headers)
    elif request.method == "POST":
        data = json.loads(request.data)
        merchant_employee_id = data["email"]
        merchant_id = data["merchantId"]
        merchant = Merchant_Service().get_merchant(merchant_id)
        Merchant_Employee_Service().add_staged_merchant_employee(
            merchant_id, merchant_employee_id)
        jwt_token = jwt.encode(
            {"sub": merchant_employee_id}, key=secret, algorithm="HS256")
        send_confirmation_email(
            jwt_token=jwt_token, email_type="staged_merchant_employee_confirmation", user=merchant)
        return Response(status=200)

    elif request.method == "PUT":
        data = json.loads(request.data)
        merchant_employee_id = data["merchant_employee_id"]
        Merchant_Employee_Service().remove_staged_merchant_employee(merchant_employee_id)
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
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
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


@app.route('/pin_number', methods=['POST'])
def authenticate_merchant_pin_number():
    headers = {}
    data = json.loads(request.data)
    pin_number = data['pin_number']
    print('pin_number', pin_number)
    entity_id = data['email']
    business_id = data['business_id']
    print('business_id', business_id)
    login_status = data['logged_in']
    new_merchant_employee = Merchant_Employee_Service().authenticate_pin_number(
        entity_id, pin_number, login_status)
    if new_merchant_employee != False:
        # have to reset the pin number otherwise it will be the hashed version
        new_merchant_employee.pin_number = pin_number
        headers["jwt_token"] = jwt.encode(
            {"sub": new_merchant_employee.id}, key=secret, algorithm="HS256")
        return Response(status=200, response=json.dumps(new_merchant_employee.dto_serialize()), headers=headers)
    else:
        # the pin number might be for the merchant
        merchant_pin_status = Business_Service(
        ).authenticate_merchant_pin_number(business_id, pin_number)
        if merchant_pin_status:
            return Response(status=204)
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
    response = {}
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
        validate = request.headers.get('validate')
        merchant = ''

        # this will be to check if the merchant email is already registered in the system
        if validate:
            merchant = merchant = Merchant_Service().validate_merchant(username)
        # this is for signing in purposes
        else:
            # if the merchant exists it will return False, if it doesn't it will return True
            merchant = Merchant_Service().authenticate_merchant(username, password)
        if merchant:
            jwt_token = jwt.encode(
                {"sub": merchant.id}, key=secret, algorithm="HS256")
            headers["jwt_token"] = jwt_token
            return Response(status=200, response=json.dumps(merchant.dto_serialize()), headers=headers)
        else:
            response["msg"] = "customer not found"
            return Response(status=204, response=json.dumps(response), headers=headers)


@app.route('/merchant/pin_number/<string:session_token>', methods=['POST'])
def authenticate_pin_number(session_token):
    headers = {}
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    data = json.loads(request.data)
    pin_number = data['pin_number']
    business_id = data['business_id']
    Business_Service().set_merchant_pin_number(
        business_id, pin_number)
    return Response(status=200)


@app.route('/business/capacity/<string:session_token>', methods=['POST'])
def business_capacity(session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    data = json.loads(request.data)
    business_capacity_status = data['capacity']
    business_id = data['business_id']
    Business_Service().update_business_capacity(
        business_id, business_capacity_status)
    return Response(status=200)


@app.route('/create-stripe-account', methods=['GET', 'OPTIONS'])
def create_stripe_account():
    headers = {}
    response = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "*"

        return Response(status=200, headers=headers)
    callback_stripe_id = request.args.get('stripe')
    account_links = ''
    if callback_stripe_id:
        account_links = stripe.AccountLink.create(
            account=callback_stripe_id,
            refresh_url='https://quickbev.us/payout-setup-callback',
            return_url='https://quickbev.us/home',
            # refresh_url='http://localhost:3000/payout-setup-callback',
            # return_url='http://localhost:3000/home',
            type='account_onboarding',
        )
        headers["stripe_id"] = callback_stripe_id
    else:
        new_account = Merchant_Service().create_stripe_account()
        account_links = stripe.AccountLink.create(
            account=new_account.id,
            refresh_url='https://quickbev.us/payout-setup-callback',
            return_url='https://quickbev.us/home',
            # refresh_url='http://localhost:3000/payout-setup-callback',
            # return_url='http://localhost:3000/home',
            type='account_onboarding',
        )
        headers["stripe_id"] = new_account.id

    headers["Access-Control-Allow-Origin"] = request.origin
    headers["Access-Control-Expose-Headers"] = "*"
    response = Response(status=200, response=json.dumps(
        account_links), headers=headers)
    return response


@app.route('/validate-merchant-stripe-account', methods=['GET', 'OPTIONS'])
def validate_merchant_stripe_account():
    headers = {}
    response = {}
    if request.method == 'OPTIONS':
        headers["Access-Control-Allow-Origin"] = request.origin
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
        headers["Access-Control-Expose-Headers"] = "*"

        return Response(status=200, headers=headers)
    elif request.method == 'GET':
        callback_stripe_id = request.args.get('stripe')
        merchant_stripe_status = Merchant_Service(
        ).authenticate_merchant_stripe(callback_stripe_id)
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
        drink_image_file_exists = json.loads(request.form.get("selectedFile"))
        drink_image_file_names = json.loads(
            request.form.get("selectedFileName"))
        business_id = json.loads(request.form.get("businessId"))

        new_drinks = [{"name": x} for x in drink_names]
        for i in range(len(new_drinks)):
            drink = new_drinks[i]
            drink["description"] = drink_descriptions[i]
            drink["price"] = float(drink_prices[i])
            drink["has_image"] = drink_image_file_exists[i]

        added_drinks = Drink_Service().add_drinks(business_id, new_drinks)
        ETag_Service().update_etag("drink")
        files = request.files
        drinks_with_images = [
            x for x in added_drinks if x.has_image == True]
        if 'selectedFile' in files:
            multi_dict_files = MultiDict(files).getlist('selectedFile')
            for i in range(len(multi_dict_files)):
                file = multi_dict_files[i]
                # file_type = file.filename.split('.')[1]
                # if file_type != 'jpg':
                #     file.filename = file.filename.split('.')[0] + '.jpg'
                drink = drinks_with_images[i]

                # update the drink image url for each drink, keeping the proper index intact by extracting only drinks with an image
                drink.set_image_url(file.filename)
                drink.file = file
                Google_Cloud_Storage_API().upload_drink_image_file(drink)
                response["msg"] = "File successfully uploaded!"
            Drink_Service().update_drinks(drinks_with_images)
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


@app.route('/quick_pass/<string:session_token>', methods=['POST', 'PUT', 'GET', 'OPTIONS'])
def quick_pass(session_token):
    response = {}
    headers = {}
    headers["Access-Control-Allow-Origin"] = request.origin
    headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')

    headers["Access-Control-Expose-Headers"] = "*"
    if request.method == 'OPTIONS':
        return Response(status=200, headers=headers)
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    if request.method == 'PUT':
        if request.headers.get('entity') == 'bouncer':
            quick_pass_to_update = json.loads(request.data)['quick_pass']
            Quick_Pass_Service().update_quick_pass(quick_pass_to_update)
            return Response(status=200, headers=headers)
        else:
            quick_pass_values = json.loads(request.data)
            Quick_Pass_Service().set_business_quick_pass(quick_pass_values)
            return Response(status=200, headers=headers)

    elif request.method == 'POST':
        quick_pass = json.loads(request.data)
        updated_quick_pass = Quick_Pass_Service().add_quick_pass(quick_pass)
        response['quick_pass_order'] = updated_quick_pass.dto_serialize()
        return Response(status=200, response=json.dumps(response), headers=headers)
    elif request.method == 'GET':
        print('request.headers.g',request.headers.get('customer_id'))
        customer_id = request.headers.get('customer_id')
        print('customer_id',customer_id)
        business_id = request.headers.get('business_id')
        quick_pass = Quick_Pass_Service().get_current_queue(
            business_id=business_id, customer_id=customer_id)

        response["quick_pass"] = quick_pass.dto_serialize()
        return Response(status=200, response=json.dumps(response), headers=headers)

# get quickpasses for the bouncer to validate at the door. goes to front end page with list of active passes
@app.route('/quick_pass/bouncer', methods=['POST', 'PUT', 'GET', 'OPTIONS'])
def get_bouncer_quick_passes():
    headers = {}
    response = {}
    headers["Access-Control-Allow-Origin"] = request.origin
    headers["Access-Control-Allow-Headers"] = request.headers.get(
            'Access-Control-Request-Headers')
    headers["Access-Control-Expose-Headers"] = "*"
    if request.method == 'OPTIONS':
        return Response(status=200, headers=headers)
    if request.method == 'GET':
        business_id = request.headers.get("business_id")
        quick_passes = Quick_Pass_Service().get_quick_passes(business_id = business_id)
        # if len(quick_passes) <1:
        #     dummy_quick_pass = Quick_Pass_Domain()
        #     quick_passes.append(dummy_quick_pass)
        response['quick_passes'] = [x.dto_serialize() for x in quick_passes]
        print('response',response)
        return Response(status=200, headers=headers, response=json.dumps(response))


@app.route('/bouncer/verify_jwt', methods=['GET'])
def verify_bouncer_jwt():
    session_token = request.args.get("session_token")
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    else:
        return Response(status=200, response=json.dumps({"msg": "All good baby baby"}))


@app.route('/quick_pass/payment_intent/<string:session_token>', methods=['POST', 'PUT', 'GET'])
def quick_pass_payment_intent(session_token):
    response = {}
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))

    data = json.loads(request.data)
    quick_pass = data["quick_pass"]
    client_secret = Quick_Pass_Service().create_stripe_payment_intent(quick_pass)
    response["secret"] = client_secret["secret"]
    response["payment_intent_id"] = client_secret["payment_intent_id"]
    return Response(status=200, response=json.dumps(response))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port='5000')
