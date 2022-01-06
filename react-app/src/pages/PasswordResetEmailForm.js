import React, { useState, useReducer } from "react";
import API from "../helpers/Api.js";
import Navbar from "../Navbar.js";
import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";
import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import "../css/Signup.css";

const Signin = () => {
  const [successMsg, setSuccessMsg] = useState(null);
  const [authorization, setAuthorization] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      email: "",
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

  const onSubmit = (event) => {
    event.preventDefault();
    const form = event.target;
    if (validate(form)) {
      const entityHeader = { entity: "merchant" };
      API.makeRequest(
        "GET",
        `/password/reset/${authorization.email}`,
        false,
        entityHeader
      ).then((response) => {
        setSuccessMsg(
          "If your email is associated with an account, you will receive a password reset email. \n If you did not receive it make sure to check your spam inbox."
        );
        return;
      });
    } else {
      return false;
    }
  };

  return (
    <>
      <Navbar />
      <div className="signupBody">
        <div id="msform" style={{ marginTop: "5vh" }}>
          <fieldset>
            <h2 className="fs-title">Reset your password</h2>
            <Row style={{ marginTop: "10%" }}>
              <Col xs={10}>
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
                <p style={{ marginTop: "10%" }}>{successMsg}</p>
              </Col>
            </Row>
            <Row>
              <Col>
                <Button
                  className="btn btn-primary text-center"
                  onClick={(event) => {
                    onSubmit(event);
                  }}
                >
                  Send reset email
                </Button>
              </Col>
            </Row>
          </fieldset>
        </div>
      </div>
    </>
  );
};
export default Signin;
