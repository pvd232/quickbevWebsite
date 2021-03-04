import { React, useState } from "react";
import { useTheme, makeStyles } from "@material-ui/core/styles";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Label,
  ResponsiveContainer,
} from "recharts";
import Title from "./Title";
import { Order } from "../../Models";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
const useStyles = makeStyles((theme) => ({
  formControl: {
    margin: theme.spacing(1),
    width: "250px",
  },
  formButton: {
    height: "fit-content",
  },
}));
export default function Chart(props) {
  const theme = useTheme();
  const [business, setBusiness] = useState("all");

  console.log("props.data", props.data);
  // Generate Sales Data
  const orders = props.data.orders.map((orderObject) => {
    return new Order(orderObject);
  });
  for (var i in orders) {
    console.log("order", orders[i]);
  }
  const handleBusiness = (event) => {
    const value = event.target.value;
    console.log("value", value);
    setBusiness(value);
  };
  const createData = (order) => {
    console.log("order", order);
    const time = order.dateTime;
    console.log("time", time);
    const amount = order.cost;
    return { time, amount };
  };

  const classes = useStyles();

  const dataFormatted = orders.map((order) => createData(order));
  console.log("dataFormatted", dataFormatted);
  return (
    <>
      <Title>Sales</Title>
      <FormControl variant="outlined" className={classes.formControl}>
        <InputLabel id="demo-simple-select-outlined-label">Business</InputLabel>
        <Select
          labelId="demo-simple-select-outlined-label"
          id="demo-simple-select-outlined"
          value={business}
          className={classes.formButton}
          onChange={handleBusiness}
          label="Business"
          displayEmpty
        >
          <MenuItem value={"all"}>All Businesses</MenuItem>
          <MenuItem value={10}>Ten</MenuItem>
          <MenuItem value={20}>Twenty</MenuItem>
          <MenuItem value={30}>Thirty</MenuItem>
        </Select>
      </FormControl>
      <ResponsiveContainer>
        <LineChart
          data={dataFormatted}
          margin={{
            top: 16,
            right: 16,
            bottom: 0,
            left: 24,
          }}
        >
          <XAxis dataKey="time" stroke={theme.palette.text.secondary} dy={10} />
          <YAxis stroke={theme.palette.text.secondary} dx={-5}>
            <Label
              angle={270}
              position="left"
              style={{ textAnchor: "middle", fill: theme.palette.text.primary }}
            >
              Sales ($)
            </Label>
          </YAxis>
          <Line
            type="monotone"
            dataKey="amount"
            stroke={theme.palette.primary.main}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </>
  );
}
