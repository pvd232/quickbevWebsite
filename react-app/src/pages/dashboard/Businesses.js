import React from "react";
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
import { Business } from "../../Models";
import { CSVLink } from "react-csv";

const useStyles = makeStyles({
  table: {
    width: "100%",
  },
});
const capitalize = (word) => {
  return word.charAt(0).toUpperCase() + word.substring(1);
};
const toCapitalizedWords = (name) => {
  var words = name.match(/[A-Za-z][a-z]*/g) || [];

  return words.map(capitalize).join(" ");
};

const Businesses = (props) => {
  const classes = useStyles();
  const mappedBusinesses = props.businesses.map((businessJSON) => {
    return new Business(businessJSON, false, true);
  });
  var csvData = mappedBusinesses.map((business) => {
    var businessData = [];
    Object.values(business).map((value) => {
      switch (value) {
        case typeof value === "string":
          businessData.push(value.replace("_", ""));
          return value;
        case value === true:
          businessData.push("yes");
          return value;
        default:
          businessData.push(value);
          return value;
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
          <Table className={classes.table} aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell align="left" key={"row #"}>
                  Row
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
