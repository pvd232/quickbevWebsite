import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import IconButton from "@material-ui/core/IconButton";
import Paper from "@material-ui/core/Paper";
import Title from "./dashboard/Title";
import { QuickPass } from "../Models";
import API from "../helpers/Api.js";
import Grid from "@material-ui/core/Grid";
import CheckCircleIcon from "@material-ui/icons/CheckCircle";
import SearchBar from "material-ui-search-bar";
const BouncerQuickPass = () => {
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
  const [quickPasses, setQuickPasses] = useState(null);
  const [filteredQuickPasses, setFilteredQuickPasses] = useState(null);

  const [validated, setValidated] = useState(null);
  const [searchBarText, setSearchBarText] = useState("");

  let { sessionToken, businessId } = useParams();
  useEffect(() => {
    let mounted = true;
    console.log("businessId", businessId);
    console.log("hi");
    API.checkTokenStatus(sessionToken).then((value) => {
      console.log("value", value);
      if (mounted && !value) {
        setValidated(false);
        window.location.assign("/");
      } else if (mounted && value) {
        setValidated(true);
      }
    });
    API.getQuickPasses(businessId).then((items) => {
      if (mounted && items) {
        console.log("items", items);
        console.log("items.quick_passes b4", items.quick_passes);
        console.log("items.quick_passes after", items.quick_passes);
        setQuickPasses(
          items.quick_passes.map(
            (quickPassJSON) => new QuickPass(quickPassJSON)
          )
        );
        setFilteredQuickPasses(
          items.quick_passes.map(
            (quickPassJSON) => new QuickPass(quickPassJSON)
          )
        );
      }
    });
    return () => (mounted = false);
  }, [businessId, sessionToken]);
  const filterData = () => {
    const newQuickPassList = [];
    const firstNameFilter =
      searchBarText.split(" ")[0] === undefined
        ? ""
        : searchBarText.split(" ")[0];
    console.log("firstNameFilter", firstNameFilter);
    const lastNameFilter =
      searchBarText.split(" ")[1] === undefined
        ? ""
        : searchBarText.split(" ")[1];
    console.log("lastNameFilter", lastNameFilter);

    if (searchBarText === "") {
      setFilteredQuickPasses(quickPasses);
    } else {
      for (var i = 0; i < quickPasses.length; i++) {
        const quickPass = quickPasses[i];
        console.log("quickPass", quickPass);
        var nameBool = true;
        const customerFirstName = quickPass.customerFirstName.toLowerCase();
        const customerLastName = quickPass.customerLastName.toLowerCase();
        const customerFirstNameLength = customerFirstName.length;
        const customerLastNameLength = customerLastName.length;
        for (var j = 0; j < firstNameFilter.split("").length; j++) {
          if (j >= customerFirstNameLength) {
            break;
          }
          const character = firstNameFilter.split("")[j];
          const otherCharacter = quickPass.customerFirstName
            .toLowerCase()
            .split("")[j];

          if (character !== otherCharacter) {
            nameBool = false;
          }
        }
        for (var k = 0; k < lastNameFilter.split("").length; k++) {
          if (k >= customerLastNameLength) {
            break;
          }
          const character = lastNameFilter.split("")[k];
          const otherCharacter = quickPass.customerLastName
            .toLowerCase()
            .split("")[k];

          if (character !== otherCharacter) {
            nameBool = false;
          }
        }
        if (nameBool === true) {
          newQuickPassList.push(quickPass);
        }
      }
      setFilteredQuickPasses(newQuickPassList);
    }
  };
  const handleAdmitPass = (index) => {
    console.log("index", index);
    const quickPass = filteredQuickPasses[index];
    const a = Date.now();
    console.log("a", a);
    quickPass.timeCheckedIn = Date.now() / 1000;
    console.log("stagedQuickPassToRemove", quickPass);
    const data = { quick_pass: quickPass };
    const headers = { entity: "bouncer" };
    API.makeRequest("PUT", `/quick_pass/${sessionToken}`, data, headers).then(
      setQuickPasses((prevMapppedQuickPasses) => {
        prevMapppedQuickPasses.splice(index, 1);
        const newMappedQuickPasses = [];
        for (var i in prevMapppedQuickPasses) {
          newMappedQuickPasses.push(prevMapppedQuickPasses[i]);
        }
        setFilteredQuickPasses(newMappedQuickPasses);
        return newMappedQuickPasses;
      })
    );
  };
  if (validated && quickPasses && filteredQuickPasses) {
    return (
      <Paper className={classes.content}>
        <Grid
          container
          item
          xs={12}
          spacing={0}
          justify="center"
          style={{ marginTop: "3vh" }}
        >
          <Title>Quick Pass Verification Page</Title>
        </Grid>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell align="center">Active Quick Passes</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <SearchBar
                    value={searchBarText}
                    onChange={(newValue) => setSearchBarText(newValue)}
                    onRequestSearch={() => filterData()}
                  />
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                {filteredQuickPasses.map((mappedQuickPass, i) => (
                  <TableCell key={i} align="center">
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "flex-end",
                        alignItems: "center",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          flexGrow: 2,
                          justifyContent: "center",
                          alignItems: "center",
                        }}
                      >
                        <p style={{ marginBottom: "0" }}>
                          {mappedQuickPass.customerFirstName}
                        </p>
                        <span style={{ color: "white" }}>"</span>
                        <p style={{ marginBottom: "0" }}>
                          {mappedQuickPass.customerLastName}
                        </p>
                        <span style={{ color: "white" }}>"""""</span>

                        <p style={{ marginRight: "1rem", marginBottom: "0" }}>
                          {mappedQuickPass.formatTimestamp()}
                        </p>
                      </div>
                      <IconButton
                        style={{
                          marginLeft: "auto",
                          marginTop: "1vh",
                          marginRight: "1vw",
                          marginBottom: "1vh",
                          transform: "scale(1.8)",
                        }}
                        onClick={() => handleAdmitPass(i)}
                      >
                        <CheckCircleIcon
                          style={{ color: "#4CBB17" }}
                        ></CheckCircleIcon>
                      </IconButton>
                    </div>
                  </TableCell>
                ))}
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    );
  } else {
    return <></>;
  }
};
export default BouncerQuickPass;
