
# beginning of Models.py
# note that at this point you should have created "quickbev" database (see install_postgres.txt).
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import os
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
import uuid
import json
from datetime import date
from datetime import datetime
import stripe
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_method
from random import randrange
from datetime import datetime
#   https://stackoverflow.com/questions/38678336/sqlalchemy-how-to-implement-drop-table-cascade

stripe.api_key = "sk_test_51I0xFxFseFjpsgWvh9b1munh6nIea6f5Z8bYlIDfmKyNq6zzrgg8iqeKEHwmRi5PqIelVkx4XWcYHAYc1omtD7wz00JiwbEKzj"


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


app = Flask(__name__)
username = os.environ.get("USER", "postgres")
password = os.environ.get("PASSWORD", "Iqopaogh23!")
connection_string_beginning = "postgres://"
connection_string_end = "@localhost:5432/quickbevdb"
connection_string = connection_string_beginning + \
    username + ":" + password + connection_string_end
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DB_STRING", connection_string)


# to suppress a warning message
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Drink(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    has_image = db.Column(db.Boolean(), default=False, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    business_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'business.id'), nullable=False)
    order_drink = relationship('Order_Drink', lazy=True)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

class Business_Schedule_Day(db.Model):
    __tablename__ = 'business_schedule_day'
    business_id = db.Column(UUID(as_uuid=True), db.ForeignKey('business.id'), primary_key=True,
                    nullable=False)
    day = db.Column(db.String(80), primary_key=True, nullable=False)
    is_closed = db.Column(db.Boolean(), default=False, nullable=False)
    opening_time = db.Column(db.Time(), nullable=True)
    closing_time = db.Column(db.Time(), nullable=True)
    business = relationship("Business", back_populates="schedule")

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

class Business(db.Model):
    __tablename__ = 'business'
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   unique=True, nullable=False)
    merchant_stripe_id = db.Column(db.String(80), db.ForeignKey(
        'merchant_stripe_account.id'), nullable=False)
    merchant_id = db.Column(db.String(80), db.ForeignKey(
        'merchant.id'), nullable=False)
    merchant_pin_number = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    classification = db.Column(db.String(80), nullable=False)
    date_joined = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    sales_tax_rate = db.Column(db.Float(), nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    device_token = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.BigInteger(), nullable=False)

    # not all businesses will have a menu URL or file upload, but they could be specific to each business
    menu_url = db.Column(db.String(80), nullable=True)
    street = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    zipcode = db.Column(db.Integer(), nullable=True)
    suite = db.Column(db.String(80), nullable=True)
    address = db.Column(db.String(80), nullable=False)
    at_capacity = db.Column(db.Boolean(), default=True, nullable=False)
    quick_pass_price = db.Column(db.Float(), default = 20.0, nullable=False)
    quick_passes_per_hour = db.Column(db.Integer(), default = 30, nullable=False)
    current_queue = db.Column(db.Integer(), default = 0, nullable=True)
    schedule = relationship(
        "Business_Schedule_Day", lazy=True,  uselist=True)
    merchant_employee = relationship(
        "Merchant_Employee", lazy=True, backref="business")
    drink = relationship('Drink', lazy=True, backref="business")
    order = relationship('Order', lazy=True, backref="business")
    tab = relationship('Tab', lazy=True, backref="business")

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

class Staged_Bouncer(db.Model):
    __tablename__ = 'staged_bouncer'
    id = db.Column(db.String(80), primary_key=True,
                   unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    business_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "business.id"),  nullable=False)
    merchant_id = db.Column(db.String(80), db.ForeignKey(
        "merchant.id"),   nullable=False)
    status = db.Column(db.String(80), nullable=False)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Bouncer(db.Model):
    __tablename__ = 'bouncer'
    id = db.Column(db.String(80), primary_key=True,
                   unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    logged_in = db.Column(db.Boolean(), default=False, nullable=False)
    business_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "business.id"),  nullable=False)
    merchant_id = db.Column(db.String(80), db.ForeignKey(
        "merchant.id"),   nullable=False)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

