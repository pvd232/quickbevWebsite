const formatName = (name) => {
  const nameWords = name.split(" ");
  if (nameWords.length > 1) {
    var newName = [];
    for (const name of nameWords) {
      const nameCharacters = Array.from(name);
      if (nameCharacters.length > 2) {
        if (nameCharacters[0].toUpperCase() !== nameCharacters[0]) {
          const capitalizedWord = capitalizeFirstLetter(name);
          newName.push(capitalizedWord);
        } else {
          newName.push(name);
        }
      } else {
        newName.push(name);
      }
    }
    return newName.join(" ");
  } else {
    return capitalizeFirstLetter(name);
  }
};
function capitalizeFirstLetter(string) {
  return string[0].toUpperCase() + string.slice(1);
}
export class LocalStorageManager {
  static shared = new LocalStorageManager();
  constructor() {
    this.storage = localStorage;
  }
  getRawItem(key) {
    return this.storage.getItem(key);
  }
  setRawItem(key, object) {
    localStorage.setItem(key, object);
  }
  getItem(key) {
    const itemJSON = this.storage.getItem(key);
    if (itemJSON !== "undefined") {
      return JSON.parse(this.storage.getItem(key));
    } else {
      return false;
    }
  }
  setItem(key, object) {
    if (typeof object !== "undefined") {
      localStorage.setItem(key, JSON.stringify(object));
    }
  }
  get drinks() {
    const drinks = [];
    if (this.getItem("drinks")) {
      for (const drink of this.getItem("drinks")) {
        drinks.push(new Drink(drink["drink"]));
      }
      return drinks;
    }
    // this should never happen, either drinks are not set in localStorage because the merchant is logging in for the first time, thus drinks will be set before they are requested, or drinks will already exist in local storage
    return [];
  }
  set drinks(newDrinkArray) {
    // if drinks are being set then they have been received from the backend
    this.setItem("drinks", newDrinkArray);

    for (const business of this.businesses) {
      const businessModel = new Business(business);
      const newMenu = [];
      for (const drink of newDrinkArray) {
        const drinkModel = new Drink(drink);
        if (drinkModel.businessId === businessModel.id) {
          newMenu.push(drinkModel);
        }
      }
      businessModel.menu = newMenu;
    }
    this.setItem("businesses", this.businesses);
  }
  getDrink(drinkId) {
    for (const drink of this.drinks) {
      if (drink.id === drinkId) {
        return drink;
      }
    }
  }
  get orders() {
    const orders = [];
    if (this.getItem("orders")) {
      for (const order of this.getItem("orders")) {
        orders.push(new Order(order));
      }
      return orders;
    }
    return orders;
  }
  set orders(newOrdersArray) {
    this.setItem("orders", newOrdersArray);
  }
  get businesses() {
    const businesses = [];
    if (this.getItem("businesses")) {
      for (const business of this.getItem("businesses")) {
        businesses.push(new Business(business));
      }
      return businesses;
    } else {
      // this should never happen, either drinks are not set in localStorage because the merchant is logging in for the first time, thus drinks will be set before they are requested, or drinks will already exist in local storage
      return [];
    }
  }
  set businesses(newBusinessesArray) {
    // if drinks are being set then they have been received from the backend
    this.setItem("businesses", newBusinessesArray);
  }
  addBusiness(newBusiness) {
    const copyOfBusinessArray = [...this.businesses];
    copyOfBusinessArray.push(newBusiness);
    this.businesses = copyOfBusinessArray;
  }
  get firstLogin() {
    return this.getItem("first_login");
  }
  get currentMerchant() {
    return new Merchant("json", this.getItem("merchant"));
  }
  get currentBusiness() {
    return new Business(this.getItem("business"));
  }
  get sessionToken() {
    return this.getItem("session_token");
  }
  get drinkETag() {
    if (this.getItem("drink_etag") !== false) {
      return this.getItem("drink_etag");
    } else {
      return 0;
    }
  }
  set drinkETag(newDrinkETagId) {
    this.setItem("drink_etag", newDrinkETagId);
  }
  get businessETag() {
    return this.getItem("business_etag");
  }
  set businessEtag(newETagId) {
    this.setItem("business_etag", newETagId);
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
    if (customerObject) {
      this.id = customerObject.id;
      this.firstName = customerObject.first_name;
      this.lastName = customerObject.last_name;
    } else {
      this.id = "";
      this.firstName = "";
      this.lastName = "";
    }
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
      this.businessId = drinkObject.business_id;
      this.imageUrl = drinkObject.image_url;
      this.isActive = drinkObject.is_active;
    } else {
      this.id = "";
      this.name = "";
      this.price = "";
      this.quantity = "";
      this.description = "";
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
      business_id: this.businessId,
      image_url: this.imageUrl,
    };
    return data;
  }
}
export class DrinkItem {
  constructor(drinkObject = null) {
    if (drinkObject) {
      this.id = drinkObject.id;
      this.name = drinkObject.name;
      this.price = drinkObject.price;
      this.quantity = drinkObject.quantity;
      this.description = drinkObject.description;
      this.businessId = drinkObject.business_id;
      this.imageUrl = drinkObject.image_url;
    } else {
      this.id = "";
      this.name = "";
      this.price = "";
      this.quantity = "";
      this.description = "";
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
      business_id: this.businessId,
      image_url: this.imageUrl,
    };
    return data;
  }
}
export class OrderDrinkItem {
  constructor(orderDrinkObject) {
    this.drinkId = orderDrinkObject.drinkId;
    this.quantity = orderDrinkObject.quantity;
    this.drinkName = LocalStorageManager.shared.getDrink(this.drinkId).name;
  }
}
// new order drink data structure
export class OrderDrink {
  constructor(orderDrinkObject) {
    this.orderId = orderDrinkObject.order_id;
    this.drinkId = orderDrinkObject.drink_id;
    this.quantity = orderDrinkObject.quantity;
  }
}

