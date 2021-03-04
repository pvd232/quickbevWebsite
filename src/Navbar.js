import { Link } from "react-router-dom";
import { ReactComponent as Logo } from "./static/landscapelogo.svg";
const Navbar = (props) => {
  var navbarCenteredStyle;
  if (props) {
    navbarCenteredStyle = {
      minWidth: "auto",
      minHeight: "150px",

      marginBottom: "auto",
      marginTop: "auto",
      backgroundColor: props.backgroundColor,
    };
  } else {
    navbarCenteredStyle = {
      minWidth: "auto",
      minHeight: "150px",
      marginBottom: "auto",
      marginTop: "auto",
    };
  }
  return (
    <nav
      className="header-navbar navbar-dark navbar-expand-lg"
      style={navbarCenteredStyle}
    >
      <button
        className="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarTogglerDemo02"
        aria-controls="navbarTogglerDemo02"
        aria-expanded="false"
        aria-label="Toggle navigation"
        style={{ color: "black", marginTop: "20px" }}
      >
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className="collapse navbar-collapse" id="navbarTogglerDemo02">
        <ul
          className="navbar-nav"
          style={{
            position: "relative",
            marginLeft: "50vw",
            transform: "translateX(-50%)",
            marginBottom: "20px",
            marginTop: "40px",
            alignItems: "center",
          }}
        >
          <li className="nav-item px-3">
            <Link to="/">
              <Logo />
            </Link>
          </li>
        </ul>
        <ul className="navbar-nav ml-auto" style={{ alignItems: "center" }}>
          <li className="nav-item px-3">
            <Link to="/signin" className="nav-link navbar-link-size">
              Sign in
            </Link>
          </li>
          <li className="nav-item px-3">
            <Link to="/signup" className="nav-link navbar-link-size">
              Sign up
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};
export default Navbar;
