import React from "react";
import { Switch, Route } from "react-router-dom";

import Home from "./pages/Home.js";
import Signup from "./pages/Signup.js";
import Signin from "./pages/Signin.js";
import Splash from "./pages/Splash.js";
import PayoutSetupCallback from "./pages/PayoutSetupCallback.js";
import MerchantEmployeePayoutSetup from "./pages/MerchantEmployeePayoutSetup.js";
import MerchantEmployeePayoutSetupCallback from "./pages/MerchantEmployeePayoutSetupCallback.js";
import MerchantEmployeePayoutSetupComplete from "./pages/MerchantEmployeePayoutSetupComplete.js";
import ResetPassword from "./pages/PasswordReset.js";
import MenuBuilder from "./pages/admin/MenuBuilder.js";

const Main = () => {
  return (
    <Switch>
      {/* The Switch decides which component to show based on the current URL.*/}
      <Route exact path="/home" component={Home}></Route>
      <Route exact path="/signup" component={Signup}></Route>
      <Route exact path="/signin" component={Signin}></Route>
      <Route
        exact
        path="/merchant-employee-payout-setup-complete"
        component={MerchantEmployeePayoutSetupComplete}
      ></Route>

      <Route
        exact
        path="/payout-setup-callback"
        component={PayoutSetupCallback}
      ></Route>
      <Route
        exact
        path="/merchant-employee-payout-setup-callback"
        component={MerchantEmployeePayoutSetupCallback}
      ></Route>
      <Route exact path="/menubuilder" component={MenuBuilder}></Route>

      <Route exact path="/" component={Splash}></Route>
      <Switch>
        <Route
          path="/reset-password/:sessionToken"
          children={<ResetPassword />}
        />
        <Route
          path="/merchant-employee-payout-setup/:merchantEmployeeId"
          // path="/reset-password1/:sessionToken"
          children={<MerchantEmployeePayoutSetup />}
          // children={<ResetPassword />}
        />
      </Switch>
    </Switch>
  );
};

export default Main;
