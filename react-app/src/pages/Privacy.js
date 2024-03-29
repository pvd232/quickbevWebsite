import Navbar from "../Navbar.js";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Container from "react-bootstrap/Container";
import "../css/Splash.css";

const PrivacyHeader = () => {
  return (
    <Container fluid className="splashBody">
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
              <h1>Privacy Policy</h1>
            </Col>
          </Row>
          <Row>
            <Col sm={12}>
              <h4 style={{ lineHeight: 2.0 }}>
                Information that is gathered from visitors in common with other
                websites, log files are stored on the web server saving details
                such as the visitor's IP address, browser type, referring page
                and time of visit. Cookies may be used to remember visitor
                preferences when interacting with the website. Where
                registration is required, the visitor's email and a username
                will be stored on the server. How the Information is used The
                information is used to enhance the vistor's experience when
                using the website to display personalised content and possibly
                advertising. E-mail addresses will not be sold, rented or leased
                to 3rd parties. E-mail may be sent to inform you of news of our
                services or offers by us or our affiliates. Visitor Options If
                you have subscribed to one of our services, you may unsubscribe
                by following the instructions which are included in e-mail that
                you receive. You may be able to block cookies via your browser
                settings but this may prevent you from access to certain
                features of the website. Cookies Cookies are small digital
                signature files that are stored by your web browser that allow
                your preferences to be recorded when visiting the website. Also
                they may be used to track your return visits to the website. 3rd
                party advertising companies may also use cookies for tracking
                purposes.
              </h4>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

const Privacy = () => {
  return (
    <>
      <Navbar backgroundColor={"#8682e6"} />
      <PrivacyHeader />
    </>
  );
};
export default Privacy;
