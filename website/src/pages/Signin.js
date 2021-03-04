import React, { useState, useReducer, useEffect } from "react";
import { Merchant, Business, setLocalStorage } from "../Models.js";
import API from "../helpers/Api.js";
import Navbar from "../Navbar.js";
// import logo from "../static/landscapeLogo.svg";
// import SearchLocationInput from "../SearchLocationInput.js";
// import PayoutSetup from "./PayoutSetup";
import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";
import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
// import Card from "react-bootstrap/Card";
import "../css/Signup.css";

// const ProgressBar = (props) => {
//   const statusValues = [
//     "Account setup",
//     "Promote your menu",
//     "Start getting paid",
//   ];
//   return (
//     <ul id="progressbar">
//       {statusValues.map((item, i) => {
//         return (
//           <li className={i <= props.i ? "active" : ""} key={i}>
//             {item}
//           </li>
//         );
//       })}
//     </ul>
//   );
// };
// const CreateYourAccountFieldset = (props) => {
//   // use reducer takes 2 parameters, the first is a function called a reducer, the second is the initial value of the state
//   // usually the reducer funciton takes in two parameters, the state, and the action being performed. but the way ive defined it, it takes in an object that stores the new value the user has type in
//   // the syntax of the reducer funciton is such that parenthesis are used for the return value instead of brackets because the only logic in the return value is the value that it returns. the return word is also omitted
//   // i supply an anonymous reducer function that takes in the current and new state and returns the updated state object spreading syntax
//   // this reduction function is applied in the formChangeHandler which dynamically sets the state value based on the name passed in through the event
//   // i am telling React how to update the state with the reducer function, and then i am binding those instructions to my setFormValue function which then implements that logic.
//   // react is passing the current state into the function, and i am passing in the second parameter, new state, i could implement some logic if i wanted, then i return what i want the new state to be to react and react updates it
//   const [formValue, setFormValue] = useReducer(
//     (state, newState) => ({ ...state, ...newState }),
//     {
//       firstName: "",
//       lastName: "",
//       phoneNumber: "",
//       email: "",
//       password: "",
//       confirmPassword: "",
//     }
//   );
//   const [errorMsg, setErrorMsg] = useReducer(
//     (state, newState) => ({ ...state, ...newState }),
//     {
//       confirmPwdDisplay: "none",
//       emailDisplay: "none",
//     }
//   );
//   const formChangeHandler = (event) => {
//     let name = event.target.name;
//     let value = event.target.value;
//     setFormValue({ [name]: value });
//   };
//   const validate = (form) => {
//     form.classList.add("was-validated");
//     return form.checkValidity();
//   };
//   const handleNext = (event) => {
//     event.preventDefault();
//     const form = event.target;

//     if (validate(form)) {
//       var newErrorMsgState = {
//         confirmPwdDisplay: "none",
//       };
//       if (formValue.password !== formValue.confirmPassword) {
//         console.log("passwords dont match");

//         newErrorMsgState["confirmPasswordErrorMsg"] =
//           "* Your passwords do not match";
//         newErrorMsgState["confirmPwdDisplay"] = "inline-block";
//         setErrorMsg(newErrorMsgState);
//         return false;
//       } else {
//         const newMerchant = new Merchant("merchantObject", formValue);
//         const merchantData = { merchant: newMerchant };
//         API.makeRequest(
//           "POST",
//           "/validate-merchant",
//           merchantData,
//           false
//         ).then((response) => {
//           if (response) {
//             // if the username is available the response from the API will be true
//             props.onClick("next", "merchant", newMerchant);
//           } else {
//             // otherwise it will be false
//             newErrorMsgState["emailErrorMsg"] = "* Username already claimed";
//             newErrorMsgState["emailDisplay"] = "inline-block";
//             setErrorMsg(newErrorMsgState);
//             return false;
//           }
//         });
//       }
//     } else {
//       return false;
//     }
//   };
//   const confirmPwdErrorMsgStyle = {
//     display: errorMsg.confirmPwdDisplay,
//     textAlign: "left",
//     marginTop: "0",
//   };
//   const emailErrorMsgStyle = {
//     display: errorMsg.emailDisplay,
//     textAlign: "left",
//     marginTop: "0",
//   };

