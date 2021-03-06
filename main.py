from flask import Flask, jsonify, Response, request, redirect, url_for, render_template
import requests
from models import app
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
from pushjack_http2 import APNSHTTP2SandboxClient, APNSAuthToken
from werkzeug.security import generate_password_hash, check_password_hash


merchant_menu_upload_folder = os.getcwd() + "/files"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = merchant_menu_upload_folder

stripe.api_key = "sk_test_51I0xFxFseFjpsgWvh9b1munh6nIea6f5Z8bYlIDfmKyNq6zzrgg8iqeKEHwmRi5PqIelVkx4XWcYHAYc1omtD7wz00JiwbEKzj"
secret = '3327aa0ee1f61998369e815c17b1dc5eaf7e728bca14f6fe557af366ee6e20f9'
# theme color RGB = rgb(134,130,230), hex = #8682E6
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

    client = APNSHTTP2SandboxClient(
        token=token,
        bundle_id='com.theQuickCompany.QuickBev')

    if action == "email":
        client.send(
            ids=[device_token],
            title="Email verified",
            message="Email verification complete. Lets get this party started",
            category="email"
        )
    # response = client.send(
    #     ids=[device_token],
    #     message="Your order is ready for pickup. Head to the pickup area.",
    #     content_available=False,
    #     title="Order Ready",
    #     category="order"
    # )


@app.route("/b")
def b():
    # test_service = Test_Service()
    # test_service.test_connection()
    instantiate_db_connection()
    return Response(status=200)
# this is called by the customer to update their device token after they have successfully logged in


@app.route('/apn-token/<string:customer_id>/<string:session_token>', methods=["POST"])
def apn_token(customer_id, session_token):
    device_token = request.headers.get("DeviceToken")
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    else:
        Customer_Service().update_device_token(device_token, customer_id)
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
        serialized_customer = customer.serialize()
        jwt_token = jwt.encode(
            {"sub": {serialized_customer["id"]}}, key=secret, algorithm="HS256")
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
    print('ETag_Service().validate_etag(client_etag) for drinks',
          ETag_Service().validate_etag(client_etag))
    if client_etag:
        if not ETag_Service().validate_etag(client_etag):
            for drink in drinks:
                drinkDTO = {}
                drinkDTO['drink'] = drink.dto_serialize()
                drink_list.append(drinkDTO)
            response['drinks'] = drink_list

            etag = ETag_Service().get_etag("drink")
            headers["E-tag-id"] = etag.id
            headers["E-tag-category"] = etag.category
    else:
        etag = ETag_Service().get_etag("drink")
        headers["E-tag-id"] = etag.id
        headers["E-tag-category"] = etag.category

    return Response(status=200, response=json.dumps(response), headers=headers)


