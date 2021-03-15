import React from "react";
import Typography from "@material-ui/core/Typography";
import Title from "./Title";

export default function Deposits(props) {
  return (
    <>
      <Title>
        {props.businessAndInterval === "Year"
          ? props.businessAndInterval + " " + "to Date Sales"
          : props.businessAndInterval + " " + "Sales"}
      </Title>
      <Typography component="p" variant="h4">
        ${Math.round(props.sales)}
      </Typography>
    </>
  );
}
