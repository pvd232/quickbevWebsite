import React, { useState, useReducer, useEffect } from "react";
import { useParams } from "react-router-dom";
import API from "../helpers/Api.js";
import Navbar from "../Navbar.js";
import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";
import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import "../css/Signup.css";

const ResetPassword = () => {
  const [redirect, setRedirect] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [formValue, setformValue] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      password: "",
      confirmPassword: "",
    }
  );
  let { sessionToken } = useParams();

  const formChangeHandler = (event) => {
    let name = event.target.name;
    let value = event.target.value;
    setformValue({ [name]: value });
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

  const onSubmit = (event) => {
    event.preventDefault();
    const form = event.target;
    if (validate(form)) {
      if (formValue.password !== formValue.confirmPassword) {
        console.log("passwords dont match");
        setErrorMsg("* Your passwords don't match");
        return false;
      } else {
        API.makeRequest(
          "POST",
          "/reset-password/" + sessionToken,
          formValue.password
        ).then((response) => {
          if (response) {
            // if the username is available the response from the API will be true
            alert("Password successfully updated!");
            setRedirect("/");
          } else {
            // otherwise it will be false
            setErrorMsg(
              "There was a problem with updating your password, please resend the confirmation email from the app and try again."
            );
            return false;
          }
        });
      }
    } else {
      return false;
    }
  };
  const errorMsgStyle = {
    display: errorMsg ? "inline-block" : "none",
    textAlign: "left",
    marginTop: "0",
    fontSize: ".95rem",
    marginBottom: "10px",
  };
  return (
    <>
      <Navbar />
      <div className="signupBody">
        <div id="msform" style={{ marginTop: "5vh" }}>
          <fieldset>
            <h2 className="fs-title">Reset password</h2>
            <Row>
              <Col xs={10}>
                <div className="invalid-feedback" style={errorMsgStyle}>
                  {errorMsg}
                </div>
                <Form.Label style={{ fontSize: "1.05rem" }}>
                  New password
                </Form.Label>
                <Form.Control
                  type="text"
                  name="password"
                  required
                  onChange={(e) => {
                    formChangeHandler(e);
                  }}
                  value={formValue.password}
                />
              </Col>
            </Row>
            <Row>
              <Col xs={10}>
                <Form.Label style={{ fontSize: "1.05rem" }}>
                  Confirm new password
                </Form.Label>
                <Form.Control
                  type="text"
                  name="confirmPassword"
                  required
                  onChange={(e) => {
                    formChangeHandler(e);
                  }}
                  value={formValue.confirmPassword}
                />
              </Col>
            </Row>
            <Row>
              <Col>
                <Button
                  className="btn btn-primary text-center"
                  style={{ marginTop: "10%" }}
                  onClick={(event) => {
                    onSubmit(event);
                  }}
                >
                  Submit
                </Button>
              </Col>
            </Row>
          </fieldset>
        </div>
      </div>
    </>
  );
};
export default ResetPassword;