//   return (
//     <Form
//       onSubmit={(e) => {
//         handleNext(e);
//       }}
//     >
//       <fieldset>
//         <h2 className="fs-title">Create your account</h2>
//         <Row>
//           <Col>
//             <Form.Label>First name</Form.Label>
//             <Form.Control
//               type="text"
//               name="firstName"
//               required
//               onChange={(e) => {
//                 formChangeHandler(e);
//               }}
//               value={formValue.firstName}
//             />
//           </Col>
//           <Col>
//             <Form.Label>Last name</Form.Label>
//             <Form.Control
//               type="text"
//               name="lastName"
//               required
//               onChange={(e) => {
//                 formChangeHandler(e);
//               }}
//               value={formValue.lastName}
//             />
//           </Col>
//         </Row>
//         <Row>
//           <Col>
//             <div className="invalid-feedback" style={emailErrorMsgStyle}>
//               {errorMsg.emailErrorMsg}
//             </div>
//             <Form.Label>Email</Form.Label>
//             <Form.Control
//               type="email"
//               name="email"
//               required
//               onChange={(e) => {
//                 formChangeHandler(e);
//               }}
//               value={formValue.email}
//             />
//           </Col>
//         </Row>
//         <Row>
//           <Col>
//             <Form.Label>Phone number</Form.Label>
//             <Form.Control
//               type="tel"
//               name="phoneNumber"
//               required
//               pattern="[0-9]{10}"
//               onChange={(e) => {
//                 formChangeHandler(e);
//               }}
//               value={formValue.phoneNumber}
//             />
//           </Col>
//         </Row>
//         <Row>
//           <Col>
//             <Form.Label>Password</Form.Label>
//             <Form.Control
//               type="password"
//               name="password"
//               required
//               onChange={(e) => {
//                 formChangeHandler(e);
//               }}
//               value={formValue.password}
//             />
//           </Col>
//         </Row>

//         <Row>
//           <Col>
//             <div className="invalid-feedback" style={confirmPwdErrorMsgStyle}>
//               {errorMsg.confirmPasswordErrorMsg}
//             </div>
//             <Form.Label>Confirm password</Form.Label>
//             <Form.Control
//               type="password"
//               name="confirmPassword"
//               required
//               onChange={(e) => {
//                 formChangeHandler(e);
//               }}
//               value={formValue.confirmPassword}
//             />
//           </Col>
//         </Row>
//         <Row>
//           <Col>
//             <Button type="submit" name="next" className="next action-button">
//               Next
//             </Button>
//           </Col>
//         </Row>
//       </fieldset>
//     </Form>
//   );
// };
// const PromoteYourMenuFieldset = (props) => {
//   const [formValue, setFormValue] = useReducer(
//     (state, newState) => ({ ...state, ...newState }),
//     {
//       menuUrl: "",
//       typeOfBusiness: "",
//       numberOfBusinesses: "",
//     }
//   );
//   const [errorMsg, setErrorMsg] = useReducer(
//     (state, newState) => ({ ...state, ...newState }),
//     {
//       menuSubmittedErrorMsgDisplay: "none",
//     }
//   );
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [selectedFileName, setSelectedFileName] = useState("");

//   const [tablet, setTablet] = useState(false);

//   const onFileChange = (event) => {
//     console.log("event", event);
//     // Update the state
//     console.log("event.target.files[0]", event.target.files[0].name);
//     console.log("event.target.files", event.target.files);
//     setSelectedFile(event.target.files[0]);
//     setSelectedFileName(event.target.files[0].name);
//   };

//   const formChangeHandler = (event) => {
//     let name = event.target.name;
//     console.log("formValue.typeOfBusiness", formValue.typeOfBusiness);
//     console.log("name", name);
//     let value = event.target.value;
//     console.log("value", value);
//     setFormValue({ [name]: value });
//   };
//   const validate = (form) => {
//     if (form.checkValidity()) {
//       form.classList.add("was-validated");
//       return true;
//     } else {
//       return false;
//     }
//   };

//   const handleNext = (event) => {
//     event.preventDefault();
//     const form = event.target;
//     console.log(selectedFile);
//     console.log(selectedFileName);

