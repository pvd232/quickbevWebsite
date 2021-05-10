import MerchantEmployeePayoutSetup from "./MerchantEmployeePayoutSetup.js";
import "../css/Signup.css";

const MerchantEmployeePayoutSetupCallback = () => {
  return (
    <div className="signupBody">
      <div id="msform">
        <fieldset>
          <MerchantEmployeePayoutSetup
            callback={true}
          ></MerchantEmployeePayoutSetup>
        </fieldset>
      </div>
    </div>
  );
};
export default MerchantEmployeePayoutSetupCallback;
