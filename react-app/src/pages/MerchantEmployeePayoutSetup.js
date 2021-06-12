import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Button from "react-bootstrap/Button";
import API from "../helpers/Api.js";
import bankIcon from "../static/icon-bank.svg";
import Row from "react-bootstrap/Row";
import Container from "react-bootstrap/Container";

import Col from "react-bootstrap/Col";
const MerchantEmployeePayoutSetup = (props) => {
  console.log("merchantEMployee");

  let { merchantEmployeeId } = useParams();
  const [redirect, setRedirect] = useState(null);
  var redirectUrl = null;
  const getRedirectInfo = async () => {
    return API.makeRequest(
      "GET",
      `/merchant_employee_stripe_account?merchant_employee_id=${merchantEmployeeId}`
    );
  };
  const handleConnect = async () => {
    let responseContent = await getRedirectInfo();
    let url = responseContent.url;
    if (url) {
      redirectUrl = url;
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
      <Row
        style={{
          justifyContent: "center",
          height: "100vh",
          marginTop: "0",
          marginBottom: "0",
        }}
      >
        <Col
          sm={4}
          id="payoutSetup"
          style={{
            borderRadius: "7px",
            padding: "3rem",
            justifyContent: "center",
            display: "flex",
            backgroundColor: "white",
            height: "100vh",
          }}
        >
          <div className="text-center box">
            <img src={bankIcon} alt="" className="icon" />
            <h5 style={{ marginTop: "5%", marginBottom: "5%" }}>
              Stripe account onboarding incomplete
            </h5>
            <p>
              Please click the button below to be redirected to Stripe to
              complete the onboarding proces
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
        </Col>
      </Row>
    );
  } else {
    return (
      <Row
        style={{
          justifyContent: "center",
          height: "100vh",
        }}
      >
        <Col
          sm={12}
          id="payoutSetup"
          style={{
            borderRadius: "7px",
            padding: "3rem",
            justifyContent: "center",
            display: "flex",
            backgroundColor: "white",
          }}
        >
          <Container>
            <Row>
              <Col
                sm={12}
                style={{
                  display: "flex",
                  textAlign: "center",
                }}
              >
                <div className="fs-title">
                  Input your bank account to recieve your tips
                </div>
              </Col>
            </Row>
            <Row>
              <Col
                sm={12}
                style={{
                  textAlign: "center",
                  display: "flex",
                  justifyContent: "center",
                }}
              >
                <div className="text-center box">
                  <img src={bankIcon} alt="" className="icon" />
                  <p>
                    QuickBev partners with Stripe to transfer your tips to your
                    bank account.
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
                  <p className="text-center notice">
                    You'll be redirected to Stripe to complete the onboarding
                    proces.
                  </p>
                </div>
              </Col>
            </Row>
          </Container>
        </Col>
      </Row>
    );
  }
};

export default MerchantEmployeePayoutSetup;
