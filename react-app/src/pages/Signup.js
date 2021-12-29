import React, { useState, useReducer } from "react";
import { Merchant, Business, LocalStorageManager } from "../Models.js";
import API from "../helpers/Api.js";
import Navbar from "../Navbar.js";
// import logo from "../static/landscapeLogo.svg";
import SearchLocationInput from "../SearchLocationInput.js";
import PayoutSetup from "./PayoutSetup";
import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";
import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import "../css/Signup.css";

const ProgressBar = (props) => {
  const statusValues = [
    "Account setup",
    "Promote your menu",
    "Start getting paid",
  ];
  return (
    <ul id="progressbar">
      {statusValues.map((item, i) => {
        return (
          <li className={i <= props.i ? "active" : ""} key={i}>
            {item}
          </li>
        );
      })}
    </ul>
  );
};
const CreateYourAccountFieldset = (props) => {
  // use reducer takes 2 parameters, the first is a function called a reducer, the second is the initial value of the state
  // usually the reducer funciton takes in two parameters, the state, and the action being performed. but the way ive defined it, it takes in an object that stores the new value the user has type in
  // the syntax of the reducer funciton is such that parenthesis are used for the return value instead of brackets because the only logic in the return value is the value that it returns. the return word is also omitted
  // i supply an anonymous reducer function that takes in the current and new state and returns the updated state object spreading syntax
  // this reduction function is applied in the formChangeHandler which dynamically sets the state value based on the name passed in through the event
  // i am telling React how to update the state with the reducer function, and then i am binding those instructions to my setFormValue function which then implements that logic.
  // react is passing the current state into the function, and i am passing in the second parameter, new state, i could implement some logic if i wanted, then i return what i want the new state to be to react and react updates it

  const [formValue, setFormValue] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      firstName: "",
      lastName: "",
      phoneNumber: "",
      id: "",
      password: "",
      confirmPassword: "",
    }
  );
  const [errorMsg, setErrorMsg] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      confirmPasswordErrorMsg: "",
      emailErrorMsg: "",
    }
  );
  const formChangeHandler = (event) => {
    let name = event.target.name;
    let value = event.target.value;
    if (
      typeof value === "string" &&
      name !== "password" &&
      name !== "confirmPassword"
    ) {
      setFormValue({ [name]: value.trim().toLowerCase() });
    } else {
      setFormValue({ [name]: value });
    }
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };
  const handleNext = (event) => {
    event.preventDefault();
    const form = event.target;

    if (validate(form)) {
      var newErrorMsgState = {
        confirmPwdDisplay: "none",
      };
      if (formValue.password !== formValue.confirmPassword) {
        newErrorMsgState["confirmPasswordErrorMsg"] =
          "* Your passwords do not match";
        newErrorMsgState["confirmPwdDisplay"] = "inline-block";
        setErrorMsg(newErrorMsgState);
        return false;
      } else {
        const newMerchant = new Merchant("merchantStateObject", formValue);
        const headers = { email: newMerchant.id };
        API.makeRequest("GET", "/merchant/validate", false, headers).then(
          (response) => {
            console.log("response", response);
            console.log("response.status", response.status);
            if (response.status === 200) {
              // if the username is available the response from the API will be true
              props.onClick("next", "merchant", newMerchant);
            } else {
              // otherwise it will be false
              newErrorMsgState["emailErrorMsg"] = "* Username already claimed";
              newErrorMsgState["emailDisplay"] = "inline-block";
              setErrorMsg(newErrorMsgState);
              return false;
            }
          }
        );
      }
    } else {
      return false;
    }
  };
  const confirmPwdErrorMsgStyle = {
    display: errorMsg ? errorMsg.confirmPwdDisplay : "none",
    textAlign: "left",
    marginTop: "0",
  };
  const emailErrorMsgStyle = {
    display: errorMsg ? errorMsg.emailDisplay : "none",
    textAlign: "left",
    marginTop: "0",
  };

  return (
    <Form
      onSubmit={(e) => {
        handleNext(e);
      }}
    >
      <fieldset>
        <h2 className="fs-title">Create your account</h2>
        <Row>
          <Col>
            <Form.Label>First name</Form.Label>
            <Form.Control
              type="text"
              name="firstName"
              required
              onChange={(e) => {
                formChangeHandler(e);
              }}
              value={formValue.firstName}
            />
          </Col>
          <Col>
            <Form.Label>Last name</Form.Label>
            <Form.Control
              type="text"
              name="lastName"
              required
              onChange={(e) => {
                formChangeHandler(e);
              }}
              value={formValue.lastName}
            />
          </Col>
        </Row>
        <Row>
          <Col>
            <div className="invalid-feedback" style={emailErrorMsgStyle}>
              {errorMsg.emailErrorMsg}
            </div>
            <Form.Label>Email</Form.Label>
            <Form.Control
              type="email"
              name="id"
              required
              onChange={(e) => {
                formChangeHandler(e);
              }}
              value={formValue.id}
            />
          </Col>
        </Row>
        <Row>
          <Col>
            <Form.Label>Phone number (no dashes)</Form.Label>
            <Form.Control
              type="tel"
              name="phoneNumber"
              required
              pattern="[0-9]{10}"
              onChange={(e) => {
                formChangeHandler(e);
              }}
              value={formValue.phoneNumber}
            />
          </Col>
        </Row>
        <Row>
          <Col>
            <Form.Label>Password</Form.Label>
            <Form.Control
              type="password"
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
          <Col>
            <div className="invalid-feedback" style={confirmPwdErrorMsgStyle}>
              {errorMsg.confirmPasswordErrorMsg}
            </div>
            <Form.Label>Confirm password</Form.Label>
            <Form.Control
              type="password"
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
            <Button type="submit" name="next" className="next action-button">
              Next
            </Button>
          </Col>
        </Row>
      </fieldset>
    </Form>
  );
};
const PromoteYourMenuFieldset = (props) => {
  const [formValue, setFormValue] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      menuUrl: "",
      classification: "bar",
      numberOfBusinesses: "",
    }
  );
  const [errorMsg, setErrorMsg] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      menuSubmittedErrorMsgDisplay: "none",
    }
  );
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState("");

  const onFileChange = (event) => {
    console.log("event", event);
    // Update the state
    console.log("event.target.files[0]", event.target.files[0].name);
    console.log("event.target.files", event.target.files);
    setSelectedFile(event.target.files[0]);
    setSelectedFileName(event.target.files[0].name);
  };

  const formChangeHandler = (event) => {
    let name = event.target.name;
    let value = event.target.value;
    if (typeof value === "string") {
      setFormValue({ [name]: value.trim().toLowerCase() });
    } else {
      setFormValue({ [name]: value });
    }
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };
  const handleNext = (event) => {
    event.preventDefault();
    const form = event.target;
    if (validate(form)) {
      if (!(formValue.menuUrl || selectedFile)) {
        const newErrorMsgState = {};
        newErrorMsgState["menuSubmittedErrorMsg"] =
          "* Please upload your menu and or submit a link to it";
        newErrorMsgState["menuSubmittedErrorMsgDisplay"] = "inline-block";
        setErrorMsg(newErrorMsgState);
        return false;
      }
      const formDataObject = {};
      // Update the formData object
      formDataObject.numberOfBusinesses = formValue.numberOfBusinesses;
      formDataObject.classification = formValue.classification;
      if (formValue.menuUrl) {
        formDataObject.menuUrl = formValue.menuUrl;
      }
      if (selectedFile) {
        formDataObject.menuFile = selectedFile;
        formDataObject.menuFileName = selectedFileName;
      }
      props.onClick("next", "formDataObject", formDataObject);
    } else {
      return false;
    }
  };
  const menuSubmittedErrorMsgStyle = {
    display: errorMsg.menuSubmittedErrorMsgDisplay,
    textAlign: "left",
    marginTop: "0",
  };
  return (
    <Form
      onSubmit={(e) => {
        handleNext(e);
      }}
    >
      <fieldset>
        <p
          className="text-muted"
          style={{ fontSize: "11px", margin: "0", textAlign: "left" }}
        >
          Step 2/3
        </p>
        <h2 className="fs-title">Promote your menu</h2>
        <h5 className="fs-subtitle">
          Show off your business by uploading a link, image, PDF, or any other
          file with your menu!
        </h5>
        <Row>
          <Form.Group
            as={Col}
            style={{ paddingLeft: "5px", marginBottom: "0" }}
          >
            <div
              className="invalid-feedback"
              style={menuSubmittedErrorMsgStyle}
            >
              {errorMsg.menuSubmittedErrorMsg}
            </div>
            <Form.Label>Website link</Form.Label>
            <Form.Control
              type="url"
              name="menuUrl"
              placeholder="https://yourwebsite.com"
              onChange={(e) => {
                formChangeHandler(e);
              }}
              value={formValue.menuUrl}
              noValidate
              // required={formValue.selectedFile ? false : true}
            />
          </Form.Group>
        </Row>

        <Row>
          <Col
            sm={2}
            className="fs-subtitle"
            style={{
              alignSelf: "center",
              marginTop: "0px",
              marginBottom: "0px",
            }}
          >
            or
          </Col>
        </Row>
        <Row>
          <Form.Group as={Col} style={{ paddingLeft: "5px" }} id="fileInputCol">
            <Form.Label>PDF or Image</Form.Label>
            <Form.File
              id="fileInput"
              name="menuImg"
              type="file"
              custom
              style={{
                border: "none",
                borderRadius: "3px",
                fontFamily: "montserrat",
                fontSize: "12px",
                height: "4vh",
                padding: "0",
              }}
              onChange={(event) => onFileChange(event)}
              label={selectedFileName}
              noValidate

              // value={selectedFile}
            />
          </Form.Group>
        </Row>
        <Row>
          <Form.Group
            as={Col}
            controlId="classification"
            style={{ paddingLeft: "5px" }}
          >
            <Form.Label>Type of business</Form.Label>
            <Form.Control
              as="select"
              required
              custom
              name="classification"
              onChange={(event) => formChangeHandler(event)}
              style={{
                paddingLeft: "15px",
                paddingRight: "0",
                paddingTop: "0",
                paddingBottom: "0",
              }}
            >
              <option>Bar</option>
              <option>Restaurant</option>
              <option>Club</option>
              <option>Music Festival</option>
              <option>Sporting Event</option>
            </Form.Control>
          </Form.Group>
          <Form.Group as={Col} controlId="numberOfBusinesses">
            <Form.Label>Number of businesses</Form.Label>
            <Form.Control
              type="text"
              name="numberOfBusinesses"
              required
              onChange={(e) => {
                formChangeHandler(e);
              }}
              value={formValue.numberOfBusinesses}
            />
          </Form.Group>
        </Row>

        <h2 className="fs-title" style={{ marginTop: "40px" }}>
          How do you want to recieve your orders?
        </h2>

        <Row style={{ paddingLeft: "5px", paddingRight: "15px" }}>
          <h5
            className="fs-subtitle"
            style={{
              paddingLeft: "15px",
              paddingRight: "5px",
            }}
          >
            To maximize your business' efficieny, orders will be received
            through an Android tablet and labeled using a bluetooth label
            printer.
          </h5>
          <Card>
            <Card.Body>
              <Row>
                <Col xs={2}>
                  <Form.Check
                    type="radio"
                    label=""
                    required
                    name="tablet"
                    id="formHorizontalRadios2"
                  />
                </Col>
                <Col xs={10}>
                  <Form.Label>Tablet</Form.Label>
                  <Card.Text
                    className="text-muted"
                    style={{
                      textIndent: "0",
                      textAlign: "left",
                      fontSize: "14px",
                      fontWeight: "bold",
                    }}
                  >
                    The tablet will be shipped to your business free of charge!
                  </Card.Text>

                  <Card.Text
                    className="text-muted"
                    style={{
                      textIndent: "0",
                      textAlign: "left",
                      fontSize: "14px",
                      fontWeight: "bolder",
                    }}
                  >
                    Included in the shipment will be a charger and stand to hold
                    the tablet.
                  </Card.Text>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Row>
        <Button
          name="previous"
          className="previous action-button"
          required
          onClick={() => {
            props.onClick("previous");
          }}
        >
          Previous
        </Button>
        <Button type="submit" name="next" className="next action-button">
          Next
        </Button>
      </fieldset>
    </Form>
  );
};
const BusinessFieldset = (props) => {
  const [formValue, setFormValue] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      name: "",
      phoneNumber: "",
      address: "",
      street: "",
      suite: "",
      city: "",
      state: "",
      zipcode: "",
      schedule: [],
    }
  );
  const [schedule, setSchedule] = useState([
    { day: "monday", openingTime: "", closingTime: "", isClosed: false },
    { day: "tuesday", openingTime: "", closingTime: "", isClosed: false },
    { day: "wednesday", openingTime: "", closingTime: "", isClosed: false },
    { day: "thursday", openingTime: "", closingTime: "", isClosed: false },
    { day: "friday", openingTime: "", closingTime: "", isClosed: false },
    { day: "saturday", openingTime: "", closingTime: "", isClosed: false },
    { day: "sunday", openingTime: "", closingTime: "", isClosed: false },
  ]);
  const setAddress = (address) => {
    if (address.split(",").length === 4) {
      const addressObject = {};
      addressObject.address = address;
      const addressArray = address.split(",");
      addressObject.street = addressArray[0];
      addressObject.city = addressArray[1];
      const stateZipcodeArray = addressArray[2].split(" ");
      addressObject.state = stateZipcodeArray[1];
      addressObject.zipcode = stateZipcodeArray[2];
      setFormValue(addressObject);
    }
  };
  const handleScheduleChange = (event) => {
    const name = event.target.name;
    const dayIndex = parseInt(name.split("-")[0]);
    const time = event.target.value;
    const isOpenOrClosed = name.split("-")[1];
    // must create new date object outside the scope of the setSchedule callback or the state doesnt update
    const newDateObject = {
      day: dayIndex,
      openingTime: "",
      closingTime: "",
      isClosed: false,
    };
    setSchedule((prevSchedule) => {
      if (isOpenOrClosed === "closed") {
        newDateObject.isClosed = !prevSchedule[dayIndex].isClosed;
      } else if (isOpenOrClosed === "open") {
        newDateObject.openingTime = time;
        newDateObject.closingTime = prevSchedule[dayIndex].closingTime;
      } else if (isOpenOrClosed === "closing") {
        newDateObject.closingTime = time;
        newDateObject.openingTime = prevSchedule[dayIndex].openingTime;
      }
      // creating new object makes setState func work for some reason
      const newSchedule = prevSchedule.map((a) => ({ ...a }));
      newSchedule[dayIndex] = newDateObject;
      return newSchedule;
    });
  };
  const formChangeHandler = (event) => {
    let name = event.target.name;
    let value = event.target.value;
    if (typeof value === "string" && name !== "name") {
      setFormValue({ [name]: value.trim().toLowerCase() });
    } else {
      setFormValue({ [name]: value });
    }
  };

  const handleSubmit = async (eventTarget, merchantStripeId) => {
    // the event target is the button that was clicked inside the payout setup component inside the business fieldset
    const form = eventTarget.closest("form");
    if (validate(form)) {
      // set all the values for the business
      // if the user comes back to this page before submitting to change stuff it will reset the values
      const copyOfFormValue = {
        name: formValue["name"],
        phone_number: formValue["phoneNumber"],
        address: formValue["address"],
        street: formValue["street"],
        suite: formValue["suite"],
        city: formValue["city"],
        state: formValue["state"],
        zipcode: formValue["zipcode"],
        schedule: [],
      };

      copyOfFormValue.schedule = schedule;
      const newBusiness = new Business(copyOfFormValue);
      const result = await props.onSubmit(newBusiness, merchantStripeId);
      return result;
    } else {
      return false;
    }
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };
  const daysOfWeek = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
  ];
  console.log("schedule", schedule);
  return (
    <Form autocomplete="off">
      <fieldset>
        <h2 className="fs-title">Your Business</h2>
        <Form.Label>Name</Form.Label>
        <Form.Control
          type="text"
          className="mb-3"
          name="name"
          placeholder="Business Name"
          value={formValue.name}
          required
          onChange={(e) => {
            formChangeHandler(e);
          }}
        />
        <Form.Label>Phone number</Form.Label>
        <Form.Control
          type="tel"
          name="phoneNumber"
          className="mb-3"
          required
          pattern="[0-9]{10}"
          placeholder="5128999160"
          value={formValue.phoneNumber}
          onChange={(e) => {
            formChangeHandler(e);
          }}
        />
        ,
        {daysOfWeek.map((day, i) => (
          <>
            <Form.Label>Closed on {day}</Form.Label>
            <Row
              key={i}
              style={{
                display: "flex",
                height: "1vh",
                marginTop: "0",
                alignItems: "flex-start",
                justifyContent: "flex-start",
              }}
            >
              <Col
                xs={2}
                key={"col" + i}
                style={{
                  display: "flex",
                  height: "1vh",
                  alignItems: "flex-start",
                  justifyContent: "flex-start",
                }}
              >
                <Form.Check
                  type="checkbox"
                  key={i + "-closed"}
                  name={i + "-closed"}
                  value={schedule[i].isClosed}
                  onChange={(e) => handleScheduleChange(e)}
                />
              </Col>
            </Row>

            <Form.Label>{day} opening time</Form.Label>

            <Form.Control
              type="time"
              key={i + "-open"}
              name={i + "-open"}
              className="mb-3"
              required={!schedule[i].isClosed}
              pattern="[0-9]{10}"
              placeholder="06:00 PM"
              disabled={schedule[i].isClosed}
              value={schedule[i].openingTime}
              onChange={(e) => handleScheduleChange(e)}
            />

            <Form.Label>Closing time</Form.Label>
            <Form.Control
              type="time"
              key={i + "-closing"}
              name={i + "-closing"}
              className="mb-3"
              required={schedule[i].isClosed}
              placeholder="04:00 AM"
              disabled={schedule[i].isClosed}
              value={schedule[i].closingTime}
              onChange={(e) => handleScheduleChange(e)}
            />
          </>
        ))}
        ,<Form.Label>Address</Form.Label>
        <SearchLocationInput onUpdate={(address) => setAddress(address)} />
        <Row>
          <Col
            sm={12}
            id="payoutSetup"
            style={{ justifyContent: "center", display: "flex" }}
          >
            <PayoutSetup
              onSubmit={(eventTarget, merchantStripeId) =>
                handleSubmit(eventTarget, merchantStripeId)
              }
            ></PayoutSetup>
          </Col>
        </Row>
        {/* <Row style={{ justifyContent: "space-around" }}>
          <Form.Control
            type="button"
            name="previous"
            className="previous action-button"
            value="Previous"
            style={{ marginTop: "10%" }}
            onClick={() => {
              props.onClick("previous");
            }}
          />
        </Row> */}
      </fieldset>
    </Form>
  );
};

