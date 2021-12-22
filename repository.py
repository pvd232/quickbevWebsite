from ctypes import Array
from sqlalchemy.orm.scoping import scoped_session
from models import *
from domain import Bouncer_Domain, Business_Domain, Customer_Domain, Drink_Domain, ETag_Domain, Merchant_Domain, Merchant_Employee_Domain, Order_Domain, Quick_Pass_Domain, Tab_Domain
import stripe
from werkzeug.security import generate_password_hash, check_password_hash



class Drink_Repository(object):
    def get_drinks(self, session):
        drinks = session.query(Drink)
        return drinks

    def add_drinks(self, session: scoped_session, drink_list: list[Drink_Domain]):
        for drink in drink_list:
            new_drink = Drink(id=drink.id, name=drink.name, description=drink.description,
                              price=drink.price, business_id=drink.business_id, has_image=drink.has_image)
            session.add(new_drink)
        return drink_list

    def update_drinks(self, session: scoped_session, drinks: list[Drink_Domain]):
        for drink in drinks:
            drink_to_update = session.query(Drink).filter(
                Drink.id == drink.id).first()
            drink_to_update.image_url = drink.image_url
        return True


class Order_Repository(object):
    def get_customer_order_status(self, session: scoped_session, customer_id: str):
        customer_orders = session.query(Order).filter(
            Order.customer_id == customer_id).all()
        return customer_orders

    def get_order(self, session: scoped_session, order_id: str):
        database_order = session.query(Order, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                                       Business.address.label("business_address"), Business.name.label("business_name"), Customer.first_name.label('customer_first_name'), Customer.last_name.label('customer_last_name')).select_from(Order).join(Business, Order.business_id == Business.id).join(Customer, Order.customer_id == Customer.id).filter(Order.id == order_id).all()
        # database_order.completed = True
        drinks = session.query(Drink)
        return database_order, drinks

    def update_order(self, session: scoped_session, order: Order_Domain):
        database_order = session.query(Order).filter(
            Order.id == order.id).first()
        if database_order:
            database_order.completed = order.completed
            database_order.refunded = order.refunded
            return

    def create_order(self, session: scoped_session, order: Order_Domain):
        new_order = Order(id=order.id, customer_id=order.customer_id, merchant_stripe_id=order.merchant_stripe_id,
                          business_id=order.business_id, tip_percentage=order.tip_percentage, sales_tax_percentage=order.sales_tax_percentage, service_fee_percentage=order.service_fee_percentage, stripe_fee_percentage=order.stripe_fee_percentage, subtotal=order.subtotal, tip_total=order.tip_total, sales_tax_total=order.sales_tax_total, stripe_application_fee_total=order.stripe_application_fee_total, service_fee_total=order.service_fee_total,  total=order.total, stripe_fee_total=order.stripe_fee_total, net_stripe_application_fee_total=order.net_stripe_application_fee_total, net_service_fee_total=order.net_service_fee_total, payment_intent_id=order.payment_intent_id, card_information=order.card_information, refunded=order.refunded, completed=order.completed)
        session.add(new_order)
        for each_order_drink in order.order_drink:
            # create a unique instance of Order_Drink for the number of each type of drink that were ordered. the UUID for the Order_Drink is generated in the database
            for _ in range(each_order_drink.quantity):
                new_order_drink = Order_Drink(
                    order_id=each_order_drink.order_id, drink_id=each_order_drink.drink_id)
                session.add(new_order_drink)

        # get the list of merchant_employees that are clocked in when the sale was made and give them each an equal part of the tip
        servers = session.query(Merchant_Employee).filter(
            Merchant_Employee.business_id == order.business_id, Merchant_Employee.logged_in == True).all()
        if len(servers) > 0:
            tip_per_server = order.tip_total/len(servers)
            for server in servers:
                new_order_tip = Order_Tip(
                    order_id=order.id, merchant_employee_id=server.id, tip_total=tip_per_server)
                session.add(new_order_tip)
        print('order', order.dto_serialize())
        return order

    def get_customer_orders(self, session: scoped_session, username: str):
        orders = session.query(Order, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                               Business.address.label("business_address"), Business.name.label("business_name")).select_from(Order).join(Business, Order.business_id == Business.id).filter(Order.customer_id == username).all()
        return orders

    def get_merchant_orders(self, session: scoped_session, username: str):
        orders = session.query(Order, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                               Business.address.label("business_address"), Business.name.label("business_name"), Customer.first_name.label('customer_first_name'), Customer.last_name.label('customer_last_name')).select_from(Order).join(Business, Order.business_id == Business.id).join(Customer, Order.customer_id == Customer.id).filter(Business.merchant_id == username).all()
        # businesses_associated_with_merchant = session.query(Business).filter(Business.merchant_id == username).all()
        # business_id_list = []
        # for business in businesses_associated_with_merchant:
        #     business_id_list.append(business.id)
        drinks = session.query(Drink)
        orders
        print('orders',len(orders))
        return orders, drinks

    def get_merchant_employee_orders(self, session: scoped_session, business_id: UUID):
        # only get active orders
        orders = session.query(Order, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                               Business.address.label("business_address"), Business.name.label("business_name"), Customer.first_name.label('customer_first_name'), Customer.last_name.label('customer_last_name')).select_from(Order).join(Business, Order.business_id == Business.id).join(Customer, Order.customer_id == Customer.id).filter(Business.id == business_id, Order.completed == False, Order.refunded == False).all()
        drinks = session.query(Drink).filter(
            Drink.business_id == business_id).all()
        return orders, drinks

    def create_stripe_ephemeral_key(self, session: scoped_session, request: dict):
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
            stripe_header = {"stripe-id": new_customer.id}
            key = stripe.EphemeralKey.create(
                customer=new_customer.id, stripe_version=request['api_version'])
            return key, stripe_header

    def refund_stripe_order(self, order: Order_Domain):
        payment_intent = stripe.PaymentIntent.retrieve(order.payment_intent_id)
        charge = payment_intent.charges.data[0]

        refund = stripe.Refund.create(
            charge=charge.id,
            refund_application_fee=True,
            reverse_transfer=True,
        )
        print('refund', refund)

        transfer_group = charge["transfer_group"]
        print('transfer_group', transfer_group)
        transfers_associated_data = stripe.Transfer.list(
            transfer_group=transfer_group)
        transfers_list = transfers_associated_data["data"]

        for transfer in transfers_list:
            print('transfer', transfer)
            print('transfer["reversed"]', transfer["reversed"])
            if transfer["reversed"] != True:
                stripe.Transfer.create_reversal(
                    transfer["id"], amount=transfer["amount"])
        return True