//     if (validate(form)) {
//       if (!(formValue.menuUrl || selectedFile)) {
//         const newErrorMsgState = {};
//         newErrorMsgState["menuSubmittedErrorMsg"] =
//           "* Please upload your menu and or submit a link to it";
//         newErrorMsgState["menuSubmittedErrorMsgDisplay"] = "inline-block";
//         setErrorMsg(newErrorMsgState);
//         return false;
//       }
//       const formDataObject = {};
//       // Update the formData object
//       formDataObject.numberOfBusinesses = formValue.numberOfBusinesses;
//       formDataObject.classification = formValue.typeOfBusiness;
//       formDataObject.tablet = tablet;
//       console.log("formDataObject", formDataObject);

//       if (formValue.menuUrl) {
//         formDataObject.menuUrl = formValue.menuUrl;
//       }
//       if (selectedFile) {
//         formDataObject.menuFile = selectedFile;
//         formDataObject.menuFileName = selectedFileName;
//       }
//       console.log("formDataObject", formDataObject);
//       props.onClick("next", "formDataObject", formDataObject);
//     } else {
//       return false;
//     }
//   };
//   const menuSubmittedErrorMsgStyle = {
//     display: errorMsg.menuSubmittedErrorMsgDisplay,
//     textAlign: "left",
//     marginTop: "0",
//   };
//   return (
//     <Form
//       onSubmit={(e) => {
//         handleNext(e);
//       }}
//     >
//       <fieldset>
//         <p
//           className="text-muted"
//           style={{ fontSize: "11px", margin: "0", textAlign: "left" }}
//         >
//           Step 2/3
//         </p>
//         <h2 className="fs-title">Promote your menu</h2>
//         <h5 className="fs-subtitle">
//           Show off your business by uploading a link, image, or PDF of your
//           menu!
//         </h5>
//         <Row>
//           <Form.Group
//             as={Col}
//             style={{ paddingLeft: "5px", marginBottom: "0" }}
//           >
//             <div
//               className="invalid-feedback"
//               style={menuSubmittedErrorMsgStyle}
//             >
//               {errorMsg.menuSubmittedErrorMsg}
//             </div>
//             <Form.Label>Website link</Form.Label>
//             <Form.Control
//               type="url"
//               name="menuUrl"
//               placeholder="https://yourwebsite.com"
//               onChange={(e) => {
//                 formChangeHandler(e);
//               }}
//               value={formValue.menuUrl}
//               noValidate
//               // required={formValue.selectedFile ? false : true}
//             />
//           </Form.Group>
//         </Row>

//         <Row>
//           <Col
//             sm={2}
//             className="fs-subtitle"
//             style={{
//               alignSelf: "center",
//               marginTop: "0px",
//               marginBottom: "0px",
//             }}
//           >
//             or
//           </Col>
//         </Row>
//         <Row>
//           <Form.Group as={Col} style={{ paddingLeft: "5px" }} id="fileInputCol">
//             <Form.Label>PDF or Image</Form.Label>
//             <Form.File
//               id="fileInput"
//               name="menuImg"
//               type="file"
//               custom
//               style={{
//                 border: "none",
//                 borderRadius: "3px",
//                 fontFamily: "montserrat",
//                 fontSize: "12px",
//                 height: "4vh",
//                 padding: "0",
//               }}
//               onChange={(event) => onFileChange(event)}
//               label={selectedFileName}
//               noValidate

//               // value={selectedFile}
//             />
//           </Form.Group>
//         </Row>
//         <Row>
//           <Form.Group
//             as={Col}
//             controlId="typeOfBusiness"
//             style={{ paddingLeft: "5px" }}
//           >
//             <Form.Label>Type of business</Form.Label>
//             <Form.Control
//               as="select"
//               required
//               custom
//               name="typeOfBusiness"
//               onChange={(event) => formChangeHandler(event)}
//               style={{
//                 paddingLeft: "15px",
//                 paddingRight: "0",
//                 paddingTop: "0",
//                 paddingBottom: "0",
//               }}
//             >
//               <option>Choose ...</option>
//               <option>Bar</option>
//               <option>Restaurant</option>
//               <option>Club</option>
//               <option>Music Festival</option>
//               <option>Sporting Event</option>
//             </Form.Control>
//           </Form.Group>
//           <Form.Group as={Col} controlId="numberOfBusinesses">
//             <Form.Label>Number of businesses</Form.Label>
//             <Form.Control
//               type="text"
//               name="numberOfBusinesses"
//               required
//               onChange={(e) => {
//                 formChangeHandler(e);
//               }}
//               value={formValue.numberOfBusinesses}
//             />
//           </Form.Group>
//         </Row>

