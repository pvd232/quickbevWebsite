import Dashboard from "./dashboard/Dashboard.js";
import { useState, useEffect } from "react";
import API from "../helpers/Api.js";

const Home = () => {
  const [list, setList] = useState(null);

  useEffect(() => {
    let mounted = true;
    API.getOrders().then((items) => {
      console.log("items", items);
      if (mounted) {
        setList(items);
      }
    });
    return () => (mounted = false);
  }, []);
  if (list) {
    return <Dashboard orderArray={list}></Dashboard>;
  } else {
    return <></>;
  }
};
export default Home;
