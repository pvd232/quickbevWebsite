export const setLocalStorage = (key, object) => {
  localStorage.setItem(key, JSON.stringify(object));
};
const capitalize = (word) => {
  return word.charAt(0).toUpperCase() + word.substring(1);
};
export const toCapitalizedWords = (name) => {
  var words = name.match(/[A-Za-z][a-z]*/g) || [];

  return words.map(capitalize).join(" ");
};
export class Customer {
  constructor(customerObject) {
    this.id = customerObject.id;
    this.firstName = customerObject.first_name;
    this.lastName = customerObject.last_name;
  }
  toJSON() {
    const data = {
      id: this.id,
      first_name: this.firstName,
      last_name: this.lastName,
    };
    return data;
  }
}
export class Drink {
  constructor(drinkObject = null) {
    if (drinkObject) {
      this.id = drinkObject.id;
      this.name = drinkObject.name;
      this.price = drinkObject.price;
      this.quantity = drinkObject.quantity;
      this.description = drinkObject.description;
      this.orderDrinkId = drinkObject.order_drink_id;
      this.businessId = drinkObject.business_id;
      this.imageUrl = drinkObject.image_url;
    } else {
      this.id = "";
      this.name = "";
      this.price = "";
      this.quantity = "";
      this.description = "";
      this.orderDrinkId = "";
      this.businessId = "";
      this.imageUrl = "";
    }
  }
  toJSON() {
    const data = {
      id: this.id,
      name: this.name,
      price: this.price,
      quantity: this.quantity,
      description: this.description,
      orderDrinkId: this.orderDrinkId,
      businessId: this.businessId,
      imageUrl: this.imageUrl,
    };
    return data;
  }
}

export class OrderDrink {
  constructor(orderDrinkObject) {
    this.orderDrink = [];
    for (var i = 0; i < orderDrinkObject.order_drink.length; i++) {
      const newDrink = new Drink(orderDrinkObject.order_drink[i]);
      if (!this.orderDrink.find((drink) => drink.id === newDrink.id)) {
        this.orderDrink.push(newDrink);
      } else {
        this.orderDrink.find((drink) => drink.id === newDrink.id).quantity += 1;
      }
    }
  }
}

export class Order {
  constructor(order_object) {
    this.id = order_object.id;
    this.customerId = order_object.customer_id;
    this.cost = order_object.cost;
    this.subtotal = order_object.subtotal;
    this.tipPercentage = order_object.tip_percentage;
    this.tipAmount = order_object.tip_amount;
    this.salesTax = order_object.sales_tax;
    this.businessId = order_object.business_id;
    // this property will be extracted from the business in the front end and set after the business is initialized
    this.businessName = "";
    this.businessAddress = order_object.business_address;
    this.dateTime = order_object.date_time;
    this.serviceFee = parseFloat(order_object.service_fee);
    this.orderDrink = [];
    // if there are no orders then the backend will send an empty order so we dont need to construct an order drink
    console.log('typeof order_object.orderDrink',typeof order_object.orderDrink)
    console.log('typeof order_object.orderDrink === Array',typeof order_object.orderDrink === Array)
    if (
      typeof order_object.orderDrink === Array &&
      order_object.orderDrink[0].cost > 0
    ) {
      this.orderDrink = new OrderDrink(order_object.order_drink);
      this.orderDrink.orderId = this.id;
    }
  }

  toJSON() {
    const data = {
      id: this.id,
      customer_id: this.userId,
      cost: this.cost,
      subtotal: this.subtotal,
      tip_percentage: this.tipPercentage,
      tip_amount: this.tipAmount,
      sales_tax: this.salesTax,
      business_id: this.businessId,
      address: this.businessAddress,
      order_drink: this.orderDrink,
      date_time: this.dateTime,
      service_fee: this.serviceFee,
    };
    return data;
  }
}

export class Merchant {
  constructor(objectType, object) {
    console.log("objectType", objectType);

    console.log("object", object);
    this.isAdministrator = false;
    if (objectType === "json") {
      // the merchant object will be pre-populated with values from the form thus it will use camelCase notation
      this.id = object.id;
      this.stripeId = object.stripe_id
      this.password = object.password;
      this.firstName = object.first_name;
      this.lastName = object.last_name;
      this.phoneNumber = object.phone_number;
      this.numberOfBusinesses = object.number_of_businesses;
      this.isAdministrator = object.is_administrator;
    } else if (objectType === "merchantStateObject") {
      // the merchant stripe id is created on submission those wont exist during the sign up process when the merchant state object is relevant
      this.id = object.id;
      this.password = object.password;
      this.firstName = object.firstName;
      this.lastName = object.lastName;
      this.phoneNumber = object.phoneNumber;
    } else if (objectType === "localStorage") {
      // number of businessess and stripe id is set extraneously after object initialization so it will only need to be recalled from local storage
      const data = JSON.parse(object);
      this.id = data.id;
      this.password = data.password;
      this.firstName = data.first_name;
      this.lastName = data.last_name;
      this.phoneNumber = data.phone_number;
      this.numberOfBusinesses = data.number_of_businesses;
      this.stripeId = data.stripe_id;
      this.isAdministrator = data.is_administrator;
    } else {
      this.id = null;
      this.password = null;
      this.firstName = null;
      this.lastName = null;
      this.phoneNumber = null;
      this.stripeId = null;
    }
  }
  toJSON() {
    const data = {
      id: this.id,
      password: this.password,
      first_name: this.firstName,
      last_name: this.lastName,
      phone_number: this.phoneNumber,
      number_of_businesses: this.numberOfBusinesses,
      stripe_id: this.stripeId,
      is_administrator: this.isAdministrator,
    };
    return data;
  }
}
export class Business {
  constructor(
    businessObject,
    isCamelCase = false,
    isJSON = false,
    tableDisplay = false
  ) {
    if (businessObject && !isCamelCase && !isJSON && !tableDisplay) {
      this.id = businessObject.id;
      this.name = businessObject.name;
      this.merchantId = businessObject.merchantId;
      this.merchantStripeId = businessObject.merchantStripeId;
      this.address = businessObject.address;
      this.street = businessObject.street;
      this.city = businessObject.city;
      this.state = businessObject.state;
      this.zipcode = businessObject.zipcode;
      this.phoneNumber = businessObject.phoneNumber;
      this.tablet = businessObject.tablet;
      this.menuUrl = businessObject.menuUrl;
      this.classification = businessObject.classification;
      this.salesTaxRate = businessObject.salesTaxRate;
      this.menu = businessObject.menu;
    } else if (businessObject && isCamelCase && !isJSON && !tableDisplay) {
      this.id = businessObject.id;
      this.name = businessObject.name;
      this.merchantId = businessObject.merchant_id;
      this.merchantStripeId = businessObject.merchant_stripe_id;
      this.address = businessObject.address;
      this.street = businessObject.street;
      this.city = businessObject.city;
      this.state = businessObject.state;
      this.zipcode = businessObject.zipcode;
      this.phoneNumber = businessObject.phone_number;
      this.tablet = businessObject.tablet;
      this.menuUrl = businessObject.menu_url;
      this.classification = businessObject.classification;
      this.salesTaxRate = businessObject.sales_tax_rate;
      this.menu = businessObject.menu;
    } else if (businessObject && isJSON && isCamelCase) {
      const businessJson = JSON.parse(businessObject);
      this.id = businessJson.id;
      this.name = businessJson.name;
      this.merchantId = businessJson.merchant_id;
      this.merchantStripeId = businessJson.merchant_stripe_id;
      this.address = businessJson.address;
      this.street = businessJson.street;
      this.city = businessJson.city;
      this.state = businessJson.state;
      this.zipcode = businessJson.zipcode;
      this.phoneNumber = businessJson.phone_number;
      this.tablet = businessJson.tablet;
      this.menuUrl = businessJson.menu_url;
      this.classification = businessJson.classification;
      this.salesTaxRate = businessJson.sales_tax_rate;
      this.menu = businessJson.menu;
    } else if (businessObject && !isJSON && tableDisplay) {
      this.id = businessObject.id;
      this.name = businessObject.name;
      this.address = businessObject.address;
      this.phoneNumber = businessObject.phone_number;
      this.tablet = businessObject.tablet;
      this.classification = businessObject.classification;
      this.salesTaxRate = businessObject.sales_tax_rate;
    } else {
      this.id = null;
      this.name = null;
      this.merchantId = null;
      this.merchantStripeId = null;
      this.stripeId = null;
      this.address = null;
      this.street = null;
      this.city = null;
      this.state = null;
      this.zipcode = null;
      this.phoneNumber = null;
      this.numberOfBusinesses = null;
      this.tablet = null;
      this.menuUrl = null;
      this.classification = null;
      this.salesTaxRate = null;
      this.menu = null;
    }
  }

  toJSON() {
    const data = {
      id: this.id,
      name: this.name,
      merchant_id: this.merchantId,
      merchant_stripe_id: this.merchantStripeId,
      address: this.address,
      street: this.street,
      city: this.city,
      state: this.state,
      zipcode: this.zipcode,
      phone_number: this.phoneNumber,
      number_of_businesses: this.numberOfBusinesses,
      tablet: this.tablet,
      menu_url: this.menuUrl,
      classification: this.classification,
      sales_tax: this.salesTaxRate,
    };
    return data;
  }
}
