import { React, useReducer, useEffect } from "react";
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
import { Order, Business } from "../../Models";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Form from "react-bootstrap/Form";
import Col from "react-bootstrap/Col";
import Select from "@material-ui/core/Select";
import { FormGroup } from "@material-ui/core";
import Sales from "./Sales";
import Divider from "@material-ui/core/Divider";
import { CSVLink } from "react-csv";

const useStyles = makeStyles((theme) => ({
  formControl: {
    margin: theme.spacing(1),
    width: "fit-content",
  },
  formButton: {
    height: "fit-content",
  },
}));
export default function Chart(props) {
  const theme = useTheme();
  const [orderState, setOrderState] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      data: [],
      sales: 0,
      months: [],
    }
  );
  // Generate Sales Data
  const orders = props.orders.map((orderJSON) => {
    return new Order(orderJSON);
  });
  const businesses = props.businesses.map((businessJSON) => {
    return new Business(businessJSON);
  });

  const monthsLookup = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
  ];
  const weeks = [1, 2, 3, 4];

  const years = [2021];
  const intermediaryMonths = [];
  const [formValue, setFormValue] = useReducer(
    (state, newState) => ({ ...state, ...newState }),
    {
      business: "all",
      week: "all",
      month: "all",
      year: years[0],
      months: [],
    }
  );
  const formChangeHandler = (event) => {
    let name = event.target.name;
    let value = event.target.value;
    if (name === "month") {
      // the month is changed we reset the week value to its default of all weeks
      setFormValue({
        [name]: value,
        week: "all",
      });
    }
    setFormValue({
      [name]: value,
    });
  };
  const createData = (order, dataGroupedByDate, month = false) => {
    const dateWithYear = order.dateTime.split("/");
    const orderDay = dateWithYear[1];
    const orderMonth = dateWithYear[0];
    const date = orderMonth + "/" + orderDay;
    const amount = order.cost;
    const orderDateTime = new Date(order.dateTime);
    const monthIndex = monthsLookup.indexOf(month);
    const monthPresentIndex = intermediaryMonths.indexOf(
      monthsLookup[orderDateTime.getMonth()]
    );
    const orderBusinessId = order.businessId;
    const orderBusiness = businesses.filter(
      (business) => business.id === orderBusinessId
    )[0];

    if (monthPresentIndex === -1) {
      intermediaryMonths.push(monthsLookup[orderDateTime.getMonth()]);
      intermediaryMonths.sort(function (a, b) {
        return monthsLookup.indexOf(a) - monthsLookup.indexOf(b);
      });
    }
    var filterBusiness = "";
    // the first filtration will be done by business, because this will affect the normalization of the order dates
    if (formValue.business !== "all") {
      filterBusiness = new Business(formValue.business, true);
      if (orderBusinessId !== filterBusiness.id) {
        return;
      }
    }
    if (month === false) {
      // if no month is passed in then we sort the entire year's dates
      if (!dataGroupedByDate.find((data) => data.date === date)) {
        // if a matching date hasn't been added to the array then we append it to the list
        dataGroupedByDate.push({
          date: date,
          dateTime: new Date(orderDateTime),
          amount: amount,
          businessName: orderBusiness.name,
          businessAddress: orderBusiness.address,
        });
      } else {
        // otherwise if the date is already present, add the order value to the data object with the associated data and the running sum of costs for that date
        dataGroupedByDate.find((data) => data.date === date).amount += amount;
      }
    } else if (monthIndex !== false) {
      // if a month value was specified
      if (
        // if the monthIndex of the data is the same of the desired monthIndex
        orderDateTime.getMonth() !== monthIndex
      ) {
        return;
      }
      if (
        // if the date of the data is not present in the array yet
        !dataGroupedByDate.find(
          (data) => data.dateTime.getDate() === orderDateTime.getDate()
        )
      ) {
        dataGroupedByDate.push({
          date: date,
          dateTime: new Date(orderDateTime),
          amount: amount,
          businessName: orderBusiness.name,
          businessAddress: orderBusiness.address,
        });
      } else {
        // otherwise if the date is already present, add the order value to the data object with the associated data and the running sum of costs
        dataGroupedByDate.find(
          (data) => data.dateTime.getDate() === orderDateTime.getDate()
        ).amount += amount;
      }
    }
  };
  const getFormattedDate = (date) => {
    let month = (1 + date.getMonth()).toString().padStart(2, "0");
    let day = date.getDate().toString().padStart(2, "0");
    return month + "/" + day;
  };
  const classes = useStyles();

  const addMissingDates = (dateArray) => {
    var copyOfDateArray = [...dateArray];
    const lastday = (y, m) => {
      return new Date(y, m + 1, 0).getDate();
    };
    const monthForSet = copyOfDateArray[
      copyOfDateArray.length - 1
    ].dateTime.getMonth();
    const lastMonthDayForSet = lastday(2021, monthForSet);
    for (var i = 0; i < copyOfDateArray.length - 1; i++) {
      const currentIndexmonth = copyOfDateArray[i].dateTime.getMonth();
      const nextIndexmonth = copyOfDateArray[i + 1].dateTime.getMonth();

      var currentIndexDay = copyOfDateArray[i].dateTime.getDate();
      var nextIndexDay = copyOfDateArray[i + 1].dateTime.getDate();
      const lastMonthDay = lastday(2021, currentIndexmonth);

      // check to make sure the first day of the month is 1
      if (!currentIndexDay === 1) {
        // if not prepend a new order for 0 dollars on the first day of the month, which will trigger the function to add all the days after that
        const newDate = Date(2021, currentIndexmonth, 1).getDate();
        copyOfDateArray.unshift({
          date: getFormattedDate(newDate),
          dateTime: newDate,
          amount: 0,
        });
        i = 0; // reset index to 0 with the new element at the front of the list
      } else {
        // if we are only filtering one month of data then this will always be true
        // if the next data value month is not the same as the first then we don't want to compare them for the purpose of filling in missing days with no orders, and we have also reached the end of the data for the current month
        if (currentIndexmonth === nextIndexmonth) {
          if (nextIndexDay - currentIndexDay !== 1) {
            const newDate = copyOfDateArray[i].dateTime;
            // get tomorrow's date
            newDate.setDate(copyOfDateArray[i].dateTime.getDate() + 1);
            // add an empty order to represent 0 sales on that date
            copyOfDateArray.splice(i + 1, 0, {
              date: getFormattedDate(newDate),
              dateTime: newDate,
              amount: 0,
            });
          }
        } else {
          // once we reach the end of the orders for the current month, which goes up until the last order was placed for that month, then we want to fill in any remaining missing orders up until the last day of that month
          while (currentIndexDay !== lastMonthDay) {
            var nextDay = new Date(copyOfDateArray[i].dateTime);
            nextDay.setDate(nextDay.getDate() + 1);
            copyOfDateArray.splice(i + 1, 0, {
              date: getFormattedDate(nextDay),
              dateTime: nextDay,
              amount: 0,
            });
            i = i + 1;
            currentIndexDay = copyOfDateArray[i].dateTime.getDate();
          }
        }
      }
    }
    if (formValue.month !== "all") {
      // after completing the for loop we want to check if we were only filtering one month of data, if that is the case then we want to add the remaining days up until the end of the month
      // if the value is only one month then when the for loop finishes we can add the missing dates
      i = copyOfDateArray.length - 1;
      while (lastMonthDayForSet !== copyOfDateArray[i].dateTime.getDate()) {
        currentIndexDay = copyOfDateArray[i].dateTime.getDate();
        nextDay = new Date(copyOfDateArray[i].dateTime);
        nextDay.setDate(nextDay.getDate() + 1);
        copyOfDateArray.push({
          date: getFormattedDate(nextDay),
          dateTime: nextDay,
          amount: 0,
        });
        i = copyOfDateArray.length - 1;
      }
    }
    return copyOfDateArray;
  };
  const getWeekDays = (dateArray) => {
    var copyOfDateArray = [...dateArray];
    var newWeekDateArray = [];

    const oddDaysOut = copyOfDateArray.length % 4;
    const weekLength = Math.floor(copyOfDateArray.length / 4);
    const weekStartDay = weekLength * (formValue.week - 1);

    var weekEndDay = weekStartDay + weekLength;
    if (formValue.week === 4) {
      weekEndDay = weekEndDay + oddDaysOut;
    }
    for (var i = 0; i < copyOfDateArray.length; i++) {
      if (i >= weekStartDay && i <= weekEndDay) {
        newWeekDateArray.push(copyOfDateArray[i]);
      }
    }
    return newWeekDateArray;
  };
  const summateSales = (dateArray) => {
    var sum = 0;
    for (var i = 0; i < dateArray.length; i++) {
      sum += dateArray[i].amount;
    }
    return sum;
  };
  const getTimeIntervalAndBusiness = () => {
    var businessName = "";
    if (formValue.business !== "all") {
      const filterBusiness = new Business(formValue.business, true);
      businessName = filterBusiness.name;
      businessName += " ";
    }
    if (formValue.month === "all") {
      return businessName + "Year";
    } else if (formValue.month !== "all" && formValue.week === "all") {
      let monthNameFormat =
        formValue.month.charAt(0).toUpperCase() + formValue.month.slice(1);
      return businessName + " " + monthNameFormat;
    } else if (formValue.month !== "all" && formValue.week !== "all") {
      let monthNameFormat =
        formValue.month.charAt(0).toUpperCase() + formValue.month.slice(1);
      return (
        businessName +
        " " +
        monthNameFormat +
        " " +
        "Week" +
        " " +
        formValue.week
      );
    }
  };
  const prepareData = () => {
    var dataGroupedByDate = [];
    if (formValue.month !== "all") {
      // if a month has been specified
      orders.map((order) =>
        createData(order, dataGroupedByDate, formValue.month)
      );
      dataGroupedByDate.sort((a, b) => {
        return a.dateTime.getTime() - b.dateTime.getTime();
      });
      const fullDateArray = addMissingDates(dataGroupedByDate);
      if (formValue.week === "all") {
        const salesSum = summateSales(fullDateArray);
        const orderInformation = {
          data: fullDateArray,
          sales: salesSum,
          months: intermediaryMonths,
        };
        setOrderState(orderInformation);
      } else {
        // if a week has been selected
        const weekDays = getWeekDays(fullDateArray);
        const salesSum = summateSales(weekDays);
        const orderInformation = {
          data: weekDays,
          sales: salesSum,
          months: intermediaryMonths,
        };
        setOrderState(orderInformation);
      }
    } else if (formValue.month === "all") {
      // if a month has not been spcified we do year to date sales
      orders.map((order) => createData(order, dataGroupedByDate));
      dataGroupedByDate.sort((a, b) => {
        return a.dateTime.getTime() - b.dateTime.getTime();
      });

      const fullDateArray = addMissingDates(dataGroupedByDate);
      const salesSum = summateSales(fullDateArray);
      const orderInformation = {
        data: fullDateArray,
        sales: salesSum,
        months: intermediaryMonths,
      };
      setOrderState(orderInformation);
    }
  };

  useEffect(() => {
    prepareData(); // the formValue stateful variable is a dependency because the prepare data function relies on it to properly update the UI. because it is listed as a dependency react will make sure to get the updated values for it when the useEffect hook is called, which is whenever the page re-renders, which occurs when state changes which occures when the user selects a filter option
  }, [formValue]);

  return (
    <>
      <Title>Sales</Title>
      <Form>
        <FormGroup>
          <Form.Row>
            <Col xs={"auto"}>
              <FormControl variant="outlined" className={classes.formControl}>
                <InputLabel id="business-select-label">Business</InputLabel>
                <Select
                  labelId="business-select-label"
                  id="business-select-outlined"
                  value={formValue.business}
                  className={classes.formButton}
                  onChange={formChangeHandler}
                  label="Business"
                  name="business"
                >
                  <MenuItem value={"all"}>All Businesses</MenuItem>
                  {businesses.map((business, i) => (
                    <MenuItem key={i} value={JSON.stringify(business)}>
                      {business.name}
                      <br />
                      {business.address}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Col>
            <Col xs={"auto"}>
              <FormControl variant="outlined" className={classes.formControl}>
                <InputLabel id="year-select-label">Year</InputLabel>
                <Select
                  labelId="year-select-label"
                  id="year-select"
                  value={formValue.year}
                  className={classes.formButton}
                  onChange={formChangeHandler}
                  label="Year"
                  name="year"
                >
                  {years.map((year, i) => (
                    <MenuItem key={i} value={year}>
                      {year}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Col>
            <Col xs={"auto"}>
              <FormControl variant="outlined" className={classes.formControl}>
                <InputLabel id="month-select-label">Month</InputLabel>
                <Select
                  labelId="month-select-label"
                  id="month-select"
                  value={formValue.month}
                  className={classes.formButton}
                  onChange={formChangeHandler}
                  label="Month"
                  name="month"
                >
                  <MenuItem value={"all"}>All months</MenuItem>

                  {orderState.months.map((month, i) => (
                    <MenuItem key={i} value={month}>
                      {month.charAt(0).toUpperCase() + month.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Col>
            <Col xs={"auto"}>
              <FormControl variant="outlined" className={classes.formControl}>
                <InputLabel id="week-select-label">Week</InputLabel>
                <Select
                  labelId="week-select-label"
                  id="week-select"
                  value={formValue.week}
                  className={classes.formButton}
                  onChange={formChangeHandler}
                  label="Week"
                  name="week"
                  disabled={formValue.month === "all" ? true : false}
                >
                  <MenuItem value={"all"}>All weeks</MenuItem>

                  {weeks.map((week, i) => (
                    <MenuItem key={i} value={week}>
                      {week}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Col>
            <Col xs={"auto"} style={{ marginLeft: "auto" }}>
              <CSVLink data={orderState.data} style={{ marginLeft: "auto" }}>
                Export Data
              </CSVLink>
            </Col>
          </Form.Row>
        </FormGroup>
      </Form>
      <ResponsiveContainer>
        <LineChart
          data={orderState.data}
          margin={{
            top: 16,
            right: 16,
            bottom: 0,
            left: 24,
          }}
        >
          <XAxis dataKey="date" stroke={theme.palette.text.secondary} dy={10} />
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
      <Divider
        style={{
          marginTop: "3%",
          marginBottom: "1%",
          backgroundColor: "white",
          height: ".1rem",
        }}
      />
      <Sales
        businessAndInterval={getTimeIntervalAndBusiness()}
        sales={orderState.sales}
      />
      <Divider
        style={{
          marginTop: "0%",
          marginBottom: "3%",
          backgroundColor: "white",
          height: ".1rem",
        }}
      />
    </>
  );
}
