import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import Chart from "./Chart";

const HomeSplash = (props) => {
  return (
    <>
      <Grid item={true} xs={12} md={12} lg={12}>
        <Paper className={props.fixedHeightPaper}>
          <Chart orders={props.orders} businesses={props.businesses} />
        </Paper>
      </Grid>
    </>
  );
};
export default HomeSplash;
