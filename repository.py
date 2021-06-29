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
            new_drink = Drink(id=drink.id, name=drink.name, description=drink.description,
                              price=drink.price, business_id=drink.business_id, has_image=drink.has_image)
            session.add(new_drink)
        return drink_list

    def update_drinks(self, session, drinks):
        for drink in drinks:
            drink_to_update = session.query(Drink).filter(
                Drink.id == drink.id).first()
            drink_to_update.image_url = drink.image_url
        return True


class Order_Repository(object):
    def update_order(self, session, order):
        database_order = session.query(Order).filter(
            Order.id == order.id).first()
        if database_order:
            database_order.completed = order.completed
            database_order.rejected = order.rejected
            database_order.refunded = order.refunded
            return

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
        pre_fee_cost = int(round(subtotal+tip_amount+sales_tax, 2) * 100)
        merchant_stripe_id = order.merchant_stripe_id
        service_fee = int(round(.1 * cost, 2) * 100)
        cost = pre_fee_cost + service_fee
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

    def get_customer_orders(self, session, username):
        orders = session.query(Order, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                               Business.address.label("business_address"), Business.name.label("business_name")).select_from(Order).join(Business, Order.business_id == Business.id).filter(Order.customer_id == username).all()
        drinks = session.query(Drink)
        return orders, drinks

    def get_merchant_orders(self, session, username):
        orders = session.query(Order, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                               Business.address.label("business_address"), Business.name.label("business_name"), Customer.first_name.label('customer_first_name'), Customer.last_name.label('customer_last_name')).select_from(Order).join(Business, Order.business_id == Business.id).join(Customer, Order.customer_id == Customer.id).filter(Business.merchant_id == username).all()

        drinks = session.query(Drink)
        return orders, drinks

    def get_business_orders(self, session, business_id):
        orders = session.query(Order, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                               Business.address.label("business_address"), Business.name.label("business_name"), Customer.first_name.label('customer_first_name'), Customer.last_name.label('customer_last_name')).select_from(Order).join(Business, Order.business_id == Business.id).join(Customer, Order.customer_id == Customer.id).filter(Business.id == business_id).all()

        drinks = session.query(Drink)
        return orders, drinks

    def create_stripe_ephemeral_key(self, session, request):
        customer = request['stripe_id']
        customer_bool = False
        if customer:
            print('customer',customer)
            confirm_customer_existence = session.query(Stripe_Customer).filter(
                Stripe_Customer.id == customer).first()
            # Lookup the customer in the database so that if they exist we can attach their stripe id to the Ephermeral key such that later when they create the payment intent it will include their payment methods
            if confirm_customer_existence:
                print('confirm_customer_existence',confirm_customer_existence)
                customer_bool = True
                key = stripe.EphemeralKey.create(
                    customer=customer, stripe_version=request['api_version'])
                header = None
                return key, header

        if not customer_bool:
            print('not customer_bool')
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

        # get the list of merchant_employees that are clocked in when the sale was made and give them each an equal part of the tip
        servers = session.query(Merchant_Employee).filter(
            Merchant_Employee.business_id == order.business_id, Merchant_Employee.logged_in == True)


        # for server in servers:
        #     tip_per_server = tip_amount/len(servers)
        #     server_token = stripe.Token.create(customer=order.customer.stripe_id, stripe_account=server.stripe_id)
        #     server_tokenized_customer = stripe.Customer.create(source=server_token.id, stripe_account=server.stripe_id)

            # create a direct charge that is sourced from the customer and sent to the merchant
            # tip_payment_intent = stripe.PaymentIntent.create(
            #     amount=tip_per_server,
            #     customer=server_tokenized_customer.id,
            #     setup_future_usage='on_session',
            #     currency='usd',
            #     stripe_account=server.stripe_id
            # )
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
        # merchant_token = stripe.Token.create(customer=order.customer.stripe_id, stripe_account=merchant_stripe_id)
        # merchant_tokenized_customer = stripe.Customer.create(source=merchant_token.id, stripe_account= merchant_stripe_id)
        # payment_intent = stripe.PaymentIntent.create(
        #     amount=amount,
        #     customer=order.customer.stripe_id,
        #     setup_future_usage='on_session',
        #     currency='usd',
        #     application_fee_amount=service_fee,
        #     stripe_account= merchant_stripe_id,
        # )
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
        print('customer',customer.dto_serialize())
        print('customer',customer)
        test_customer = session.query(Customer).filter(
            Customer.id == customer.id).first()
        print('test_customer',test_customer)

        test_stripe_id = session.query(Stripe_Customer).filter(
            Stripe_Customer.id == customer.stripe_id).first()
        print('test_stripe_id',test_stripe_id)

        if not test_customer and test_stripe_id:
            print('if not test_customer and test_stripe_id')
            new_customer = Customer(id=customer.id, password=customer.password,
                                    first_name=customer.first_name, last_name=customer.last_name, stripe_id=test_stripe_id.id, email_verified=customer.email_verified, has_registered=False)
            session.add(new_customer)
            return new_customer
        elif not test_customer and not test_stripe_id:
            print('elif not test_customer and not test_stripe_id')
            new_customer = stripe.Customer.create()
            new_stripe = Stripe_Customer(id=new_customer.id)
            session.add(new_stripe)
            new_customer = Customer(id=customer.id, password=customer.password,
                                    first_name=customer.first_name, last_name=customer.last_name, stripe_id=new_stripe.id, email_verified=customer.email_verified, has_registered=False)
            session.add(new_customer)
            return new_customer
        # if the customer that has been requested for registration from the front end is unverified then we overwrite the customer values with the new values and return True to let the front end know that this customer has previously attempted to have been registered but was never verified. that way if a customer never verfies the account can continue to be modified as necessary while still preserving its unverified state
        elif test_customer and test_customer.email_verified == False and not test_stripe_id:
            print('elif test_customer and test_customer.email_verified == False and not test_stripe_id')
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
            print('test_customer and test_customer.email_verified == False and test_stripe_id')
            test_customer.password = customer.password
            test_customer.first_name = customer.first_name
            test_customer.last_name = customer.last_name
            test_customer.stripe_id = customer.stripe_id
            test_customer.has_registered = True
            return test_customer
        else:
            return False

    def get_customers(self, session, merchant_id):
        # this is probably a super inefficient query lol, should work from merchant list filtered by merchant ID to wittle down initial subset not work from entire dataset and wittle it with merchant_id ? idk maybe this is just as bad because you still have to compare all the businesses
        customers = session.query(Customer).join(Order, Order.customer_id == Customer.id).join(Business, Business.id == Order.business_id).join(
            Merchant, Merchant.id == Business.merchant_id).filter(Business.merchant_id == merchant_id).distinct().all()
        return customers

    def update_device_token(self, session, device_token, customer_id):
        customer_to_update = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if customer_to_update:
            customer_to_update.device_token = device_token
            return True
        else:
            return False

    def get_device_token(self, session, customer_id):
        requested_customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
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
    def authenticate_business(self, session, business_id):
        business_status = session.query(Business).filter(
            Business.id == business_id).first()
        if business_status:
            return True
        else:
            return False

    def get_businesses(self, session):
        businesses = session.query(Business).all()
        return businesses

    def add_business(self, session, business):
        # will have to plug in an API here to dynamically pull information (avalara probs if i can get the freaking credentials to work)
        new_business = Business(id=business.id, name=business.name, classification=business.classification, date_joined=date.today(
        ), sales_tax_rate=business.sales_tax_rate, merchant_id=business.merchant_id, street=business.street, city=business.city,
            state=business.state, zipcode=business.zipcode, address=business.address, tablet=business.tablet, phone_number=business.phone_number, merchant_stripe_id=business.merchant_stripe_id)
        session.add(new_business)
        return business

    # dont need this anymore because i no longer generate a new stripe ID when the user hits the redirect_url. felt cute, will probably delete later
    # def update_business(self, session, business):
    #     business_database_object_to_update = session.query(
    #         Business).filter(Business.id == business.id).first()
    #     print('business_database_object_to_update',business_database_object_to_update)

    #     if business_database_object_to_update:
    #         business_database_object_to_update.merchant_stripe_id = business.merchant_stripe_id
    #         return True
    #     else:
    #         return False

    def get_merchant_businesses(self, session, merchant_id):
        businesses = session.query(Business).filter(
            Business.merchant_id == merchant_id).all()
        if businesses:
            return businesses
        else:
            return False

    def get_menu(self, session, business_id):
        business = session.query(Business).filter(
            Business.id == business_id).first()
        if business:
            menu = business.drink
            return menu
        else:
            return False

    def get_business_phone_number(self, session, business_phone_number):
        business_with_corresponding_phone_number = session.query(Business).filter(
            Business.phone_number == business_phone_number).first()
        if business_with_corresponding_phone_number:
            return business_with_corresponding_phone_number
        else:
            return False

    def update_device_token(self, session, device_token, business_id):
        business_to_update = session.query(Business).filter(
            Business.id == business_id).first()
        if business_to_update:
            business_to_update.device_token = device_token
            return True
        else:
            return False

    def get_device_token(self, session, business_id):
        requested_business = session.query(Business).filter(
            Business.id == business_id).first()
        if requested_business:
            device_token = requested_business.device_token
            return device_token
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
            type="standard",
            country="US"
        )
        new_stripe_account_id = Merchant_Stripe_Account(id=new_account.id)
        session.add(new_stripe_account_id)
        return new_account

    def authenticate_merchant(self, session, email, password):
        print('password',password)
        print('email',email)
        for merchant in session.query(Merchant):
            print('merchant in auth merchant',merchant.serialize)
            if merchant.id == email and check_password_hash(merchant.password, password) == True:
                return merchant
        return False

    def authenticate_merchant_stripe(self, session, stripe_id):
        merchant_stripe_status = stripe.Account.retrieve(stripe_id)
        print('authenticating merchant stripe')
        print('merchant_stripe_status', merchant_stripe_status)
        return merchant_stripe_status['charges_enabled']

    def add_merchant(self, session, requested_merchant):
        print('requested_merchant', requested_merchant.dto_serialize())
        new_merchant = Merchant(id=requested_merchant.id, password=generate_password_hash(requested_merchant.password), first_name=requested_merchant.first_name,
                                last_name=requested_merchant.last_name, phone_number=requested_merchant.phone_number, number_of_businesses=requested_merchant.number_of_businesses, stripe_id=requested_merchant.stripe_id)
        session.add(new_merchant)
        return requested_merchant


