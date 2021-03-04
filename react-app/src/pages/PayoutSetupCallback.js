import Form from "react-bootstrap/Form";
import PayoutSetup from "./PayoutSetup.js";
import "../css/Signup.css";

const payoutSetupCallback = () => {
  return (
    <div className="signupBody">
      <div id="msform">
        <Form>
          <fieldset>
            <PayoutSetup callback={true}></PayoutSetup>
          </fieldset>
        </Form>
      </div>
    </div>
  );
};
export default payoutSetupCallback;
