from domain import *
from models import stripe_fee_percentage, service_fee_percentage, quick_pass_service_fee_percentage
import uuid
import os, time
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from models import instantiate_db_connection, stripe_fee_percentage, service_fee_percentage, quick_pass_service_fee_percentage
from repository import *
import inspect
should_diplay_expiration_time = True


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

# TODO add error message to tell user if they tried to upload a word doc or another doc to either convert it to a pdf or email the docuement to quickbev
# local_time_zone = datetime.utcnow().astimezone().tzinfo
# print('local_time_zone',local_time_zone)
# os.environ['TZ'] = str(local_time_zone)
# time.tzset()


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
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
        
    def get_merchant_drinks(self, merchant_id: str):
        with session_scope() as session:
            return [Drink_Domain(drink_object=x) for x in Drink_Repository().get_merchant_drinks(session=session, merchant_id=merchant_id)]


    def add_drinks(self, business_id, drinks):
        with session_scope() as session:
            new_drink_list = [Drink_Domain(
                drink_json=x, init=True) for x in drinks]
            for drink in new_drink_list:
                drink.business_id = business_id
                id = uuid.uuid4()
                drink.id = id
            return Drink_Repository().add_drinks(session, new_drink_list)

    def update_drinks(self, drinks):
        with session_scope() as session:
            return Drink_Repository().update_drinks(session, drinks)


