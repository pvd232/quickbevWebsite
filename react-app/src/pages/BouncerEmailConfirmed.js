import React, { useEffect } from "react";
import API from "../helpers/Api.js";
import Row from "react-bootstrap/Row";
import Container from "react-bootstrap/Container";
import { useParams } from "react-router-dom";
import MailOutlineIcon from "@material-ui/icons/MailOutline";
import Col from "react-bootstrap/Col";
const MerchantEmployeePayoutSetupComplete = () => {
  let { sessionToken } = useParams();
  useEffect(() => {
    let mounted = true;
    API.checkTokenStatus(sessionToken).then((value) => {
      console.log("value", value);
      if (mounted && !value) {
        window.location.assign("/");
      } else if (mounted && value) {
        API.makeRequest("POST", `/bouncer/${sessionToken}`);
      }
    });

    return () => (mounted = false);
  });
  return (
    <Row
      style={{
        justifyContent: "center",
        height: "100vh",
      }}
    >
      <Col
        xs={12}
        id="payoutSetup"
        style={{
          borderRadius: "7px",
          padding: "3rem",
          justifyContent: "center",
          alignItems: "center",
          display: "flex",
          backgroundColor: "white",
        }}
      >
        <Container>
          <Row style={{ height: "fit-content" }}>
            <Col
              sm={12}
              style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "flex-end",
              }}
            >
              <div className="fs-title">
                Congratulations, your email is verified!
              </div>
            </Col>
          </Row>
          <Row>
            <Col
              xs={12}
              style={{
                textAlign: "center",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "center",
              }}
            >
              <MailOutlineIcon
                className="icon"
                style={{
                  transform: "scale(2.8)",
                }}
              ></MailOutlineIcon>
            </Col>
            <Col
              xs={12}
              style={{
                textAlign: "center",
                display: "flex",
                justifyContent: "center",
                marginTop: "3vh",
              }}
            >
              <p>
                Check your inbox for another email with a button/link to sign
                in! If you don't see it, make sure to check your spam.
              </p>
            </Col>
          </Row>
        </Container>
      </Col>
    </Row>
  );
};

export default MerchantEmployeePayoutSetupComplete;
