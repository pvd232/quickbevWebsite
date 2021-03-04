import React from "react";
import { Switch, Route } from "react-router-dom";

import Home from "./pages/Home.js";
import Signup from "./pages/Signup.js";
import Signin from "./pages/Signin.js";
import Splash from "./pages/Splash.js";
import PayoutSetupCallback from "./pages/PayoutSetupCallback.js";
import ResetPassword from "./pages/PasswordReset.js";

const Main = () => {
  return (
    <Switch>
      {/* The Switch decides which component to show based on the current URL.*/}
      <Route exact path="/home" component={Home}></Route>
      <Route exact path="/signup" component={Signup}></Route>
      <Route exact path="/signin" component={Signin}></Route>
      <Route
        exact
        path="/payout-setup-callback"
        component={PayoutSetupCallback}
      ></Route>
      <Route exact path="/" component={Splash}></Route>
      <Switch>
        <Route
          path="/reset-password/:sessionToken"
          children={<ResetPassword />}
        />
      </Switch>
    </Switch>
  );
};

export default Main;
