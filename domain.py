from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class Drink_Domain(object):
    def __init__(self, drink_object=None, drink_json=None, init=False):
        self.quantity = 1
        self.id = ''
        self.name = ''
        self.description = ''
        self.price = ''
        self.order_drink_id = ''
        self.business_id = ''
        self.has_image = False
        if drink_object:
            self.id = drink_object.id
            self.name = drink_object.name
            self.description = drink_object.description
            self.price = drink_object.price
            self.business_id = drink_object.business_id
            self.has_image = drink_object.has_image
            if drink_object.has_image == True:
                # the drink image url will always follow this pattern
                self.image_url = f'https://storage.googleapis.com/my-new-quickbev-bucket/business/{str(self.business_id)}/menu-images/' + str(
                    self.name.lower()) + '.jpg'
            else:
                self.image_url = "https://storage.googleapis.com/my-new-quickbev-bucket/charter-roman-black-logo-no-words.png"
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
            self.business_id = drink_json["business_id"]
            self.quantity = drink_json["quantity"]

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
    def __init__(self, order_object=None, order_json=None, drinks=None):
        self.id = ''
        self.customer_id = ''
        self.customer_first_name = ''
        self.customer_last_name = ''
        self.cost = 0
        self.subtotal = 0
        self.tip_percentage = 0
        self.tip_amount = 0
        self.sales_tax_percentage = 0
        self.sales_tax = 0
        self.business_id = ''
        self.business_address = ''
        self.order_drink = ''
        self.date_time = ''
        self.merchant_stripe_id = ''
        self.service_fee = 0
        self.business_id = ''
        self.business_address = ''
        self.order_drink = []
        self.completed = False
        self.rejected = False
        self.refunded = False
        if order_object:
            # these attributes were from the join and are not nested in the result object
            self.business_name = order_object.business_name
            self.business_id = order_object.business_id
            self.business_address = order_object.business_address
            self.customer_first_name = order_object.customer_first_name
            self.customer_last_name = order_object.customer_last_name
            # the order db model object is nested inside the result as "Order"
            self.id = order_object.Order.id
            self.customer_id = order_object.Order.customer_id
            self.cost = order_object.Order.cost
            self.subtotal = order_object.Order.subtotal
            self.tip_percentage = order_object.Order.tip_percentage
            self.tip_amount = order_object.Order.tip_amount
            self.sales_tax = order_object.Order.sales_tax
            self.sales_tax_percentage = order_object.Order.sales_tax_percentage
            self.service_fee = order_object.Order.service_fee
            # formatted date string
            self.date_time = order_object.Order.date_time.strftime(
                "%m/%d/%Y")
            self.merchant_stripe_id = order_object.Order.merchant_stripe_id
            self.order_drink = Order_Drink_Domain(
                order_id=order_object.Order.id, order_drink_object=order_object.Order.order_drink, drinks=drinks)
            self.completed = order_object.Order.completed
            self.rejected = order_object.Order.rejected
            self.refunded = order_object.Order.refunded
        elif order_json:
            self.id = order_json["id"]
            self.customer_id = order_json['customer_id']
            self.merchant_stripe_id = order_json["merchant_stripe_id"]
            self.cost = order_json["cost"]
            self.subtotal = order_json["subtotal"]
            self.tip_percentage = order_json["tip_percentage"]
            self.tip_amount = order_json["tip_amount"]
            self.sales_tax_percentage = order_json["sales_tax_percentage"]
            self.business_id = order_json["business_id"]
            self.date_time = datetime.fromtimestamp(
                int(order_json["date_time"]))
            self.order_drink = Order_Drink_Domain(
                order_id=self.id, order_drink_json=order_json['order_drink'])
            self.completed = order_json["completed"]
            self.rejected = order_json["rejected"]
            self.refunded = order_json["refunded"]

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            # UUID is not json serializable so i have to stringify it
            if attribute_names[i] == "id" or attribute_names[i] == "business_id":
                serialized_attributes[attribute_names[i]] = str(attributes[i])
            elif attribute_names[i] == "order_drink" and not isinstance(attributes[i], list):
                serialized_attributes[attribute_names[i]
                                      ] = attributes[i].dto_serialize()
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Order_Drink_Domain(object):
    def __init__(self, order_id=None, order_drink_object=None, order_drink_json=None, drinks=None):
        self.order_id = order_id
        self.order_drink = list()
        if order_drink_object:
            for order_drink_instance in order_drink_object:
                for drink in drinks:
                    if order_drink_instance.drink_id == drink.id:
                        new_drink = Drink_Domain(drink_object=drink)
                        # order drink id will only exist when data if being pulled from the backend because the UUID is generated by the database
                        new_drink.order_drink_id = order_drink_instance.id
                        self.order_drink.append(new_drink)
                        break
        elif order_drink_json:
            drink_id_list = list()
            for customer_drink in order_drink_json:
                drink_domain = Drink_Domain(drink_json=customer_drink["drink"])
                if drink_domain.id not in drink_id_list:
                    drink_id_list.append(drink_domain.id)
                    self.order_drink.append(drink_domain)
                else:
                    for drink in self.order_drink:
                        if drink.id == drink_domain.id:
                            drink.quantity += drink_domain.quantity

    def dto_serialize(self):
        serialized_attributes = {}
        serialized_attributes['order_id'] = str(self.order_id)
        serialized_attributes["order_drink"] = [
            x.dto_serialize() for x in self.order_drink]
        return serialized_attributes