class Customer_Repository(object):
    def authenticate_customer(self, session: scoped_session, email: str, password: str):
      # check to see if the customer exists in the database by querying the Customer_Info table for the giver username and password
      # if they don't exist this will return a null value for customer which i check for in line 80

        for customer in session.query(Customer):
            if customer.id == email and check_password_hash(customer.password, password):
                return customer
        else:
            return False

    def validate_username(self, session: scoped_session, username: str, hashed_username: str):
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

    def register_new_customer(self, session: scoped_session, customer: Customer_Domain):
        test_customer = session.query(Customer).filter(
            Customer.id == customer.id).first()

        test_customer_apple_id = session.query(Customer).filter(
            Customer.apple_id == customer.apple_id).first()

        if not test_customer and test_customer_apple_id:
            return test_customer_apple_id
        elif test_customer and not test_customer_apple_id:
            return test_customer
        elif not test_customer and not test_customer_apple_id:
            new_customer = stripe.Customer.create()
            new_stripe = Stripe_Customer(id=new_customer.id)
            session.add(new_stripe)
            new_customer = Customer(id=customer.id, password=customer.password,
                                    first_name=customer.first_name, last_name=customer.last_name, stripe_id=new_stripe.id, email_verified=customer.email_verified, has_registered=False, date_time=customer.date_time)
            # registering with Apple ID
            if customer.apple_id != "":
                new_customer.apple_id = customer.apple_id
            session.add(new_customer)
            print('new_customer', new_customer.serialize)
            print('new_customer.date_time', new_customer.date_time)
            return new_customer
        else:
            return False

    def get_customers(self, session: scoped_session, merchant_id: str):
        # this is probably a super inefficient query lol, should work from merchant list filtered by merchant ID to wittle down initial subset not work from entire dataset and wittle it with merchant_id ? idk maybe this is just as bad because you still have to compare all the businesses
        customers = session.query(Customer).join(Order, Order.customer_id == Customer.id).join(Business, Business.id == Order.business_id).join(
            Merchant, Merchant.id == Business.merchant_id).filter(Business.merchant_id == merchant_id).distinct().all()
        return customers

    def update_device_token(self, session: scoped_session, device_token: str, customer_id: str):
        customer_to_update = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if customer_to_update:
            customer_to_update.device_token = device_token
            return True
        else:
            return False

    def get_device_token(self, session: scoped_session, customer_id: str):
        requested_customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if requested_customer:
            device_token = requested_customer.device_token
            return device_token
        else:
            return False

    def update_email_verification(self, session: scoped_session, customer_id: str):
        requested_customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if requested_customer:
            requested_customer.email_verified = True
            return True
        else:
            return False

    def update_password(self, session: scoped_session, customer_id: str, new_password: str):
        requested_customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if requested_customer:
            requested_customer.password = generate_password_hash(new_password)
            return True
        else:
            return False

    def get_customer(self, session: scoped_session, customer_id: str):
        customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        if customer:
            return customer
        else:
            return False

    def get_customer_apple_id(self, session: scoped_session, apple_id: str):
        customer = session.query(Customer).filter(
            Customer.apple_id == apple_id).first()
        if customer:
            return customer
        else:
            return False

    def set_customer_apple_id(self, session: scoped_session, customer_id: str, apple_id: str):
        customer = session.query(Customer).filter(
            Customer.id == customer_id).first()
        customer.apple_id = apple_id
        return


