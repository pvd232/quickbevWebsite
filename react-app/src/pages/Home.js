import Dashboard from "./dashboard/Dashboard.js";
import { useState, useEffect } from "react";
import API from "../helpers/Api.js";
import { setLocalStorage } from "../Models.js";
import PayoutSetup from "./PayoutSetup.js";
import Navbar from "../Navbar.js";
import "../css/Signup.css";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
const Home = () => {
  const [orders, setOrders] = useState(null);
  const [customers, setCustomers] = useState(null);
  const [businesses, setBusinesses] = useState(null);
  const [isValidated, setIsValidated] = useState(true);
  useEffect(() => {
    console.log("fuck this shit", JSON.parse(localStorage.getItem('merchant')))
    console.log("fuck this shit 2", JSON.parse(localStorage.getItem('business')))
localStorage.
    let mounted = true;
    API.checkStripeStatus().then((value) => {
      console.log('value',value)
      if (!value && mounted) {
        setIsValidated(false);
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
    return ( <> <Navbar/>
    <div className="signupBody">
      <div id="msform">  <Row>
          <Col
            sm={12}
            id="payoutSetup"
            style={{ justifyContent: "center", display: "flex" }}
          >
            <PayoutSetup callback={true}></PayoutSetup> 
            </Col></Row></div></div></>)
  }
};
export default Home;
