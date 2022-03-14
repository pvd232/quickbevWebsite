import Button from "@material-ui/core/Button";
import React, { useState, useReducer, useEffect } from "react";
import { TextField } from "@material-ui/core";
import Form from "react-bootstrap/Form";
import API from "../../helpers/Api.js";
import { makeStyles } from "@material-ui/core/styles";
import Title from "../dashboard/Title";
import Paper from "@material-ui/core/Paper";
import Grid from "@material-ui/core/Grid";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { LocalStorageManager } from "../../Models.js";

const DeactivateDrink = (props) => {
  // eslint-disable-next-line no-unused-vars
  const drinkId = LocalStorageManager.shared.editDrinkId;
  const drink = LocalStorageManager.shared.getDrink(drinkId);
  console.log("drink", drink);
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

  const [isSpinning, setIsSpinning] = useState(false);
  const [isDisabled, setIsDisabled] = useState(false);
  const [redirect, setRedirect] = useState(null);

  useEffect(() => {
    //had to do this because memory leak due to component not unmounting properly
    let mount = true;
    if (mount && redirect) {
      window.location.assign(redirect);
    }

    return () => (mount = false);
  }, [redirect]);

  const Spinner = () => (
    <FontAwesomeIcon icon={faSpinner} className="fa-spin" size="lg" />
  );

  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };
  const handleSubmit = async (event, formValues) => {
    const form = event.target.closest("form");
    if (validate(form)) {
      formValues.append("drinkId", JSON.stringify(drinkId));
      // set all the values for the business
      // if the user comes back to this page before submitting to change stuff it will reset the values
      const response = await API.makeRequest(
        "PUT",
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
        API.getDrinks().then((items) => {
          if (typeof items.drinks !== "undefined") {
            if (items) {
              LocalStorageManager.shared.drinks = items.drinks;
            }
          }
        });
      }
    } else {
      alert(
        "Upload failed due to missing menu data. Please fill out all the required form values."
      );
    }
    setIsSpinning(false);
    setIsDisabled(false);
    setRedirect("/home");
  };
  const DrinkIdInput = (props) => {
    const drinkId = props.drinkId;
    return (
      <Grid
        item
        xs={2}
        style={{
          textAlign: "center",
          marginBottom: "2vh",
          marginTop: "2vh",
          marginRight: "7vw",
        }}
        key={"grid-3"}
      >
        <TextField
          fullWidth
          name="drinkId"
          label="Drink Id"
          multiline
          value={drinkId}
          required
          key={"grid-4"}
          disabled={true}
        />
      </Grid>
    );
  };
  const FormRow = (props) => {
    const [formValue, setFormValue] = useReducer(
      (state, newState) => ({ ...state, ...newState }),
      {
        drinkName: drink.name,
        drinkDescription: drink.description,
        drinkPrice: drink.price,
        selectedFile: "",
        selectedFileName: "",
      }
    );

    const formChangeHandler = (event) => {
      if (event.target.name === "selectedFile") {
        const newFileObject = {
          selectedFile: event.target.files[0],
          selectedFileName: event.target.files[0].name.replace(/ /g, "-"),
        };
        setFormValue(newFileObject);
        console.log("newFileObject", newFileObject);
        const propsFileObject = {
          name: "selectedFile",
          value: event.target.files[0],
        };
        props.updateValue(propsFileObject);
        const propsFileName = {
          name: "selectedFileName",
          value: newFileObject.selectedFileName,
        };
        props.updateValue(propsFileName);
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
          });
        } else {
          let name = event.target.name;
          let value = event.target.value.toLowerCase();
          setFormValue({ [name]: value });
          props.updateValue({ name: name, value: value });
        }
      } else {
        let name = event.target.name;
        let value = event.target.value;
        setFormValue({ [name]: value });
        props.updateValue({ name: name, value: value });
      }
    };
    return (
      <Grid
        container
        item
        xs={11}
        spacing={0}
        key={"grid-1-" + props.k}
        style={{
          marginLeft: "auto",
          marginRight: "auto",
          justifyContent: "center",
        }}
      >
        <div className={classes.root} key={"asdf-" + props.k}>
          <Grid
            key={"grid-1-1-" + props.k}
            item
            xs={12}
            style={{
              justifyContent: "center",
              marginBottom: "20px",
              marginTop: "20px",
            }}
          ></Grid>
          <Grid container key={"grid-2-" + props.k} item xs={12}>
            <Grid
              key={"grid-1-1-1-" + props.k}
              item
              xs={2}
              style={{ textAlign: "left", marginRight: "20px" }}
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
              key={"grid-1-1-1-1-" + props.k}
              item
              xs={4}
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
              alignItems="flex-end"
              style={{ marginLeft: "20px", justifyContent: "center" }}
            >
              <p
                style={{
                  marginBottom: "0px",
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
              xs={3}
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
    const formValues = {
      // the drink instance being edited will be deactivated upon submission of the edited drink
      drinkIdToDeactivate: drink.id,
      drinkBusinessId: drink.businessId,
      drinkName: drink.name,
      drinkDescription: drink.description,
      drinkPrice: drink.price,
      // if the drink is an original, it wont have a parent drink id and the parent drink id will be the drink's id
      parentDrinkId:
        drink.parentDrinkId === "None" ? drink.id : drink.parentDrinkId,
      selectedFile: "",
      selectedFileName: "",
      imageUrl: drink.imageUrl,
    };

    const formChangeHandler = (newValue) => {
      formValues[newValue.name] = newValue.value;
    };

    const handleSubmit = (event) => {
      const newForm = new FormData();
      // loop through each drink property and append it to the form
      Object.keys(formValues).forEach((key) => {
        if (key !== "selectedFile") {
          newForm.append(key, JSON.stringify(formValues[key]));
        } else {
          // if there is a file, then we append the file to the form. a dictionary is appended, with a key called 'selectedFile', a file name using the file's name, and the value is the file itself
          if (formValues.selectedFile !== "") {
            newForm.append("hasImage", JSON.stringify(true));
            newForm.append(
              String(key), // key name
              formValues[key], // value associated with the key, which is the file
              formValues.selectedFileName // the file's name
            );
          } else {
            // if there is no drink image then the value appended will be false and the form.files on the backend will be an empty dictionary
            newForm.append("hasImage", JSON.stringify(false));
          }
        }
      });
      for (var pair of newForm.entries()) {
        console.log(pair[0] + ", " + pair[1]);
      }
      props.onSubmit(event, newForm);
    };

    const SubmitButton = (props) => {
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
    return (
      <>
        <FormRow updateValue={(e) => formChangeHandler(e)}></FormRow>,
        <SubmitButton onClick={(e) => handleSubmit(e)}></SubmitButton>
      </>
    );
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
          <DrinkIdInput drinkId={drinkId} key={"asdfz"}></DrinkIdInput>
          <Grid
            key={"asdf12"}
            container
            item
            xs={8}
            spacing={0}
            style={{
              marginTop: "3vh",
              paddingRight: "22vw",
              justifyContent: "center",
            }}
          >
            <Title>Drink Editor</Title>
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
export default DeactivateDrink;
