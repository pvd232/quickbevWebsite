import Navbar from "../Navbar.js";
import Row from "react-bootstrap/Row";
import Button from "react-bootstrap/Button";
import { Link } from "react-router-dom";
import Col from "react-bootstrap/Col";
import Container from "react-bootstrap/Container";
import "../css/Splash.css";
import ipadIcon from "../static/ipad-icon.png";
import dollarIcon from "../static/dollar-icon.png";
import timeIcon from "../static/time-icon.png";
import starIcon from "../static/star-icon.png";
import healthIcon from "../static/health-icon.png";

const SplashHeader = () => {
  return (
    <Container fluid className="splashHeader">
      <Row
        style={{
          width: "100vw",
          display: "flex",
          marginTop: "50px",
          marginBottom: "50px",
        }}
      >
        <Col xs={8} style={{ justifySelf: "center", alignSelf: "center" }}>
          <Row>
            <Col sm={12}>
              <h1>We all deserve a drink in 2021</h1>
            </Col>
          </Row>
          <Row>
            <Col sm={12}>
              <h4>
                QuickBev is leading technological innovation in the Bar &
                Nightclub industry
              </h4>
            </Col>
          </Row>
          <Row>
            <Col sm={12}>
              <Link to="/signup">
                <Button className="action-button">Become a Merchant</Button>
              </Link>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};
const SplashBody = () => {
  return (
    <Container fluid className="splashBody">
      <Row
        style={{
          width: "100vw",
          justifySelf: "center",
          alignSelf: "flex-start",
        }}
      >
        <Col sm={1}></Col>
        <Col sm={10}>
          <Row style={{ alignItems: "flex-start" }}>
            <Col>
              <img src={timeIcon} className="time-icon" alt="$"></img>
              <h4
                style={{
                  width: "100%",
                  textAlign: "center",
                }}
              >
                Decrease wait times
              </h4>
              <p className="solutionDescription">
                Have you ever had to wait thirty minutes to get a drink? It
                isn't fun, and it can ruin the customer experience. QuickBev
                solves this problem by allowing customers to effortlessly,
                instantly order from their phones.
              </p>
            </Col>
            <Col>
              <img src={dollarIcon} className="dollar-icon" alt="$"></img>
              <h4
                style={{
                  width: "100%",
                  textAlign: "center",
                }}
              >
                Increase Revenue
              </h4>
              <p className="solutionDescription">
                Long wait times aren't just a bummer, they{" "}
                <strong> drastically reduce your sales.</strong> QuickBev
                empowers businesses, servers, and consumers by offloading the
                ordering process back onto consumers. You get paid first, and
                deliver your drinks later.
              </p>
            </Col>
            <Col>
              <img src={ipadIcon} className="ipad-icon" alt="NA"></img>
              <h4
                style={{
                  width: "100%",
                  textAlign: "center",
                }}
              >
                Measure performance
              </h4>
              <p className="solutionDescription">
                The QuickBev platform provides our merchant partners with nifty
                dashboard to analyze their sales and gain an edge over
                competitors. You will be constantly reminded of how much revenue
                we generate for you.
              </p>
            </Col>
          </Row>
        </Col>
        <Col sm={1}></Col>
        <Row style={{ alignItems: "flex-start" }}>
          <Col></Col>
          <Col sm={7}>
            <Row
              style={{
                alignItems: "flex-start",
                justifySelf: "center",
              }}
            >
              <Col>
                <img src={healthIcon} className="health-icon" alt="$"></img>
                <h4
                  style={{
                    width: "100%",
                    textAlign: "center",
                  }}
                >
                  Promote social distance
                </h4>
                <p className="solutionDescription">
                  Waiting in line isn't just huring your sales and customer
                  experience, its probably leading to the spread of COVID-19.
                  People in lines tend to cluster together. Using QuickBev
                  naturally eliminates this health hazard.
                </p>
              </Col>
              <Col>
                <img src={starIcon} className="star-icon" alt="NA"></img>
                <h4
                  style={{
                    width: "100%",
                    textAlign: "center",
                  }}
                >
                  Personalized marketing
                </h4>
                <p className="solutionDescription">
                  Have you ever wanted to get the word out about a happy hour
                  using more than just a sign? The QuickBev platform allows you
                  to export your customer data for personalized marketing
                  campaigns.
                </p>
              </Col>
            </Row>
          </Col>
          <Col></Col>
        </Row>
      </Row>
    </Container>
  );
};
const Splash = () => {
  return (
    <>
      <Navbar backgroundColor={"#8682e6"} />
      <SplashHeader />
      <SplashBody />
    </>
  );
};
export default Splash;