class Order_Service(object):
    def get_customer_order_status(self, customer_id: str):
        with session_scope() as session:
            customer_order_status = [Customer_Order_Status(order_object=x).dto_serialize(
            ) for x in Order_Repository().get_customer_order_status(session, customer_id)]
            return customer_order_status

    def get_order(self, order_id: str):
        with session_scope() as session:
            order = Order_Repository().get_order(session, order_id)
            new_order_domain = Order_Domain(order_object=order, is_merchant_employee_order=True)
            return new_order_domain

    def update_order(self, order):
        with session_scope() as session:
            new_order_domain = Order_Domain(order_json=order, is_merchant_employee_order=True)
            Order_Repository().update_order(session, new_order_domain)

    def create_order(self, order):
        # calculate order values on backend to prevent malicious clients
        new_order_domain = Order_Domain(order_json=order, is_customer_order=True)

        # 1 subtotal is the sum of drink quantity to price
        subtotal = 0.0
        for order_drink in new_order_domain.order_drink:
            order_drink_cost = order_drink.price * order_drink.quantity
            subtotal += order_drink_cost

        # 2 tip is calculated on the subtotal
        tip_total = new_order_domain.tip_percentage * subtotal

        # 3 service fee base will include the tip because stripe includes this in their fee
        pre_service_fee_total = subtotal + tip_total

        # 4 service fee is calculated as % of pre service fee total
        service_fee_total = pre_service_fee_total * service_fee_percentage

        # 5 stripe application fee includes tip_total because the tip is transfered from the QuickBev account to the server
        stripe_application_fee_total = service_fee_total + tip_total

        # 6 sales tax is calcualted as % of subtotal + service fee because only tip is exempt from sales tax
        pre_sales_tax_total = pre_service_fee_total - tip_total + service_fee_total

        # 7 sales tax is calcualted as % of subtotal + service fee because only tip is exempt from sales tax
        sales_tax_total = pre_sales_tax_total * new_order_domain.sales_tax_percentage

        # 8 the customer is charge the top line value of sales tax + subtotal + tip + service fee, then stripe deducts their fee from the service fee, and the net result is paid out to quickbev
        total = subtotal + service_fee_total + sales_tax_total + tip_total

        # 9 stripe charge is calculated on pre stripe app fee total
        stripe_fee_total = (total * stripe_fee_percentage) + 0.30

        # 10 stripe charge is deducted from application fee, making the application fee net of the stripe charge and the tip_total which is later transfered to the server
        net_stripe_application_fee_total = stripe_application_fee_total - stripe_fee_total

        # 11 subtract out the tip_total which will be transfered from platform account to server connected account later
        net_service_fee_total = net_stripe_application_fee_total - tip_total

        # no need to set tip_percentage nor sales_tax_percentage because these values were sent from iOS device
        new_order_domain.service_fee_percentage = service_fee_percentage
        new_order_domain.stripe_fee_percentage = stripe_fee_percentage

        new_order_domain.subtotal = subtotal
        new_order_domain.tip_total = tip_total
        new_order_domain.service_fee_total = service_fee_total
        new_order_domain.stripe_application_fee_total = stripe_application_fee_total
        new_order_domain.sales_tax_total = sales_tax_total
        new_order_domain.total = total

        new_order_domain.stripe_fee_total = stripe_fee_total
        new_order_domain.net_stripe_application_fee_total = net_stripe_application_fee_total
        new_order_domain.net_service_fee_total = net_service_fee_total

        with session_scope() as session:
            return Order_Repository().create_order(session, new_order_domain)

    def get_customer_orders(self, username):
        response = []
        with session_scope() as session:
            orders = Order_Repository().get_customer_orders(session, username)
            for order in orders:
                order_domain = Order_Domain(order_object=order)
                order_dto = order_domain.dto_serialize()
                response.append(order_dto)
            return response

    def get_merchant_orders(self, username):
        response = []
        with session_scope() as session:
            orders = Order_Repository().get_merchant_orders(
                session, username)
            for order in orders:
                order_domain = Order_Domain(order_object=order, is_merchant_order=True)
                response.append(order_domain)
            return response

    def get_merchant_employee_orders(self, business_id):
        response = []
        with session_scope() as session:
            orders = Order_Repository().get_merchant_employee_orders(
                session, business_id)
            print('orders in merchant employee',orders)
            for order in orders:
                order_domain = Order_Domain(order_object=order, is_merchant_employee_order = True)
                response.append(order_domain)
            return response

    def create_stripe_ephemeral_key(self, request):
        with session_scope() as session:
            return Order_Repository().create_stripe_ephemeral_key(session, request)

    def create_stripe_payment_intent(self, request):
        new_order_domain = Order_Domain(order_json=request['order'], is_customer_order=True)

        # 1 subtotal is the sum of drink quantity to price
        subtotal = 0.0
        for order_drink_domain in new_order_domain.order_drink:
            drink_cost = order_drink_domain.price * order_drink_domain.quantity
            subtotal += drink_cost

        # 2 tip is calculated on the subtotal
        tip_total = new_order_domain.tip_percentage * subtotal

        # 3 service fee base will include the tip because stripe includes this in their fee
        pre_service_fee_total = subtotal + tip_total

        # 4 service fee is calculated as % of pre service fee total
        service_fee_total = pre_service_fee_total * service_fee_percentage

        # 5 stripe application fee includes tip_total because the tip is transfered from the QuickBev account to the server
        stripe_application_fee_total = service_fee_total + tip_total

        # 6 convert to stripe units (cents)
        stripe_units_application_fee_total = int(
            round(stripe_application_fee_total * 100, 2))

        # 7 sales tax is calcualted as % of subtotal + service fee because only tip is exempt from sales tax
        pre_sales_tax_total = pre_service_fee_total - tip_total + service_fee_total

        # 8 sales tax is calcualted as % of subtotal + service fee because only tip is exempt from sales tax
        sales_tax_total = pre_sales_tax_total * new_order_domain.sales_tax_percentage

        # 9 the customer is charge the top line value of sales tax + subtotal + tip + service fee, then stripe deducts their fee from the service fee, and the net result is paid out to quickbev
        total = subtotal + service_fee_total + sales_tax_total + tip_total

        # 10 stripe units
        stripe_units_total = int(round(100 * total, 2))

        merchant_stripe_id = new_order_domain.merchant_stripe_id
        payment_intent = stripe.PaymentIntent.create(
            amount=stripe_units_total,
            customer=new_order_domain.customer_stripe_id,
            setup_future_usage='on_session',
            currency='usd',
            application_fee_amount=stripe_units_application_fee_total,
            transfer_group=new_order_domain.id,
            transfer_data={
                "destination": merchant_stripe_id
            }
        )
        with session_scope() as session:
            servers = Merchant_Employee_Repository().get_servers(
                session, business_id=new_order_domain.business_id)
            for server in servers:
                tip_per_server = int(round(tip_total/len(servers), 2) * 100)
                stripe.Transfer.create(
                    amount=tip_per_server,
                    currency='usd',
                    destination=server.stripe_id,
                    transfer_group=new_order_domain.id,
                )
            response = {"payment_intent_id": payment_intent.id,
                        "secret": payment_intent["client_secret"]}
            return response

    def refund_stripe_order(self, order):
        with session_scope() as session:
            new_order_domain = Order_Domain(order_json=order)
            return Order_Repository().refund_stripe_order(new_order_domain)


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

    def validate_username(self, username=None, hashed_username=None):
        with session_scope() as session:
            customer_object = Customer_Repository().validate_username(
                session, username, hashed_username)
            if customer_object:
                return True
            else:
                return False

    def register_new_customer(self, customer):
        with session_scope() as session:
            requested_new_customer_domain = Customer_Domain(customer_json=customer)
            registered_new_customer = Customer_Repository().register_new_customer(
                session, requested_new_customer_domain)
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

    def get_customer_apple_id(self, apple_id):
        with session_scope() as session:
            customer = Customer_Repository().get_customer_apple_id(session, apple_id)
            if customer:
                return Customer_Domain(customer_object=customer)
            else:
                return customer

    def set_customer_apple_id(self, customer_id, apple_id):
        with session_scope() as session:
            return Customer_Repository().set_customer_apple_id(session=session, customer_id=customer_id, apple_id=apple_id)


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

    def validate_merchant(self, email):
        with session_scope() as session:
            status = Merchant_Repository().validate_merchant(session, email)
            if status:
                return Merchant_Domain(merchant_object=status)
            else:
                return False

    def authenticate_merchant_stripe(self, stripe_id):
        return Merchant_Repository().authenticate_merchant_stripe(stripe_id)

    def add_merchant(self, merchant):
        with session_scope() as session:
            requested_new_merchant = Merchant_Domain(merchant_json=merchant)
            return Merchant_Repository().add_merchant(
                session, requested_new_merchant)

    def get_merchant(self, merchant_id):
        with session_scope() as session:
            return Merchant_Domain(merchant_object=Merchant_Repository().get_merchant(session, merchant_id))


