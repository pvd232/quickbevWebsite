import Button from "@material-ui/core/Button";
import React, { useState, useReducer, useEffect } from "react";
import { capitalize, TextField } from "@material-ui/core";
import Form from "react-bootstrap/Form";
import API from "../../helpers/Api.js";
import { makeStyles } from "@material-ui/core/styles";
import Title from "../dashboard/Title";
import Paper from "@material-ui/core/Paper";
import Grid from "@material-ui/core/Grid";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { LocalStorageManager } from "../../Models.js";

const MenuBuilder = (props) => {
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
  const [redirect, setRedirect] = useState(null);

  useEffect(() => {
    //had to do this because memory leak due to component not unmounting properly
    let mount = true;
    if (mount && redirect) {
      window.location.assign(redirect);
    }

    return () => (mount = false);
  }, [redirect]);
  const classes = useStyles();

  const businessId = LocalStorageManager.shared.menuBuilderBusinessId;
  const [isSpinning, setIsSpinning] = useState(null);
  const Spinner = () => (
    <FontAwesomeIcon icon={faSpinner} className="fa-spin" />
  );

  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };
  const handleSubmit = async (event, formValues) => {
    const form = event.target.closest("form");
    validate(form);
    if (validate(form)) {
      formValues.append("businessId", JSON.stringify(businessId));
      // set all the values for the business
      // if the user comes back to this page before submitting to change stuff it will reset the values
      const response = await API.makeRequest(
        "POST",
        `/drink/${LocalStorageManager.shared.sessionToken}`,
        formValues,
        false,
        true
      );

      if (!response) {
        alert(
          "A server error occured. We are currently working on a solution."
        );
      } else {
        alert("Menu successfully uploaded!");
      }
    } else {
      alert(
        "Upload failed due to missing menu data. Please fill out all the required form values."
      );
    }
    setRedirect("/home");
  };
  const BusinessIdInput = (props) => {
    const [businessId, setbusinessId] = useState(props.businessId);
    return (
      <Grid
        item
        xs={2}
        style={{
          textAlign: "center",
          marginBottom: "20px",
          marginTop: "20px",
          paddingLeft: "2.3vw",
        }}
        key={"grid-3"}
      >
        <TextField
          fullWidth
          name="businessId"
          label="Business Id"
          multiline
          value={businessId}
          required
          key={"grid-4"}
          onChange={(event) => {
            const businessId = event.target.value.trimStart().trimEnd();
            setbusinessId(businessId);
            props.updateBusinessId(businessId);
          }}
          disabled={true}
        />
      </Grid>
    );
  };
  const FormRow = (props) => {
    const [formValue, setFormValue] = useReducer(
      (state, newState) => ({ ...state, ...newState }),
      {
        drinkName: "",
        drinkCategory: "beer",
        drinkDescription: "",
        drinkPrice: "",
        selectedFileName: "",
        selectedFile: "",
      }
    );
    useEffect(() => {
      // for some reason formValues gets reset when changing numRows, but the values in the rows are cached, so need to send the values back up the formValues
      props.updateValue({
        name: "drinkName",
        value: formValue.drinkName,
        index: props.k,
      });
      props.updateValue({
        name: "drinkCategory",
        value: formValue.drinkCategory,
        index: props.k,
      });
      props.updateValue({
        name: "drinkDescription",
        value: formValue.drinkDescription,
        index: props.k,
      });
      props.updateValue({
        name: "drinkPrice",
        value: formValue.drinkPrice,
        index: props.k,
      });
      props.updateValue({
        name: "selectedFile",
        value: formValue.selectedFile,
        index: props.k,
      });
      props.updateValue({
        name: "selectedFileName",
        value: formValue.selectedFileName,
        index: props.k,
      });
    });
    const formChangeHandler = (event) => {
      if (event.target.name === "selectedFile") {
        const newFileObject = {
          selectedFile: event.target.files[0],
          selectedFileName: event.target.files[0].name.replace(/ /g, "-"),
        };
        setFormValue(newFileObject);
        const propsFileObject = {
          name: "selectedFile",
          value: event.target.files[0],
          index: props.k,
        };
        props.updateValue(propsFileObject);
      } else if (event.target.name === "drinkName") {
        let name = event.target.name;

        const drinkNameArray = event.target.value.split(" ");
        if (drinkNameArray.length > 0) {
          const newDrinkNameArray = [];
          for (const drinkNameFragment of drinkNameArray) {
            const lowerCaseName = drinkNameFragment.toLowerCase();
            newDrinkNameArray.push(lowerCaseName);
          }
          const newDrinkName = newDrinkNameArray.join(" ");
          setFormValue({ [name]: newDrinkName });
          props.updateValue({
            name: name,
            value: newDrinkName,
            index: props.k,
          });
        } else {
          let name = event.target.name;
          let value = event.target.value.toLowerCase();
          setFormValue({ [name]: value });
          props.updateValue({ name: name, value: value, index: props.k });
        }
      } else if (event.target.name === "drinkCategory") {
        let name = event.target.name;
        let value = event.target.value.toLowerCase();
        setFormValue({ [name]: value });
        props.updateValue({ name: name, value: value, index: props.k });
      } else {
        let name = event.target.name;
        let value = event.target.value;
        setFormValue({ [name]: value });
        props.updateValue({ name: name, value: value, index: props.k });
      }
    };
    return (
      <Grid
        container
        item
        xs={11}
        spacing={0}
        justifyContent="center"
        key={"grid-1-" + props.k}
        style={{ marginLeft: "auto", marginRight: "auto" }}
      >
        <div className={classes.root} key={"asdf-" + props.k}>
          <Grid
            key={"grid-1-1-" + props.k}
            item
            xs={12}
            justifyContent="center"
            style={{
              marginBottom: "20px",
              marginTop: "20px",
            }}
          ></Grid>
          <Grid container key={"grid-2-" + props.k} item xs={12}>
            <Grid
              key={"grid-1-1-1-" + props.k}
              item
              xs={2}
              style={{ textAlign: "left", marginRight: "0px" }}
            >
              <TextField
                fullWidth
                required
                key={"textField-1-" + props.k}
                name="drinkName"
                label="Name"
                multiline
                value={formValue.drinkName}
                onChange={(event) => formChangeHandler(event)}
              />
            </Grid>
            <Grid
              item
              xs={1}
              key={"grid-1-1-1-1-1-1--1--2" + props.k}
              container
              direction="row"
              justifyContent="center"
              alignItems="flex-end"
              style={{ marginLeft: "0px" }}
            >
              <p
                style={{
                  marginBottom: "10px",
                  marginRight: "0px",
                  fontWeight: "500",
                }}
                key={"p-1-a-" + props.k}
              >
                Category
              </p>
            </Grid>

            <Grid
              key={"grid-1-1--1-1-1-1-1" + props.k}
              item
              xs={1}
              style={{
                textAlign: "left",
                marginRight: "20px",
                marginTop: "10px",
              }}
            >
              <Form.Control
                as="select"
                required
                custom
                key={"grid-1-1-1-1-1--1-1-1" + props.k}
                name="drinkCategory"
                onChange={(event) => formChangeHandler(event)}
                style={{
                  paddingLeft: "15px",
                  paddingRight: "0",
                  paddingTop: "0",
                  paddingBottom: "0",
                }}
              >
                {LocalStorageManager.shared.drinkCategories.map(
                  (drinkCategory) => {
                    return <option>{capitalize(drinkCategory.id)}</option>;
                  }
                )}
              </Form.Control>
            </Grid>
            <Grid
              key={"grid-1-1-1-1-" + props.k}
              item
              xs={3}
              style={{ textAlign: "right" }}
            >
              <TextField
                fullWidth
                required
                key={"textField-1-1-" + props.k}
                name="drinkDescription"
                label="Description"
                multiline
                value={formValue.drinkDescription}
                onChange={(event) => formChangeHandler(event)}
              />
            </Grid>
            <Grid key={"grid-1-1-1-1-1-" + props.k} item xs={1}>
              <TextField
                required
                key={"textField-1-1-1-" + props.k}
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
              key={"grid-1-1-1-1-1-1-" + props.k}
              container
              direction="row"
              justifyContent="center"
              alignItems="flex-end"
              style={{ marginLeft: "20px" }}
            >
              <p
                style={{
                  marginBottom: "10px",
                  marginRight: "5px",
                  fontWeight: "500",
                }}
                key={"p-1-" + props.k}
              >
                Drink image
              </p>
            </Grid>
            <Grid
              item
              key={"grid-1-1-1-1-1-1-1-" + props.k}
              xs={2}
              container
              direction="row"
              justifyContent="flex-end"
              alignItems="flex-end"
            >
              <Form.File
                name="selectedFile"
                type="file"
                custom
                key={"grid-1-1-1-1-1-1-1-1-" + props.k}
                style={{
                  fontFamily: "montserrat",
                  fontSize: "12px",
                  textColor: "black",
                  height: "4vh",
                  padding: "0",
                  textAlign: "left",
                  marginTop: "15px",
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
    const formValues = {
      drinkName: [],
      drinkCategory: [],
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
          formValues.drinkCategory.pop();
          formValues.drinkDescription.pop();
          formValues.drinkPrice.pop();
          formValues.selectedFile.pop();
          formValues.selectedFileName.pop();
        }
      } else if (newNumRows > numRows) {
        const difference = newNumRows - numRows;
        for (var j = 0; j < difference; j++) {
          formValues.drinkName.push("");
          formValues.drinkCategory.push("");
          formValues.drinkDescription.push("");
          formValues.drinkPrice.push("");
          formValues.selectedFile.push("");
          formValues.selectedFileName.push("");
        }
      }
      setNumRows(newNumRows);
      return;
    };
    // set initial values
    if (numRows === 1) {
      for (let i = 0; i < numRows; i++) {
        formValues.drinkName.push("");
        formValues.drinkCategory.push("beer");
        formValues.drinkDescription.push("");
        formValues.drinkPrice.push("");
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
        <FormRow
          k={k}
          updateValue={(e) => formChangeHandler(e)}
          key={"formRow-" + k}
        ></FormRow>
      );
    }
    const handleSubmit = (event) => {
      const newForm = new FormData();
      console.log("formValues", formValues);
      Object.keys(formValues).forEach((key) => {
        if (key !== "selectedFile") {
          newForm.append(key, JSON.stringify(formValues[key]));
        } else {
          const newFileArray = [];
          for (var i = 0; i < formValues.selectedFile.length; i++) {
            // this is a boolean flag that tells the backend if there is a photo associated with the drink, super jank and should replace it in the future
            if (formValues.selectedFile[i] !== "") {
              newFileArray.push(true);
            } else {
              newFileArray.push(false);
            }
          }
          newForm.append(String(key), JSON.stringify(newFileArray));
          var j = 0;
          formValues[key].forEach((value) => {
            // because of the third parameter this flags that the value is a form value
            if (value !== "") {
              newForm.append(
                String(key),
                value,
                formValues.selectedFileName[j]
              );
            }
            j = j + 1;
          });
        }
      });
      props.onSubmit(event, newForm);
    };
    const RowNumTextField = () => {
      return (
        <Grid
          key={"grid-3-3"}
          container
          item
          xs={1}
          spacing={0}
          style={{
            marginTop: "3vh",
            marginRight: "4vw",
            paddingRight: "3vw",
          }}
        >
          <TextField
            key={"textField-3-4"}
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
          key={"1-11-1"}
          xs={12}
          spacing={0}
          justifyContent="center"
          style={{ marginTop: "3vh", justifyContent: "center" }}
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
            key={"buttonasdf"}
          >
            {isSpinning ? <Spinner></Spinner> : "Submit"}
          </Button>
        </Grid>
      );
    };
    formRowArray.push(
      <SubmitButton
        onClick={(e) => handleSubmit(e)}
        key={"asdfzzz"}
      ></SubmitButton>
    );
    formRowArray.unshift(<RowNumTextField key={"ccc"}></RowNumTextField>);
    return formRowArray;
  };
  return (
    <Paper className={props.classes.paper} key={"getthtpaper"}>
      <form
        autoComplete="off"
        key={"bbbb"}
        onSubmit={() => {
          handleSubmit();
        }}
      >
        <Grid
          container
          spacing={2}
          direction="row"
          justifyContent="center"
          key={"asdf"}
        >
          <BusinessIdInput
            businessId={businessId}
            key={"asdfz"}
          ></BusinessIdInput>
          <Grid
            key={"asdf12"}
            container
            item
            xs={8}
            spacing={0}
            justifyContent="center"
            style={{
              marginTop: "3vh",
              justifyContent: "center",
            }}
          >
            <Title>Menu Builder</Title>
          </Grid>
          <BuildPage
            key={"asd3434f"}
            onSubmit={(e, formValues) => handleSubmit(e, formValues)}
          ></BuildPage>
        </Grid>
      </form>
    </Paper>
  );
};
export default MenuBuilder;
