import React, { useState, useReducer } from "react";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import Title from "./Title";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import { Business, LocalStorageManager } from "../../Models";
import { CSVLink } from "react-csv";
import { toCapitalizedWords } from "../../Models";
import CloseIcon from "@material-ui/icons/Close";
import IconButton from "@material-ui/core/IconButton";
import Button from "@material-ui/core/Button";
import Modal from "@material-ui/core/Modal";
import Form from "react-bootstrap/Form";
import API from "../../helpers/Api.js";
import AddIcon from "@material-ui/icons/Add";
import SearchLocationInput from "../../SearchLocationInput.js";
import "../../css/businesses.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";

const useStyles = makeStyles((theme) => ({
  table: {
    width: "100%",
  },
  paper: {
    padding: theme.spacing(2),
    display: "flex",
    overflow: "auto",
    flexDirection: "column",
    height: "115vh",
    maxHeight: "800px",
  },

  modal: {
    position: "absolute",
    left: "50%",
    top: "50%",
    transform: "translateY(-50%) translateX(-50%)",
    width: 400,
    display: "block",
    overflow: "scroll",
    backgroundColor: theme.palette.background.paper,
    border: "2px solid #000",
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
  },
  content: { position: "absolute", marginTop: "3vh" },
  buttonContent: { position: "relative" },
}));