class Bouncer_Service(object):
    def add_bouncer(self, bouncer_id):
        with session_scope() as session:
            return Bouncer_Domain(bouncer_object=Bouncer_Repository().add_bouncer(
                session, bouncer_id))

    def validate_username(self, username):
        with session_scope() as session:
            return Bouncer_Repository().validate_username(
                session, username)

    def get_bouncers(self, merchant_id):
        with session_scope() as session:
            staged_bouncers, bouncers = Bouncer_Repository().get_bouncers(
                session, merchant_id)
            bouncer_domains = [Bouncer_Domain(
                bouncer_object=x) for x in bouncers]

            # when a merchant employee domain is created without a merchant employee object or merchant employee json the c
            staged_bouncer_domains = [
                Bouncer_Domain(bouncer_object=x, isStagedBouncer=True) for x in staged_bouncers]

            for staged_domain in staged_bouncer_domains:
                duplicate = False
                for bouncer_domain in bouncer_domains:
                    if bouncer_domain.id == staged_domain.id:
                        bouncer_domain.status = staged_domain.status
                        duplicate = True
                if duplicate == False:
                    bouncer_domains.insert(0, staged_domain)
            return bouncer_domains

    def add_staged_bouncer(self, bouncer):
        with session_scope() as session:
            return Bouncer_Domain(bouncer_object=Bouncer_Repository().add_staged_bouncer(session, Bouncer_Domain(bouncer_json=bouncer)), isStagedBouncer=True)

    def remove_staged_bouncer(self, bouncer_id):
        with session_scope() as session:
            return Bouncer_Repository().remove_staged_bouncer(session, bouncer_id)

    def get_bouncer(self, bouncer_id):
        with session_scope() as session:
            bouncer_domain = Bouncer_Domain(
                bouncer_object=Bouncer_Repository().get_bouncer(session, bouncer_id))
            return bouncer_domain


