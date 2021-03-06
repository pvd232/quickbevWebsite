from domain import *
from repository import *
from models import db
import uuid
import os
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager


username = "postgres"
password = "Iqopaogh23!"
connection_string_beginning = "postgres://"
connection_string_end = "@localhost:5432/quickbevdb"
connection_string = connection_string_beginning + \
    username + ":" + password + connection_string_end

# an Engine, which the Session will use for connection
# resources
drink_engine = create_engine(
    os.environ.get("DB_STRING", connection_string), pool_size=100, max_overflow=10)

# create a configured "Session" class
session_factory = sessionmaker(bind=drink_engine)

# create a Session
Session = scoped_session(session_factory)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        print("service exception", e)
        session.rollback()
        raise e
    finally:
        session.close()

    # now all calls to Session() will create a thread-local session


class Drink_Service(object):
    def get_drinks(self):
        response = []
        with session_scope() as session:
            for drink in Drink_Repository().get_drinks(session):
                drink_domain = Drink_Domain(drink_object=drink)
                response.append(drink_domain)
            return response

    def add_drinks(self, business_id, drinks):
        with session_scope() as session:
            new_drink_list = [Drink_Domain(
                drink_json=x, init=True) for x in drinks]
            for drink in new_drink_list:
                drink.business_id = business_id
            return Drink_Repository().add_drinks(session, new_drink_list)

    def get_drinks_etag(self):
        with session_scope() as session:
            return ETag_Domain(etag_object=ETag_Repository().get_etag(session, "drink"))

    def validate_etag(self, etag):
        return ETag_Repository().validate_etag(etag)


class Order_Service(object):
    def create_order(self, order):
        with session_scope() as session:
            print('order JSON', order)
            new_order_domain = Order_Domain(order_json=order)
            Order_Repository().post_order(session, new_order_domain)
            return

    def get_orders(self, username):
        response = []
        with session_scope() as session:
            orders, drinks = Order_Repository().get_orders(
                session, username)
            for order in orders:
                order_domain = Order_Domain(order_object=order, drinks=drinks)
                order_dto = order_domain.dto_serialize()
                response.append(order_dto)
            return response

    def create_stripe_ephemeral_key(self, request):
        with session_scope() as session:
            return Order_Repository().create_stripe_ephemeral_key(session, request)

    def stripe_payment_intent(self, request):
        with session_scope() as session:
            new_order_domain = Order_Domain(order_json=request["order"])
            return Order_Repository().stripe_payment_intent(session, new_order_domain)


class Customer_Service(object):
    def authenticate_customer(self, email, password):
        with session_scope() as session:
            customer_object = Customer_Repository().authenticate_customer(
                session, email, password)
            if customer_object:
                customer_domain = Customer_Domain(
                    customer_object=customer_object)
                return customer_domain
            else:
                return False

    def authenticate_username(self, username=None, hashed_username=None):
        with session_scope() as session:
            customer_object = Customer_Repository().authenticate_username(
                session, username, hashed_username)
            if customer_object:
                return True
            else:
                return False

    def register_new_customer(self, customer):
        with session_scope() as session:
            requested_new_customer = Customer_Domain(customer_json=customer)
            registered_new_customer = Customer_Repository().register_new_customer(
                session, requested_new_customer)
            if registered_new_customer:
                registered_new_customer_domain = Customer_Domain(
                    customer_object=registered_new_customer)
                print('registered_new_customer_domain',
                      registered_new_customer_domain.serialize())
                return registered_new_customer_domain
            else:
                return False

    def get_customers(self, merchant_id):
        with session_scope() as session:
            # pheew this is sexy. list comprehension while creating a customer dto
            customers = [Customer_Domain(customer_object=x).dto_serialize() for x in Customer_Repository().get_customers(
                session, merchant_id)]
            return customers

    def update_device_token(self, device_token, customer_id):
        with session_scope() as session:
            return Customer_Repository().update_device_token(session, device_token, customer_id)

    def get_device_token(self, customer_id):
        with session_scope() as session:
            return Customer_Repository().get_device_token(session, customer_id)

    def update_email_verification(self, customer_id):
        with session_scope() as session:
            return Customer_Repository().update_email_verification(session, customer_id)

    def add_guest_device_token(self, device_token):
        with session_scope() as session:
            return Customer_Repository().add_guest_device_token(session, device_token)

    def update_password(self, customer_id, new_password):
        with session_scope() as session:
            return Customer_Repository().update_password(session, customer_id, new_password)

    def get_customer(self, customer_id):
        with session_scope() as session:
            customer = Customer_Repository().get_customer(session, customer_id)
            if customer:
                return Customer_Domain(customer_object=Customer_Repository().get_customer(session, customer_id))
            else:
                return customer


class Merchant_Service(object):
    def create_stripe_account(self):
        with session_scope() as session:
            return Merchant_Repository().create_stripe_account(session)

    def authenticate_merchant(self, email, password):
        with session_scope() as session:
            merchant_object = Merchant_Repository().authenticate_merchant(
                session, email, password)
            if merchant_object:
                merchant_domain = Merchant_Domain(
                    merchant_object=merchant_object)
                return merchant_domain
            else:
                return False

    def add_merchant(self, merchant):
        with session_scope() as session:
            requested_new_merchant = Merchant_Domain(merchant_json=merchant)
            return Merchant_Repository().add_merchant(
                session, requested_new_merchant)


class Business_Service(object):
    def get_businesss(self):
        with session_scope() as session:
            response = []
            for business in Business_Repository().get_businesss(session):
                business_domain = Business_Domain(business_object=business)
                response.append(business_domain)
            return response

    def add_business(self, business):
        with session_scope() as session:
            business_domain = Business_Domain(business_json=business)
            business_database_object = Business_Repository().add_business(
                session, business_domain)
            if business_database_object:
                # the new business domain has a UUID that was created during initialization
                return business_domain
            else:
                return False

    def update_business(self, business):
        with session_scope() as session:
            business_domain = Business_Domain(business_json=business)
            return Business_Repository().update_business(session, business_domain)


class Tab_Service(object):
    def post_tab(self, tab):
        with session_scope() as session:
            new_tab_domain = Tab_Domain(tab_json=tab)
            return Tab_Repository().post_tab(session, new_tab_domain)


class ETag_Service(object):
    def get_etag(self, category):
        with session_scope() as session:
            return ETag_Domain(etag_object=ETag_Repository().get_etag(session, category))

    def validate_etag(self, etag):
        with session_scope() as session:
            return ETag_Repository().validate_etag(session, etag)

    def update_etag(self, category):
        with session_scope() as session:
            ETag_Repository().update_etag(session, category)


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
