import Button from "@material-ui/core/Button";
import React, { useState, useReducer } from "react";
import { TextField } from "@material-ui/core";
import Form from "react-bootstrap/Form";
import API from "../../helpers/Api.js";
import { makeStyles } from "@material-ui/core/styles";
import Title from "../dashboard/Title";
import Paper from "@material-ui/core/Paper";
import Grid from "@material-ui/core/Grid";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const MenuBuilder = () => {
  const useStyles = makeStyles((theme) => ({
    root: {
      width: "100vw",
    },
    paper: {
      padding: theme.spacing(2),
      textAlign: "center",
      color: theme.palette.text.secondary,
    },
    content: {
      flexGrow: 1,
      height: "100vh",
      overflow: "auto",
    },
  }));

  const classes = useStyles();

  const [isSpinning, setIsSpinning] = useState(null);
  const Spinner = () => (
    <FontAwesomeIcon icon={faSpinner} className="fa-spin" />
  );

  var businessId = "";
  const updateBusinessId = (newBusinessId) => {
    businessId = newBusinessId;
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };
  const handleSubmit = async (event, formValues) => {
    // for (var pair of formValues.entries()) {
    //   console.log(pair[0] + ", " + pair[1]);
    // }

    const form = event.target.closest("form");
    validate(form);
    if (validate(form)) {
      formValues.append("businessId", JSON.stringify(businessId));
      // set all the values for the business
      // if the user comes back to this page before submitting to change stuff it will reset the values
      let response = await API.makeRequest(
        "POST",
        "/menu",
        formValues,
        false,
        true
      );
      if (response.status !== 200) {
        alert("A server error occured. Tell Peter.");
      } else {
        alert("Menu successfully uploaded!");
        window.location.reload();
      }
    } else {
      alert(
        "Menu upload failed. Make sure you filled out the form correctly and your internet is working."
      );
      window.location.reload();
    }
  };
  const BusinessIdInput = (props) => {
    const [businessId, setbusinessId] = useState("");
    return (
      <Grid
        item
        xs={2}
        style={{
          textAlign: "center",
          marginBottom: "20px",
          marginTop: "20px",
          paddingLeft: "4vw",
        }}
      >
        <TextField
          fullWidth
          name="businessId"
          label="Business Id"
          multiline
          value={businessId}
          required
          onChange={(event) => {
            setbusinessId(event.target.value);
            props.updateBusinessId(event.target.value);
          }}
        />
      </Grid>
    );
  };
  const FormRow = (props) => {
    const [formValue, setFormValue] = useReducer(
      (state, newState) => ({ ...state, ...newState }),
      {
        drinkName: "",
        drinkDescription: "",
        drinkPrice: "",
        selectedFileName: "",
        selectedFile: "",
      }
    );
    const formChangeHandler = (event) => {
      if (event.target.name === "selectedFile") {
        const newFileObject = {
          selectedFile: event.target.files[0],
          selectedFileName: event.target.files[0].name,
        };
        setFormValue(newFileObject);
        const propsFileObject = {
          name: "selectedFile",
          value: event.target.files[0],
          index: props.k,
        };
        props.updateValue(propsFileObject);
      } else {
        let name = event.target.name;
        let value = event.target.value;
        setFormValue({ [name]: value });
        props.updateValue({ name: name, value: value, index: props.k });
      }
    };
    return (
      <Grid container item xs={11} spacing={0} justify="center" key={props.k}>
        <div className={classes.root}>
          <Grid
            key={props.k}
            item
            xs={12}
            style={{
              textAlign: "center",
              marginBottom: "20px",
              marginTop: "20px",
            }}
          ></Grid>
          <Grid container key={props.k + 2} item xs={12}>
            <Grid
              key={props.k}
              item
              xs={2}
              style={{ textAlign: "left", marginRight: "20px" }}
            >
              <TextField
                fullWidth
                required
                key={props.k}
                name="drinkName"
                label="Name"
                multiline
                value={formValue.drinkName}
                onChange={(event) => formChangeHandler(event)}
              />
            </Grid>
            <Grid key={props.k + 3} item xs={4} style={{ textAlign: "right" }}>
              <TextField
                fullWidth
                required
                key={props.k + 2}
                name="drinkDescription"
                label="Description"
                multiline
                value={formValue.drinkDescription}
                onChange={(event) => formChangeHandler(event)}
              />
            </Grid>
            <Grid key={props.k + 3} item xs={1}>
              <TextField
                required
                key={props.k + 3}
                style={{ textAlign: "left", marginLeft: "20px" }}
                name="drinkPrice"
                label="Price"
                type="number"
                value={formValue.drinkPrice}
                onChange={(event) => formChangeHandler(event)}
              />
            </Grid>
            <Grid
              item
              xs={1}
              key={props.k + 4}
              container
              direction="row"
              justify="center"
              alignItems="flex-end"
              style={{ marginLeft: "20px" }}
            >
              <p
                style={{
                  marginBottom: "0px",
                  marginRight: "5px",
                  fontWeight: "500",
                }}
              >
                Drink image
              </p>
            </Grid>
            <Grid
              item
              key={props.k + 5}
              xs={3}
              container
              direction="row"
              justify="flex-end"
              alignItems="flex-end"
            >
              <Form.File
                name="selectedFile"
                type="file"
                custom
                key={props.k + 6}
                style={{
                  fontFamily: "montserrat",
                  fontSize: "12px",
                  textColor: "black",
                  height: "4vh",
                  padding: "0",
                  textAlign: "left",
                }}
                onChange={(event) => formChangeHandler(event)}
                label={formValue.selectedFileName}
                noValidate
              />
            </Grid>
          </Grid>
        </div>
      </Grid>
    );
  };
  const BuildPage = (props) => {
    var formValues = {
      drinkName: [],
      drinkDescription: [],
      drinkPrice: [],
      selectedFile: [],
      selectedFileName: [],
    };
    const [numRows, setNumRows] = useState(1);
    const handleChangeNumRows = (newNumRows) => {
      if (newNumRows < 0) {
        return;
      }
      if (newNumRows < numRows) {
        const difference = numRows - newNumRows;
        for (var i = 0; i < difference; i++) {
          formValues.drinkName.pop();
          formValues.drinkDescription.pop();
          formValues.selectedFile.pop();
          formValues.selectedFileName.pop();
        }
      } else if (newNumRows > numRows) {
        const difference = newNumRows - numRows;
        for (var j = 0; j < difference; j++) {
          formValues.drinkName.push("");
          formValues.drinkDescription.pop("");
          formValues.selectedFile.pop("");
          formValues.selectedFileName.pop("");
        }
      }
      setNumRows(newNumRows);
      return;
    };
    // set initial values
    if (formValues.drinkName.length !== numRows) {
      for (let i = 0; i < numRows; i++) {
        formValues.drinkName.push("");
        formValues.drinkDescription.push("");
        formValues.selectedFile.push("");
        formValues.selectedFileName.push("");
      }
    }

    const formChangeHandler = (newValue) => {
      formValues[newValue.name][newValue.index] = newValue.value;
    };
    const formRowArray = [];
    for (let k = 0; k < numRows; k++) {
      formRowArray.push(
        <FormRow k={k} updateValue={(e) => formChangeHandler(e)}></FormRow>
      );
    }
    const handleSubmit = (event) => {
      const newForm = new FormData();
      Object.keys(formValues).forEach((key) => {
        if (key !== "selectedFile") {
          newForm.append(key, JSON.stringify(formValues[key]));
        } else {
          const newFileArray = [];
          for (var i = 0; i < formValues.selectedFile.length; i++) {
            if (formValues.selectedFile[i] !== "") {
              newFileArray.push(true);
            } else {
              newFileArray.push(false);
            }
          }
          newForm.append(String(key), JSON.stringify(newFileArray));

          formValues[key].forEach((value) => {
            if (value !== "") {
              newForm.append(String(key), value, value.fileName);
            }
          });
        }
      });
      props.onSubmit(event, newForm);
    };
    const RowNumTextField = () => {
      return (
        <Grid
          container
          item
          xs={1}
          spacing={0}
          style={{
            marginTop: "3vh",
            marginRight: "6vw",
            paddingRight: "3vw",
          }}
        >
          <TextField
            name="numRows"
            label="Rows"
            type="number"
            value={numRows}
            onChange={(event) => handleChangeNumRows(event.target.value)}
          />
        </Grid>
      );
    };
    const SubmitButton = (props) => {
      const [isDisabled, setIsDisabled] = useState(false);
      const handleSubmit = (event) => {
        setIsSpinning(true);
        setIsDisabled(!isDisabled);
        props.onClick(event);
      };

      return (
        <Grid
          container
          item
          xs={12}
          spacing={0}
          justify="center"
          style={{ marginTop: "3vh" }}
        >
          <Button
            onClick={(e) => handleSubmit(e)}
            disabled={props.isDisabled}
            style={{
              backgroundColor: "#8682E6",
              width: "15vw",
              fontWeight: "bold",
              fontSize: "1rem",
              marginBottom: "5vh",
            }}
          >
            {isSpinning ? <Spinner></Spinner> : "Submit"}
          </Button>
        </Grid>
      );
    };
    formRowArray.push(
      <SubmitButton onClick={(e) => handleSubmit(e)}></SubmitButton>
    );
    formRowArray.unshift(<RowNumTextField></RowNumTextField>);
    return formRowArray;
  };
  return (
    <Paper className={classes.content}>
      <form autoComplete="off">
        <Grid container spacing={2} direction="row" justify="center">
          <BusinessIdInput
            updateBusinessId={(newBusinessId) =>
              updateBusinessId(newBusinessId)
            }
          ></BusinessIdInput>
          <Grid
            container
            item
            xs={8}
            spacing={0}
            justify="center"
            style={{ marginTop: "3vh" }}
          >
            <Title>Menu Builder</Title>
          </Grid>
          <BuildPage
            onSubmit={(e, formValues) => handleSubmit(e, formValues)}
          ></BuildPage>
        </Grid>
      </form>
    </Paper>
  );
};
export default MenuBuilder;