class Merchant_Employee_Service(object):
    def get_stripe_account(self, merchant_employee_id):
        with session_scope() as session:
            return Merchant_Employee_Repository().get_stripe_account(session, merchant_employee_id)

    def validate_pin(self, business_id, pin):
        with session_scope() as session:
            pin_status = Merchant_Employee_Repository().validate_pin(session,
                                                                     business_id, pin)
            return pin_status

    def authenticate_pin(self, pin, login_status):
        with session_scope() as session:
            merchant_employee_object = Merchant_Employee_Repository().authenticate_pin(
                session, pin, login_status)
            if merchant_employee_object:
                merchant_employee_domain = Merchant_Employee_Domain(
                    merchant_employee_object=merchant_employee_object)
                return merchant_employee_domain
            else:
                return False

    def reset_pin(self, merchant_employee_id, pin):
        with session_scope() as session:
            merchant_employee_object = Merchant_Employee_Repository().reset_pin(
                session, merchant_employee_id, pin)
            if merchant_employee_object:
                merchant_employee_domain = Merchant_Employee_Domain(
                    merchant_employee_object=merchant_employee_object)
                return merchant_employee_domain
            else:
                return False

    def add_merchant_employee(self, merchant_employee):
        with session_scope() as session:
            requested_new_merchant_employee = Merchant_Employee_Domain(
                merchant_employee_json=merchant_employee)
            return Merchant_Employee_Repository().add_merchant_employee(
                session, requested_new_merchant_employee)

    def validate_username(self, username):
        with session_scope() as session:
            return Merchant_Employee_Repository().validate_username(
                session, username)

    def authenticate_merchant_employee_stripe(self, stripe_id):
        with session_scope() as session:
            return Merchant_Employee_Repository().authenticate_merchant_employee_stripe(stripe_id)

    def get_merchant_employees(self, merchant_id):
        with session_scope() as session:
            staged_merchant_employees, merchant_employees = Merchant_Employee_Repository().get_merchant_employees(
                session, merchant_id)
            merchant_employee_domains = [Merchant_Employee_Domain(
                merchant_employee_object=x) for x in merchant_employees]
            for merchant_employee_domain in merchant_employee_domains:
                merchant_employee_domain.status = "confirmed"

            # when a merchant employee domain is created without a merchant employee object or merchant employee json it is a staged merchant employee
            staged_merchant_employee_domains = [
                Merchant_Employee_Domain() for x in staged_merchant_employees]
            for i in range(len(staged_merchant_employee_domains)):
                staged_merchant_employee_domains[i].id = staged_merchant_employees[i].id
                staged_merchant_employee_domains[i].status = staged_merchant_employees[i].status
            for staged_domain in staged_merchant_employee_domains:
                merchant_employee_domains.insert(0, staged_domain)
            return merchant_employee_domains

    def log_out_merchant_employees(self, business_id):
        with session_scope() as session:
            return Merchant_Employee_Repository().log_out_merchant_employees(session = session, business_id = business_id)
    
    def add_staged_merchant_employee(self, merchant_id, merchant_employee_id):
        with session_scope() as session:
            return Merchant_Employee_Repository().add_staged_merchant_employee(session, merchant_id, merchant_employee_id)

    def remove_staged_merchant_employee(self, merchant_employee_id):
        with session_scope() as session:
            return Merchant_Employee_Repository().remove_staged_merchant_employee(session, merchant_employee_id)


class Business_Service(object):
    def authenticate_business(self, business_id):
        with session_scope() as session:
            business_status = Business_Repository().authenticate_business(
                session, business_id)
            return business_status

    def update_device_token(self, device_token, business_id):
        with session_scope() as session:
            return Business_Repository().update_device_token(session, device_token, business_id)

    def get_device_token(self, business_id):
        with session_scope() as session:
            return Business_Repository().get_device_token(session, business_id)

    def get_businesses(self):
        with session_scope() as session:
            response = []
            for business in Business_Repository().get_businesses(session):
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

    def get_merchant_business(self, merchant_id):
        with session_scope() as session:
            response = []
            for business in Business_Repository().get_merchant_businesses(session, merchant_id):
                business_domain = Business_Domain(business_object=business)
                response.append(business_domain)
            return response

    def get_menu(self, business_id):
        with session_scope() as session:
            menu = Business_Repository().get_menu(session, business_id)
            if menu:
                menu = [Drink_Domain(drink_object=x) for x in menu]
            return menu

    def get_business_phone_number(self, business_phone_number):
        with session_scope() as session:
            business_with_associated_phone_number = Business_Repository(
            ).get_business_phone_number(session, business_phone_number)
            business_domain = Business_Domain(
                business_object=business_with_associated_phone_number)
            return business_domain

    def set_merchant_pin(self, business_id, pin):
        with session_scope() as session:
            return Business_Repository().set_merchant_pin(session, business_id, pin)

    def authenticate_merchant_pin(self, business_id, pin):
        with session_scope() as session:
            merchant = Business_Repository().authenticate_merchant_pin(session, business_id, pin)
            if merchant:
                merchant_domain = Merchant_Domain(merchant_object=merchant)
                return merchant_domain
            return merchant

    def update_business_capacity(self, business_id, capacity_status):
        with session_scope() as session:
            return Business_Repository().update_capactiy_status(session, business_id, capacity_status)


