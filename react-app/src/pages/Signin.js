import React, { useState, useReducer, useEffect } from "react";
import API from "../helpers/Api.js";
import Navbar from "../Navbar.js";
import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";
import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import "../css/Signup.css";
import { Link } from "react-router-dom";
import "../css/Signup.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
import { LocalStorageManager } from "../Models";
const Signin = () => {
  const [redirect, setRedirect] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [isSpinning, setIsSpinning] = useState(null);
  const [authorization, setAuthorization] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      email: "",
      password: "",
    }
  );
  const formChangeHandler = (event) => {
    let name = event.target.name;
    let value = event.target.value;
    setAuthorization({ [name]: value });
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };

  useEffect(() => {
    //had to do this because memory leak due to component not unmounting properly
    let mount = true;
    if (mount && redirect) {
      window.location.assign(redirect);
    }

    return () => (mount = false);
  }, [redirect]);
  const Spinner = () => (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <p style={{ marginBottom: "0", marginRight: ".4rem" }}>Submit</p>
      <FontAwesomeIcon icon={faSpinner} className="fa-spin" />
    </div>
  );
  const onSubmit = (event) => {
    event.preventDefault();
    const form = event.target;
    if (validate(form)) {
      API.getMerchant(authorization).then((response) => {
        if (response) {
          console.log(
            "LocalStorageManager.shared.currentMerchant",
            LocalStorageManager.shared.currentMerchant
          );
          setRedirect("/home");
        } else {
          const newErrorMsgState = {};
          // otherwise it will be false
          newErrorMsgState["errorMsg"] =
            "Invalid username or password, please try again";
          newErrorMsgState["errorDisplay"] = "inline-block";
          setErrorMsg(newErrorMsgState);
          setIsSpinning(false);
          return false;
        }
      });
    } else {
      return false;
    }
  };
  const errorMsgStyle = {
    display: errorMsg ? errorMsg.errorDisplay : "none",
    textAlign: "left",
    marginTop: "0",
  };
  return (
    <>
      <Navbar />
      <div className="signupBody">
        <div id="msform" style={{ marginTop: "5vh" }}>
          <fieldset>
            <h2 className="fs-title">Sign in</h2>
            <Row style={{ marginTop: "10%" }}>
              <Col xs={10}>
                <div className="invalid-feedback" style={errorMsgStyle}>
                  {errorMsg ? errorMsg.errorMsg : ""}
                </div>
                <Form.Label>Email</Form.Label>
                <Form.Control
                  type="text"
                  name="email"
                  required
                  onChange={(e) => {
                    formChangeHandler(e);
                  }}
                  value={authorization.email}
                />
              </Col>
            </Row>
            <Row>
              <Col xs={10}>
                <Form.Label>Password</Form.Label>
                <Form.Control
                  type="password"
                  name="password"
                  required
                  onChange={(e) => {
                    formChangeHandler(e);
                  }}
                  value={authorization.password}
                />
              </Col>
            </Row>
            <Row>
              <Col
                style={{
                  display: "flex",
                  alignItems: "flex-end",
                  justifyContent: "center",
                }}
              >
                <Button
                  className="btn btn-primary text-center"
                  disabled={isSpinning}
                  style={{
                    marginTop: "10%",
                  }}
                  onClick={(event) => {
                    setIsSpinning(true);
                    onSubmit(event);
                  }}
                >
                  {isSpinning ? <Spinner></Spinner> : "Submit"}
                </Button>
                <Link
                  to="/password-reset-email-form"
                  style={{ marginLeft: "1vw" }}
                >
                  Forgot password
                </Link>
              </Col>
            </Row>
          </fieldset>
        </div>
      </div>
    </>
  );
};
export default Signin;
