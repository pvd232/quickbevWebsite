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
import { useSearchParams } from "react-router-dom";

const DeactivateDrink = () => {
  // eslint-disable-next-line no-unused-vars
  const [searchParams, setSearchParams] = useSearchParams();
  var drinkId = searchParams.get("drink_id") ?? "";

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

  const updateDrinkId = (newDrinkId) => {
    drinkId = newDrinkId;
  };
  const validate = (form) => {
    form.classList.add("was-validated");
    return form.checkValidity();
  };

  const handleSubmit = async (event) => {
    setIsSpinning(true);
    setIsDisabled(true);
    event.preventDefault();
    const form = event.target.closest("form");
    if (validate(form)) {
      const response = await API.makeRequest(
        "POST",
        `/drink/deactivate/${LocalStorageManager.shared.sessionToken}?drink_id=${drinkId}`,
        false,
        false,
        false
      );
      if (response.status !== 200) {
        alert("A server error occured. Tell Peter.");
        setIsSpinning(false);
        setIsDisabled(false);
      } else {
        alert("Drink sucessfully updated!");
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
    const [drinkId, setdrinkId] = useState(props.drinkId);
    return (
      <Grid
        item
        xs={2}
        style={{
          textAlign: "center",
          marginTop: "20vh",
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
            props.updateDrinkId(drinkId);
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
            drinkId={drinkId}
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
            disabled={isDisabled}
          >
            {isSpinning ? <Spinner></Spinner> : "Submit"}
          </Button>
        </Grid>
      </form>
    </Paper>
  );
};
export default DeactivateDrink;
