# set up a scoped_session

import uuid
import os
# from models import Drink, Order, Order_Drink, Customer, Business, Tab, Stripe_Customer, Stripe_Account
from models import *
import stripe
from datetime import date
import requests
import base64
from sqlalchemy.sql import text
from sqlalchemy.inspection import inspect
from werkzeug.security import generate_password_hash, check_password_hash

stripe.api_key = "sk_test_51I0xFxFseFjpsgWvh9b1munh6nIea6f5Z8bYlIDfmKyNq6zzrgg8iqeKEHwmRi5PqIelVkx4XWcYHAYc1omtD7wz00JiwbEKzj"


class Drink_Repository(object):
    def get_drinks(self, session):
        drinks = session.query(Drink)
        return drinks

    def add_drinks(self, session, drink_list):
        for drink in drink_list:
            id = uuid.uuid4().hex
            new_drink = Drink(id=id, name=drink.name, description=drink.description,
                              price=drink.price, business_id=drink.business_id)
            session.add(new_drink)
        return True


class Order_Repository(object):
    def post_order(self, session, order):
        # calculate order values on backend to prevent malicious clients
        cost = 0
        subtotal = 0
        tip_amount = 0
        sales_tax = 0

        for drink in order.order_drink.order_drink:
            drink_cost = drink.price * drink.quantity
            subtotal += drink_cost
        subtotal = round(subtotal, 2)
        tip_amount = round(order.tip_percentage * subtotal, 2)
        sales_tax = round(subtotal * order.sales_tax_percentage, 2)
        cost = int(round(subtotal+tip_amount+sales_tax, 2) * 100)
        merchant_stripe_id = order.merchant_stripe_id
        service_fee = int(round(.1 * cost, 2) * 100)

        new_order = Order(id=order.id, customer_id=order.customer_id, merchant_stripe_id=order.merchant_stripe_id,
                          business_id=order.business_id, cost=cost, subtotal=subtotal, tip_percentage=order.tip_percentage, tip_amount=tip_amount, sales_tax=sales_tax, sales_tax_percentage=order.sales_tax_percentage, date_time=order.date_time, service_fee=service_fee)
        session.add(new_order)

        for each_order_drink in order.order_drink.order_drink:
            # create a unique instance of Order_Drink for the number of each type of drink that were ordered. the UUID for the Order_Drink is generated in the database
            for i in range(each_order_drink.quantity):
                new_order_drink = Order_Drink(
                    order_id=new_order.id, drink_id=each_order_drink.id)
                session.add(new_order_drink)
        return True

    def get_orders(self, session, username):
        orders = session.query(Order, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                               Business.address.label("business_address"), Business.name.label("business_name")).select_from(Order).join(Business, Order.business_id == Business.id).filter(Order.customer_id == username).all()
        drinks = session.query(Drink)
        return orders, drinks

    def create_stripe_ephemeral_key(self, session, request):
        customer = request['stripe_id']
        customer_bool = False
        if customer:
            confirm_customer_existence = session.query(Stripe_Customer).filter(
                Stripe_Customer.id == customer).first()
            # Lookup the customer in the database so that if they exist we can attach their stripe id to the Ephermeral key such that later when they create the payment intent it will include their payment methods
            if confirm_customer_existence:
                customer_bool = True
                key = stripe.EphemeralKey.create(
                    customer=customer, stripe_version=request['api_version'])
                header = None
                return key, header

        if not customer_bool:
            new_customer = stripe.Customer.create()
            new_stripe = Stripe_Customer(id=new_customer.id)
            session.add(new_stripe)
            stripe_header = {"stripe_id": new_customer.id}
            key = stripe.EphemeralKey.create(
                customer=new_customer.id, stripe_version=request['api_version'])
            return key, stripe_header

    def stripe_payment_intent(self, session, order):
        # formatting for stripe requires everything in cents
        amount = 0
        subtotal = 0
        tip_amount = 0
        sales_tax = 0

        for drink in order.order_drink.order_drink:
            drink_cost = drink.price * drink.quantity
            subtotal += drink_cost
        subtotal = round(subtotal, 2)
        tip_amount = round(order.tip_percentage * subtotal, 2)
        sales_tax = round(subtotal * order.sales_tax_percentage, 2)
        amount = int(round(subtotal+tip_amount+sales_tax, 2) * 100)
        merchant_stripe_id = order.merchant_stripe_id
        service_fee = int(round(.1 * amount, 2))

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            customer=order.customer.stripe_id,
            setup_future_usage='on_session',
            currency='usd',
            application_fee_amount=service_fee,
            transfer_data={
                'destination': f'{merchant_stripe_id}',
            }
        )

        # now we return the client secret to the front end which is used to pay for the order
        return payment_intent["client_secret"]