class Staged_Merchant_Employee(db.Model):
    __tablename__ = 'staged_merchant_employee'
    id = db.Column(db.String(80), primary_key=True,
                   unique=True, nullable=False)
    merchant_id = db.Column(db.String(80), db.ForeignKey(
        "merchant.id"),   nullable=False)
    status = db.Column(db.String(80), nullable=False)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Merchant_Employee(db.Model):
    __tablename__ = 'merchant_employee'
    id = db.Column(db.String(80), primary_key=True,
                   unique=True, nullable=False)
    pin_number = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.BigInteger(), nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    logged_in = db.Column(db.Boolean(), default=False, nullable=False)
    business_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "business.id"),  nullable=False)
    merchant_id = db.Column(db.String(80), db.ForeignKey(
        "merchant.id"),   nullable=False)
    stripe_id = db.Column(db.String(80), db.ForeignKey(
        "merchant_employee_stripe_account.id"),   nullable=False)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Merchant(db.Model):
    id = db.Column(db.String(80), primary_key=True,
                   unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.BigInteger(), nullable=False)
    number_of_businesses = db.Column(db.Integer(), nullable=False)
    stripe_id = db.Column(db.String(80), db.ForeignKey(
        'merchant_stripe_account.id'), nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    merchant_employee = relationship(
        "Merchant_Employee", lazy=True, backref="merchant")
    business = relationship(
        "Business", lazy=True, backref="merchant")

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.String(200), primary_key=True,
                   unique=True, nullable=False)
    stripe_id = db.Column(db.String(80), db.ForeignKey('stripe_customer.id'), unique=True,
                          nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email_verified = db.Column(db.Boolean(), nullable=False)
    has_registered = db.Column(db.Boolean(), nullable=False)
    is_active = db.Column(db.Boolean(), default=True, nullable=False)
    device_token = db.Column(db.String(200), nullable=True)
    quick_pass = relationship('Quick_Pass', lazy=True, uselist=True)

    order = relationship('Order', lazy=True, backref="customer")
    tab = relationship('Tab', lazy=True, backref="customer")

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   unique=True, nullable=False)
    customer_id = db.Column(db.String(200), db.ForeignKey(
        'customer.id'), nullable=False)
    business_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'business.id'), nullable=False)
    merchant_stripe_id = db.Column(
        db.String(80), db.ForeignKey('merchant_stripe_account.id'))
    total = db.Column(db.Float(), nullable=False)
    subtotal = db.Column(db.Float(), nullable=False)
    pre_sales_tax_total = db.Column(db.Float(), nullable=False)
    pre_service_fee_total = db.Column(db.Float(), nullable=False)
    stripe_charge_total = db.Column(db.Float(), nullable=False)
    sales_tax_total = db.Column(db.Float(), nullable=False)
    sales_tax_percentage = db.Column(db.Float(), nullable=False)
    tip_percentage = db.Column(db.Float(), nullable=False)
    tip_total = db.Column(db.Float(), nullable=False)
    service_fee = db.Column(db.Float(), nullable=False)
    date_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    payment_intent_id = db.Column(db.String(80), unique=True, nullable=False)
    completed = db.Column(db.Boolean(), default=False, nullable=True)
    refunded = db.Column(db.Boolean(), default=False, nullable=True)
    order_drink = relationship(
        "Order_Drink", lazy=True, backref="order", uselist=True)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Quick_Pass(db.Model):
    __tablename__ = 'quick_pass'
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True,
                   unique=True, nullable=False)
    customer_id = db.Column(db.String(200), db.ForeignKey(
        'customer.id'), nullable=False)
    business_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'business.id'), nullable=False)
    merchant_stripe_id = db.Column(
        db.String(80), db.ForeignKey('merchant_stripe_account.id'))
    price = db.Column(db.Float(), nullable=False)
    sales_tax = db.Column(db.Float(), nullable=False)
    sales_tax_percentage = db.Column(db.Float(), nullable=False)
    service_fee = db.Column(db.Float(), nullable=False)
    stripe_total = db.Column(db.Float(), nullable=False)
    pre_sales_tax_total = db.Column(db.Float(), nullable=False)
    total = db.Column(db.Float(), nullable=False)
    date_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    payment_intent_id = db.Column(db.String(80), unique=True, nullable=False)
    current_queue = db.Column(db.Integer(), nullable=False)
    # the time the pass was actually used to get into the bar
    time_checked_in = db.Column(db.DateTime(), nullable=True)
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    # the time the pass will become active and the user is able to enter the bar with it
    activation_time = db.Column(db.DateTime(), nullable=True)
    expiration_time = db.Column(db.DateTime(), nullable=True)
    customer=relationship("Customer", back_populates="quick_pass")
    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

