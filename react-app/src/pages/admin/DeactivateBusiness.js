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

const DeactivateBusiness = () => {
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

  var businessId = "";
  const updateBusinessId = (newBusinessId) => {
    businessId = newBusinessId;
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
        `/business/deactivate/${LocalStorageManager.shared.sessionToken}?business_id=${businessId}`,
        false,
        false,
        false
      );
      if (response.status !== 200) {
        alert("A server error occured. Tell Peter.");
        setIsSpinning(false);
        setIsDisabled(false);
      } else {
        alert("Business sucessfully updated!");
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

  const BusinessIdInput = (props) => {
    const [businessId, setbusinessId] = useState("");
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
          name="businessId"
          label="Business Id to deactivate"
          multiline
          value={businessId}
          required
          onChange={(event) => {
            const businessId = event.target.value.trimStart().trimEnd();
            setbusinessId(businessId);
            props.updateBusinessId(businessId);
          }}
        />
      </Grid>
    );
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
export default DeactivateBusiness;
