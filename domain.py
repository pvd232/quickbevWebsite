from datetime import datetime
from werkzeug.security import generate_password_hash
import uuid
from models import Bouncer, Business, Business_Schedule_Day, Customer, Drink, ETag, Merchant, Merchant_Employee, Order, Order_Drink, Quick_Pass, Tab, service_fee_percentage


class Customer_Order_Status(object):
    def __init__(self, order_object: Order):
        self.id = order_object.id
        self.completed = order_object.completed
        self.refunded = order_object.refunded

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == 'id':
                serialized_attributes[attribute_names[i]] = str(attributes[i])
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Drink_Domain(object):
    def __init__(self, drink_object: Drink = None, drink_json: dict = None, init: bool = False):
        self.quantity = 1
        self.id = ''
        self.name = ''
        self.description = ''
        self.price = ''
        self.business_id: uuid = ''
        self.image_url = ''
        if drink_object:
            self.id = drink_object.id
            self.name = drink_object.name
            self.description = drink_object.description
            self.price = drink_object.price
            self.business_id = drink_object.business_id
            self.is_active = drink_object.is_active
            self.image_url = drink_object.image_url

            if drink_object.image_url != None:
                # the drink image url will always follow this pattern
                self.image_url = drink_object.image_url
            else:
                self.image_url = "https://storage.googleapis.com/my-new-quickbev-bucket/original.png"
        elif init == True and drink_json:
            # this is the initialization for creating the menu and adding the menu drinks to the database
            self.name = drink_json["name"]
            self.description = drink_json["description"]
            self.price = drink_json["price"]
            self.has_image = drink_json["has_image"]
            # only use this for attaching the file to the drink when uploading it to google cloud
            self.file = ''
        elif drink_json:
            # no need to receive image_url from the front end
            self.id = drink_json["id"]
            self.name = drink_json["name"]
            self.description = drink_json["description"]
            self.price = drink_json["price"]
            self.business_id = uuid.UUID(drink_json["business_id"])

    def set_image_url(self, file_name: str):
        self.image_url = f'https://storage.googleapis.com/my-new-quickbev-bucket/business/{str(self.business_id)}/menu-images/' + \
            file_name
        self.blob_name = f'business/{str(self.business_id)}/menu-images/' + \
            file_name

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == 'id' or attribute_names[i] == 'order_drink_id' or attribute_names[i] == 'business_id':
                serialized_attributes[attribute_names[i]] = str(attributes[i])
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Order_Domain(object):
    def __init__(self, order_object: Order = None, order_result=None, order_json: dict = None, is_customer_order=True):
        self.id = ''
        self.customer_id = ''
        # this property does not exist in the database, it is used for stripe_payment_intent and is captured in iOS during the order process
        self.business_id = ''
        self.merchant_stripe_id = ''

        self.sales_tax_percentage = 0.0
        self.tip_percentage = 0.0
        self.service_fee_percentage = 0.0
        self.stripe_fee_percentage = 0.0

        self.subtotal = 0.0
        self.tip_total = 0.0
        self.service_fee_total = 0.0
        self.stripe_application_fee_total = 0.0
        self.sales_tax_total = 0.0
        self.total = 0.0
        self.stripe_fee_total = 0.0
        self.net_stripe_application_fee_total = 0.0
        self.net_service_fee_total = 0.0

        self.date_time = ''
        self.payment_intent_id = ''
        self.card_information = ''
        self.completed = False
        self.refunded = False
        self.order_drink = []
        self.formatted_date_time = datetime.now().strftime(
            "%m/%d/%Y")

        if order_object and is_customer_order == True:
            self.id = order_object.id
            self.customer_id = order_object.customer_id
            self.business_id = order_object.business_id
            self.total = order_object.total
            self.subtotal = order_object.subtotal
            self.tip_percentage = order_object.tip_percentage
            self.tip_total = order_object.tip_total
            self.sales_tax_total = order_object.sales_tax_total
            self.sales_tax_percentage = order_object.sales_tax_percentage
            self.service_fee_total = order_object.service_fee_total
            self.stripe_application_fee_total = order_object.stripe_application_fee_total
            self.stripe_fee_percantage = order_object.stripe_fee_percentage
            self.net_service_fee_total = order_object.net_service_fee_total
            self.net_stripe_application_fee_total = order_object.net_stripe_application_fee_total
            self.card_information = order_object.card_information
            # formatted date string
            self.formatted_date_time = order_object.date_time.strftime(
                "%m/%d/%Y")
            self.date_time = order_object.date_time
            self.merchant_stripe_id = order_object.merchant_stripe_id
            unique_drinks_ids = []
            for order_drink in order_object.order_drink:
                if order_drink.drink_id not in unique_drinks_ids:
                    unique_drinks_ids.append(order_drink.drink_id)
                    new_order_drink = Order_Drink_Domain(
                        order_drink_object=order_drink)
                    self.order_drink.append(new_order_drink)
                else:
                    for previous_order_drink in self.order_drink:
                        if previous_order_drink.drink_id == order_drink.drink_id:
                            previous_order_drink.quantity += 1
                            break
            self.completed = order_object.completed
            self.refunded = order_object.refunded
            self.payment_intent_id = order_object.payment_intent_id

        # dart orders need customer name
        elif order_result:
            self.id = order_result.Order.id
            self.customer_id = order_result.Order.customer_id
            self.business_id = order_result.Order.business_id

            # custom properties for android tablet
            self.customer_first_name = order_result.customer_first_name
            self.customer_last_name = order_result.customer_last_name

            self.total = order_result.Order.total
            self.subtotal = order_result.Order.subtotal
            self.tip_percentage = order_result.Order.tip_percentage
            self.tip_total = order_result.Order.tip_total
            self.sales_tax_total = order_result.Order.sales_tax_total
            self.sales_tax_percentage = order_result.Order.sales_tax_percentage
            self.service_fee_total = order_result.Order.service_fee_total
            self.stripe_application_fee_total = order_result.Order.stripe_application_fee_total
            self.stripe_fee_percantage = order_result.Order.stripe_fee_percentage
            self.net_service_fee_total = order_result.Order.net_service_fee_total
            self.net_stripe_application_fee_total = order_result.Order.net_stripe_application_fee_total
            self.card_information = order_result.Order.card_information
            # formatted date string
            self.formatted_date_time = order_result.Order.date_time.strftime(
                "%m/%d/%Y")
            self.date_time = order_result.Order.date_time
            self.merchant_stripe_id = order_result.Order.merchant_stripe_id
            unique_drinks_ids = []
            for order_drink in order_result.Order.order_drink:
                if order_drink.drink_id not in unique_drinks_ids:
                    unique_drinks_ids.append(order_drink.drink_id)
                    new_order_drink = Order_Drink_Domain(
                        order_drink_object=order_drink)
                    self.order_drink.append(new_order_drink)
                else:
                    for previous_order_drink in self.order_drink:
                        if previous_order_drink.drink_id == order_drink.drink_id:
                            previous_order_drink.quantity += 1
                            break
            self.completed = order_result.Order.completed
            self.refunded = order_result.Order.refunded
            self.payment_intent_id = order_result.Order.payment_intent_id
        elif order_json:
            # an order received as order_json will be an order sent from an iOS device, thus service fee is not included as a value because it is calculated in the backend
            self.id = uuid.UUID(order_json["id"])
            # these props will only be send from iOS

            self.customer_id = order_json["customer_id"]
            self.merchant_stripe_id = order_json["merchant_stripe_id"]
            self.total = order_json["total"]
            self.subtotal = order_json["subtotal"]
            self.tip_percentage = order_json["tip_percentage"]
            self.sales_tax_percentage = order_json["sales_tax_percentage"]
            self.business_id = order_json["business_id"]
            for order_drink in order_json['order_drink']:
                new_order_drink = Order_Drink_Domain(
                    order_drink_json=order_drink, is_customer_order=is_customer_order)
                self.order_drink.append(new_order_drink)
            self.date_time = datetime.fromtimestamp(
                int(order_json["date_time"]))
            self.completed = order_json["completed"]
            self.refunded = order_json["refunded"]
            self.payment_intent_id = order_json["payment_intent_id"]
            self.card_information = order_json["card_information"]

    def dto_serialize(self):
        serialized_attributes = {}
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == "id" or attribute_names[i] == "business_id":
                serialized_attributes[attribute_names[i]] = str(attributes[i])
            elif attribute_names[i] == 'date_time':
                serialized_attributes[attribute_names[i]
                                      ] = attributes[i].timestamp()
            elif attribute_names[i] == "order_drink":
                order_drink_list = []
                for order_drink in attributes[i]:
                    order_drink_list.append(order_drink.dto_serialize())
                serialized_attributes[attribute_names[i]
                                      ] = order_drink_list
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Order_Drink_Domain(object):
    def __init__(self, order_drink_object: Order_Drink = None, order_drink_json: dict = None, is_customer_order: bool = False):
        self.is_customer_order = is_customer_order
        if order_drink_object:
            self.order_id = order_drink_object.order_id
            self.drink_id = order_drink_object.drink_id
            self.quantity = 1
        # this is for a customer order coming from iOS, much simpler data structure
        elif order_drink_json:
            self.order_id = uuid.UUID(order_drink_json["order_id"])
            self.drink_id = uuid.UUID(order_drink_json["drink_id"])
            self.quantity = order_drink_json["quantity"]
            if is_customer_order == True:
                self.price = order_drink_json["price"]

    def dto_serialize(self):
        serialized_attributes = {}
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] in ['id', 'drink_id', 'order_id']:
                serialized_attributes[attribute_names[i]] = str(
                    attributes[i])
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Customer_Domain(object):
    def __init__(self, customer_object: Customer = None, customer_json: dict = None):
        if customer_json == None and customer_object == None:
            # this will be dummy data to display customer attributes to newly signed merchants
            self.id = ""
            self.first_name = ""
            self.last_name = ""
            self.has_registered = False
            self.stripe_id = ""
        if customer_object:
            self.id = customer_object.id
            self.first_name = customer_object.first_name
            self.last_name = customer_object.last_name
            self.email_verified = customer_object.email_verified
            self.date_time = customer_object.date_time
            self.is_active = customer_object.is_active
            if "has_registered" in customer_object.__dict__.keys():
                self.has_registered = customer_object.has_registered
            # might not want to send this sensitive information in every request
            if "password" in customer_object.__dict__.keys():
                self.password = customer_object.password
            if "stripe_id" in customer_object.__dict__.keys():
                self.stripe_id = customer_object.stripe_id
            if "apple_id" in customer_object.__dict__.keys():
                self.apple_id = customer_object.apple_id
        elif customer_json:
            # has registered property will be false when the customer is created initially
            self.id = customer_json["id"]
            self.password = generate_password_hash(
                customer_json["password"], "sha256")
            self.email_verified = customer_json["email_verified"]
            self.first_name = customer_json["first_name"]
            self.last_name = customer_json["last_name"]
            self.stripe_id = customer_json["stripe_id"]
            # convert swift timestamp to python datetime
            self.date_time = datetime.fromtimestamp(
                int(customer_json["date_time"]))
            if "apple_id" in customer_json:
                self.apple_id = customer_json["apple_id"]
            else:
                self.apple_id = ""

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == 'id':
                serialized_attributes['id'] = str(self.id)
            elif attribute_names[i] == 'date_time':
                # return timestamp whenever sending python datetime object in JSON
                serialized_attributes[attribute_names[i]
                                      ] = self.date_time.timestamp()
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Merchant_Domain(object):
    def __init__(self, merchant_object: Merchant = None, merchant_json: dict = None):
        self.id = ''
        self.password = ''
        self.first_name = ''
        self.last_name = ''
        self.phone_number = ''
        self.number_of_businesses = ''
        self.stripe_id = ''
        self.is_administrator = False
        self.status = ""
        self.drink_e_tag_id = ""
        self.business_e_tag_id = ""
        if merchant_object:
            self.id = merchant_object.id
            self.password = merchant_object.password
            self.first_name = merchant_object.first_name
            self.last_name = merchant_object.last_name
            self.phone_number = merchant_object.phone_number
            self.number_of_businesses = merchant_object.number_of_businesses
            self.stripe_id = merchant_object.stripe_id
            self.status = "confirmed"
            if merchant_object.id == 'patardriscoll@gmail.com':
                self.is_administrator = True
            self.drink_e_tag_id = merchant_object.drink_e_tag_id
            self.business_e_tag_id = merchant_object.business_e_tag_id

        elif merchant_json:
            self.id = merchant_json["id"]
            self.password = merchant_json["password"]
            self.first_name = merchant_json["first_name"]
            self.last_name = merchant_json["last_name"]
            self.phone_number = merchant_json["phone_number"]
            if merchant_json["id"] == 'patardriscoll@gmail.com':
                self.is_administrator = True
            # number of locations is added as a property later in the signup process so it won't be present when checking if the merchant exists at step one
            if "number_of_businesses" in merchant_json:
                self.number_of_businesses = merchant_json["number_of_businesses"]
            # when the merchant object is validated it wont be present initially
            if "stripe_id" in merchant_json:
                self.stripe_id = merchant_json["stripe_id"]

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == 'id':
                serialized_attributes['id'] = str(self.id)
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Bouncer_Domain(object):
    def __init__(self, bouncer_object: Bouncer = None, bouncer_json: dict = None, isStagedBouncer: bool = False):
        self.id = ''
        self.first_name = ''
        self.last_name = ''
        self.business_id = ''
        self.merchant_id = ''
        self.logged_in = False
        self.status = ''
        if bouncer_object:
            self.id = bouncer_object.id
            self.merchant_id = bouncer_object.merchant_id
            self.business_id = bouncer_object.business_id
            self.first_name = bouncer_object.first_name
            self.last_name = bouncer_object.last_name
            if isStagedBouncer == True:
                self.status = bouncer_object.status
            if isStagedBouncer == False:
                self.logged_in = bouncer_object.logged_in

        elif bouncer_json:
            self.id = bouncer_json["id"]
            self.first_name = bouncer_json["first_name"]
            self.last_name = bouncer_json["last_name"]
            self.business_id = uuid.UUID(bouncer_json['business_id'])
            self.merchant_id = bouncer_json['merchant_id']
            self.logged_in = bouncer_json['logged_in']
            self.status = bouncer_json['status']

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == 'id':
                serialized_attributes['id'] = str(self.id)
            elif attribute_names[i] == 'merchant_id' or attribute_names[i] == 'business_id':
                serialized_attributes[attribute_names[i]] = str(attributes[i])
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Merchant_Employee_Domain(object):
    def __init__(self, merchant_employee_object: Merchant_Employee = None, merchant_employee_json: dict = None):
        self.id = ''
        self.pin = ''
        self.first_name = ''
        self.last_name = ''
        self.pin = ''
        self.business_id = ''
        self.merchant_id = ''
        self.stripe_id = ''
        self.logged_in = ''
        self.status = ''
        if merchant_employee_object:
            self.id = merchant_employee_object.id
            self.merchant_id = merchant_employee_object.merchant_id
            self.business_id = merchant_employee_object.business_id
            self.pin = merchant_employee_object.pin
            self.first_name = merchant_employee_object.first_name
            self.last_name = merchant_employee_object.last_name
            self.logged_in = merchant_employee_object.logged_in
            # stripe ID is in an associative table now so if a vanilla merchant_employee object is returned then it wont have the stripe id
            if 'stripe_id' in merchant_employee_object.__dict__:
                self.stripe_id = merchant_employee_object.stripe_id

        elif merchant_employee_json:
            self.id = merchant_employee_json["id"]
            self.pin = merchant_employee_json["pin"]
            self.first_name = merchant_employee_json["first_name"]
            self.last_name = merchant_employee_json["last_name"]
            self.business_id = uuid.UUID(merchant_employee_json['business_id'])
            self.merchant_id = merchant_employee_json['merchant_id']
            self.logged_in = merchant_employee_json['logged_in']
            # when the merchant_employee object is validated it wont be present initially
            if "stripe_id" in merchant_employee_json:
                self.stripe_id = merchant_employee_json["stripe_id"]

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == 'id':
                serialized_attributes['id'] = str(self.id)
            elif attribute_names[i] == 'merchant_id':
                serialized_attributes['merchant_id'] = str(self.merchant_id)
            elif attribute_names[i] == 'business_id':
                serialized_attributes['business_id'] = str(self.business_id)
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Business_Schedule_Day_Domain(object):
    def __init__(self, business_schedule_day_object: Business_Schedule_Day = None, business_schedule_day_json: dict = None):
        self.day = ''
        self.opening_time = ''
        self.closing_time = ''
        self.is_closed = ''
        self.business_id = ''

        if business_schedule_day_object != None:
            self.day = business_schedule_day_object.day
            self.is_closed = business_schedule_day_object.is_closed
            self.business_id = business_schedule_day_object.business_id
            if self.is_closed == False:
                self.opening_time = business_schedule_day_object.opening_time
                self.closing_time = business_schedule_day_object.closing_time

        if business_schedule_day_json != None:
            self.day = business_schedule_day_json["day"]
            self.is_closed = business_schedule_day_json["isClosed"]
            if self.is_closed == False:
                self.opening_time = datetime.strptime(
                    business_schedule_day_json["openingTime"], '%H:%M').time()
                self.closing_time = datetime.strptime(
                    business_schedule_day_json["closingTime"], '%H:%M').time()
            else:
                self.opening_time = ""
                self.closing_time = ""

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == 'opening_time' or attribute_names[i] == 'closing_time' or attribute_names[i] == 'business_id':
                if self.is_closed == False or attribute_names[i] == 'business_id':
                    serialized_attributes[attribute_names[i]] = str(
                        attributes[i])
                else:
                    serialized_attributes[attribute_names[i]] = ""
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Business_Domain(object):
    def __init__(self, business_object: Business = None, business_json: dict = None):
        self.sales_tax_rate = 0.0625
        self.id = ''
        self.merchant_id = ''
        self.name = ''
        self.phone_number = ''
        self.address = ''
        self.classification = ''
        self.merchant_stripe_id = ''
        self.street = ''
        self.city = ''
        self.state = ''
        self.zipcode = ''
        self.at_capacity = False
        self.schedule = []
        self.service_fee_percentage = service_fee_percentage
        if business_object:
            self.id = business_object.id
            self.merchant_id = business_object.merchant_id
            self.name = business_object.name
            self.phone_number = business_object.phone_number

            self.address = business_object.address

            address_list = business_object.address.split(",")

            self.street = address_list[0]
            self.city = address_list[1]

            state_and_zipcode = address_list[2].split(" ")

            self.state = state_and_zipcode[1]
            self.zipcode = state_and_zipcode[2]

            self.sales_tax_rate = business_object.sales_tax_rate
            self.classification = business_object.classification
            self.merchant_stripe_id = business_object.merchant_stripe_id
            self.menu = [Drink_Domain(drink_object=x)
                         for x in business_object.drink]
            self.at_capacity = business_object.at_capacity
            for day_object in business_object.schedule:
                new_day_domain = Business_Schedule_Day_Domain(
                    business_schedule_day_object=day_object)
                self.schedule.append(new_day_domain)
            self.is_active = business_object.is_active
            self.quick_pass_price = business_object.quick_pass_price
            self.quick_pass_queue = business_object.quick_pass_queue
            self.quick_pass_queue_hour = business_object.quick_pass_queue_hour

        if business_json:
            self.id = uuid.uuid4()
            self.phone_number = business_json["phone_number"]
            self.merchant_id = business_json["merchant_id"]
            self.merchant_stripe_id = business_json["merchant_stripe_id"]
            self.name = business_json["name"]
            self.classification = business_json["classification"]
            self.address = business_json["address"]

            # this property is set in the backend
            # self.at_capacity = business_json['at_capacity']

            for day_json in business_json["schedule"]:
                day_json['business_id'] = self.id
                new_day_domain = Business_Schedule_Day_Domain(
                    business_schedule_day_json=day_json)
                self.schedule.append(new_day_domain)
            try:
                address_list = [x.strip()
                                for x in business_json["address"].split(",")]
                self.street = address_list[0]
                self.city = address_list[1]

                state_and_zipcode = address_list[2].split(" ")
                while "" in state_and_zipcode:
                    state_and_zipcode.remove("")
                if len(state_and_zipcode) > 1:
                    self.state = state_and_zipcode[0]
                    self.zipcode = state_and_zipcode[1]
                elif len(state_and_zipcode) == 1:
                    self.state = state_and_zipcode[0]
                    self.zipcode = None
            except Exception as e:
                print('address exception', e)
            if "menu_url" in business_json:
                self.menu_url = business_json["menu_url"]
            else:
                self.menu_url = None

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            if attribute_names[i] == 'id':
                serialized_attributes['id'] = str(attributes[i])
            elif attribute_names[i] == 'menu':
                serialized_attributes['menu'] = [
                    x.dto_serialize() for x in attributes[i]]
            elif attribute_names[i] == 'schedule':
                serialized_attributes['schedule'] = [
                    x.dto_serialize() for x in self.schedule]
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Tab_Domain(object):
    def __init__(self, tab_object: Tab = None, tab_json: dict = None):
        self.id = ''
        self.name = ''
        self.business_id = ''
        self.customer_id = ''
        self.address = ''
        self.date_time = ''
        self.description = ''
        self.minimum_contribution = ''
        self.fundraising_goal = ''
        if tab_object:
            self.id = tab_object.id
            self.name = tab_object.name
            self.business_id = tab_object.business_id
            self.customer_id = tab_object.customer_id
            self.address = tab_object.address
            self.description = tab_object.description
            self.minimum_contribution = tab_object.minimum_contribution
            self.fundraising_goal = tab_object.fundraising_goal
        if tab_json:
            self.id = tab_json["id"]
            self.name = tab_json["name"]
            self.business_id = tab_json["business_id"]
            self.customer_id = tab_json["customer_id"]
            self.address = tab_json["address"]

            address_list = tab_json["address"].split(",")
            self.street = address_list[0]
            self.city = address_list[1]
            self.state = address_list[2]
            self.zipcode = address_list[3]
            self.description = tab_json["description"]
            self.minimum_contribution = tab_json["minimum_contribution"]
            self.fundraising_goal = tab_json["fundraising_goal"]

    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class ETag_Domain(object):
    def __init__(self, etag_object: ETag = None, etag_json: dict = None):
        if etag_object:
            self.id = etag_object.id
            self.category = etag_object.category
        elif etag_json:
            self.id = etag_json["id"]
            self.category = etag_json["category"]

    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Quick_Pass_Domain(object):
    def __init__(self, quick_pass_object: Quick_Pass = None, quick_pass_json: dict = None, js_object: dict = None, should_display_expiration_time: bool = False):
        self.id = ''
        self.customer_id = ''
        self.customer_first_name = ''
        self.customer_last_name = ''
        self.business_id = ''
        self.merchant_stripe_id = ''
        self.price = 0.0
        self.service_fee_total = 0.0
        self.sales_tax_total = 0.0
        self.sales_tax_percentage = 0.0
        self.total = 0.0
        self.subtotal = 0.0
        self.date_time = ''
        self.payment_intent_id = ''
        self.activation_time = datetime.now()
        self.expiration_time = ''
        self.time_checked_in = ''
        self.should_display_expiration_time = should_display_expiration_time
        self.sold_out = False
        self.card_information = ''
        if quick_pass_object:
            self.id = quick_pass_object.id
            self.business_id = quick_pass_object.business_id
            self.customer_id = quick_pass_object.customer_id
            self.customer_first_name = quick_pass_object.customer.first_name
            self.customer_last_name = quick_pass_object.customer.last_name
            self.price = quick_pass_object.price
            self.total = quick_pass_object.total
            self.service_fee_total = quick_pass_object.service_fee_total
            self.sales_tax_total = quick_pass_object.sales_tax_total
            self.merchant_stripe_id = quick_pass_object.merchant_stripe_id
            self.activation_time = quick_pass_object.activation_time
            self.expiration_time = quick_pass_object.expiration_time
            self.card_information = quick_pass_object.card_information
        elif quick_pass_json:
            # service_fee_total will never be sent from front end, it will always be computed or pulled from database
            self.id = uuid.UUID(quick_pass_json["id"])
            self.customer_id = quick_pass_json["customer_id"]
            self.activation_time = datetime.fromtimestamp(
                int(quick_pass_json['activation_time']))
            self.date_time = datetime.fromtimestamp(
                int(quick_pass_json['date_time']))
            # will only need this property when receiving a new business queue order from a customer
            self.business_id = uuid.UUID(quick_pass_json["business_id"])
            self.merchant_stripe_id = quick_pass_json["merchant_stripe_id"]
            self.payment_intent_id = quick_pass_json["payment_intent_id"]
            self.total = quick_pass_json["total"]
            self.price = quick_pass_json["price"]
            self.sales_tax_percentage = quick_pass_json["sales_tax_percentage"]
            self.sales_tax_total = quick_pass_json["sales_tax_total"]
            self.expiration_time = datetime.fromtimestamp(
                int(quick_pass_json["expiration_time"]))
            self.card_information = quick_pass_json["card_information"]
            # optional values
            if quick_pass_json.__contains__('time_checked_in'):
                self.time_checked_in = datetime.fromtimestamp(
                    int(quick_pass_json["time_checked_in"]))
        elif js_object:
            self.id = js_object["id"]
            self.customer_id = js_object["customer_id"]
            self.activation_time = datetime.fromtimestamp(
                int(js_object['activation_time']))
            self.business_id = uuid.UUID(js_object["business_id"])
            self.time_checked_in = datetime.fromtimestamp(
                int(js_object["time_checked_in"]))

        # this is dummy data if there at no quick passes created yet
        elif quick_pass_json == None and quick_pass_object == None and js_object == None:
            self.expiration_time = datetime.now()
            self.activation_time = datetime.now()
            self.date_time = datetime.now()

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            # UUID is not json serializable so i have to stringify it
            if attribute_names[i] == "id" or attribute_names[i] == "business_id":
                serialized_attributes[attribute_names[i]] = str(attributes[i])
            elif attribute_names[i] == 'date_time' or attribute_names[i] == 'activation_time' or attribute_names[i] == 'time_checked_in' or attribute_names[i] == 'expiration_time':
                if attributes[i] != '':
                    my_date = attributes[i].timestamp()
                    serialized_attributes[attribute_names[i]] = my_date
                else:
                    serialized_attributes[attribute_names[i]] = attributes[i]
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes
