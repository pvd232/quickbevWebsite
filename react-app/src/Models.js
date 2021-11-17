export class LocalStorageManager {
  static shared = new LocalStorageManager();
  getLocalStorage(key) {
    return JSON.parse(localStorage.getItem(key));
  }
  setLocalStorage(key, object) {
    localStorage.setItem(key, JSON.stringify(object));
  }
  get firstLogin() {
    return JSON.parse(localStorage.getItem("first_login"));
  }
  get currentMerchant() {
    return new Merchant("localStorage", localStorage.getItem("merchant"));
  }
  get currentBusiness() {
    return new Business(localStorage.getItem("business"), false, true, false);
  }
  get sessionToken() {
    return JSON.parse(localStorage.getItem("session_token"));
  }
}

export const nonCamelCaseWords = (name) => {
  var words = name.match(/[A-Za-z][a-z]*/g) || [];
  return words.join(" ");
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
    this.total = order_object.total;
    this.subtotal = order_object.subtotal;
    this.tipPercentage = order_object.tip_percentage;
    this.tipTotal = order_object.tip_total;
    this.salesTaxTotal = order_object.sales_tax_total;
    this.preSalesTaxTotal = order_object.pre_sales_tax_total;
    this.preServiceFeeTotal = order_object.pre_service_fee_total;
    this.businessId = order_object.business_id;
    // this property will be extracted from the business in the front end and set after the business is initialized
    this.businessName = "";
    this.businessAddress = order_object.business_address;
    this.dateTime = order_object.formatted_date_time;
    this.serviceFee = order_object.service_fee;
    this.orderDrink = [];
    // if there are no orders then the backend will send an empty order so we dont need to construct an order drink
    if (
      Array.isArray(order_object.order_drink.order_drink) &&
      order_object.order_drink.order_drink.length >= 1 &&
      order_object.order_drink.order_drink[0].id !== ""
    ) {
      this.orderDrink = new OrderDrink(order_object.order_drink);
      this.orderDrink.orderId = this.id;
    }
  }

  toJSON() {
    const data = {
      id: this.id,
      customer_id: this.userId,
      cost: this.total,
      subtotal: this.subtotal,
      tip_percentage: this.tipPercentage,
      tip_otal: this.tipTotal,
      sales_tax_total: this.salesTaxTotal,
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
    console.log("object", object);
    this.isAdministrator = false;
    if (objectType === "json") {
      // the merchant object will be pre-populated with values from the form thus it will use camelCase notation
      this.id = object.id;
      this.stripeId = object.stripe_id;
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
      console.log("object", object);
      console.log("data", data);
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
    isSnakeCase = false,
    isJSON = false,
    tableDisplay = false
  ) {
    // this is the business that is created from the form during the signup process
    if (businessObject && !isSnakeCase && !isJSON && !tableDisplay) {
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
      this.menuUrl = businessObject.menuUrl;
      this.classification = businessObject.classification;
      this.salesTaxRate = businessObject.salesTaxRate;
      this.menu = businessObject.menu;
      this.atCapacity = false;
      this.schedule = businessObject.schedule;
      // this is the business that is saved in local storage when received as a confirmed business from the backend
    } else if (businessObject && isSnakeCase && !isJSON && !tableDisplay) {
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
      this.menuUrl = businessObject.menu_url;
      this.classification = businessObject.classification;
      this.salesTaxRate = businessObject.sales_tax_rate;
      this.menu = businessObject.menu;
      this.atCapacity = businessObject.at_capacity;
      this.schedule = businessObject.schedule;
    } else if (businessObject && isJSON && isSnakeCase) {
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
      this.menuUrl = businessJson.menu_url;
      this.classification = businessJson.classification;
      this.salesTaxRate = businessJson.sales_tax_rate;
      this.menu = businessJson.menu;
      this.atCapacity = businessJson.at_capacity;
      this.schedule = businessObject.schedule;
    } else if (businessObject && !isJSON && tableDisplay) {
      this.id = businessObject.id;
      this.name = businessObject.name;
      this.address = businessObject.address;
      this.phoneNumber = businessObject.phone_number;
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
      this.menuUrl = null;
      this.classification = null;
      this.salesTaxRate = null;
      this.menu = null;
      this.atCapacity = null;
      this.schedule = null;
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
      menu_url: this.menuUrl,
      classification: this.classification,
      sales_tax: this.salesTaxRate,
      at_capacity: this.atCapacity,
      schedule: this.schedule,
    };
    return data;
  }
}
export class QuickPass {
  constructor(quickPassObject) {
    if (quickPassObject) {
      console.log("quickPassObject", quickPassObject);
      this.id = quickPassObject.id;
      this.customerFirstName = quickPassObject.customer_first_name;
      this.customerLastName = quickPassObject.customer_last_name;
      this.customerId = quickPassObject.customer_id;
      this.businessId = quickPassObject.business_id;
      this.activationTime = quickPassObject.activation_time;
      this.timeCheckedIn = quickPassObject.time_checked_in;
    } else {
      this.id = "";
      this.customerFirstName = "";
      this.customerLastName = "";
      this.customerId = "";
      this.businessId = "";
      this.activationTime = "";
      this.timeCheckedIn = "";
    }
  }
  toJSON() {
    const data = {
      id: this.id,
      customer_first_name: this.customerFirstName,
      customer_last_name: this.customerLastName,
      customer_id: this.customerId,
      business_id: this.businessId,
      activation_time: this.activationTime,
      time_checked_in: this.timeCheckedIn,
    };
    return data;
  }
  formatTimestamp() {
    // Create a new JavaScript Date object based on the timestamp
    // multiplied by 1000 so that the argument is in milliseconds, not seconds.
    const unixTimestamp = this.activationTime;
    console.log("this.activationTime", this.activationTime);
    console.log("unixTimestamp", unixTimestamp);
    const date = new Date(unixTimestamp * 1000);
    // console.log("date", date);
    // // Hours part from the timestamp
    // const hours = date.getHours();
    // console.log("hours", hours);
    // // Minutes part from the timestamp
    // const minutes = "0" + date.getMinutes();
    // // Seconds part from the timestamp
    // const seconds = "0" + date.getSeconds();

    // Will display time in 10:30:23 format
    // const formattedTime =
    //   hours + ":" + minutes.substr(-2) + ":" + seconds.substr(-2);
    return date.toLocaleString("en-US", {
      hour: "numeric",
      minute: "numeric",
      hour12: true,
    });
  }
}
export class MerchantEmployee {
  constructor(merchantEmployeeObject) {
    if (merchantEmployeeObject) {
      this.id = merchantEmployeeObject.id;
      this.firstName = merchantEmployeeObject.first_name;
      this.lastName = merchantEmployeeObject.last_name;
      this.phoneNumber = merchantEmployeeObject.phone_number;
      this.loggedIn = merchantEmployeeObject.logged_in;
      this.businessId = merchantEmployeeObject.business_id;
      this.status = merchantEmployeeObject.status;
    } else {
      this.id = "";
      this.firstName = "";
      this.lastName = "";
      this.phoneNumber = "";
      this.loggedIn = "";
      this.businessId = "";
      this.status = "pending";
    }
  }
  toJSON() {
    const data = {
      id: this.id,
      first_name: this.firstName,
      last_name: this.lastName,
      phone_number: this.phoneNumber,
      logged_in: this.loggedIn,
      business_id: this.businessId,
    };
    return data;
  }
}
export class Bouncer {
  constructor(bouncerObject, isForm) {
    if (bouncerObject && !isForm) {
      this.id = bouncerObject.id;
      this.firstName = bouncerObject.first_name;
      this.lastName = bouncerObject.last_name;
      this.loggedIn = bouncerObject.logged_in;
      this.businessId = bouncerObject.business_id;
      this.merchantId = bouncerObject.merchant_id;
      this.status = bouncerObject.status;
    } else if (bouncerObject && isForm) {
      this.id = bouncerObject.id;
      this.firstName = bouncerObject.firstName;
      this.lastName = bouncerObject.lastName;
      this.loggedIn = bouncerObject.loggedIn;
      this.businessId = bouncerObject.businessId;
      this.merchantId = bouncerObject.merchantId;
      this.status = bouncerObject.status;
    } else {
      this.id = "";
      this.firstName = "";
      this.lastName = "";
      this.loggedIn = "";
      this.businessId = "";
      this.merchantId = "";
      this.status = "pending";
    }
  }
  toJSON() {
    const data = {
      id: this.id,
      first_name: this.firstName,
      last_name: this.lastName,
      logged_in: !this.loggedIn ? false : this.loggedIn,
      status: !this.status ? "pending" : this.status,
      merchant_id: this.merchantId,
      business_id: this.businessId,
    };

    return data;
  }
}
