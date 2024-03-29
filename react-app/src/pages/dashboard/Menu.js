import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
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
import { BusinessItem, DrinkItem, LocalStorageManager } from "../../Models";
import Grid from "@material-ui/core/Grid";
import EditIcon from "@material-ui/icons/Edit";
import AddIcon from "@material-ui/icons/Add";
import IconButton from "@material-ui/core/IconButton";

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
  const businesses = LocalStorageManager.shared.businesses;
  const businessItems = businesses.map(
    (business) => new BusinessItem(business)
  );

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
        <Form style={{ marginTop: "2vh" }}>
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
                    {businessItems.map((businessItem, i) => (
                      <MenuItem key={i} value={i}>
                        {businessItem.name}
                        <br />
                        {businessItem.address}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Col>
              <Col
                xs={"auto"}
                style={{
                  justifyContent: "center",
                  alignItems: "center",
                  display: "flex",
                  backgroundColor: "white",
                }}
              >
                <IconButton
                  onClick={() => {
                    LocalStorageManager.shared.setItem(
                      "menu_builder_business_id",
                      businessItems[businessIndex].id
                    );
                    props.handleMenuClick();
                  }}
                  color="primary"
                >
                  <AddIcon></AddIcon>
                  <h6 style={{ marginBottom: "0", marginLeft: "1vw" }}>
                    Add to menu
                  </h6>
                </IconButton>
              </Col>
            </Form.Row>
          </FormGroup>
        </Form>
        <Grid
          container
          className={classes.gridRoot}
          spacing={2}
          xs={12}
          item={true}
        >
          {businesses.length > 0 ? (
            businesses[businessIndex].menu.map((drink, i) => {
              const menuDrink = new DrinkItem(drink);
              if (menuDrink.isActive === true) {
                return (
                  <Grid
                    container
                    align="center"
                    direction="row"
                    xs={3}
                    key={i}
                    alignItems="stretch"
                    item={true}
                  >
                    <Grid item xs={12} key={i}>
                      <Card
                        key={i}
                        className={classes.root}
                        style={{ backgroundColor: "white" }}
                      >
                        <CardActionArea>
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "flex-end",
                            }}
                          >
                            <IconButton
                              onClick={() => {
                                LocalStorageManager.shared.editDrinkId =
                                  menuDrink.id;
                                props.handleDrinkEditClick();
                              }}
                            >
                              <EditIcon></EditIcon>
                            </IconButton>
                          </div>
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "center",
                            }}
                          >
                            <CardMedia
                              style={{
                                width: "auto",
                                maxHeight: "16vh",
                                marginTop: "2vh",
                              }}
                              component="img"
                              src={menuDrink.imageUrl}
                              title="Contemplative Reptile"
                            />
                          </div>
                          <CardContent>
                            <Typography gutterBottom variant="body1">
                              {menuDrink.formattedName}
                            </Typography>

                            <Typography variant="body2" component="p">
                              {menuDrink.description}
                            </Typography>
                            <Typography
                              variant="body2"
                              component="p"
                              style={{ marginTop: "1vh" }}
                            >
                              {`$${menuDrink.price}`}
                            </Typography>
                          </CardContent>
                        </CardActionArea>
                      </Card>
                    </Grid>
                  </Grid>
                );
              } else {
                return <></>;
              }
            })
          ) : (
            <></>
          )}
        </Grid>
      </Paper>
    </Container>
  );
};
export default Menu;