// new order structure
export class Order {
  constructor(orderObject) {
    if (orderObject) {
      this.id = orderObject.id;
      this.customerId = orderObject.customer_id;
      this.total = Math.round(orderObject.total);
      this.subtotal = Math.round(orderObject.subtotal);
      this.tipTotal = Math.round(orderObject.tip_total);
      this.salesTaxTotal = Math.round(orderObject.sales_tax_total);
      this.serviceFeeTotal = Math.round(orderObject.service_fee_total);
      this.tipPercentage = orderObject.tip_percentage;
      this.businessId = orderObject.business_id;
      this.formattedDateTime = orderObject.formatted_date_time;
      this.dateTime = new Date(orderObject.date_time);
      this.orderDrink = [];
      if (orderObject.order_drink.length > 0) {
        for (const orderDrink of orderObject.order_drink) {
          const newOrderDrink = new OrderDrink(orderDrink);
          this.orderDrink.push(newOrderDrink);
        }
      }
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
export class OrderItem {
  constructor(orderObject) {
    if (orderObject) {
      this.orderId = orderObject.id;
      this.customerId = orderObject.customerId;
      this.total = orderObject.total;
      this.subtotal = orderObject.subtotal;
      this.tip = orderObject.tipTotal;
      this.salesTax = orderObject.salesTaxTotal;
      this.serviceFee = orderObject.serviceFeeTotal;
      // these properties will be extracted from the business and set after the OrderItem is initialized
      this.businessName = "";
      this.address = "";
      this.dateAndTime =
        orderObject.formattedDateTime +
        " at " +
        orderObject.dateTime
          .toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
          })
          .replace(/^0(?:0:0?)?/, "");
      this.orderDrinks = [];
      if (orderObject.orderDrink.length > 0) {
        for (const orderDrink of orderObject.orderDrink) {
          const newOrderDrink = new OrderDrinkItem(orderDrink);
          this.orderDrinks.push(newOrderDrink);
        }
      }
    } else {
      this.orderId = "";
      this.customerId = "";
      this.total = 0.0;
      this.subtotal = 0.0;
      this.tip = 0.0;
      this.salesTax = 0.0;
      this.serviceFee = 0.0;
      // these properties will be extracted from the business and set after the OrderItem is initialized
      this.businessName = "";
      this.address = "";
      this.dateAndTime = "";
      this.orderDrink = [];
    }
  }
}

export class Merchant {
  constructor(objectType, object) {
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
  constructor(businessObject) {
    this.id = businessObject.id;
    this.name = businessObject.name;
    this.merchantId = businessObject.merchant_id;
    this.merchantStripeId = businessObject.merchant_stripe_id;
    this.address = businessObject.address;
    this.street = businessObject.street;
    this.city = businessObject.city.trim();
    this.state = businessObject.state;
    this.zipcode = businessObject.zipcode;
    this.phoneNumber = businessObject.phone_number;
    this.menuUrl = businessObject.menu_url;
    this.classification = businessObject.classification;
    this.salesTaxRate = businessObject.sales_tax_rate;
    this.menu = businessObject.menu;
    this.atCapacity = businessObject.at_capacity;
    this.schedule = businessObject.schedule;
    this.isActive = businessObject.is_active;
    this.imageUrl = businessObject.image_url;
    if (LocalStorageManager.shared.currentMerchant.isAdministrator === true) {
      this.merchantStripeStatus = businessObject.merchant_stripe_status;
    }
  }
  get formattedName() {
    return formatName(this.name);
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
      logo_file: this.logoFile,
    };
    return data;
  }
}
export class BusinessItem {
  constructor(businessObject) {
    if (businessObject) {
      this.id = businessObject.id;
      this.name = formatName(businessObject.name);
      this.address = businessObject.address;
      this.phoneNumber = businessObject.phoneNumber;
      this.classification = capitalizeFirstLetter(
        businessObject.classification
      );
      this.salesTaxRate = businessObject.salesTaxRate;
      if (LocalStorageManager.shared.currentMerchant.isAdministrator === true) {
        this.merchantStripeStatus = businessObject.merchantStripeStatus;
      }
    } else {
      this.id = "";
      this.name = "";
      this.address = "";
      this.phoneNumber = "";
      this.classification = "";
      this.salesTaxRate = "";
      if (LocalStorageManager.shared.currentMerchant.isAdministrator === true) {
        this.merchantStripeStatus = "";
      }
    }
  }
}
export class QuickPass {
  constructor(quickPassObject) {
    if (quickPassObject) {
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
    const date = new Date(unixTimestamp * 1000);
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
      this.loggedIn = merchantEmployeeObject.logged_in;
      this.businessId = merchantEmployeeObject.business_id;
      this.status = merchantEmployeeObject.status;
    } else {
      this.id = "";
      this.firstName = "";
      this.lastName = "";
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
