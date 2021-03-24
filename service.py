from domain import *
from repository import *
from models import db
import uuid
import os
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from models import instantiate_db_connection

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

#TODO add error message to tell user if they tried to upload a word doc or another doc to either convert it to a pdf or email the docuement to quickbev
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
            new_order_domain = Order_Domain(order_json=order)
            Order_Repository().post_order(session, new_order_domain)
            return

    def get_customer_orders(self, username):
        response = []
        with session_scope() as session:
            orders, drinks = Order_Repository().get_customer_orders(
                session, username)
            for order in orders:
                order_domain = Order_Domain(order_object=order, drinks=drinks)
                order_dto = order_domain.dto_serialize()
                response.append(order_dto)
            return response

    def get_merchant_orders(self, username):
        response = []
        with session_scope() as session:
            orders, drinks = Order_Repository().get_merchant_orders(
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
                return registered_new_customer_domain
            else:
                return False

    def get_customers(self, merchant_id):
        with session_scope() as session:
            # pheew this is sexy. list comprehension while creating a customer dto
            customers = [Customer_Domain(customer_object=x) for x in Customer_Repository().get_customers(
                session, merchant_id)]
            customers_without_passswords = []
            for customer in customers:
                new_customer_without_password = customer
                new_customer_without_password.password = None
                customers_without_passswords.append(
                    new_customer_without_password)
            return customers_without_passswords

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
    def get_businesses(self):
        with session_scope() as session:
            response = []
            for business in Business_Repository().get_businesess(session):
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

    def get_merchant_business(self, merchant_id):
        with session_scope() as session:
            response = []
            for business in Business_Repository().get_merchant_businesses(session, merchant_id):
                business_domain = Business_Domain(business_object=business)
                response.append(business_domain)
            return response


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
        self.connection_string_end = "@localhost: 5432/quickbevdb"
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

class PDF_Reader(object):
    import base64
    def encode(self, data):
        """
        Return base-64 encoded value of binary data.
        """
        return base64.b64encode(data)

    def decode(self, data):
        """
        Return decoded value of a base-64 encoded string.
        """
        return base64.b64decode(data.encode())

    def get_pdf_data(self, file):
        """
        Open pdf file in binary mode,
        return a string encoded in base-64.
        """
        with open(file.filename, 'rb') as file:
            return encode(file.read())

class Google_Cloud_Storage_API(object):
    def __init__(self):
        super().__init__()
          # Imports the Google Cloud client library
        from google.cloud import storage
        app.config['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.getcwd(),"quickbev-60da4e7ea092.json")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = app.config['GOOGLE_APPLICATION_CREDENTIALS']
        self.bucket_name = "my-new-quickbev-bucket" 
          # Instantiates a client
        self.storage_client = storage.Client()

        self.bucket = self.storage_client.bucket(self.bucket_name)
       
    def create_bucket(self):
        # The name for the new bucket
        bucket_name = "new-bucket"

        # Creates the new bucket
        bucket = self.storage_client.create_bucket(bucket_name)

        print("Bucket {} created.".format(bucket.name))

    def upload_blob(self, file, destination_blob_name):
        """Uploads a file to the bucket."""
        # bucket_name = "your-bucket-name"
        # file = "local/path/to/file" this will be the business folder, with a folder named after the business' unique id, which will have the menu file in it
        # destination_blob_name = "storage-object-name" this will be the business uuid
        from werkzeug.utils import secure_filename

        file_type = file.filename.rsplit('.', 1)[1].lower()
        destination_blob_name = "business/" + str(destination_blob_name) + "/menu" + "." + file_type
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], "tmp"))
        # file_location = os.path.join(app.config['UPLOAD_FOLDER'], "tmp")
        # if file_type == 'doc' or file_type == 'docx' or file_type == 'ppt' or file_type == 'pptx':
        #     print('docx')
        #     file.filename = destination_blob_name + "." + file_type
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # else:
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_file(file)
        return True