const Signup = () => {
  const [merchant, setMerchant] = useState(null);
  const [formDataObject, setformDataObject] = useState(null);

  const handleClick = (buttonType, objectType = null, objectData = null) => {
    if (objectType === "merchant") {
      console.log("merchant data", merchant);
      console.log("objectData", objectData);

      setMerchant({ ...merchant, ...objectData });
    } else if (objectType === "formDataObject") {
      console.log("formDataObject", formDataObject);

      setformDataObject({ ...formDataObject, ...objectData });
    }
    if (buttonType === "previous") {
      if (currentFieldsetIndex > 0) {
        setCurrentFieldsetIndex(currentFieldsetIndex - 1);
      }
    } else if (buttonType === "next") {
      if (currentFieldsetIndex < 2) {
        setCurrentFieldsetIndex(currentFieldsetIndex + 1);
      }
    }
  };

  const onSubmit = async (newBusiness, merchantStripeId) => {
    console.log("merchantStripeId", merchantStripeId);
    const newForm = new FormData();
    // set values from formDataObject into business object
    newBusiness.classification = formDataObject.classification;
    newBusiness.merchantStripeId = merchantStripeId;
    if (formDataObject.menuUrl) {
      newBusiness.menuUrl = formDataObject.menuUrl;
    }
    if (formDataObject.menuFile) {
      newForm.append(
        "file",
        formDataObject.menuFile,
        formDataObject.menuFileName
      );
    }

    // the merchant in state was being converted back to a regular object
    const newMerchant = new Merchant("merchantStateObject", merchant);

    newMerchant.numberOfBusinesses = formDataObject.numberOfBusinesses;
    newMerchant.stripeId = merchantStripeId;
    console.log("newMerchant", newMerchant);

    // set the stripe ID returned from the backend
    newForm.append("merchant", JSON.stringify(newMerchant));

    // set the merchant id in business to be the same as the new merchant
    newBusiness.merchantId = newMerchant.id;
    console.log("newBusiness", newBusiness);
    newForm.append("business", JSON.stringify(newBusiness));

    LocalStorageManager.shared.setItem("merchant", newMerchant);
    LocalStorageManager.shared.setItem("business", newBusiness);
    // set in local storage if user has multiple businesses so we can display a tab to add more businesses late
    let responseBody = await API.makeRequest(
      "POST",
      "/merchant/sign_up",
      newForm,
      false,
      true
    );
    console.log("responseBody", responseBody);

    const confirmed_new_business = new Business(
      responseBody.confirmed_new_business
    );
    const confirmed_new_merchant = new Merchant(
      "json",
      responseBody.confirmed_new_merchant
    );
    console.log("confirmed_new_business", confirmed_new_business);
    console.log("responseBody.token", responseBody.headers.token);

    LocalStorageManager.shared.setItem("business", confirmed_new_business);
    LocalStorageManager.shared.setItem("merchant", confirmed_new_merchant);
    LocalStorageManager.shared.setItem(
      "session_token",
      responseBody.headers.token
    );
    return true;
  };
  const fieldSets = [
    <CreateYourAccountFieldset
      onClick={(buttonType, objectType, merchant) =>
        handleClick(buttonType, objectType, merchant)
      }
    ></CreateYourAccountFieldset>,
    <PromoteYourMenuFieldset
      onClick={(buttonType, objectType, merchant) =>
        handleClick(buttonType, objectType, merchant)
      }
    ></PromoteYourMenuFieldset>,
    <BusinessFieldset
      onSubmit={(newBusiness, merchantStripeId) =>
        onSubmit(newBusiness, merchantStripeId)
      }
      onClick={(buttonType) => handleClick(buttonType)}
    ></BusinessFieldset>,
  ];
  const [currentFieldsetIndex, setCurrentFieldsetIndex] = useState(0);

  return (
    <>
      <Navbar />
      {/* <!-- multistep form -->*/}
      <div className="signupBody">
        <div id="msform">
          {/* <!-- progressbar --> */}
          <ProgressBar i={currentFieldsetIndex}></ProgressBar>
          {/* <!-- fieldsets --> */}
          {fieldSets[currentFieldsetIndex]}
        </div>
      </div>
    </>
  );
};
export default Signup;