class Business_Repository(object):
    def authenticate_business(self, session: scoped_session, business_id: UUID):
        business_status = session.query(Business).filter(
            Business.id == business_id).first()
        if business_status:
            return True
        else:
            return False

    def get_businesses(self, session: scoped_session):
        businesses = session.query(Business).all()
        return businesses

    def get_business(self, session: scoped_session, business_id: UUID):
        business = session.query(Business).filter(
            Business.id == business_id).first()
        if business:
            business_domain = Business_Domain(business_object=business)
            return business_domain
        else:
            return False

    def add_business(self, session: scoped_session, business: Business_Domain):
        # will have to plug in an API here to dynamically pull information (avalara probs if i can get the freaking credentials to work)

        new_business = Business(id=business.id, name=business.name, classification=business.classification, sales_tax_rate=business.sales_tax_rate, merchant_id=business.merchant_id, street=business.street, city=business.city,
                                state=business.state, zipcode=business.zipcode, address=business.address, phone_number=business.phone_number, merchant_stripe_id=business.merchant_stripe_id)
        session.add(new_business)
        days_of_week = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for i in range(len(days_of_week)):
            day = days_of_week[i]
            if business.schedule[i].is_closed == True:
                new_business_schedule_day = Business_Schedule_Day(
                    business_id=new_business.id, day=day, is_closed=business.schedule[i].is_closed)
            elif business.schedule[i].is_closed == False:
                new_business_schedule_day = Business_Schedule_Day(
                    business_id=new_business.id, day=day, opening_time=business.schedule[i].opening_time, closing_time=business.schedule[i].closing_time, is_closed=business.schedule[i].is_closed)
            session.add(new_business_schedule_day)
        return business

    def get_merchant_businesses(self, session: scoped_session, merchant_id: str):
        businesses = session.query(Business).filter(
            Business.merchant_id == merchant_id).all()
        return businesses

    def get_menu(self, session: scoped_session, business_id: UUID):
        business = session.query(Business).filter(
            Business.id == business_id).first()
        if business:
            menu = business.drink
            return menu
        else:
            return False

    def get_business_phone_number(self, session: scoped_session, business_phone_number: int):
        business_with_corresponding_phone_number = session.query(Business).filter(
            Business.phone_number == business_phone_number).first()
        if business_with_corresponding_phone_number:
            return business_with_corresponding_phone_number
        else:
            return False

    def update_device_token(self, session: scoped_session, device_token: str, business_id: UUID):
        business_to_update = session.query(Business).filter(
            Business.id == business_id).first()
        if business_to_update:
            business_to_update.device_token = device_token
            return True
        else:
            return False

    def get_device_token(self, session: scoped_session, business_id: UUID):
        requested_business = session.query(Business).filter(
            Business.id == business_id).first()
        if requested_business:
            device_token = requested_business.device_token
            return device_token
        else:
            return False

    def set_merchant_pin(self, session: scoped_session, business_id, pin):
        requested_business = session.query(Business).filter(
            Business.id == business_id).first()
        requested_business.merchant_pin = generate_password_hash(
            pin)
        return

    def authenticate_merchant_pin(self, session: scoped_session, business_id: UUID, pin: str):
        requested_business = session.query(Business).filter(
            Business.id == business_id).first()
        if requested_business:
            if check_password_hash(requested_business.merchant_pin, pin) == True:
                merchant = session.query(Merchant).filter(
                    Merchant.id == requested_business.merchant_id).first()
                return merchant
            else:
                return False

    def update_capacity_status(self, session: scoped_session, business_id: UUID, capacity: bool):
        business_to_update = session.query(Business).filter(
            Business.id == business_id).first()
        business_to_update.at_capacity = capacity
        return

    def update_quick_pass_queue(self, session: scoped_session, business_id: UUID, queue):
        business_to_update = session.query(Business).filter(
            Business.id == business_id).first()
        business_to_update.quick_pass_queue = queue
        return

    def update_quick_pass_queue_hour(self, session: scoped_session, business_id: UUID, queue_hour: int):
        business_to_update = session.query(Business).filter(
            Business.id == business_id).first()
        business_to_update.quick_pass_queue_hour = queue_hour
        return


