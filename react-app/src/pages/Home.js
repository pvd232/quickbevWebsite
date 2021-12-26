import Dashboard from "./dashboard/Dashboard.js";
import { useState, useEffect } from "react";
import API from "../helpers/Api.js";
import { LocalStorageManager } from "../Models.js";
const Home = () => {
  const [orders, setOrders] = useState(null);
  const [customers, setCustomers] = useState(null);
  const [businesses, setBusinesses] = useState(null);
  const [merchantEmployees, setMerchantEmployees] = useState(null);
  const [bouncers, setBouncers] = useState(null);
  const [drinks, setDrinks] = useState(null);
  const [validated, setValidated] = useState(null);

  const handleBusinessUpdate = (newBusinesses) => {
    console.log("newBusinesses", newBusinesses);
    setBusinesses(newBusinesses);
  };
  const handleMerchantEmployeeUpdate = (newMerchantEmployeees) => {
    if (newMerchantEmployeees.length === 1) {
      setMerchantEmployees(newMerchantEmployeees);
      return;
    } else {
      if (newMerchantEmployeees[0].id === "") {
        newMerchantEmployeees.shift();
      }
      setMerchantEmployees(newMerchantEmployeees);
    }
  };
  useEffect(() => {
    let mounted = true;
    API.checkStripeStatus().then((value) => {
      if (mounted && !value) {
        setValidated(false);
        window.location.assign("payout-setup-callback");
      } else if (mounted && value) {
        setValidated(true);
      }
    });
    API.getOrders().then((items) => {
      if (typeof items.orders !== "undefined") {
        if (mounted && items) {
          LocalStorageManager.shared.orders = items.orders;
          setOrders(items.orders);
        }
      } else {
        setOrders(LocalStorageManager.shared.orders);
      }
    });
    API.getCustomers().then((items) => {
      if (mounted && items) {
        // console.log("items", items);
        LocalStorageManager.shared.setItem("customers", items.customers);

        setCustomers(items.customers);
      }
    });
    API.getBusinesses().then((items) => {
      if (mounted && items) {
        if (typeof items.businesses !== "undefined") {
          LocalStorageManager.shared.businesses = items.businesses;
          setBusinesses(items.businesses);
        } else {
          setBusinesses(LocalStorageManager.shared.businesses);
        }
      }
    });
    API.getMerchantEmployees().then((items) => {
      if (mounted && items) {
        LocalStorageManager.shared.setItem(
          "merchant_employees",
          items.merchant_employees
        );
        setMerchantEmployees(items.merchant_employees);
      }
    });
    API.getBouncers().then((items) => {
      LocalStorageManager.shared.setItem("bouncers", items.bouncers);
      if (mounted && items) {
        setBouncers(items.bouncers);
      }
    });
    API.getDrinks().then((items) => {
      if (typeof items.drinks !== "undefined") {
        if (mounted && items) {
          LocalStorageManager.shared.drinks = items.drinks;
          setDrinks(items.drinks);
        }
      } else {
        setDrinks(LocalStorageManager.shared.drinks);
      }
    });

    return () => (mounted = false);
  }, []);
  if (
    orders &&
    customers &&
    businesses &&
    merchantEmployees &&
    bouncers &&
    drinks &&
    validated
  ) {
    // console.log("validated", validated);
    // console.log("merchantEmployees", merchantEmployees);
    // console.log("bouncers", bouncers);
    // console.log("businesses", businesses);
    // console.log("customers", customers);
    // console.log("orders", orders);
    // console.log("drinks", drinks);
    return (
      <Dashboard
        // orders={orders}
        customers={customers}
        // businesses={businesses}
        merchantEmployees={merchantEmployees}
        bouncers={bouncers}
        // drinks={drinks}
        updateBusinesses={(newBusinesses) =>
          handleBusinessUpdate(newBusinesses)
        }
        updateMerchantEmployee={(newMerchantEmployee) =>
          handleMerchantEmployeeUpdate(newMerchantEmployee)
        }
      ></Dashboard>
    );
  } else {
    // console.log("validated", validated);
    // console.log("merchantEmployees", merchantEmployees);
    // console.log("bouncers", bouncers);
    // console.log("businesses", businesses);
    // console.log("customers", customers);
    // console.log("orders", orders);
    console.log("drinks", drinks);
    console.log("not orders && others");
    return <></>;
  }
};
export default Home;
