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
import { Bouncer, LocalStorageManager } from "../../Models";
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

const Bouncers = (props) => {
  const classes = useStyles();
  const [modalOpen, setModalOpen] = useState(false);
  const [formValue, setFormValue] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      id: "",
      firstName: "",
      lastName: "",
      businessId: "",
      merchantId: LocalStorageManager.shared.currentMerchant.id,
      status: "pending",
    }
  );
  const rowHeaders = new Bouncer();

  const [mappedBouncers, setMappedBouncers] = useState(
    props.bouncers.map((bouncerJSON) => {
      return new Bouncer(bouncerJSON, false);
    })
  );
  const [csvData, setCsvData] = useState(() => makeCSVData());
  const [errorMsg, setErrorMsg] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      emailErrorMsg: "",
      emailDisplay: "",
    }
  );

  function makeCSVData() {
    const csvData = mappedBouncers.map((bouncer) => {
      const bouncerData = [
        bouncer.id,
        bouncer.firstName,
        bouncer.lastName,
        bouncer.loggedIn === true ? "yes" : "no",
        bouncer.businessId,
      ];
      return bouncerData;
    });
    // add row headers
    csvData.unshift(
      Object.keys(rowHeaders).map((key) =>
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
    const stagedBouncerToRemove = mappedBouncers[index];
    const data = { bouncer_id: stagedBouncerToRemove.id };
    API.makeRequest(
      "PUT",
      `/bouncer/staging/${LocalStorageManager.shared.sessionToken}`,
      data
    ).then(
      setMappedBouncers((prevMapppedBouncers) => {
        prevMapppedBouncers.splice(index, 1);
        const newMappedBouncers = [];
        for (var i in prevMapppedBouncers) {
          newMappedBouncers.push(prevMapppedBouncers[i]);
        }
        return newMappedBouncers;
      })
    );
  };
  const handleAddPerson = (event) => {
    event.preventDefault();
    const form = event.target.closest("form");
    var newErrorMsgState = {};

    newErrorMsgState["emailDisplay"] = "none";
    if (validate(form)) {
      API.makeRequest(
        "GET",
        `/bouncer/validate?bouncer_id=${formValue.id}`
      ).then((response) => {
        // the merchant bouncer username is not taken by either a real or staged merchant bouncer
        if (response.status === 200) {
          // create the merchant bouncer with a null parameter assigns pending to the status property of the staged merchant bouncer
          const newBouncer = new Bouncer(formValue, true);
          API.makeRequest(
            "POST",
            `/bouncer/staging/${LocalStorageManager.shared.sessionToken}`,
            newBouncer
          );
          setMappedBouncers((prevMapppedBouncers) => {
            // if the merchant had 0 bouncers then the mappedBouncers array will have 1 single dummy merchant bouncer. so we want to remove this once a real merchant emplyee is added
            if (prevMapppedBouncers[0].id === "") {
              const newMappedBouncers = [];
              newMappedBouncers.unshift(newBouncer);
              return newMappedBouncers;
            } else {
              prevMapppedBouncers.unshift(newBouncer);
              return prevMapppedBouncers;
            }
          });
          setCsvData(makeCSVData());
          setModalOpen((prevModalOpen) => !prevModalOpen);
          setErrorMsg(newErrorMsgState);
          return true;
          // the requested username is already assigned to a staged merchant bouncer
        } else if (response.status === 204) {
          // otherwise it will be false
          newErrorMsgState["emailErrorMsg"] =
            "* Email already associated with a pending account";
          newErrorMsgState["emailDisplay"] = "inline-block";
          setErrorMsg(newErrorMsgState);
          return false;
        }
        // the requested username is already assigned to a real merchant bouncer
        else if (response.status === 400) {
          // otherwise it will be false
          newErrorMsgState["emailErrorMsg"] =
            "* Email already associated with a confirmed account";
          newErrorMsgState["emailDisplay"] = "inline-block";
          setErrorMsg(newErrorMsgState);
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
        Add new bouncer
      </h4>

      <Form autoComplete="off">
        <fieldset>
          <Form.Label>Email</Form.Label>
          <div className="invalid-feedback" style={emailErrorMsgStyle}>
            {errorMsg.emailErrorMsg}
          </div>
          <Form.Control
            type="email"
            className="mb-3"
            name="id"
            placeholder="bouncer@gmail.com"
            value={formValue.id}
            required
            onChange={(e) => {
              handleFormChange(e);
            }}
          />
          <Form.Label>First name</Form.Label>
          <Form.Control
            type="text"
            className="mb-3"
            name="firstName"
            placeholder="Robert"
            value={formValue.firstName}
            required
            onChange={(e) => {
              handleFormChange(e);
            }}
          />
          <Form.Label>Last name</Form.Label>
          <Form.Control
            type="text"
            className="mb-3"
            name="lastName"
            placeholder="Smith"
            value={formValue.lastName}
            required
            onChange={(e) => {
              handleFormChange(e);
            }}
          />
          <Form.Label>Business id</Form.Label>
          <Form.Control
            type="text"
            className="mb-3"
            name="businessId"
            placeholder="adfidijfvigf"
            value={formValue.businessid}
            required
            onChange={(e) => {
              handleFormChange(e);
            }}
          />
        </fieldset>
        <Button
          variant="contained"
          color="primary"
          style={{
            textAlign: "center",
            marginLeft: "47%",
            transform: "translateX(-47%)",
          }}
          onClick={(e) => {
            handleAddPerson(e);
          }}
        >
          Submit
        </Button>
      </Form>
    </div>
  );
  if (mappedBouncers) {
    return (
      <TableContainer>
        <Paper className={props.classes.paper}>
          <Row style={{ width: "100%", height: "fit-content" }}>
            <Col xs={9}>
              <Title style={{ marginLeft: "auto", maxWidth: "15%" }}>
                Bouncers
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
                {Object.keys(rowHeaders).map((key, i) => (
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
              {mappedBouncers.length > 0 ? (
                mappedBouncers.map((row, i) => (
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
                    {mappedBouncers[i].status === "pending" ? (
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
export default Bouncers;
