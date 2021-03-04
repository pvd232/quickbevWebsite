import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import Orders from "./Orders";
import Chart from "./Chart";

const HomeSplash = (props) => {
  return (
    <>
      <Grid item xs={12} md={12} lg={12}>
        <Paper className={props.fixedHeightPaper}>
          <Chart data={props.orderArray} />
        </Paper>
      </Grid>

      {/* Recent Orders */}
      <Grid item xs={12}>
        <Paper className={props.classes.paper}>
          <Orders orderArray={props.orderArray} />
        </Paper>
      </Grid>
    </>
  );
};
export default HomeSplash;