class Tab_Service(object):
    def post_tab(self, tab: dict):
        with session_scope() as session:
            new_tab_domain = Tab_Domain(tab_json=tab)
            return Tab_Repository().post_tab(session, new_tab_domain)


class ETag_Service(object):
    def get_etag(self, category: str):
        with session_scope() as session:
            return ETag_Domain(etag_object=ETag_Repository().get_etag(session, category))
        
    def get_merchant_etag(self, e_tag: dict, merchant_id: str):
        with session_scope() as session:
            e_tag_domain = ETag_Domain(etag_json=e_tag)
            return ETag_Repository().get_merchant_etag(session=session,e_tag_category=e_tag_domain.category, merchant_id=merchant_id)

    def validate_etag(self, etag: dict):
        with session_scope() as session:
            etag_domain = ETag_Domain(etag_json=etag)
            return ETag_Repository().validate_etag(session, etag_domain)

    def update_etag(self, category: str):
        with session_scope() as session:
            return ETag_Domain(etag_object=ETag_Repository().update_etag(session, category))

    def update_merchant_etag(self, business_id: str, e_tag: dict):
        with session_scope() as session:
            ETag_Repository().update_merchant_etag(session=session, business_id=business_id, e_tag=e_tag)

    def validate_merchant_etag(self, merchant_id: int, e_tag: dict):
        with session_scope() as session:
            e_tag_domain = ETag_Domain(etag_json=e_tag)
            return ETag_Repository().validate_merchant_etag(session=session, merchant_id=merchant_id, e_tag=e_tag_domain)
        
    def validate_business_etag(self, business_id: int, e_tag: dict):
        with session_scope() as session:
            e_tag_domain = ETag_Domain(etag_json=e_tag)
            return ETag_Repository().validate_business_etag(session=session, business_id=business_id, e_tag=e_tag_domain)


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


class Google_Cloud_Storage_API(object):
    def __init__(self):
        super().__init__()
        # Imports the Google Cloud client library
        from google.cloud import storage
        app.config['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
            os.getcwd(), "quickbev-60da4e7ea092.json")
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

    def upload_menu_file(self, file, destination_blob_name):
        """Uploads a file to the bucket."""
        # bucket_name = "your-bucket-name"
        # file = "local/path/to/file" this will be the business folder, with a folder named after the business' unique id, which will have the menu file in it
        # destination_blob_name = "storage-object-name" this will be the business uuid
        from werkzeug.utils import secure_filename

        file_type = file.filename.rsplit('.', 1)[1].lower()
        destination_blob_name = "business/" + \
            str(destination_blob_name) + "/menu/" + "menu" "." + file_type
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_file(file)
        return True

    def upload_drink_image_file(self, drink):
        """Uploads a file to the bucket."""
        # bucket_name = "your-bucket-name"
        # file = "local/path/to/file" this will be the business folder, with a folder named after the business' unique id, which will have the menu file in it
        # destination_blob_name = "storage-object-name" this will be the business uuid
        file = drink.file
        destination_blob_name = drink.blob_name
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_file(file)
        blob.make_public()
        return True