//         <h2 className="fs-title" style={{ marginTop: "40px" }}>
//           How do you want to recieve your orders?
//         </h2>

//         <Row style={{ paddingLeft: "5px", paddingRight: "15px" }}>
//           <h5
//             className="fs-subtitle"
//             style={{
//               paddingLeft: "15px",
//               paddingRight: "5px",
//             }}
//           >
//             Choose how to recieve your orders. We highly reccomend the tablet
//             solution to maximize your business' efficieny in fulfilling orders.
//           </h5>
//           <Card>
//             <Card.Body>
//               <Row>
//                 <Col xs={2}>
//                   <Form.Check
//                     type="radio"
//                     label=""
//                     name="tablet"
//                     id="formHorizontalRadios2"
//                     onClick={() => {
//                       console.log("tablet true");

//                       setTablet(true);
//                     }}
//                   />
//                 </Col>
//                 <Col xs={10}>
//                   <Form.Label>Tablet (Highly Reccomended)</Form.Label>
//                   <Card.Text
//                     className="text-muted"
//                     style={{
//                       textIndent: "0",
//                       textAlign: "left",
//                       fontSize: "13px",
//                       fontWeight: "bold",
//                     }}
//                   >
//                     $0 for 30 days, then $5/month without cell service, or
//                     $15/month with cell service
//                   </Card.Text>

//                   <Card.Text
//                     className="text-muted"
//                     style={{
//                       textIndent: "0",
//                       textAlign: "left",
//                       fontSize: "12px",
//                       fontWeight: "bolder",
//                     }}
//                   >
//                     Your orders will be sent to your tablet for convenience and
//                     efficiency.
//                   </Card.Text>
//                 </Col>
//               </Row>
//             </Card.Body>
//           </Card>
//         </Row>
//         <Row style={{ paddingLeft: "5px", paddingRight: "15px" }}>
//           <Card>
//             <Card.Body>
//               <Row>
//                 <Col xs={2}>
//                   <Form.Check
//                     type="radio"
//                     label=""
//                     name="tablet"
//                     id="formHorizontalRadios2"
//                     onClick={() => {
//                       console.log("tablet false");
//                       setTablet(false);
//                     }}
//                   />
//                 </Col>
//                 <Col xs={10}>
//                   <Form.Label>Email + Phone Confirmation</Form.Label>
//                   <Card.Text
//                     className="text-muted"
//                     style={{
//                       textIndent: "0",
//                       textAlign: "left",
//                       fontSize: "13px",
//                       fontWeight: "bold",
//                     }}
//                   >
//                     $0
//                   </Card.Text>

//                   <Card.Text
//                     className="text-muted"
//                     style={{
//                       textIndent: "0",
//                       textAlign: "left",
//                       fontSize: "12px",
//                       fontWeight: "bolder",
//                     }}
//                   >
//                     Your orders will be sent to your tablet for convenience and
//                     efficiency.
//                   </Card.Text>
//                 </Col>
//               </Row>
//             </Card.Body>
//           </Card>
//         </Row>
//         <Button
//           name="previous"
//           className="previous action-button"
//           required
//           onClick={() => {
//             props.onClick("previous");
//           }}
//         >
//           Previous
//         </Button>
//         <Button type="submit" name="next" className="next action-button">
//           Next
//         </Button>
//       </fieldset>
//     </Form>
//   );
// };
// const BusinessFieldset = (props) => {
//   const [formValue, setFormValue] = useReducer(
//     (state, newState) => ({ ...state, ...newState }),
//     {
//       name: "",
//       phoneNumber: "",
//       email: "",
//       address: "",
//       street: "",
//       suite: "",
//       city: "",
//       state: "",
//       zipcode: "",
//     }
//   );
//   const setAddress = (address) => {
//     if (address.split(",").length === 4) {
//       const addressObject = {};
//       addressObject.address = address;
//       const addressArray = address.split(",");
//       addressObject.street = addressArray[0];
//       addressObject.city = addressArray[1];
//       const stateZipcodeArray = addressArray[2].split(" ");
//       addressObject.state = stateZipcodeArray[1];
//       addressObject.zipcode = stateZipcodeArray[2];
//       setFormValue(addressObject);
//     }
//   };
//   const formChangeHandler = (event) => {
//     let name = event.target.name;
//     let value = event.target.value;
//     setFormValue({ [name]: value });
//   };

