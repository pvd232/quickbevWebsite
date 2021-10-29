import React, { useState, useEffect } from "react";
import Button from "react-bootstrap/Button";
import API from "../helpers/Api.js";
import bankIcon from "../static/icon-bank.svg";
import { LocalStorageManager } from "../Models.js";
import "../css/Signup.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
const PayoutSetup = (props) => {
  const [redirect, setRedirect] = useState(null);
  const [isPlacingOrder, setIsPlacingOrder] = useState(null);
  const Spinner = () => (
    <FontAwesomeIcon icon={faSpinner} className="fa-spin" />
  );
  var redirectUrl = null;
  const getRedirectInfo = async () => {
    if (!props.callback) {
      console.log("not callback");
      return API.makeRequest("GET", `/merchant/stripe`);
    } else {
      return API.makeRequest(
        "GET",
        `/merchant/stripe?stripe=${LocalStorageManager.shared.currentMerchant.stripeId}`
      );
    }
  };
  const handleConnect = async () => {
    let responseContent = await getRedirectInfo();
    const merchantStripeId = responseContent.headers.stripe;
    console.log("merchantStripeId", merchantStripeId);

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
            disabled={isPlacingOrder}
            onClick={(event) => {
              // if this is the payout redirect then all values for business and merchant have been set in the backend and we dont need to propogate back upwards
              event.preventDefault();
              handleConnect().then(() => setRedirect(redirectUrl));
            }}
          >
            {isPlacingOrder ? <Spinner></Spinner> : "Set up payouts"}
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
            style={{ display: "inline-block" }}
            disabled={isPlacingOrder}
            onClick={(event) => {
              setIsPlacingOrder(true);
              event.preventDefault();
              const eventTarget = event.target;
              handleConnect().then((merchantStripeId) =>
                props.onSubmit(eventTarget, merchantStripeId).then(() => {
                  LocalStorageManager.shared.setLocalStorage(
                    "first_login",
                    true
                  );
                  setRedirect(redirectUrl);
                })
              );
            }}
          >
            {isPlacingOrder ? <Spinner></Spinner> : "Set up payouts"}
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
