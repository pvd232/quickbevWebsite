import Dashboard from "./dashboard/Dashboard.js";
import { useState, useEffect } from "react";
import API from "../helpers/Api.js";
import { setLocalStorage } from "../Models.js";
import PayoutSetup from "./PayoutSetup.js";

const Home = () => {
  const [orders, setOrders] = useState(null);
  const [customers, setCustomers] = useState(null);
  const [businesses, setBusinesses] = useState(null);
  const [isValidated, setIsValidated] = useState(false);
  useEffect(() => {
    let mounted = true;
    API.checkStripeStatus().then((value) => {
      if (value.capabilities.charges_enabled && mounted) {
        setIsValidated(true);
      }
    });
    API.getOrders().then((items) => {
      setLocalStorage("orders", items.orders);
      if (mounted) {
        setOrders(items.orders);
      }
    });
    API.getCustomers().then((items) => {
      setLocalStorage("customers", items.customers);
      if (mounted) {
        setCustomers(items.customers);
      }
    });
    API.getBusinesses().then((items) => {
      setLocalStorage("businesses", items.businesses);
      if (mounted) {
        setBusinesses(items.businesses);
      }
    });
    return () => (mounted = false);
  }, []);
  if (isValidated) {
    if (orders && customers && businesses) {
      return (
        <Dashboard
          orders={orders}
          customers={customers}
          businesses={businesses}
        ></Dashboard>
      );
    } else {
      return <></>;
    }
  } else {
    return <PayoutSetup callback={true}></PayoutSetup>;
  }
};
export default Home;