//   const handleSubmit = async (event, merchantStripeId) => {
//     event.preventDefault();
//     // the event target is the button that was clicked inside the payout setup component inside the business fieldset
//     const form = event.target.closest("form");
//     if (validate(form)) {
//       // set all the values for the business
//       // if the user comes back to this page before submitting to change stuff it will reset the values
//       const newBusiness = new Business();
//       newBusiness.name = formValue.name;
//       newBusiness.email = formValue.email;
//       newBusiness.phoneNumber = formValue.phoneNumber;
//       newBusiness.address = formValue.address;
//       newBusiness.street = formValue.street;
//       newBusiness.suite = formValue.suite;
//       newBusiness.city = formValue.city;
//       newBusiness.state = formValue.state;
//       newBusiness.zipcode = formValue.zipcode;
//       const result = await props.onSubmit(newBusiness, merchantStripeId);
//       console.log("result", result);
//       return result;
//     } else {
//       return false;
//     }
//   };
//   const validate = (form) => {
//     form.classList.add("was-validated");
//     return form.checkValidity();
//   };
//   return (
//     <Form autoComplete="off">
//       <fieldset>
//         <h2 className="fs-title">Your Business</h2>
//         <Form.Label>Name</Form.Label>
//         <Form.Control
//           type="text"
//           className="mb-3"
//           name="name"
//           placeholder="Business Name"
//           value={formValue.name}
//           required
//           onChange={(e) => {
//             formChangeHandler(e);
//           }}
//         />
//         <Form.Label>Phone Number</Form.Label>
//         <Form.Control
//           type="tel"
//           name="phoneNumber"
//           className="mb-3"
//           required
//           pattern="[0-9]{10}"
//           placeholder="5128999160"
//           value={formValue.phoneNumber}
//           onChange={(e) => {
//             formChangeHandler(e);
//           }}
//         />
//         <Form.Label>Address</Form.Label>
//         <SearchLocationInput onUpdate={(address) => setAddress(address)} />
//         <Row>
//           <Col
//             sm={12}
//             id="payoutSetup"
//             style={{ justifyContent: "center", display: "flex" }}
//           >
//             <PayoutSetup
//               onSubmit={(event, merchantStripeId, redirect) =>
//                 handleSubmit(event, merchantStripeId, redirect)
//               }
//             ></PayoutSetup>
//           </Col>
//         </Row>
//         <Row style={{ justifyContent: "space-around" }}>
//           <Form.Control
//             type="button"
//             name="previous"
//             className="previous action-button"
//             value="Previous"
//             onClick={() => {
//               props.onClick("previous");
//             }}
//           />
//         </Row>
//       </fieldset>
//     </Form>
//   );
// };

const Signin = () => {
  const [merchant, setMerchant] = useState(null);
  const [business, setBusiness] = useState(null);
  const [redirect, setRedirect] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
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

  const onSubmit = (event) => {
    event.preventDefault();
    const form = event.target;
    if (validate(form)) {
      API.makeRequest("POST", "/validate-merchant", authorization).then(
        (response) => {
          if (response) {
            // if the username is available the response from the API will be true
            setRedirect("/home");
          } else {
            const newErrorMsgState = {};
            // otherwise it will be false
            newErrorMsgState["errorMsg"] =
              "Invalid username or password, please try again";
            newErrorMsgState["errorDisplay"] = "inline-block";
            setErrorMsg(newErrorMsgState);
            return false;
          }
        }
      );
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
                  type="text"
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
export default Signin;