class Tab_Repository(object):
    def post_tab(self, session: scoped_session, tab: Tab_Domain):
        new_tab = Tab(id=tab.id, name=tab.name, business_id=tab.business_id, customer_id=tab.customer_id, address=tab.address, street=tab.street, city=tab.city, state=tab.state,
                      zipcode=tab.zipcode, suite=tab.suite, description=tab.description, minimum_contribution=tab.minimum_contribution, fundraising_goal=tab.fundraising_goal)
        session.add(new_tab)
        return True


class Merchant_Repository(object):
    def create_stripe_account(self, session: scoped_session):
        new_account = stripe.Account.create(
            type="express",
            country="US"
        )
        new_stripe_account_id = Merchant_Stripe_Account(id=new_account.id)
        session.add(new_stripe_account_id)
        return new_account

    def authenticate_merchant(self, session: scoped_session, email: str, password: str):
        print('password', password)
        print('email', email)
        for merchant in session.query(Merchant):
            print('merchant',merchant.id)
            print('check_password_hash(merchant.password, password)',check_password_hash(merchant.password, password))
            if merchant.id == email and check_password_hash(merchant.password, password) == True:
                return merchant
        return False

    def validate_merchant(self, session: scoped_session, email: str):
        print('email', email)
        for merchant in session.query(Merchant):
            print('merchant', merchant.serialize)
            if merchant.id == email:
                return merchant
        return False

    def authenticate_merchant_stripe(self, stripe_id: str):
        merchant_stripe_status = stripe.Account.retrieve(stripe_id)
        return merchant_stripe_status['charges_enabled']

    def add_merchant(self, session: scoped_session, requested_merchant: Merchant_Domain):
        new_merchant = Merchant(id=requested_merchant.id, password=generate_password_hash(requested_merchant.password), first_name=requested_merchant.first_name,
                                last_name=requested_merchant.last_name, phone_number=requested_merchant.phone_number, number_of_businesses=requested_merchant.number_of_businesses, stripe_id=requested_merchant.stripe_id)
        session.add(new_merchant)
        return requested_merchant

    def get_merchant(self, session: scoped_session, merchant_id: str):
        requested_merchant = session.query(Merchant).filter(
            Merchant.id == merchant_id).first()
        if requested_merchant:
            requested_merchant_domain = Merchant_Domain(merchant_object=requested_merchant)
            return requested_merchant_domain
        else:
            return False


