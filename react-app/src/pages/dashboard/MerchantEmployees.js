import React, { useState, useReducer } from "react";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import IconButton from "@material-ui/core/IconButton";
import Paper from "@material-ui/core/Paper";
import Title from "./Title";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import { MerchantEmployee, LocalStorageManager } from "../../Models";
import { CSVLink } from "react-csv";
import { toCapitalizedWords } from "../../Models";
import PersonAddIcon from "@material-ui/icons/PersonAdd";
import Button from "@material-ui/core/Button";
import Modal from "@material-ui/core/Modal";
import Form from "react-bootstrap/Form";
import CheckIcon from "@material-ui/icons/Check";
import AccessTimeIcon from "@material-ui/icons/AccessTime";
import API from "../../helpers/Api.js";
import CloseIcon from "@material-ui/icons/Close";
import "../../css/Signup.css";
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
    backgroundColor: theme.palette.background.paper,
    border: "2px solid #000",
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
  },
}));

const MerchantEmployees = (props) => {
  const classes = useStyles();
  const [modalOpen, setModalOpen] = useState(false);
  const [formValue, setFormValue] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      email: "",
      merchantId: LocalStorageManager.shared.currentMerchant.id,
    }
  );
  const mappedMerchantEmployees = props.merchantEmployees.map(
    (merchantEmployeeJSON) => {
      return new MerchantEmployee(merchantEmployeeJSON);
    }
  );
  const [csvData, setCsvData] = useState(() => makeCSVData());
  const [errorMsg, setErrorMsg] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      emailErrorMsg: "",
      emailDisplay: "",
    }
  );

  const [isSpinning, setIsSpinning] = useState(null);
  const Spinner = () => (
    <FontAwesomeIcon icon={faSpinner} className="fa-spin" />
  );
  function makeCSVData() {
    const csvData = mappedMerchantEmployees.map((merchantEmployee) => {
      console.log("merchantEmployee", merchantEmployee);
      const merchantEmployeeData = [
        merchantEmployee.id,
        merchantEmployee.firstName,
        merchantEmployee.lastName,
        merchantEmployee.phoneNumber,
        merchantEmployee.loggedIn === true ? "yes" : "no",
        merchantEmployee.businessId,
      ];
      return merchantEmployeeData;
    });
    // add row headers
    csvData.unshift(
      Object.keys(mappedMerchantEmployees[0]).map((key) =>
        // if the key is "id" than we want to display an email label
        toCapitalizedWords(
          // the object keys are the objects private properties so we have to remove the underscores
          key === "id" ? "email" : key
        )
      )
    );
    return csvData;
  }

  const handleFormChange = (event) => {
    let name = event.target.name;
    let value = event.target.value;
    setFormValue({ [name]: value.trim().toLowerCase() });
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };
  const handleRemovePerson = (index) => {
    const stagedMerchantEmployeeToRemove = mappedMerchantEmployees[index];
    const data = { merchant_employee_id: stagedMerchantEmployeeToRemove.id };
    API.makeRequest(
      "PUT",
      `/merchant_employee/staging/${LocalStorageManager.shared.sessionToken}`,
      data
    ).then(() => {
      console.log("mappedMerchantEmployees", mappedMerchantEmployees);
      mappedMerchantEmployees.splice(index, 1);
      if (mappedMerchantEmployees.length === 0) {
        console.log("<1");
        // add a dummy merchantemployee to populate the row values if there are 0 merchantemployee objects left in the list
        const dummyMerchantEmployee = new MerchantEmployee();
        mappedMerchantEmployees.push(dummyMerchantEmployee);
      }
      console.log("mappedMerchantEmployees", mappedMerchantEmployees);
      props.onUpdate(mappedMerchantEmployees);
      setIsSpinning(false);
      return true;
    });
  };
  const handleAddPerson = (event) => {
    event.preventDefault();
    const form = event.target.closest("form");
    var newErrorMsgState = {};
    newErrorMsgState["emailDisplay"] = "none";
    if (validate(form)) {
      API.makeRequest(
        "GET",
        `/merchant_employee?merchant_employee_id=${formValue.email}`
      ).then((response) => {
        // the merchant employee username is not taken by either a real or staged merchant employee
        if (response.status === 200) {
          // create the merchant employee with a null parameter assigns pending to the status property of the staged merchant employee
          const newMerchantEmployee = new MerchantEmployee(null);
          newMerchantEmployee.id = formValue.email;

          formValue.merchantId = LocalStorageManager.shared.currentMerchant.id;
          API.makeRequest(
            "POST",
            `/merchant_employee/staging/${LocalStorageManager.shared.sessionToken}`,
            formValue
          ).then(() => {
            mappedMerchantEmployees.push(newMerchantEmployee);
            props.onUpdate(mappedMerchantEmployees);
            setCsvData(makeCSVData());
            setModalOpen((prevModalOpen) => !prevModalOpen);
            setErrorMsg(newErrorMsgState);
            setFormValue({ email: "" });
            setIsSpinning(false);
            return true;
          });

          // the requested username is already assigned to a staged merchant employee
        } else if (response.status === 204) {
          // otherwise it will be false
          newErrorMsgState["emailErrorMsg"] =
            "* Email already associated with a pending account";
          newErrorMsgState["emailDisplay"] = "inline-block";
          setErrorMsg(newErrorMsgState);
          setIsSpinning(false);
          return false;
        }
        // the requested username is already assigned to a real merchant employee
        else if (response.status === 400) {
          // otherwise it will be false
          newErrorMsgState["emailErrorMsg"] =
            "* Email already associated with a confirmed account";
          newErrorMsgState["emailDisplay"] = "inline-block";
          setErrorMsg(newErrorMsgState);
          setIsSpinning(false);
          return false;
        }
      });
    } else {
      setErrorMsg(newErrorMsgState);
    }
  };
  const emailErrorMsgStyle = {
    display: errorMsg ? errorMsg.emailDisplay : "none",
    textAlign: "left",
    marginTop: "0",
  };
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
        Add new employee
      </h4>

      <Form autoComplete="off">
        <fieldset>
          <Form.Label>Employee email</Form.Label>
          <div className="invalid-feedback" style={emailErrorMsgStyle}>
            {errorMsg.emailErrorMsg}
          </div>
          <Form.Control
            type="email"
            className="mb-3"
            name="email"
            placeholder="employee@gmail.com"
            value={formValue.email}
            required
            onChange={(e) => {
              handleFormChange(e);
            }}
          />
        </fieldset>
        <Button
          variant="contained"
          disabled={isSpinning}
          color="primary"
          style={{
            textAlign: "center",
            marginLeft: "47%",
            transform: "translateX(-47%)",
          }}
          onClick={(e) => {
            setIsSpinning(true);
            handleAddPerson(e);
          }}
        >
          {isSpinning ? <Spinner></Spinner> : "Submit"}
        </Button>
      </Form>
    </div>
  );
  if (mappedMerchantEmployees) {
    return (
      <TableContainer>
        <Paper className={props.classes.paper}>
          <Row style={{ width: "100%", height: "fit-content" }}>
            <Col xs={9}>
              <Title style={{ marginLeft: "auto", maxWidth: "15%" }}>
                Employees
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
                    <PersonAddIcon style={{ color: "#007bff" }} />
                  </IconButton>
                </TableCell>
                {Object.keys(mappedMerchantEmployees[0]).map((key, i) => (
                  <TableCell align="left" key={i + 1}>
                    {
                      // if the key is "id" than we want to display an email label
                      toCapitalizedWords(
                        // the object keys are the objects private properties so we have to remove the underscores
                        key === "id" ? "email" : key
                      )
                    }
                  </TableCell>
                ))}
                <TableCell>{""}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mappedMerchantEmployees[0].id !== "" ? (
                mappedMerchantEmployees.map((row, i) => (
                  <TableRow key={i}>
                    <TableCell>{i}</TableCell>
                    {Object.values(row).map((key, k) => (
                      <TableCell align="left" key={k}>
                        {key === true ? (
                          "yes"
                        ) : key === false ? (
                          "no"
                        ) : key === "confirmed" ? (
                          <CheckIcon style={{ color: "#00FF00" }} />
                        ) : key === "pending" ? (
                          <AccessTimeIcon style={{ color: "#FFC300" }} />
                        ) : (
                          key
                        )}
                      </TableCell>
                    ))}
                    {mappedMerchantEmployees[i].status === "pending" ? (
                      <TableCell align="right" key={-1}>
                        <IconButton
                          onClick={() => {
                            handleRemovePerson(i);
                          }}
                        >
                          <CloseIcon />
                        </IconButton>
                      </TableCell>
                    ) : (
                      <></>
                    )}
                  </TableRow>
                ))
              ) : (
                <></>
              )}
            </TableBody>
          </Table>
        </Paper>
      </TableContainer>
    );
  } else {
    return <></>;
  }
};
export default MerchantEmployees;
