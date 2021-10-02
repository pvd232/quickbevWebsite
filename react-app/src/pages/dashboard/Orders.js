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
import { Order, OrderDrink } from "../../Models";
import { CSVLink } from "react-csv";
import { toCapitalizedWords } from "../../Models";

const useStyles = makeStyles({
  table: {
    width: "100%",
  },
});

const Orders = (props) => {
  const classes = useStyles();
  const mappedOrders = props.orders.map((orderJSON) => {
    return new Order(orderJSON);
  });

  const formattedMappedOrders = mappedOrders.map((order) => {
    order.total = Math.round(order.total);
    order.subtotal = Math.round(order.subtotal);
    order.tipAmount = Math.round(order.tipAmount);
    order.salesTax = Math.round(order.salesTax);
    order.serviceFee = Math.round(order.serviceFee);
    const orderBusiness = props.businesses.filter(
      (business) => order.businessId === business.id
    );
    if (orderBusiness.length > 0) {
      order.businessName = orderBusiness[0].name;
    }
    return order;
  });
  formattedMappedOrders.sort((a, b) => {
    const aDate = new Date(a.dateTime);
    const bDate = new Date(b.dateTime);
    return bDate.getTime() - aDate.getTime();
  });
  const csvData = formattedMappedOrders.map((order) => {
    const orderData = [];
    Object.values(order).map((key) => {
      if (key instanceof OrderDrink) {
        Object.values(key.orderDrink).map((drink) => {
          orderData.push(String(drink.quantity) + "x " + drink.name);
        });
      } else {
        orderData.push(key);
      }
    });
    return orderData;
  });

  // add row headers
  csvData.unshift(
    Object.keys(formattedMappedOrders[0]).map((key) =>
      // if the key is "id" than we want to display an email label
      key === "tipPercentage"
        ? "Tip %"
        : toCapitalizedWords(
            // the object keys are the objects private properties so we have to remove the underscores
            key
          )
    )
  );
  if (formattedMappedOrders) {
    return (
      <TableContainer>
        <Paper className={props.classes.paper}>
          <Row style={{ width: "100%", height: "fit-content" }}>
            <Col xs={9}>
              <Title style={{ marginLeft: "auto", maxWidth: "15%" }}>
                Orders
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
                {Object.keys(formattedMappedOrders[0]).map((key, i) => (
                  <TableCell align="left" key={i}>
                    {key === "tipPercentage"
                      ? "Tip %"
                      : toCapitalizedWords(
                          // the object keys are the objects private properties so we have to remove the underscores
                          key
                        )}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {formattedMappedOrders[0].id !== "" ? (
                formattedMappedOrders.map((row, i) => (
                  <TableRow key={row.id}>
                    <TableCell>{i}</TableCell>
                    {Object.values(row).map((key, i) => {
                      console.log("key", key);
                      if (key instanceof OrderDrink) {
                        console.log("orderDrink key", key);
                        return (
                          <TableCell align="left" key={i}>
                            {Object.values(key.orderDrink).map((drink) => {
                              return String(drink.quantity) + "x " + drink.name;
                            })}
                          </TableCell>
                        );
                      } else {
                        return (
                          <TableCell align="left" key={i}>
                            {key}
                          </TableCell>
                        );
                      }
                    })}
                  </TableRow>
                ))
              ) : (
                <></>
              )}
            </TableBody>
          </Table>
        </Paper>
      </TableContainer>
    );
  } else {
    return <></>;
  }
};
export default Orders;
