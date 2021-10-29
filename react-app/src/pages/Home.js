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
  const [validated, setValidated] = useState(null);

  const handleBusinessUpdate = (newBusinesses) => {
    console.log("newBusinesses", newBusinesses);
    setBusinesses(newBusinesses);
  };
  useEffect(() => {
    let mounted = true;
    API.checkStripeStatus().then((value) => {
      console.log("value", value);
      if (mounted && !value) {
        setValidated(false);
        window.location.assign("payout-setup-callback");
      } else if (mounted && value) {
        setValidated(true);
      }
    });
    API.getOrders().then((items) => {
      if (mounted && items) {
        console.log("items", items);
        LocalStorageManager.shared.setLocalStorage("orders", items.orders);

        setOrders(items.orders);
      }
    });
    API.getCustomers().then((items) => {
      if (mounted && items) {
        console.log("items", items);
        LocalStorageManager.shared.setLocalStorage(
          "customers",
          items.customers
        );

        setCustomers(items.customers);
      }
    });
    API.getBusinesses().then((items) => {
      if (mounted && items) {
        LocalStorageManager.shared.setLocalStorage(
          "businesses",
          items.businesses
        );
        setBusinesses(items.businesses);
      }
    });
    API.getMerchantEmployees().then((items) => {
      if (mounted && items) {
        console.log("items", items);
        console.log("items", items.merchant_employees);
        LocalStorageManager.shared.setLocalStorage(
          "merchant_employees",
          items.merchant_employees
        );
        setMerchantEmployees(items.merchant_employees);
      }
    });
    API.getBouncers().then((items) => {
      console.log("items", items);
      console.log("items", items.bouncers);
      LocalStorageManager.shared.setLocalStorage(
        "bouncers",
        items.merchant_employees
      );
      if (mounted && items) {
        setBouncers(items.bouncers);
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
    validated
  ) {
    console.log("validated", validated);
    console.log("merchantEmployees", merchantEmployees);
    console.log("bouncers", bouncers);
    console.log("businesses", businesses);
    console.log("customers", customers);
    console.log("orders", orders);
    return (
      <Dashboard
        orders={orders}
        customers={customers}
        businesses={businesses}
        merchantEmployees={merchantEmployees}
        bouncers={bouncers}
        updateBusinesses={(newBusinesses) =>
          handleBusinessUpdate(newBusinesses)
        }
      ></Dashboard>
    );
  } else {
    console.log("validated", validated);
    console.log("merchantEmployees", merchantEmployees);
    console.log("bouncers", bouncers);
    console.log("businesses", businesses);
    console.log("customers", customers);
    console.log("orders", orders);
    console.log("not orders && others");
    return <></>;
  }
};
export default Home;