class Quick_Pass_Service(object):
    def set_business_quick_pass(self, quick_pass):
        with session_scope() as session:
            return Quick_Pass_Repository().set_business_quick_pass(session, quick_pass)

    def create_stripe_payment_intent(self, quick_pass):
        quick_pass_domain = Quick_Pass_Domain(quick_pass_json=quick_pass)
        with session_scope() as session:
            business = Business_Domain(business_object=Business_Repository().get_business(
                session, quick_pass_domain.business_id))
            customer = Customer_Domain(customer_object= Customer_Repository().get_customer(
                session, quick_pass_domain.customer_id))

            stripe_price = business.quick_pass_price * 100
            service_fee_total = int(
                round(quick_pass_service_fee_percentage * stripe_price, 2))

            pre_sales_tax_total = service_fee_total + stripe_price

            sales_tax = round(pre_sales_tax_total *
                              business.sales_tax_rate, 2)

            total = int(round(sales_tax + stripe_price,2))

            merchant_stripe_id = quick_pass_domain.merchant_stripe_id
            payment_intent = stripe.PaymentIntent.create(
                amount=total,
                customer=customer.stripe_id,
                setup_future_usage='on_session',
                currency='usd',
                application_fee_amount=service_fee_total,
                transfer_data={
                    "destination": merchant_stripe_id
                }
            )
            response = {"payment_intent_id": payment_intent.id,
                        "secret": payment_intent["client_secret"]}
            return response

    def add_quick_pass(self, quick_pass):
        # calculate order values on backend to prevent malicious clients
        quick_pass_domain = Quick_Pass_Domain(quick_pass_json=quick_pass)
        with session_scope() as session:
            business = Business_Domain(business_object=Business_Repository().get_business(
                session, quick_pass_domain.business_id))

            if business.quick_pass_queue >= 1:
                new_queue = business.quick_pass_queue + 1
                Business_Repository().update_quick_pass_queue(session=session, business_id=business.id, queue=new_queue)
            price = business.quick_pass_price
            service_fee_total = round(.1 * price, 2)

            pre_sales_tax_total = service_fee_total + price

            sales_tax_total = round(pre_sales_tax_total *
                              business.sales_tax_rate, 2)
            # the total will not be in addition to the service fee because the business is paying the service fee
            total = price + sales_tax_total
            
            quick_pass_domain.service_fee_total = service_fee_total
            quick_pass_domain.total = total
            quick_pass_domain.subtotal = price
            
            quick_pass_domain.sales_tax_total = sales_tax_total
            quick_pass_domain.price = price
            Quick_Pass_Repository().add_quick_pass(session, quick_pass_domain)
            return quick_pass_domain

    def update_quick_pass(self, quick_pass_to_update):
        with session_scope() as session:
            quick_pass_domain = Quick_Pass_Domain(
                js_object=quick_pass_to_update)
            return Quick_Pass_Repository().update_quick_pass(session, quick_pass_domain)
        
    def get_bouncer_quick_passes(self, merchant_id):
        with session_scope() as session:
            quick_pass_domains = [Quick_Pass_Domain(quick_pass_object=x) for x in Quick_Pass_Repository().get_bouncer_quick_passes(
                session=session, merchant_id=merchant_id)]
            return quick_pass_domains
    
    def get_merchant_quick_passes(self, merchant_id):
        with session_scope() as session:
            quick_pass_domains = [Quick_Pass_Domain(quick_pass_object=x) for x in Quick_Pass_Repository().get_merchant_quick_passes(
                session=session, merchant_id=merchant_id)]
            return quick_pass_domains
    def get_business_quick_pass(self, business_id, customer_id):
        with session_scope() as session:
            sold_out = False
            business = Business_Domain(business_object=Business_Repository().get_business(session, business_id))
            merchant = Merchant_Domain(merchant_object = Merchant_Repository().get_merchant(session, business.merchant_id))
            
            new_quick_pass = Quick_Pass_Domain(
                should_display_expiration_time=should_diplay_expiration_time)
            new_quick_pass.activation_time = datetime.now()
            new_quick_pass.sold_out = sold_out
           
            # if the closing time is less than the opening time the day of closing time is 1 greater than the day of opening
            if business.schedule[datetime.today().weekday()].closing_time.hour < business.schedule[datetime.today().weekday()].opening_time.hour:
                closing_day = datetime.now().day + 1
            else:
                closing_day = datetime.now().day
            closing_date_time = datetime(datetime.now().year, datetime.now().month, closing_day,business.schedule[datetime.today().weekday()].closing_time.hour, business.schedule[datetime.today().weekday()].closing_time.minute) 
            expiration_date_time = datetime(datetime.now().year, datetime.now().month, datetime.now().day,datetime.now().hour + 2, datetime.now().minute)
            
            if expiration_date_time > closing_date_time:
                expiration_date_time = closing_date_time 
            
            if should_diplay_expiration_time == False:
                expiration_date_time = closing_date_time

            new_quick_pass.expiration_time = expiration_date_time
            new_quick_pass.price = business.quick_pass_price
            new_quick_pass.business_id = business.id
            new_quick_pass.customer_id = customer_id
            new_quick_pass.sales_tax_percentage = business.sales_tax_rate
            new_quick_pass.merchant_stripe_id = merchant.stripe_id
            new_quick_pass.date_time = datetime.now()

            # must create a dummy id for swift data type
            new_quick_pass.id = uuid.uuid4()
            return new_quick_pass
