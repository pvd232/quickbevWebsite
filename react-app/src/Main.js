import React from "react";
import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home.js";
import Signup from "./pages/Signup.js";
import Privacy from "./pages/Privacy.js";
import DataDeletion from "./pages/DataDeletion.js";
import Signin from "./pages/Signin.js";
import Splash from "./pages/Splash.js";
import PayoutSetupCallback from "./pages/PayoutSetupCallback.js";
import MerchantEmployeePayoutSetup from "./pages/MerchantEmployeePayoutSetup.js";
import MerchantEmployeePayoutSetupCallback from "./pages/MerchantEmployeePayoutSetupCallback.js";
import MerchantEmployeePayoutSetupComplete from "./pages/MerchantEmployeePayoutSetupComplete.js";
import BouncerEmailConfirmed from "./pages/BouncerEmailConfirmed.js";
import ResetPassword from "./pages/PasswordReset.js";
import PasswordResetEmailForm from "./pages/PasswordResetEmailForm.js";
import MenuBuilder from "./pages/admin/MenuBuilder.js";
import DeactivateBusiness from "./pages/admin/DeactivateBusiness.js";
import DeactivateDrink from "./pages/admin/DeactivateDrink.js";
import BouncerQuickPass from "./pages/BouncerQuickPass.js";

const Main = () => {
  return (
    <>
      <Routes>
        {/* The Routes decides which element to show based on the current URL.*/}
        <Route path="/privacy" element={<Privacy />}></Route>
        <Route path="/data-deletion" element={<DataDeletion />}></Route>
        <Route path="/home" element={<Home />}></Route>
        <Route path="/signup" element={<Signup />}></Route>
        <Route
          exact
          path="/password-reset-email-form"
          element={<PasswordResetEmailForm />}
        ></Route>
        <Route path="/signin" element={<Signin />}></Route>
        <Route
          path="/merchant-employee-payout-setup-complete"
          element={<MerchantEmployeePayoutSetupComplete />}
        ></Route>

        <Route
          path="/payout-setup-callback"
          element={<PayoutSetupCallback />}
        ></Route>
        <Route path="/menu-builder" element={<MenuBuilder />}></Route>
        <Route
          exact
          path="/deactivate-business"
          element={<DeactivateBusiness />}
        ></Route>
        <Route path="/deactivate-drink" element={<DeactivateDrink />}></Route>
        <Route path="/" element={<Splash />}></Route>
        <Route
          path="/bouncer-quick-pass/:sessionToken/:businessId/:bouncerId"
          element={<BouncerQuickPass />}
        />
        <Route
          path="/reset-password/:sessionToken"
          element={<ResetPassword />}
        />
        <Route
          path="/bouncer-email-confirmed/:sessionToken"
          element={<BouncerEmailConfirmed />}
        />
        <Route
          path="/merchant-employee-payout-setup/:merchantEmployeeId"
          element={<MerchantEmployeePayoutSetup />}
        />
        <Route
          path="/merchant-employee-payout-setup-callback/:merchantEmployeeId"
          element={<MerchantEmployeePayoutSetupCallback />}
        />
      </Routes>
    </>
  );
};

export default Main;
