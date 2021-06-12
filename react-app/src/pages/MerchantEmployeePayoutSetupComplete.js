import React from "react";
import bankIcon from "../static/icon-bank.svg";
import Row from "react-bootstrap/Row";
import Container from "react-bootstrap/Container";

import Col from "react-bootstrap/Col";
const MerchantEmployeePayoutSetupComplete = () => {
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
                Congratulations, you created your account!
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
                <p>Click the back arrow on the top left of the screen.</p>

                <p className="text-center notice">
                  You'll be redirected to login page.
                </p>
              </div>
            </Col>
          </Row>
        </Container>
      </Col>
    </Row>
  );
};

export default MerchantEmployeePayoutSetupComplete;
