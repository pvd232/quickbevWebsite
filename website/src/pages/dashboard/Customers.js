import React, { useState, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import Title from "./Title";
import { Customer } from "../../Models";
import API from "../../helpers/Api";

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
const nonCamelCaseWords = (name) => {
  var words = name.match(/[A-Za-z][a-z]*/g) || [];
  return words.join(" ");
};
const Customers = (props) => {
  const classes = useStyles();
  const [customers, setCustomers] = useState(null);
  useEffect(() => {
    let mounted = true;
    API.getCustomers().then((items) => {
      console.log("items", items);
      if (mounted) {
        const mappedCustomers = items.customers.map((customerObject) => {
          return new Customer(customerObject);
        });
        setCustomers(mappedCustomers);
      }
    });
    return () => (mounted = false);
  }, []);
  if (customers) {
    return (
      <TableContainer>
        <Paper className={props.classes.paper}>
          <Title>Customers</Title>
          <Table className={classes.table} aria-label="simple table">
            <TableHead>
              <TableRow>
                {Object.keys(customers[0]).map((key) => (
                  <TableCell align="left" key={key}>
                    {toCapitalizedWords(key.replace("_", ""))}
                  </TableCell>
                ))}
              </TableRow>

              {/* <TableRow>
              <TableCell>Dessert (100g serving)</TableCell>
              <TableCell align="right">Calories</TableCell>
              <TableCell align="right">Fat&nbsp;(g)</TableCell>
              <TableCell align="right">Carbs&nbsp;(g)</TableCell>
              <TableCell align="right">Protein&nbsp;(g)</TableCell>
            </TableRow> */}
            </TableHead>
            <TableBody>
              {customers.map((row) => (
                <TableRow key={row.id}>
                  {Object.values(row).map((key) => (
                    <TableCell align="left" key={key}>
                      {nonCamelCaseWords(key.replace("_", ""))}
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
export default Customers;