class Customer_Repository(object):
    def authenticate_customer(self, session, email, password):
      # check to see if the customer exists in the database by querying the Customer_Info table for the giver username and password
      # if they don't exist this will return a null value for customer which i check for in line 80

        for customer in session.query(Customer):
            if customer.id == email and check_password_hash(customer.password, password):
                return customer
        else:
            return False

    def authenticate_username(self, session, username, hashed_username):
        # if a username is passed then we query the db to verify it, if the hashed version is passed then we use the check_password_hash to verify it
        if username and not hashed_username:
            customer = session.query(Customer).filter(
                Customer.id == username).first()
            if customer:
                return True
            else:
                return False
        elif not username and hashed_username:
            for customer in session.query(Customer):
                if check_password_hash(hashed_username, customer.id):
                    return True
            return False

    def register_new_customer(self, session, customer):
        print('customer', customer.serialize())
        print('customer.id', customer.id)
        test_customer = session.query(Customer).filter(
            Customer.id == customer.id).first()
        test_stripe_id = session.query(Stripe_Customer).filter(
            Stripe_Customer.id == customer.stripe_id).first()
        if not test_customer and test_stripe_id:
            print(1)
            new_customer = Customer(id=customer.id, password=customer.password,
                                    first_name=customer.first_name, last_name=customer.last_name, stripe_id=test_stripe_id.id, email_verified=customer.email_verified)
            session.add(new_customer)
            return customer
        elif not test_customer and not test_stripe_id:
            print(2)
            new_customer = stripe.Customer.create()
            new_stripe = Stripe_Customer(id=new_customer.id)
            session.add(new_stripe)
            new_customer = Customer(id=customer.id, password=customer.password,
                                    first_name=customer.first_name, last_name=customer.last_name, stripe_id=new_stripe.id, email_verified=customer.email_verified)
            session.add(new_customer)
            return customer
        # if the customer that has been requested for registration from the front end is unverified then we overwrite the customer values with the new values and return True to let the front end know that this customer has previously attempted to have been registered but was never verified. that way if a customer never verfies the account can continue to be modified as necessary while still preserving its unverified state
        elif test_customer and test_customer.email_verified == False and not test_stripe_id:
            new_customer = stripe.Customer.create()
            new_stripe = Stripe_Customer(id=new_customer.id)
            session.add(new_stripe)
            test_customer.password = customer.password
            test_customer.first_name = customer.first_name
            test_customer.last_name = customer.last_name
            test_customer.stripe_id = new_stripe.id
            test_customer.has_registered = True
            return test_customer

        elif test_customer and test_customer.email_verified == False and test_stripe_id:
            test_customer.password = customer.password
            test_customer.first_name = customer.first_name
            test_customer.last_name = customer.last_name
            test_customer.stripe_id = customer.stripe_id
            test_customer.has_registered = True
            return test_customer
        else:
            return False

    def get_customers(self, session, merchant_id):
        customers = session.query(Customer.id, Customer.first_name, Customer.last_name).join(Order, Order.customer_id == Customer.id).join(Business, Business.id == Order.business_id).join(
            Merchant, Merchant.id == Business.merchant_id).filter(Business.merchant_id == merchant_id).distinct()
        return customers

    def update_device_token(self, session, device_token, customer_id):
        customer_to_update = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if customer_to_update:
            print()
            print('customer_to_update before token update',
                  customer_to_update.serialize)
            print()

            customer_to_update.device_token = device_token

            print('customer_to_update after token update',
                  customer_to_update.serialize)
            print()

            return True
        else:
            return False

    def get_device_token(self, session, customer_id):
        print('customer_id', customer_id)
        requested_customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        print('requested_customer', requested_customer)
        print('requested_customer.serialize', requested_customer.serialize)

        if requested_customer:
            device_token = requested_customer.device_token
            return device_token
        else:
            return False

    def add_guest_device_token(self, session, device_token):
        new_guest_device_token = Guest_Device_Token(id=device_token)
        exists = session.query(Guest_Device_Token).filter(
            Guest_Device_Token.id == device_token).first()
        if exists:
            return True
        else:
            session.add(new_guest_device_token)
            return True

    def update_email_verification(self, session, customer_id):
        requested_customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if requested_customer:
            requested_customer.email_verified = True
            return True
        else:
            return False

    def update_password(self, session, customer_id, new_password):
        requested_customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if requested_customer:
            requested_customer.password = generate_password_hash(new_password)
            return True
        else:
            return False

    def get_customer(self, session, customer_id):
        customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if customer:
            return customer
        else:
            return False


