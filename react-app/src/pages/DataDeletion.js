import Navbar from "../Navbar.js";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Container from "react-bootstrap/Container";
import "../css/Splash.css";

const DataDeletionHeader = () => {
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
              <h1>Data Deletion Policy</h1>
            </Col>
          </Row>
          <Row>
            <Col sm={12}>
              <h4 style={{ lineHeight: 2.0 }}>
                To have your data deleted, please email blaisebucey@utexas.edu
                with the subject "Delete Data" and provide your username in the
                email.
              </h4>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

const DataDeletion = () => {
  return (
    <>
      <Navbar backgroundColor={"#8682e6"} />
      <DataDeletionHeader />
    </>
  );
};
export default DataDeletion;
