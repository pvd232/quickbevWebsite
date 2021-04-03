import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
// import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import CardMedia from "@material-ui/core/CardMedia";
import Typography from "@material-ui/core/Typography";
import Paper from "@material-ui/core/Paper";
import Title from "./Title";
import Col from "react-bootstrap/Col";
import Container from "@material-ui/core/Container";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Form from "react-bootstrap/Form";
import Select from "@material-ui/core/Select";
import { FormGroup } from "@material-ui/core";
import InputLabel from "@material-ui/core/InputLabel";
import { useState } from "react";
import { Business, Drink } from "../../Models";
import Grid from "@material-ui/core/Grid";
import { toCapitalizedWords } from "../../Models";

const Menu = (props) => {
  const useStyles = makeStyles((theme) => ({
    root: {
      width: "200px",
      height: "350px",
    },
    media: {},
    gridRoot: {
      flexGrow: 1,
      marginTop: "20px",
      padding: theme.spacing(2),
    },
  }));
  const businesses = props.businesses.map((businessJSON) => {
    return new Business(businessJSON, true);
  });
  console.log("businesses", businesses);

  const classes = useStyles();
  const [businessIndex, setBusinessIndex] = useState(0);
  const formChangeHandler = (event) => {
    let value = event.target.value;
    setBusinessIndex(value);
  };
  return (
    <Container maxWidth="xl">
      <Paper className={props.classes.paper}>
        <Title>Menu</Title>
        <Form style={{ marginTop: "20px" }}>
          <FormGroup>
            <Form.Row>
              <Col xs={"auto"}>
                <FormControl variant="outlined" className={classes.formControl}>
                  <InputLabel id="business-select-label">Business</InputLabel>
                  <Select
                    labelId="business-select-label"
                    value={businessIndex}
                    className={classes.formButton}
                    onChange={formChangeHandler}
                    label="Business"
                    name="business"
                  >
                    {businesses.map((business, i) => (
                      <MenuItem key={i} value={i}>
                        {toCapitalizedWords(business.name)}
                        <br />
                        {business.address}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Col>
            </Form.Row>
          </FormGroup>
        </Form>
        <Grid container className={classes.gridRoot} spacing={2} xs={12}>
          {businesses[businessIndex].menu.map((drink, i) => {
            const menuDrink = new Drink(drink);
            return (
              <Grid
                container
                align="center"
                direction="row"
                xs={3}
                key={i}
                alignItems="stretch"
              >
                <Grid item xs={12} key={i}>
                  <Card
                    key={i}
                    className={classes.root}
                    style={{ maxHeight: "300px" }}
                  >
                    <CardActionArea>
                      <div
                        style={{ display: "flex", justifyContent: "center" }}
                      >
                        <CardMedia
                          style={{
                            width: "auto",
                            maxHeight: "200px",
                          }}
                          component="img"
                          src={menuDrink.imageUrl}
                          title="Contemplative Reptile"
                        />
                      </div>
                      <CardContent>
                        <Typography gutterBottom variant="h5" component="h2">
                          {toCapitalizedWords(menuDrink.name)}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="textSecondary"
                          component="p"
                        >
                          {menuDrink.description}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="textSecondary"
                          component="p"
                        >
                          {menuDrink.price}
                        </Typography>
                      </CardContent>
                    </CardActionArea>
                    {/* <CardActions>
            <Button size="small" color="primary">
              Share
            </Button>
            <Button size="small" color="primary">
              Learn More
            </Button>
          </CardActions> */}
                  </Card>
                </Grid>
              </Grid>
            );
          })}
        </Grid>
      </Paper>
    </Container>
  );
};
export default Menu;