const Businesses = (props) => {
  const classes = useStyles();
  const [mappedBusinesses, setMappedBusinesses] = useState(
    props.businesses.map((businessJSON) => {
      return new Business(businessJSON, true, false, true);
    })
  );
  const [csvData, setCsvData] = useState(() => makeCSVData());
  const [modalOpen, setModalOpen] = useState(false);
  const [isSpinning, setIsSpinning] = useState(null);

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
      menuUrl: "",
      classification: "bar",
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

  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [errorMsg, setErrorMsg] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      menuSubmittedErrorMsgDisplay: "none",
    }
  );
  const handleScheduleChange = (event) => {
    const name = event.target.name;
    const dayIndex = parseInt(name.split("-")[0]);
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
        newDateObject.openingTime = event.target.value;
        newDateObject.closingTime = prevSchedule[dayIndex].closingTime;
      } else if (isOpenOrClosed === "closing") {
        newDateObject.closingTime = event.target.value;
        newDateObject.openingTime = prevSchedule[dayIndex].openingTime;
      }
      // creating new object makes setState func work for some reason
      const newSchedule = prevSchedule.map((a) => ({ ...a }));
      newSchedule[dayIndex] = newDateObject;
      return newSchedule;
    });
  };
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

  const onFileChange = (event) => {
    console.log("event", event);
    // Update the state
    console.log("event.target.files[0]", event.target.files[0].name);
    console.log("event.target.files", event.target.files);
    setSelectedFile(event.target.files[0]);
    setSelectedFileName(event.target.files[0].name);
  };
  const handleFormChange = (event) => {
    let name = event.target.name;
    let value = event.target.value;
    if (typeof value === "string" && name !== "name") {
      setFormValue({ [name]: value.trim().toLowerCase() });
    } else {
      setFormValue({ [name]: value });
    }
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };
  const handleAddBusiness = (event) => {
    // api call here
    event.preventDefault();
    const form = event.target.closest("form");
    console.log("form", form);
    if (validate(form)) {
      if (!(formValue.menuUrl || selectedFile)) {
        const newErrorMsgState = {};
        newErrorMsgState["menuSubmittedErrorMsg"] =
          "* Please upload your menu and or submit a link to it";
        newErrorMsgState["menuSubmittedErrorMsgDisplay"] = "inline-block";
        setErrorMsg(newErrorMsgState);
        return false;
      }
      const copyOfFormValue = { ...formValue };
      copyOfFormValue.schedule = schedule;
      const newBusiness = new Business(copyOfFormValue);
      newBusiness.menuUrl = copyOfFormValue.menuUrl;
      newBusiness.merchantId = LocalStorageManager.shared.currentMerchant.id;
      newBusiness.merchantStripeId =
        LocalStorageManager.shared.currentMerchant.stripeId;
      const newForm = new FormData();
      newForm.append("business", JSON.stringify(newBusiness));
      if (selectedFile && selectedFileName) {
        newForm.append("file", selectedFile, selectedFileName);
      }
      API.makeRequest(
        "POST",
        `/business/${LocalStorageManager.shared.sessionToken}`,
        newForm,
        false, // no headers
        true // it is a form
      ).then((response) => {
        if (response.status === 200) {
          const confirmedNewBusiness = new Business(
            response.confirmed_new_business,
            true,
            false,
            true
          );
          const newMappedBusinesses = [];
          setMappedBusinesses((prevMapppedBusinesses) => {
            // if the merchant had 0 employees then the mappedEmployees array will have 1 single dummy merchant employee. so we want to remove this once a real merchant emplyee is added
            if (prevMapppedBusinesses[0].id === "") {
              newMappedBusinesses.unshift(confirmedNewBusiness);
            } else {
              for (var i in prevMapppedBusinesses) {
                newMappedBusinesses.push(prevMapppedBusinesses[i]);
              }
              newMappedBusinesses.unshift(confirmedNewBusiness);
            }
            return newMappedBusinesses;
          });
          setCsvData(makeCSVData());
          props.onUpdate(newMappedBusinesses);
          setModalOpen((prevModalOpen) => !prevModalOpen);
          setFormValue({
            name: "",
            phoneNumber: "",
            address: "",
            street: "",
            suite: "",
            city: "",
            state: "",
            zipcode: "",
            menuUrl: "",
            classification: "bar",
            schedule: [],
          });
          setIsSpinning(false)
          return true;
        } else {
          return false;
        }
      });
    } else {
      return false;
    }
  };
  function makeCSVData() {
    const csvData = mappedBusinesses.map((business) => {
      const businessData = [];
      Object.values(business).forEach((value) => {
        switch (value) {
          case value === true:
            businessData.push("yes");
            break;
          default:
            businessData.push(value);
            break;
        }
      });
      return businessData;
    });

    // add row headers
    csvData.unshift(
      Object.keys(mappedBusinesses[0]).map((key) =>
        toCapitalizedWords(
          // the object keys are the objects private properties so we have to remove the underscores
          key.replace("_", "")
        )
      )
    );
    return csvData;
  }
  const menuSubmittedErrorMsgStyle = {
    display: errorMsg.menuSubmittedErrorMsgDisplay,
    textAlign: "left",
    marginTop: "0",
  };
  const Spinner = () => (
    <FontAwesomeIcon icon={faSpinner} className="fa-spin" />
  );
  const daysOfWeek = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
  ];
  const modalBody = (
    <div className={classes.modal}>
      <Row style={{ display: "flex", margin: 0, justifyContent: "flex-end" }}>
        <IconButton
          onClick={() => {
            setModalOpen((prevModalOpen) => !prevModalOpen);
          }}
        >
          <CloseIcon style={{ marginLeft: "auto" }} />
        </IconButton>
      </Row>
      <h4 style={{ marginBottom: "10%", textAlign: "center" }}>
        Add new business
      </h4>

      <Form autoComplete="off">
        <fieldset>
          <Form.Label>Address</Form.Label>
          <SearchLocationInput onUpdate={(address) => setAddress(address)} />
          <Form.Label>Name</Form.Label>
          <Form.Control
            type="text"
            className="mb-3"
            name="name"
            placeholder="Business Name"
            value={formValue.name}
            required
            onChange={(e) => {
              handleFormChange(e);
            }}
          />
          <Form.Label>Phone Number</Form.Label>
          <Form.Control
            type="tel"
            name="phoneNumber"
            className="mb-3"
            required
            pattern="[0-9]{10}"
            placeholder="5128999160"
            value={formValue.phoneNumber}
            onChange={(e) => {
              handleFormChange(e);
            }}
          />
          <Form.Label>Type of business</Form.Label>
          <Form.Control
            as="select"
            required
            custom
            name="classification"
            onChange={(event) => handleFormChange(event)}
          >
            <option>Bar</option>
            <option>Restaurant</option>
            <option>Club</option>
            <option>Music Festival</option>
            <option>Sporting Event</option>
          </Form.Control>
          <Form.Label style={{ marginTop: "5%" }}>
            Upload a link, image, PDF, or any other file with your menu!
          </Form.Label>
          <div className="invalid-feedback" style={menuSubmittedErrorMsgStyle}>
            {errorMsg.menuSubmittedErrorMsg}
          </div>
          <Form.Control
            type="url"
            name="menuUrl"
            placeholder="https://yourwebsite.com"
            onChange={(e) => {
              handleFormChange(e);
            }}
            value={formValue.menuUrl}
            noValidate
            // required={formValue.selectedFile ? false : true}
          />
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

          <div className={classes.content}>
            <Row>
              <Col
                xs={12}
                style={{ display: "flex", justifyContent: "center" }}
              >
                <Form.Label>
                  Last step! Please fill out your business' weekly operating
                  hours below
                </Form.Label>
              </Col>
            </Row>
            <>
              {daysOfWeek.map((day, i) => (
                <div key={i + "-div"}>
                  <Row key={i + "-day-row"}>
                    <Col
                      key={i + "-day-col"}
                      xs={12}
                      style={{ display: "flex", justifyContent: "center" }}
                    >
                      <Form.Label style={{ fontWeight: "bold" }}>
                        {toCapitalizedWords(day)}
                      </Form.Label>
                    </Col>
                  </Row>

                  <Form.Label>Closed all day</Form.Label>
                  <Row
                    key={"row" + i}
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
                        onChange={(e) => {
                          handleScheduleChange(e);
                        }}
                      />
                    </Col>
                  </Row>
                  <Row>
                    <Col style={{ display: "flex" }} xs={12}>
                      <Col xs={6} style={{ padding: "0" }}>
                        <Form.Label>Opening time</Form.Label>

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
                          onChange={(e) => {
                            handleScheduleChange(e);
                          }}
                        />
                      </Col>
                      <Col xs={6}>
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
                          onChange={(e) => {
                            handleScheduleChange(e);
                          }}
                        />
                      </Col>
                    </Col>
                  </Row>
                </div>
              ))}
            </>

            <div className={classes.buttonContent}>
              <Button
                variant="contained"
                color="primary"
                disabled={isSpinning}
                style={{
                  textAlign: "center",
                  marginLeft: "47%",
                  position: "absolute",
                  transform: "translateX(-47%)",
                }}
                onClick={(e) => {
                  setIsSpinning(true);
                  handleAddBusiness(e);
                }}
              >
                {isSpinning ? <Spinner></Spinner> : "Submit"}
              </Button>
            </div>
          </div>
        </fieldset>
      </Form>
    </div>
  );
  if (mappedBusinesses) {
    return (
      <TableContainer>
        <Paper className={props.classes.paper}>
          <Row style={{ width: "100%", height: "fit-content" }}>
            <Col xs={9}>
              <Title style={{ marginLeft: "auto", maxWidth: "15%" }}>
                Businesses
              </Title>
            </Col>
            <Col
              xs={3}
              style={{
                display: "flex",
                justifyContent: "right",
                marginBottom: "0.35em",
              }}
            >
              <CSVLink data={csvData} style={{ marginLeft: "auto" }}>
                Export Data
              </CSVLink>
            </Col>
          </Row>
          <Modal
            open={modalOpen}
            scrollable={true}
            aria-labelledby="simple-modal-title"
            aria-describedby="simple-modal-description"
          >
            {modalBody}
          </Modal>
          <Table className={classes.table} aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell align="left" style={{ paddingLeft: "0" }} key={0}>
                  <IconButton
                    onClick={() => {
                      setModalOpen((prevModalOpen) => !prevModalOpen);
                    }}
                  >
                    <AddIcon style={{ color: "#007bff" }} />
                  </IconButton>
                </TableCell>
                {Object.keys(mappedBusinesses[0]).map((key, i) => (
                  <TableCell align="left" key={i}>
                    {toCapitalizedWords(
                      // the object keys are the objects private properties so we have to remove the underscores
                      key.replace("_", "")
                    )}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {mappedBusinesses.map((business, i) => (
                <TableRow key={business.id}>
                  <TableCell>{i}</TableCell>
                  {Object.values(business).map((value, i) => (
                    <TableCell align="left" key={i}>
                      {typeof value === "string"
                        ? value.replace("_", "")
                        : value === true
                        ? "yes"
                        : value}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </TableContainer>
    );
  } else {
    return <></>;
  }
};
export default Businesses;