class Bouncer_Repository(object):
    def validate_username(self, session: scoped_session, username: str):
        # if a username is passed then we query the db to verify it, if the hashed version is passed then we use the check_password_hash to verify it
        bouncer = session.query(Bouncer).filter(
            Bouncer.id == username).first()
        if bouncer != None:
            # if the merchant employee id already exists return false so a duplicate merchant employee is not created
            return 0
        else:
            staged_bouncer = session.query(Staged_Bouncer).filter(
                Staged_Bouncer.id == username, Staged_Bouncer.status == 'pending').first()
            print('staged_bouncer', staged_bouncer)

            if staged_bouncer != None:
                print(2)
                return 2
            # if the merchant employee id has not already been staged by the merchant then the account should not be created
            else:
                return 1

    def add_bouncer(self, session: scoped_session, bouncer_id: str):
        staged_bouncer = session.query(Staged_Bouncer).filter(
            Staged_Bouncer.id == bouncer_id).first()

        new_bouncer = Bouncer(id=staged_bouncer.id, first_name=staged_bouncer.first_name,
                              last_name=staged_bouncer.last_name, merchant_id=staged_bouncer.merchant_id, business_id=staged_bouncer.business_id, logged_in=False)
        session.add(new_bouncer)

        staged_bouncer.status = "confirmed"
        return new_bouncer

    def get_bouncer(self, session: scoped_session, bouncer_id: str, isStagedBouncer: bool = False):
        if isStagedBouncer == False:
            requested_bouncer = session.query(Bouncer).filter(
                Bouncer.id == bouncer_id).first()
        else:
            requested_bouncer = session.query(Staged_Bouncer).filter(
                Staged_Bouncer.id == bouncer_id)
        return requested_bouncer

    def get_bouncers(self, session: scoped_session, merchant_id: str):
        bouncers = session.query(Bouncer).filter(
            Bouncer.merchant_id == merchant_id).all()
        staged_bouncers = session.query(Staged_Bouncer).filter(
            Staged_Bouncer.merchant_id == merchant_id).all()
        return staged_bouncers, bouncers

    def add_staged_bouncer(self, session: scoped_session, bouncer: Bouncer_Domain):
        new_staged_bouncer = Staged_Bouncer(
            id=bouncer.id, first_name=bouncer.first_name, last_name=bouncer.last_name, business_id=bouncer.business_id, merchant_id=bouncer.merchant_id, status="pending")
        session.add(new_staged_bouncer)
        return new_staged_bouncer

    def remove_staged_bouncer(self, session: scoped_session, bouncer_id: str):
        print('bouncer_id', bouncer_id)
        staged_bouncer_to_remove = session.query(Staged_Bouncer).filter(
            Staged_Bouncer.id == bouncer_id).delete()
        return


