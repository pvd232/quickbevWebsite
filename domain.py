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
        if drink_object:
            self.id = drink_object.id
            self.name = drink_object.name
            self.description = drink_object.description
            self.price = drink_object.price
            self.business_id = drink_object.business_id
        elif init == True and drink_json:
            self.name = drink_json["name"]
            self.description = drink_json["description"]
            self.price = drink_json["price"]
        elif drink_json:
            print('drink_json', drink_json)
            self.id = drink_json["id"]
            self.name = drink_json["name"]
            self.description = drink_json["description"]
            self.price = drink_json["price"]
            self.business_id = drink_json["business_id"]
            self.quantity = drink_json["quantity"]

    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

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
        self.cost = 0
        self.subtotal = 0
        self.tip_percentage = 0
        self.tip_amount = 0
        self.sales_tax_rate = 0
        self.business_id = ''
        self.address = ''
        self.order_drink = ''
        self.date_time = ''
        self.merchant_stripe_id = ''
        if order_object:
            # these attributes were from the join and are not nested in the result object
            self.business_name = order_object.business_name
            self.business_id = order_object.business_id
            self.business_address = order_object.business_address
            # the order db model object is nested inside the result as "Order"
            self.id = order_object.Order.id
            self.customer_id = order_object.Order.customer_id
            self.cost = order_object.Order.cost
            self.subtotal = order_object.Order.subtotal
            self.tip_percentage = order_object.Order.tip_percentage
            self.tip_amount = order_object.Order.tip_amount
            self.sales_tax_rate = order_object.Order.sales_tax
            self.sales_tax_percentage = order_object.Order.sales_tax_percentage

            # formatted date string
            self.date_time = order_object.Order.date_time.strftime(
                "%m/%d/%Y")
            self.order_drink = Order_Drink_Domain(
                order_id=order_object.Order.id, order_drink_object=order_object.Order.order_drink, drinks=drinks)
        elif order_json:
            self.id = order_json["id"]
            self.customer = Customer_Domain(
                customer_json=order_json["customer"])
            self.customer_id = self.customer.id
            self.merchant_stripe_id = order_json["merchant_stripe_id"]
            self.cost = order_json["cost"]
            self.subtotal = order_json["subtotal"]
            self.tip_percentage = order_json["tip_percentage"]
            self.tip_amount = order_json["tip_amount"]
            self.sales_tax_percentage = order_json["sales_tax_percentage"]
            self.business_id = order_json["business_id"]
            self.date_time = datetime.fromtimestamp(order_json["date_time"])
            print('date_time', datetime.fromtimestamp(order_json["date_time"]))
            self.order_drink = Order_Drink_Domain(
                order_id=self.id, order_drink_json=order_json['order_drink'])

    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

    def dto_serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            # UUID is not json serializable so i have to stringify it
            if attribute_names[i] == "id" or attribute_names[i] == "business_id":
                serialized_attributes[attribute_names[i]] = str(attributes[i])
            elif attribute_names[i] == "order_drink":
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
            drink_id_list = list()
            for order_drink_instance in order_drink_object:
                if order_drink_instance.drink_id not in drink_id_list:
                    drink_id_list.append(order_drink_instance.drink_id)
                    for drink in drinks:
                        if order_drink_instance.drink_id == drink.id:
                            new_drink = Drink_Domain(drink_object=drink)
                            # order drink id will only exist when data if being pulled from the backend because the UUID is generated by the database
                            new_drink.order_drink_id = order_drink_instance.id
                    self.order_drink.append(new_drink)
                else:
                    for drink in self.order_drink:
                        if drink.id == order_drink_instance.id:
                            drink.quantity += order_drink_instance.quantity
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

    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

    def dto_serialize(self):
        serialized_attributes = {}
        serialized_attributes['order_id'] = str(self.order_id)
        serialized_attributes["order_drink"] = [
            x.dto_serialize() for x in self.order_drink]
        return serialized_attributes


class Customer_Domain(object):
    def __init__(self, customer_object=None, customer_json=None):
        if customer_object:
            self.id = customer_object.id
            self.first_name = customer_object.first_name
            self.last_name = customer_object.last_name
            self.email_verified = customer_object.email_verified
            # self.has_registered = customer_object.has_registered
            self.has_registered = False

            # might not want to send this sensitive information in every request
            if "password" in customer_object.__dict__.keys():
                self.password = customer_object.password
            if "stripe_id" in customer_object.__dict__.keys():
                self.stripe_id = customer_object.stripe_id
        elif customer_json:
            # has registered property will be set in repository, so it will never be sent down from front end thus wont be necessary in initialization from json
            self.id = customer_json["id"]
            self.password = generate_password_hash(
                customer_json["password"], "sha256")
            print()
            print('check_password_hash(self.password, customer_json["password"])', check_password_hash(
                self.password, customer_json["password"]))
            print()
            self.email_verified = customer_json["email_verified"]
            self.first_name = customer_json["first_name"]
            self.last_name = customer_json["last_name"]
            self.stripe_id = customer_json["stripe_id"]

    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

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
            # stripe ID is in an associative table now so if a vanilla merchant object is returned then it wont have the stripe id
            if 'stripe_id' in merchant_object.__dict__:
                self.stripe_id = merchant_object.stripe_id

        elif merchant_json:
            print('merchant_json', merchant_json)
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

    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

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
        if business_object:
            print('business_object', business_object.serialize)
            self.id = business_object.id
            self.merchant_id = business_object.merchant_id
            self.name = business_object.name
            self.address = business_object.address
            self.sales_tax_rate = business_object.sales_tax_rate
            self.classification = business_object.classification
            self.merchant_stripe_id = business_object.merchant_stripe_id
        if business_json:
            self.id = uuid.uuid4()
            self.merchant_id = business_json["merchant_id"]
            self.merchant_stripe_id = business_json["merchant_stripe_id"]
            self.name = business_json["name"]
            self.classification = business_json["classification"]
            self.address = business_json["address"]

            address_list = business_json["address"].split(",")

            self.street = address_list[0]
            self.city = address_list[1]

            state_and_zipcode = address_list[2].split(" ")

            self.state = state_and_zipcode[1]
            self.zipcode = state_and_zipcode[2]
            if "menu_file" in business_json:
                self.menu_file = business_json["menu_file"]
            else:
                self.menu_file = None
            if "menu_url" in business_json:
                self.menu_url = business_json["menu_url"]
            else:
                self.menu_url = None
            self.tablet = business_json["tablet"]
            self.phone_number = business_json["phone_number"]

    def serialize(self):
        attribute_names = list(self.__dict__.keys())
        attributes = list(self.__dict__.values())
        serialized_attributes = {}
        for i in range(len(attributes)):
            serialized_attributes[attribute_names[i]] = attributes[i]
        return serialized_attributes

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
