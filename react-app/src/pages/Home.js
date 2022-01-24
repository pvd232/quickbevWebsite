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
    return (
      <Dashboard
        customers={customers}
        merchantEmployees={merchantEmployees}
        bouncers={bouncers}
        updateBouncers={(newBouncers) =>
          handleBouncerUpdate(newBouncers)
        }
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
