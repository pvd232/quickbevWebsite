import React from "react";
import Link from "@material-ui/core/Link";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Title from "./Title";

function preventDefault(event) {
  event.preventDefault();
}

const useStyles = makeStyles({
  depositContext: {
    flex: 1,
  },
});

export default function Deposits(props) {
  const classes = useStyles();
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
