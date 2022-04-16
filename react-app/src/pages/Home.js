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
  const [drinkCategories, setDrinkCategories] = useState(null);
  const [validated, setValidated] = useState(null);

  const handleBusinessUpdate = (newBusinesses) => {
    setBusinesses(newBusinesses);
  };
  const handleMerchantEmployeeUpdate = (newMerchantEmployeees) => {
    setMerchantEmployees(newMerchantEmployeees);
  };
  const handleBouncerUpdate = (newBouncers) => {
    setBouncers(newBouncers);
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
    API.getDrinkCategories().then((items) => {
      if (mounted && items) {
        LocalStorageManager.shared.drinkCategories = items.drink_categories;
        console.log(
          "LocalStorageManager.shared.drinkCategories",
          LocalStorageManager.shared.drinkCategories
        );
        setDrinkCategories(items.drink_categories);
      }
    });
    API.getOrders().then((items) => {
      if (mounted && items) {
        // if the eTag matches then the backend will not return any data
        if (typeof items.orders !== "undefined") {
          LocalStorageManager.shared.orders = items.orders;
          setOrders(items.orders);
        } else {
          setOrders(LocalStorageManager.shared.orders);
        }
      }
    });
    API.getCustomers().then((items) => {
      if (mounted && items) {
        if (typeof items.customers !== "undefined") {
          LocalStorageManager.shared.setItem("customers", items.customers);
          setCustomers(items.customers);
        } else {
          setOrders(LocalStorageManager.shared.orders);
        }
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
      if (mounted && items) {
        if (typeof items.drinks !== "undefined") {
          LocalStorageManager.shared.drinks = items.drinks;
          setDrinks(items.drinks);
        } else {
          setDrinks(LocalStorageManager.shared.drinks);
        }
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
    return (
      <Dashboard
        customers={customers}
        merchantEmployees={merchantEmployees}
        bouncers={bouncers}
        updateBouncers={(newBouncers) => handleBouncerUpdate(newBouncers)}
        updateBusinesses={(newBusinesses) =>
          handleBusinessUpdate(newBusinesses)
        }
        updateMerchantEmployee={(newMerchantEmployee) =>
          handleMerchantEmployeeUpdate(newMerchantEmployee)
        }
      ></Dashboard>
    );
  } else {
    console.log("not orders && others");
    return <></>;
  }
};
export default Home;
