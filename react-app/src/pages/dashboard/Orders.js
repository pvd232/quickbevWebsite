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
import { LocalStorageManager, OrderItem } from "../../Models";
import { CSVLink } from "react-csv";
import { toCapitalizedWords } from "../../Models";

const useStyles = makeStyles({
  table: {
    width: "100%",
  },
});

const Orders = (props) => {
  const classes = useStyles();
  const formattedOrders = LocalStorageManager.shared.orders.map((order) => {
    // format Order objects by transforming them into OrderItems
    const orderItem = new OrderItem(order);
    const orderBusiness = LocalStorageManager.shared.businesses.filter(
      (business) => order.businessId === business.id
    );
    if (orderBusiness.length > 0) {
      orderItem.businessName = orderBusiness[0].name;
      const bizAddy = orderBusiness[0].address;
      const bizAddyParts = bizAddy.split(",");

      // remove trailing 'USA' from address, initially all businesses will be in the USA
      for (const part of bizAddyParts) {
        if (part.trim() === "USA") {
          const index = bizAddyParts.indexOf(part);
          if (index > -1) {
            bizAddyParts.splice(index, 1);
          }
        }
      }
      const newAddy = bizAddyParts.join(", ");
      orderItem.address = newAddy;
    }
    return orderItem;
  });

  const sortedFormattedOrders = formattedOrders.sort((a, b) => {
    const aDate = new Date(a.dateTime);
    const bDate = new Date(b.dateTime);
    return bDate.getTime() - aDate.getTime();
  });
  if (sortedFormattedOrders.length === 0) {
    formattedOrders.push(new OrderItem(false));
  }
  const csvData = sortedFormattedOrders.map((order) => {
    const orderData = [];
    // eslint-disable-next-line array-callback-return
    Object.values(order).map((key) => {
      if (key instanceof Array) {
        // eslint-disable-next-line array-callback-return
        Object.values(key).map((orderDrink) => {
          orderData.push(
            String(orderDrink.quantity) + "x " + orderDrink.drinkName
          );
        });
      } else {
        orderData.push(key);
      }
    });
    return orderData;
  });

  // add row headers
  csvData.unshift(
    Object.keys(sortedFormattedOrders[0]).map((key) =>
      // if the key is "id" than we want to display an email label
      key === "tipPercentage"
        ? "Tip %"
        : toCapitalizedWords(
            // the object keys are the objects private properties so we have to remove the underscores
            key
          )
    )
  );
  if (sortedFormattedOrders) {
    return (
      <TableContainer>
        <Paper className={props.classes.paper}>
          <Row style={{ width: "100%", height: "fit-content" }} key={"row-1"}>
            <Col xs={9} key={"col-1"}>
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
              key={"col-1-1"}
            >
              <CSVLink data={csvData} style={{ marginLeft: "auto" }}>
                Export Data
              </CSVLink>
            </Col>
          </Row>
          <Table className={classes.table} aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell align="left" key={"row-1-1"}>
                  Row
                </TableCell>
                {Object.keys(sortedFormattedOrders[0]).map((key, i) => (
                  <TableCell align="left" key={"row-1-1-" + i}>
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
              {sortedFormattedOrders[0].id !== "" ? (
                sortedFormattedOrders.map((row, i) => (
                  <TableRow key={"row-1-1-1-" + i}>
                    <TableCell key={"row-1-1-1-1-" + i}>{i}</TableCell>
                    {Object.values(row).map((key, i) => {
                      if (key instanceof Array) {
                        return (
                          <TableCell align="left" key={"row-1-1-1-1-1" + i}>
                            {Object.values(key).map((orderDrink) => {
                              return (
                                <div key={"div-" + i}>
                                  {String(orderDrink.quantity) +
                                    " " +
                                    orderDrink.drinkName}
                                </div>
                              );
                            })}
                          </TableCell>
                        );
                      } else {
                        return (
                          <TableCell
                            align="left"
                            key={"row-1-1-1-1-1-1-" + i}
                            style={{ maxWidth: "12vw" }}
                          >
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