class Merchant_Employee_Repository(object):
    def get_stripe_account(self, session: scoped_session, merchant_employee_id: str):
        merchant_employee = session.query(Merchant_Employee).filter(
            Merchant_Employee.id == merchant_employee_id).first()
        print('merchant_employee', merchant_employee)
        return merchant_employee.stripe_id

    # this validates that the pin number is unique for the tablet upon which the merchant employee is registering
    def validate_pin(self, session: scoped_session, business_id: str, pin: str):
        for merchant_employee in session.query(Merchant_Employee).filter(Merchant_Employee.business_id == business_id):
            if check_password_hash(merchant_employee.pin, pin) == True:
                return False
        return True

    def authenticate_pin(self, session: scoped_session, pin: str, login_status: bool):
        for merchant_employee in session.query(Merchant_Employee):
            if check_password_hash(merchant_employee.pin, pin) == True:
                merchant_employee.logged_in = login_status
                return merchant_employee
        else:
            return False

    def reset_pin(self, session: scoped_session, merchant_employee_id, pin):
        for merchant_employee in session.query(Merchant_Employee):
            if merchant_employee.id == merchant_employee_id:
                merchant_employee.pin = generate_password_hash(
                    pin)
                return merchant_employee
        else:
            return False

    def validate_username(self, session: scoped_session, username: str):
        # if a username is passed then we query the db to verify it, if the hashed version is passed then we use the check_password_hash to verify it
        merchant_employee = session.query(Merchant_Employee).filter(
            Merchant_Employee.id == username).first()
        if merchant_employee != None:
            # if the merchant employee id already exists return false so a duplicate merchant employee is not created
            return 0
        else:
            staged_merchant_employee = session.query(Staged_Merchant_Employee).filter(
                Staged_Merchant_Employee.id == username, Staged_Merchant_Employee.status == 'pending').first()
            if staged_merchant_employee != None:
                return 2
            # if the merchant employee id has not already been staged by the merchant then the account should not be created
            else:
                return 1

    def add_merchant_employee(self, session: scoped_session, requested_merchant_employee: Merchant_Employee_Domain):
        new_account = stripe.Account.create(
            type="express",
            country="US"
        )
        new_stripe_account_id = Merchant_Employee_Stripe_Account(
            id=new_account.id)
        session.add(new_stripe_account_id)
        new_merchant_employee = Merchant_Employee(id=requested_merchant_employee.id, pin=generate_password_hash(requested_merchant_employee.pin), first_name=requested_merchant_employee.first_name,
                                                  last_name=requested_merchant_employee.last_name, phone_number=requested_merchant_employee.phone_number, merchant_id=requested_merchant_employee.merchant_id, business_id=requested_merchant_employee.business_id, stripe_id=new_account.id)
        requested_merchant_employee.stripe_id = new_account.id
        session.add(new_merchant_employee)
        staged_merchant_employee = session.query(Staged_Merchant_Employee).filter(
            Staged_Merchant_Employee.id == new_merchant_employee.id).first()
        staged_merchant_employee.status = "confirmed"
        return requested_merchant_employee

    def authenticate_merchant_employee_stripe(self, stripe_id: str):
        merchant_employee_stripe_status = stripe.Account.retrieve(stripe_id)
        return merchant_employee_stripe_status['charges_enabled']

    def get_merchant_employees(self, session: scoped_session, merchant_id: str):
        merchant_employees = session.query(Merchant_Employee).filter(
            Merchant_Employee.merchant_id == merchant_id).all()
        staged_merchant_employees = session.query(Staged_Merchant_Employee).filter(
            Staged_Merchant_Employee.merchant_id == merchant_id, Staged_Merchant_Employee.status == "pending").all()
        return staged_merchant_employees, merchant_employees

    def add_staged_merchant_employee(self, session: scoped_session, merchant_id:str, merchant_employee_id: str):
        new_staged_merchant_employee = Staged_Merchant_Employee(
            id=merchant_employee_id, merchant_id=merchant_id, status="pending")
        session.add(new_staged_merchant_employee)
        return

    def remove_staged_merchant_employee(self, session: scoped_session, merchant_employee_id: str):
        print('merchant_employee_id', merchant_employee_id)
        staged_merchant_employee_to_remove = session.query(Staged_Merchant_Employee).filter(
            Staged_Merchant_Employee.id == merchant_employee_id).delete()
        return

    def get_servers(self, session: scoped_session, business_id: UUID):
        servers = session.query(Merchant_Employee).filter(
            Merchant_Employee.business_id == business_id, Merchant_Employee.logged_in == True).all()
        return servers