@app.route('/order/<string:session_token>', methods=['POST', 'GET', 'OPTIONS'])
def orders(session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    response = {}
    order_service = Order_Service()
    if request.method == 'POST':
        new_order = request.json
        order_service = Order_Service()
        order_service.create_order(new_order)
        response['msg'] = 'you good bruh'
        return Response(status=200, response=json.dumps(response))
    if request.method == 'OPTIONS':
        header = {}
        header["Access-Control-Allow-Credentials"] = "true"
        return Response(status=200, headers=header)
    if request.method == "GET":
        header = {}
        header["Access-Control-Expose-Headers"] = "authorization"
        # header["Access-Control-Allow-Origin"] = "http://localhost:3000"
        header["Access-Control-Allow-Credentials"] = "true"
        username = base64.b64decode(
            request.headers.get(
                "Authorization").split(" ")[1]).decode("utf-8").split(":")[0]
        merchant_orders = order_service.get_orders(username=username)
        print('customer_orders', merchant_orders)
        response = {"orders": merchant_orders}
        return Response(status=200, response=json.dumps(response), headers=header)


def send_confirmation_email(jwt_token, customer, url):
    print('jwt_token', jwt_token)
    host = request.headers.get('Host')
    button_url = f"http://{host}/verify-email/{jwt_token}"

    logo = os.path.join(os.path.dirname(os.path.abspath(
        __file__)), "./src/static/landscape-logo-purple.png")

    with open(logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    verify_button = f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin-right: auto; margin-left:auto; margin-top:3vh; padding-right:30px; border-collapse:separate;line-height:100%;"><tr><td><div><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://www.activecampaign.com" style="height:40px;v-text-anchor:middle;width:130px;" arcsize="5%" strokecolor="#19cca3" fillcolor="#19cca3;width: 130;"><w:anchorlock/><center style="color:#ffffff;font-family:Helvetica, sans-serif;font-size:18px; font-weight: 600;">Click here!</center></v:roundrect><![endif]--><a href={button_url} style="display: inline-block; mso-hide:all; background-color: #19cca3; color: #FFFFFF; border:1px solid #19cca3; border-radius: 6px; line-height: 220%; width: 200px; font-family: Helvetica, sans-serif; font-size:18px; font-weight:600; text-align: center; text-decoration: none; -webkit-text-size-adjust:none;" target="_blank">Verify email!</a></a></div></td></tr></table>'
    mail_body_text = f'<p style="margin-top: 15px;margin-bottom: 15px;">Hey {customer.first_name},</p><p style="margin-top: 15px;margin-bottom: 15px;">Welcome to QuickBev!</p><p style="margin-top: 15px;margin-bottom: 15px;">Please click the link below to verify your account</p><br /><p style="margin-top: 15px;margin-bottom: 15px;">Let the good times begin,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div><div style="width:100%">{verify_button}</div>'
    mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:20vh;"></tr><div style="width:calc(100% - 30px); padding:30px 30px 30px 30px; background-color:white"><div  style="display: flex; width:100%; text-align:center;"><img src="data:image/png;base64,{encoded_string} style="width:50%; height:12%" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div></div></div></div>'

    sender_address = 'patardriscoll@gmail.com'
    email = 'patardriscoll@gmail.com'

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = email

    message['Subject'] = 'Order From'  # The subject line

    mail_content = mail_body
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    # Create SMTP session for sending the mail
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # s.connect('smtp.gmail.com', 587)
    s.starttls()

    s.login(user="patardriscoll@gmail.com", password="Iqopaogh23!")
    # s = smtplib.SMTP('smtp.mailgun.org', 587)
    # s.login('postmaster@crepenshake.com',
    #         '6695313d8a619bc44dce00ad7184960a-ba042922-f2a8cfbb')
    s.sendmail(message['From'], message['To'], message.as_string())
    s.quit()


def send_password_reset_email(jwt_token, customer):
    print('jwt_token', jwt_token)
    # host = request.headers.get('Host')
    host = "quickbev.uc.r.appspot.com"

    button_url = f"https://{host}/reset-password/{jwt_token}"

    logo = os.path.join(os.path.dirname(os.path.abspath(
        __file__)), "./src/static/landscape-logo-purple.png")

    with open(logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    verify_button = f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin-right: auto; margin-top:5vh; margin-left:auto;   border-collapse:separate;line-height:100%;"><tr><td><div><!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="http://www.activecampaign.com" style="height:40px;v-text-anchor:middle;width:130px;" arcsize="5%" strokecolor="#19cca3" fillcolor="#19cca3;width: 130;"><w:anchorlock/><center style="color:#ffffff;font-family:Helvetica, sans-serif;font-size:18px; font-weight: 600;">Click here!</center></v:roundrect><![endif]--><a href={button_url} style="display: inline-block; mso-hide:all; background-color: #19cca3; color: #FFFFFF; border:1px solid #19cca3; border-radius: 6px; line-height: 220%; width: 200px; font-family: Helvetica, sans-serif; font-size:18px; font-weight:600; text-align: center; text-decoration: none; -webkit-text-size-adjust:none;" target="_blank">Reset passsword</a></a></div></td></tr></table>'
    mail_body_text = f'<p style="margin-top: 3vh;margin-bottom: 15px;">Hey {customer.first_name},</p><p style="margin-top: 15px;margin-bottom: 15px;">Having trouble logging in?</p><p style="margin-top: 15px;margin-bottom: 15px;">No worries. Click the button below to reset your password.</p><br /><p style="margin-top: 15px;margin-bottom: 15px;">Keep calm and carry on,</p><p style="margin-top: 15px;margin-bottom: 15px;">—The QuickBev Team</p></div><div style="width:100%">{verify_button}</div>'
    mail_body = f'<div style="height: 100%;"><div style="width: 100%;height: 100%;background-color: #e8e8e8;"><div style="width: 100%;max-width: 500px;height: 80vh; margin-top: 0%;margin-bottom: 10%; margin-right:auto; margin-left:auto; background-color: #e8e8e8;"><tr style="width:100%;height:10vh;"></tr><div style="width:calc(100% - 30px); height:40vh; padding:30px 30px 30px 30px; background-color:white; margin-top:auto; margin-bottom:auto"><div style="display: flex; width:100%; text-align:center;"><img src="data:image/png;base64,{encoded_string} style="width:50%; height:12%" alt="img" /></div><div  style="margin-top: 30px;">{mail_body_text}</div><tr style="width:100%;height:10vh;"></tr></div></div></div>'

    sender_address = 'patardriscoll@gmail.com'
    email = 'patardriscoll@gmail.com'

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = email

    message['Subject'] = 'Order From'  # The subject line

    mail_content = mail_body
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    # Create SMTP session for sending the mail
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # s.connect('smtp.gmail.com', 587)
    s.starttls()

    s.login(user="patardriscoll@gmail.com", password="Iqopaogh23!")
    # s = smtplib.SMTP('smtp.mailgun.org', 587)
    # s.login('postmaster@crepenshake.com',
    #         '6695313d8a619bc44dce00ad7184960a-ba042922-f2a8cfbb')
    s.sendmail(message['From'], message['To'], message.as_string())
    s.quit()


@app.route('/guest-device-token', methods=['POST'])
def guest_device_token():
    headers = {}
    device_token = request.headers.get("DeviceToken")
    print('device_token', device_token)
    Customer_Service().add_guest_device_token(device_token)
    jwt_token = jwt.encode(
        {"sub": f'{device_token}'}, key=secret, algorithm="HS256")
    headers["authorization-token"] = jwt_token
    return Response(status=200, headers=headers)


@app.route('/customer', methods=['POST', 'GET', 'OPTIONS', 'PUT'])
def customer():
    response = {}
    headers = {}
    print(json.loads(request.data))
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
                {"sub": f'{generated_new_customer.id}'}, key=secret, algorithm="HS256")
            # send the hashed user ID as a crypted key embedded in the activation link for security
            headers["authorization-token"] = jwt_token
            send_confirmation_email(
                jwt_token, generated_new_customer, request.url)
            if generated_new_customer.has_registered:
                status = 201
            else:
                status = 200
            return Response(response=json.dumps(generated_new_customer.serialize()), status=status, headers=headers)
        else:
            return Response(status=400)
    elif request.method == 'PUT':
        customer = Customer_Domain(customer_json=json.loads(
            request.data))
        jwt_token = jwt.encode(
            {"sub": f'{customer.id}'}, key=secret, algorithm="HS256")
        send_confirmation_email(
            jwt_token, customer, request.url)
        return Response(status=200)
    elif request.method == 'OPTIONS':
        header = {}
        header["Access-Control-Allow-Credentials"] = 'true'
        return Response(status=200, headers=header)
    elif request.method == "GET":
        header = {}
        header["Access-Control-Expose-Headers"] = "authorization"
        # header["Access-Control-Allow-Origin"] = "http://localhost:3000"
        header["Access-Control-Allow-Credentials"] = 'true'
        merchant_id = base64.b64decode(
            request.headers.get(
                "Authorization").split(" ")[1]).decode("utf-8")
        customers = Customer_Service().get_customers(merchant_id=merchant_id)
        response = {"customers": customers}
        return Response(status=200, response=json.dumps(response), headers=header)


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


@app.route('/business/<string:session_token>', methods=['GET'])
def get_businesss(session_token):
    if not jwt.decode(session_token, secret, algorithms=["HS256"]):
        return Response(status=401, response=json.dumps({"msg": "Inconsistent request"}))
    response = {}
    headers = {}
    business_list = []
    businesss = Business_Service().get_businesss()
    client_etag = json.loads(request.headers.get("If-None-Match"))
    print()
    print('client_etag', client_etag)
    print()

    if client_etag:
        print('ETag_Service().validate_etag(client_etag)',
              ETag_Service().validate_etag(client_etag))
        if not ETag_Service().validate_etag(client_etag):
            for business in businesss:
                # turn into dictionaries
                businessDTO = {}
                businessDTO['business'] = business.dto_serialize()
                business_list.append(businessDTO)
                response['businesses'] = business_list

            etag = ETag_Service().get_etag("business")
            headers["E-tag-category"] = etag.category
            headers["E-tag-id"] = str(etag.id)
    else:
        etag = ETag_Service().get_etag("business")
        headers["E-tag-category"] = etag.category
        headers["E-tag-id"] = str(etag.id)
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
    print('request_data', request_data)
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
    print('request_data payment intent', request_data)
    order_service = Order_Service()
    client_secret = order_service.stripe_payment_intent(request_data)
    print('client_secret', client_secret)
    response["secret"] = client_secret
    print("r", response)
    return Response(status=200, response=json.dumps(response))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/signup', methods=['POST'])
def signup():
    response = {"msg": ""}
    # check if the post request has the file part
    requested_merchant = json.loads(request.form.get("merchant"))

    print('requested_merchant', requested_merchant)

    requested_business = json.loads(request.form.get("business"))

    print('requested_business', requested_business)

    merchant_service = Merchant_Service()
    business_service = Business_Service()

    new_merchant = merchant_service.add_merchant(requested_merchant)
    new_business = business_service.add_business(requested_business)
    if new_merchant and new_business:
        response['confirmed_new_business'] = new_business.dto_serialize()

        if 'file' not in request.files:
            response["msg"] = "No file part in request"
            return Response(status=200, response=json.dumps(response))

        file = request.files['file']
        # merchant does not select file
        if file.filename == '':
            response["msg"] = "No file file uploaded"
            return Response(status=200, response=json.dumps(response))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            response["msg"] = "File successfully uploaded!"
            return Response(status=200, response=json.dumps(response))
    else:
        response["msg"] = "An unknown internal server error occured"
        return Response(status=500, response=json.dumps(response))


@app.route('/signup-redirect', methods=['POST'])
def signup_redirect():
    response = {"msg": ""}
    header = {}
    business_service = Business_Service()
    request_json = json.loads(request.data)
    business_to_update = request_json["business"]
    if business_service.update_business(business_to_update):
        header["jwt_token"] = jwt.encode(
            {"sub": {business_to_update["id"]}}, key=secret, algorithm="HS256")
        response["msg"] = "Business sucessfully updated"
        return Response(status=200, response=json.dumps(response), headers=header)
    else:
        response["msg"] = "Failed to update business"
        return Response(status=500, response=json.dumps(response))


@app.route('/merchant', methods=['GET'])
def authenticate_merchant():
    header = {}
    username = request.headers.get('email')
    password = request.headers.get('password')
    response = {"msg": "customer not found"}
    merchant = Merchant_Service().authenticate_merchant(username, password)
    # if the merchant exists it will return False, if it doesn't it will return True
    if merchant:
        header["jwt_token"] = jwt.encode(
            {"sub": merchant.id}, key=secret, algorithm="HS256")
        header["Access-Control-Expose-Headers"] = "jwt_token"
        print('header', header)
        return Response(status=200, response=json.dumps(merchant.dto_serialize()), headers=header)
    else:
        return jsonify(response), 400


@app.route('/create-stripe-account', methods=['GET'])
def create_stripe_account():
    new_account = Merchant_Service().create_stripe_account()
    account_links = stripe.AccountLink.create(
        account=new_account.id,
        refresh_url='https://quickbev.uc.r.appspot.com/payout-setup-callback',
        return_url='https://quickbev.uc.r.appspot.com/home',
        type='account_onboarding',
    )
    header = {}
    header["Access-Control-Expose-Headers"] = "*"
    header["stripe_id"] = new_account.id
    response = Response(status=200, response=json.dumps(
        account_links), headers=header)
    return response


@app.route('/add-menu', methods=['POST'])
def add_menu():
    drink_service = Drink_Service()
    menu = json.loads(request.data)
    print('menu', menu)
    business_id = request.headers.get("business_id")
    print('business_id', business_id)
    response = Response(status=200, response=json.dumps(
        drink_service.add_drinks(business_id, menu)))
    return response


if __name__ == '__main__':
    # app.run(host="192.168.86.42", port=5000, debug=True)
    app.run(host='127.0.0.1', port=8080, debug=True)