class Order_Drink(db.Model):
    __tablename__ = 'order_drink'
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True,  # https://stackoverflow.com/questions/55917056/how-to-prevent-uuid-primary-key-for-new-sqlalchemy-objects-being-created-with-th
                   unique=True, nullable=False)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'order.id'), nullable=False)
    drink_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'drink.id'), nullable=False)
    # did not set foriegn key here because there is no unique constraint on drink name thus i cant identify which drink name i am referecing. however i don't care which drink i am exactly referencing as long as the name exists

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Tab (db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    business_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'business.id'), nullable=False)
    customer_id = db.Column(db.String(80), db.ForeignKey(
        'customer.id'), nullable=False)
    street = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80),  nullable=False)
    zipcode = db.Column(db.Integer(), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    date_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    description = db.Column(db.String(280), nullable=False)
    minimum_contribution = db.Column(db.Integer(), nullable=False)
    fundraising_goal = db.Column(db.Integer(), nullable=False)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Stripe_Customer(db.Model):
    __tablename__ = 'stripe_customer'

    id = db.Column(db.String(80), primary_key=True,
                   unique=True, nullable=False)
    customer = relationship('Customer', lazy=True)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Merchant_Employee_Stripe_Account(db.Model):
    __tablename__ = 'merchant_employee_stripe_account'
    id = db.Column(db.String(80), primary_key=True,
                   unique=True, nullable=False)
    merchant_employee = relationship(
        "Merchant_Employee", lazy=True, backref="merchant_employee_stripe_account")

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Merchant_Stripe_Account(db.Model):
    __tablename__ = 'merchant_stripe_account'
    id = db.Column(db.String(80), primary_key=True,
                   unique=True, nullable=False)
    merchant = relationship('Merchant', lazy=True,
                            backref="merchant_stripe_account")
    business = relationship("Business", lazy=True,
                            backref="merchant_stripe_account")

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class ETag (db.Model):
    __tablename__ = 'etag'
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    category = db.Column(db.String(80),  primary_key=True, nullable=False)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Guest_Device_Token(db.Model):
    __tablename__ = 'guest_device_token'
    id = db.Column(db.String(200), primary_key=True, nullable=False)

    @property
    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


def load_json(filename):

    with open(filename) as file:
        jsn = json.load(file)
        file.close()

    return jsn


def create_business():
    new_account = stripe.Account.create(
        type="express",
        country="US"
    )
    new_stripe_account = Merchant_Stripe_Account(id=new_account.id)
    db.session.add(new_stripe_account)
    new_merchant = Merchant(id="a", password=generate_password_hash("a"), first_name="peter",
                            last_name="driscoll", phone_number=5126456898, number_of_businesses=2, stripe_id=new_stripe_account.id)

    db.session.add(new_merchant)
    days_of_week = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
  ]
    test_business = load_json("test_business.json")
    for business in test_business:
        merchant_id = business["merchant_id"]
        name = business['name']
        date_joined = date.today()
        sales_tax_rate = business["sales_tax_rate"]
        classification = business["classification"]
        phone_number = business["phone_number"]
        street = business['street']
        city = business['city']
        state = business['state']
        zipcode = business['zipcode']
        address = f"{street}, {city}, {state} {zipcode}"
        business_id = uuid.uuid4()
        for day in days_of_week:
            new_business_schedule_day = Business_Schedule_Day(business_id = business_id, day = day, opening_time = datetime.strptime(
                "10:00", '%H:%M').time(), closing_time = datetime.strptime(
                "02:00", '%H:%M').time(), is_closed = False )
            db.session.add(new_business_schedule_day)
        new_business = Business(id=business_id, merchant_id=merchant_id, merchant_stripe_id=new_account.id,
                                name=name, date_joined=date_joined, sales_tax_rate=sales_tax_rate, classification=classification, street=street, city=city,
                                state=state, zipcode=zipcode, address=address, phone_number=phone_number)
        # After I create the drink, I can then add it to my session.
        db.session.add(new_business)

    new_stripe_customer = stripe.Customer.create()
    new_stripe_customer_id = Stripe_Customer(id=new_stripe_customer.id)
    # id = generate_password_hash("a", "sha256")
    password = generate_password_hash("a", "sha256")
    new_customer = Customer(id="a", password=password,
                            first_name="peter", last_name="driscoll", stripe_id=new_stripe_customer.id, email_verified=False, has_registered=False)
    db.session.add(new_stripe_customer_id)
    db.session.add(new_customer)
    # commit the session to my DB.
    db.session.commit()


