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
import { Customer } from "../../Models";
import { CSVLink } from "react-csv";
import {toCapitalizedWords} from '../../Models'

const useStyles = makeStyles({
  table: {
    width: "100%",
  },
});
const Customers = (props) => {
  const classes = useStyles();
  const mappedCustomers = props.customers.map((customerJSON) => {
    return new Customer(customerJSON);
  });
  const csvData = mappedCustomers.map((customer) => {
    const customerData = [customer.id, customer.firstName, customer.lastName];
    return customerData;
  });
  // add row headers
  csvData.unshift(
    Object.keys(mappedCustomers[0]).map((key) =>
      // if the key is "id" than we want to display an email label
      toCapitalizedWords(
        // the object keys are the objects private properties so we have to remove the underscores
        key === "id" ? "email" : key
      )
    )
  );
  if (mappedCustomers) {
    return (
      <TableContainer>
        <Paper className={props.classes.paper}>
          <Row style={{ width: "100%", height: "fit-content" }}>
            <Col xs={9}>
              <Title style={{ marginLeft: "auto", maxWidth: "15%" }}>
                Customers
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
                {Object.keys(mappedCustomers[0]).map((key, i) => (
                  <TableCell align="left" key={i}>
                    {
                      // if the key is "id" than we want to display an email label
                      toCapitalizedWords(
                        // the object keys are the objects private properties so we have to remove the underscores
                        key === "id" ? "email" : key
                      )
                    }
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {
              mappedCustomers[0].id !== '' ?
              mappedCustomers.map((row, i) => (
                <TableRow key={i}>
                  <TableCell>{i}</TableCell>
                  {Object.values(row).map((key, i) => (
                    <TableCell align="left" key={i}>
                      {key}
                    </TableCell>
                  ))}
                </TableRow>
              )) : <></>
            }
            </TableBody>
          </Table>
        </Paper>
      </TableContainer>
    );
  } else {
    return <></>;
  }
};
export default Customers;
