import React, { useState, useEffect } from "react";
import Button from "react-bootstrap/Button";
import API from "../helpers/Api.js";
import bankIcon from "../static/icon-bank.svg";
import { Business, setLocalStorage, Merchant } from "../Models.js";

const PayoutSetup = (props) => {
  const [redirect, setRedirect] = useState(null);
  var redirectUrl = null;
  const getRedirectInfo = async () => {
    if (!props.callback) {
      return API.makeRequest("GET", `/create-stripe-account`);
    } else {
      const currentMerchant = new Merchant(
        "localStorage",
        localStorage.getItem("merchant")
      );
      return API.makeRequest(
        "GET",
        `/create-stripe-account?stripe=${currentMerchant.stripeId}`
      );
    }
  };
  const handleConnect = async () => {
    let responseContent = await getRedirectInfo();
    const merchantStripeId = responseContent.headers.stripe_id;

    let url = responseContent.url;
    if (url && merchantStripeId) {
      redirectUrl = url;
      return merchantStripeId;
    }
  };
  useEffect(() => {
    //had to do this because memory leak due to component not unmounting properly
    let mount = true;
    if (mount && redirect) {
      window.location.assign(redirect);
    }

    return () => (mount = false);
  }, [redirect]);

  if (props.callback) {
    return (
      <>
        <div className="text-center box">
          <img src={bankIcon} alt="" className="icon" />
          <h5 style={{ marginTop: "5%", marginBottom: "5%" }}>
            Stripe account onboarding incomplete
          </h5>
          <p>
            Please click the button below to be redirected to Stripe to complete
            the onboarding proces
          </p>

          <Button
            className="btn btn-primary text-center"
            onClick={(event) => {
              // if this is the payout redirect then all values for business and merchant have been set in the backend and we dont need to propogate back upwards
              event.preventDefault();
              handleConnect().then(() => setRedirect(redirectUrl));
            }}
          >
            Set up payouts
          </Button>
        </div>
      </>
    );
  } else {
    return (
      <>
        <div className="text-center box">
          <div className="fs-title">
            Input your bank account to recieve payouts
          </div>
          <img src={bankIcon} alt="" className="icon" />

          <p>
            QuickBev partners with Stripe to transfer earnings to your bank
            account.
          </p>
          <Button
            className="btn btn-primary text-center"
            onClick={(event) => {
              event.preventDefault();
              const eventTarget = event.target;
              handleConnect().then((merchantStripeId) =>
                props.onSubmit(eventTarget, merchantStripeId).then(() => {
                  setLocalStorage("firstLogin", true);
                  setRedirect(redirectUrl);
                })
              );
            }}
          >
            Set up payouts
          </Button>
          <p className="text-center notice">
            You'll be redirected to Stripe to complete the onboarding proces.
          </p>
        </div>
      </>
    );
  }
};

export default PayoutSetup;
