import Button from "@material-ui/core/Button";
import React, { useState } from "react";
import { TextField } from "@material-ui/core";
import API from "../../helpers/Api.js";
import { makeStyles } from "@material-ui/core/styles";
import { LocalStorageManager } from "../../Models.js";
import Paper from "@material-ui/core/Paper";
import Grid from "@material-ui/core/Grid";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const DeactivateDrink = () => {
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
  const [isDisabled, setIsDisabled] = useState(false);

  const [isSpinning, setIsSpinning] = useState(null);
  const Spinner = () => (
    <FontAwesomeIcon icon={faSpinner} className="fa-spin" />
  );

  var drinkId = "";
  const updateDrinkId = (newDrinkId) => {
    drinkId = newDrinkId;
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };

  const handleSubmit = (event) => {
    setIsSpinning(true);
    setIsDisabled(true);
    event.preventDefault();
    const form = event.target.closest("form");
    if (validate(form)) {
      const response = API.makeRequest(
        "POST",
        `/deactivate/drink/${LocalStorageManager.shared.sessionToken}?drink_id=${drinkId}`,
        false,
        false,
        true
      );
      if (response.status !== 200) {
        alert("A server error occured. Tell Peter.");
        setIsSpinning(false);
        setIsDisabled(false);
      } else {
        alert("Menu successfully uploaded!");
        setIsSpinning(false);
        setIsDisabled(false);
      }
    } else {
      alert(
        "Menu upload failed. Make sure you filled out the form correctly and your internet is working."
      );
      setIsSpinning(false);
      setIsDisabled(false);
    }
  };

  const DrinkIdInput = (props) => {
    const [drinkId, setdrinkId] = useState("");
    return (
      <Grid
        item
        xs={2}
        style={{
          textAlign: "center",
          //   marginBottom: "20px",
          marginTop: "20vh",
          //   paddingLeft: "4vw",
        }}
      >
        <TextField
          fullWidth
          name="drinkId"
          label="Drink Id to deactivate"
          multiline
          value={drinkId}
          required
          onChange={(event) => {
            const drinkId = event.target.value.trimStart().trimEnd();
            setdrinkId(drinkId);
          }}
        />
      </Grid>
    );
  };

  return (
    <Paper className={classes.content}>
      <form autoComplete="off">
        <Grid container spacing={2} direction="row" justify="center">
          <DrinkIdInput
            updateDrinkId={(newDrinkId) => updateDrinkId(newDrinkId)}
          ></DrinkIdInput>
          <Button
            onClick={(e) => handleSubmit(e)}
            style={{
              backgroundColor: "#8682E6",
              width: "15vw",
              fontWeight: "bold",
              fontSize: "1rem",
              marginBottom: "5vh",
              maxHeight: "5vh",
              marginTop: "21.7vh",
            }}
            isDisabled={isDisabled}
          >
            {isSpinning ? <Spinner></Spinner> : "Submit"}
          </Button>
        </Grid>
      </form>
    </Paper>
  );
};
export default DeactivateDrink;