def create_drink():
    businesses = db.session.query(Business)

    test_drinks = load_json("test_drinks.json")

    business_counter = 0
    for drink in test_drinks:
        id = uuid.uuid4().hex
        name = drink['name']
        description = drink['description']
        price = drink['price']
        has_image = drink["has_image"]
        new_drink = Drink(id=id, name=name,
                          description=description, price=price, business_id=businesses[business_counter].id, has_image=has_image)
        # alternate between the two business address objects when assingning the drinks a business address id
        if business_counter == 0:
            business_counter = 1
        elif business_counter == 1:
            business_counter = 0
        # After I create the drink, I can then add it to my session.
        db.session.add(new_drink)

    # commit the session to my DB.
    db.session.commit()


def create_orders_and_customers():
    businesses = db.session.query(Business)
    drinks = db.session.query(Drink)

    customer_id_list = ['b', 'c', 'd', 'e', 'f', 'g']
    customer_password_list = ['b', 'c', 'd', 'e', 'f', 'g']
    customer_first_name_list = ['Aali', 'Johnny',
                                'Blaise', 'Alfred', 'Aris', 'Daniel']
    customer_last_name_list = ['Sahay', 'Terry',
                               'Bucey', 'Driscoll', 'Sevastianos', 'Noorily']

    # create 6 new customers for testing
    for i in range(len(customer_id_list)):
        new_stripe_customer = stripe.Customer.create()
        new_my_table_stripe_customer = Stripe_Customer(
            id=new_stripe_customer.id)
        db.session.add(new_my_table_stripe_customer)
        print('customer_id_list[i]', customer_id_list[i])
        new_customer = Customer(id=customer_id_list[i], stripe_id=new_my_table_stripe_customer.id, password=generate_password_hash(
            customer_password_list[i]), first_name=customer_first_name_list[i], last_name=customer_last_name_list[i], email_verified=True, has_registered=False)
        db.session.add(new_customer)
    db.session.commit()

    # create 50 new orders for testing
    for i in range(151):
        day = randrange(1, 29)
        month = randrange(1, 4)
        date = datetime(2021, month, day)
        customer_index = randrange(6)
        test_customer_id = customer_id_list[customer_index]
        drink_index = randrange(2)
        num_drinks = randrange(10)
        drink = drinks[drink_index]

        subtotal = drink.price * num_drinks

        tip_percentage = .1
        sales_tax_percentage = .0625

        tip_amount = tip_percentage * subtotal

        pre_service_fee_total = subtotal + tip_amount

        service_fee = .1 * pre_service_fee_total

        pre_sales_tax_total = pre_service_fee_total + service_fee

        sales_tax = pre_sales_tax_total * sales_tax_percentage

        total = pre_sales_tax_total + sales_tax

        stripe_charge_total = pre_service_fee_total + sales_tax
        order_id = uuid.uuid4()

        business_where_order_occured = [
            x for x in businesses if x.id == drink.business_id][0]

        test_order = Order(id=order_id, customer_id=test_customer_id, business_id=drink.business_id, merchant_stripe_id=business_where_order_occured.merchant_stripe_id, total=total, pre_sales_tax_total=pre_sales_tax_total, pre_service_fee_total=pre_service_fee_total,
                           stripe_charge_total=stripe_charge_total, subtotal=subtotal, sales_tax_total=sales_tax, sales_tax_percentage=sales_tax_percentage, tip_percentage=tip_percentage, tip_total=tip_amount, service_fee=service_fee, payment_intent_id=uuid.uuid4().hex)
        db.session.add(test_order)
        for i in range(num_drinks):
            order_drink = Order_Drink(drink_id=drink.id, order_id=order_id)
            db.session.add(order_drink)

    db.session.commit()


def create_etag():
    db.create_all()
    new_etag = ETag(id=0, category="business")
    new_etag2 = ETag(id=0, category="drink")

    db.session.add(new_etag)
    db.session.add(new_etag2)
    db.session.commit()


def create_everything():
    db.drop_all()
    db.create_all()
    create_business()
    create_drink()
    create_orders_and_customers()
    create_etag()


def instantiate_db_connection():
    create_everything()
# instantiate_db_connection()