class Business_Repository(object):
    def get_businesss(self, session):
        businesses = session.query(Business).all()
        return businesses

    def add_business(self, session, business):
        # will have to plug in an API here to dynamically pull information (avalara probs if i can get the freaking credentials to work)
        new_business = Business(id=business.id, name=business.name, classification=business.classification, date_joined=date.today(
        ), sales_tax_rate=business.sales_tax_rate, merchant_id=business.merchant_id, street=business.street, city=business.city,
            state=business.state, zipcode=business.zipcode, address=business.address, tablet=business.tablet, phone_number=business.phone_number, merchant_stripe_id=business.merchant_stripe_id)
        session.add(new_business)
        return new_business

    def update_business(self, session, business):
        business_database_object_to_update = session.query(
            Business).filter(Business.id == business.id).first()
        if business_database_object_to_update:
            business_database_object_to_update.stripe_id = business.stripe_id
            return True
        else:
            return False


class Tab_Repository(object):
    def post_tab(self, session, tab):
        new_tab = Tab(id=tab.id, name=tab.name, business_id=tab.business_id, customer_id=tab.customer_id, address=tab.address, street=tab.street, city=tab.city, state=tab.state,
                      zipcode=tab.zipcode, suite=tab.suite, date_time=tab.date_time, description=tab.description, minimum_contribution=tab.minimum_contribution, fundraising_goal=tab.fundraising_goal)
        session.add(new_tab)
        return True


class Merchant_Repository(object):
    def create_stripe_account(self, session):
        new_account = stripe.Account.create(
            type="express",
            country="US"
        )
        new_stripe_account_id = Stripe_Account(id=new_account.id)
        new_merchant_stripe = Merchant_Stripe()
        session.add(new_stripe_account_id)
        return new_account

    def authenticate_merchant(self, session, email, password):
        for merchant in session.query(Merchant):
            if merchant.id == email and check_password_hash(merchant.password, password):
                return merchant
        else:
            return False

    def add_merchant(self, session, requested_merchant):
        new_merchant = Merchant(id=requested_merchant.id, password=requested_merchant.password, first_name=requested_merchant.first_name,
                                last_name=requested_merchant.last_name, phone_number=requested_merchant.phone_number, number_of_businesses=requested_merchant.number_of_businesses)
        new_merchant_stripe = Merchant_Stripe(
            merchant_id=requested_merchant.id, stripe_id=requested_merchant.stripe_id)
        session.add(new_merchant)
        session.add(new_merchant_stripe)
        return True


class ETag_Repository():
    def get_etag(self, session, category):
        etag = session.query(ETag).filter(ETag.category == category).first()
        return etag

    def update_etag(self, session, category):
        etag = session.query(ETag).filter(ETag.category == category).first()
        print('etag.id', etag.id)
        etag.id += 1
        print('etag.id', etag.id)
        return etag.id

    def validate_etag(self, session, etag):
        print('etag', etag)
        print('etag["category"]', etag["category"])
        print('etag["id"]', etag["id"])
        validation = session.query(ETag).filter(
            ETag.category == etag["category"], ETag.id == etag["id"]).first()
        print('validation', validation)
        if validation:
            return True
        else:
            return False


class Test_Service(object):
    def __init__(self):
        self.username = "postgres"
        self.password = "Iqopaogh23!"
        self.connection_string_beginning = "postgres://"
        self.connection_string_end = "@localhost:5432/crepenshakedb"
        self.connection_string = self.connection_string_beginning + \
            self.username + ":" + self.password + self.connection_string_end
        self.test_engine = create_engine(
            os.environ.get("DB_STRING", self.connection_string))

    def test_connection(self):
        inspector = inspect(self.test_engine)
        # use this if you want to trigger a reset of the database in GCP
        # if len(inspector.get_table_names()) > 0:
        if len(inspector.get_table_names()) == 0:
            instantiate_db_connection()
            self.test_engine.dispose()
            return