class Customer_Domain(object):
    def __init__(self, customer_object=None, customer_json=None):
        if customer_json == None and customer_object == None:
            # this will be dummy data to display customer attributes to newly signed merchants
            self.id = ""
            self.first_name = ""
            self.last_name = ""
            self.has_registered = False
        if customer_object:
            self.id = customer_object.id
            self.first_name = customer_object.first_name
            self.last_name = customer_object.last_name
            self.email_verified = customer_object.email_verified
            for key in customer_object.__dict__.keys():
                print('customer key', key)
            if "has_registered" in customer_object.__dict__.keys():
                self.has_registered = customer_object.has_registered
            # self.has_registered = False

            # might not want to send this sensitive information in every request
            if "password" in customer_object.__dict__.keys():
                self.password = customer_object.password
            if "stripe_id" in customer_object.__dict__.keys():
                self.stripe_id = customer_object.stripe_id
        elif customer_json:
            # has registered property will be false when the customer is created initially
            self.id = customer_json["id"]
            self.password = generate_password_hash(
                customer_json["password"], "sha256")
            self.email_verified = customer_json["email_verified"]
            self.first_name = customer_json["first_name"]
            self.last_name = customer_json["last_name"]
            self.stripe_id = customer_json["stripe_id"]

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


class Merchant_Domain(object):
    def __init__(self, merchant_object=None, merchant_json=None):
        self.id = ''
        self.password = ''
        self.first_name = ''
        self.last_name = ''
        self.phone_number = ''
        self.number_of_businesses = ''
        self.stripe_id = ''
        if merchant_object:
            self.id = merchant_object.id
            self.password = merchant_object.password
            self.first_name = merchant_object.first_name
            self.last_name = merchant_object.last_name
            self.phone_number = merchant_object.phone_number
            self.number_of_businesses = merchant_object.number_of_businesses
            self.stripe_id = merchant_object.stripe_id

            if merchant_object.id == 'patardriscoll@gmail.com':
                self.is_administrator = True

        elif merchant_json:
            self.id = merchant_json["id"]
            self.password = merchant_json["password"]
            self.first_name = merchant_json["first_name"]
            self.last_name = merchant_json["last_name"]
            self.phone_number = merchant_json["phone_number"]
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


class Merchant_Employee_Domain(object):
    def __init__(self, merchant_employee_object=None, merchant_employee_json=None):
        self.id = ''
        self.pin_number = ''
        self.first_name = ''
        self.last_name = ''
        self.phone_number = ''
        self.pin_number = ''
        self.business_id = ''
        self.merchant_id = ''
        self.stripe_id = ''
        self.logged_in = ''
        if merchant_employee_object:
            self.id = merchant_employee_object.id
            self.merchant_id = merchant_employee_object.merchant_id
            self.business_id = merchant_employee_object.business_id
            self.pin_number = merchant_employee_object.pin_number
            self.first_name = merchant_employee_object.first_name
            self.last_name = merchant_employee_object.last_name
            self.phone_number = merchant_employee_object.phone_number
            self.logged_in = merchant_employee_object.logged_in
            # stripe ID is in an associative table now so if a vanilla merchant_employee object is returned then it wont have the stripe id
            if 'stripe_id' in merchant_employee_object.__dict__:
                self.stripe_id = merchant_employee_object.stripe_id

        elif merchant_employee_json:
            self.id = merchant_employee_json["id"]
            self.pin_number = merchant_employee_json["pin_number"]
            self.first_name = merchant_employee_json["first_name"]
            self.last_name = merchant_employee_json["last_name"]
            self.business_id = merchant_employee_json['business_id']
            self.merchant_id = merchant_employee_json['merchant_id']
            self.phone_number = merchant_employee_json["phone_number"]
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


class Business_Domain(object):
    def __init__(self, business_object=None, business_json=None):
        self.sales_tax_rate = 0.0625
        self.id = ''
        self.merchant_id = ''
        self.name = ''
        self.address = ''
        self.classification = ''
        # this attribute will only be present when the business is being pulled from the backend
        self.merchant_stripe_id = ''
        self.street = ''
        self.city = ''
        self.state = ''
        self.zipcode = ''
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
            self.tablet = business_object.tablet

            self.sales_tax_rate = business_object.sales_tax_rate
            self.classification = business_object.classification
            self.merchant_stripe_id = business_object.merchant_stripe_id
            self.menu = [Drink_Domain(drink_object=x)
                         for x in business_object.drink]
        if business_json:
            self.id = uuid.uuid4()
            self.merchant_id = business_json["merchant_id"]
            self.merchant_stripe_id = business_json["merchant_stripe_id"]
            self.name = business_json["name"]
            self.classification = business_json["classification"]
            self.address = business_json["address"]

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
            self.tablet = business_json["tablet"]
            self.phone_number = business_json["phone_number"]

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
            else:
                serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes


class Tab_Domain(object):
    def __init__(self, tab_object=None, tab_json=None):
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
            self.date_time = tab_object.date_time
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
            self.date_time = datetime.fromtimestamp(tab_json["date_time"])
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
    def __init__(self, etag_object=None, etag_json=None):
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