class ETag_Repository(object):
    def get_etag(self, session: scoped_session, category: str):
        etag = session.query(ETag).filter(ETag.category == category).first()
        return etag

    def update_etag(self, session: scoped_session, category: str):
        etag = session.query(ETag).filter(ETag.category == category).first()
        etag.id += 1
        return etag.id

    def validate_etag(self, session: scoped_session, etag: ETag_Domain):
        validation = session.query(ETag).filter(
            ETag.category == etag.category, ETag.id == etag.id).first()
        if validation:
            return True
        else:
            return False


class Quick_Pass_Repository(object):
    def add_quick_pass(self, session: scoped_session, quick_pass: Quick_Pass_Domain):
        new_quick_pass = Quick_Pass(id=quick_pass.id, customer_id=quick_pass.customer_id, business_id=quick_pass.business_id, merchant_stripe_id=quick_pass.merchant_stripe_id,
                                    price=quick_pass.price, sales_tax_percentage=quick_pass.sales_tax_percentage, service_fee_total=quick_pass.service_fee_total, sales_tax_total=quick_pass.sales_tax_total,  subtotal=quick_pass.subtotal, total=quick_pass.total, date_time=quick_pass.date_time, payment_intent_id=quick_pass.payment_intent_id, activation_time=quick_pass.activation_time, expiration_time=quick_pass.expiration_time, card_information=quick_pass.card_information)
        session.add(new_quick_pass)
        return new_quick_pass

    def update_quick_pass(self, session: scoped_session, quick_pass_to_update: Quick_Pass_Domain):
        quick_pass = session.query(Quick_Pass).filter(
            Quick_Pass.id == quick_pass_to_update.id).first()
        quick_pass.time_checked_in = quick_pass_to_update.time_checked_in
        return

    def get_merchant_quick_passes(self, session: scoped_session, merchant_id: str = None):
        # quick passes to be displayed in dashboard
        if merchant_id != None:
            quick_passes = session.query(Quick_Pass, Business.id.label("business_id"),  # select from allows me to pull the entire Order from the database so I can get the Order_Drink relationship values
                                         Business.address.label("business_address"), Business.name.label("business_name"), Customer.first_name.label('customer_first_name'), Customer.last_name.label('customer_last_name')).select_from(Quick_Pass).join(Business, Quick_Pass.business_id == Business.id).join(Customer, Quick_Pass.customer_id == Customer.id).filter(Business.merchant_id == merchant_id).all()

        return quick_passes

    def set_business_quick_pass(self, session: scoped_session, quick_pass_values: dict):
        business_id = quick_pass_values['business_id']
        business = session.query(Business).filter(
            Business.id == business_id).first()
        business.quick_pass_price = quick_pass_values['quick_pass_price']
        business.quick_passes_per_hour = quick_pass_values['quick_passes_per_hour']
        return

    def get_bouncer_quick_passes(self, session: scoped_session, business_id: UUID):
        active_quick_passes = len(session.query(Quick_Pass).filter(
            Quick_Pass.business_id == business_id, Quick_Pass.expiration_time >= datetime.now()).all())
        return active_quick_passes