class Merchant_Employee_Repository(object):
    def get_stripe_account(self, session, merchant_employee_id):
        merchant_employee = session.query(Merchant_Employee).filter(
            Merchant_Employee.id == merchant_employee_id).first()
        return merchant_employee.stripe_id

    def authenticate_merchant_employee(self, session, email, password):
        for merchant_employee in session.query(Merchant_Employee):
            if merchant_employee.id == email and check_password_hash(merchant_employee.password, password):
                return merchant_employee
        else:
            return False

    # this validates that the pin number is unique for the tablet upon which the merchant employee is registering
    def validate_pin_number(self, session, business_id, pin_number):
        for merchant_employee in session.query(Merchant_Employee).filter(Merchant_Employee.business_id == business_id):
            if check_password_hash(merchant_employee.pin_number, pin_number) == True:
                return False
        return True

    def authenticate_pin_number(self, session, merchant_employee_id, pin_number, login_status):
        for merchant_employee in session.query(Merchant_Employee):
            if merchant_employee.id == merchant_employee_id:
                if check_password_hash(merchant_employee.pin_number, pin_number) == True:
                    merchant_employee.logged_in = login_status
                    return merchant_employee
        else:
            return False

    def reset_pin_number(self, session, merchant_employee_id, pin_number):
        for merchant_employee in session.query(Merchant_Employee):
            if merchant_employee.id == merchant_employee_id:
                print('merchant_employee.id', merchant_employee.id)
                print('merchant_employee_id', merchant_employee_id)
                merchant_employee.pin_number = generate_password_hash(
                    pin_number)
                print('pin_number', pin_number)
                print('merchant_employee', merchant_employee.serialize)
                return merchant_employee
        else:
            return False

    def authenticate_username(self, session, username):
        # if a username is passed then we query the db to verify it, if the hashed version is passed then we use the check_password_hash to verify it
        merchant_employee = session.query(Merchant_Employee).filter(
            Merchant_Employee.id == username).first()
        if merchant_employee:
            return True
        else:
            return False

    def add_merchant_employee(self, session, requested_merchant_employee):
        new_account = stripe.Account.create(
            type="standard",
            country="US"
        )
        new_stripe_account_id = Merchant_Employee_Stripe_Account(
            id=new_account.id)
        session.add(new_stripe_account_id)
        new_merchant_employee = Merchant_Employee(id=requested_merchant_employee.id, pin_number=generate_password_hash(requested_merchant_employee.pin_number), first_name=requested_merchant_employee.first_name,
                                                  last_name=requested_merchant_employee.last_name, phone_number=requested_merchant_employee.phone_number, merchant_id=requested_merchant_employee.merchant_id, business_id=requested_merchant_employee.business_id, stripe_id=new_account.id)
        requested_merchant_employee.stripe_id = new_account.id
        session.add(new_merchant_employee)
        return requested_merchant_employee


class ETag_Repository():
    def get_etag(self, session, category):
        etag = session.query(ETag).filter(ETag.category == category).first()
        return etag

    def update_etag(self, session, category):
        etag = session.query(ETag).filter(ETag.category == category).first()
        etag.id += 1
        return etag.id

    def validate_etag(self, session, etag):
        validation = session.query(ETag).filter(
            ETag.category == etag["category"], ETag.id == etag["id"]).first()
        if validation:
            return True
        else:
            return False
