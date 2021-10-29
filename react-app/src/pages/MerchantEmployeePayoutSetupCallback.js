import MerchantEmployeePayoutSetup from "./MerchantEmployeePayoutSetup.js";
import "../css/Signup.css";
import { useParams } from "react-router-dom";

const MerchantEmployeePayoutSetupCallback = () => {
  let { merchantEmployeeId } = useParams();
  return (
    <div className="signupBody">
      <div id="msform">
        <fieldset>
          <MerchantEmployeePayoutSetup
            callback={true}
            merchantEmployeeId={merchantEmployeeId}
          ></MerchantEmployeePayoutSetup>
        </fieldset>
      </div>
    </div>
  );
};
export default MerchantEmployeePayoutSetupCallback;
