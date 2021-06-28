import { Merchant, setLocalStorage } from "../Models.js";

class Client {
  constructor() {
    this.baseUrl = "";
    this.url = "";
  }
  async makeRequest(
    method,
    path,
    data = false,
    headersParam = false,
    isForm = false
  ) {
    let requestData = data || {};
    try {
      this.url = this.baseUrl + path;
      var requestHeaders = false;
      if (headersParam) {
        requestHeaders = new Headers();
        for (const [key, value] of Object.entries(headersParam)) {
          requestHeaders.set(key, value);
        }
      }
      const response = await fetch(this.url, {
        method: method,
        body:
          method === "POST" && !isForm && data
            ? JSON.stringify(requestData)
            : method === "POST" && isForm && data
            ? requestData
            : null,
        headers: headersParam ? requestHeaders : {},
      });

      if (response) {
        if (response.status === 500) {
          console.log(
            "APIclient.makeRequest.response.notOkay",
            response.statusText
          );
          return response.status;
        }

        var responseContent = {};
        if (response.body) {
          try {
            responseContent = await response.json();
          } catch (err) {
            console.log("err", err);
          }
        }
        const headers = {};
        for (const [key, value] of response.headers.entries()) {
          headers[key] = value;
        }
        responseContent.headers = headers;
        responseContent.status = response.status;
        return responseContent;
      } else {
        console.log("network error");
        return false;
      }
    } catch (err) {
      console.log(
        "APIclient.makeRequest.error, the response probably didnt have a body so it failed in turning it into JSON so ignore this",
        err
      );
      return false;
    }
  }
  // this is hitting the same endpoint as the api request made to verify that the merchant email is not taken when the merchant is signing up
  getMerchant = async (credentials) => {
    this.url = this.baseUrl + "/merchant";
    var requestHeaders = new Headers();
    for (const [key, value] of Object.entries(credentials)) {
      requestHeaders.set(key, value);
    }
    const response = await fetch(this.url, {
      headers: requestHeaders,
    });
    const headers = {};
        for (const [key, value] of response.headers.entries()) {
          headers[key] = value;
        }
    if (response.status === 204) {
      console.log('response status 204 to log in merchant')
      return false;
    } else {
      const loggedInMerchant = new Merchant("json", await response.json());
      console.log("loggedInMerchant", loggedInMerchant);

      setLocalStorage("merchant", loggedInMerchant);
      console.log("response.headers.jwt_token", headers.jwt_token);

      setLocalStorage("sessionToken", headers.jwt_token);
      return true;
    }
  };
  getOrders = async () => {
    console.log('ORDERS JSON.parse(localStorage.getItem("sessionToken"))',JSON.parse(localStorage.getItem("sessionToken")))
    this.url =
      this.baseUrl +
      "/order/" +
      JSON.parse(localStorage.getItem("sessionToken"));
    console.log("this.url", this.url);

    var headers = new Headers();
    const currentMerchant = new Merchant(
      "localStorage",
      localStorage.getItem("merchant")
    );
    console.log("currentMerchant", currentMerchant);
    headers.set(
      "Authorization",
      "Basic " + btoa(currentMerchant.id + ":" + currentMerchant.password)
    );
    headers.set("filterBy", "merchant");
    return fetch(this.url, {
      credentials: "include",
      headers: headers,
    }).then((data) => data.json());
  };
  getCustomers = async () => {
    this.url =
      this.baseUrl +
      "/customer?sessionToken=" +
      JSON.parse(localStorage.getItem("sessionToken"));
    console.log("this.url", this.url);

    var headers = new Headers();
    const currentMerchant = new Merchant(
      "localStorage",
      localStorage.getItem("merchant")
    );
    // will uncomment this when i have added menu for new businesses
    headers.set("Authorization", "Basic " + btoa(currentMerchant.id));
    return fetch(this.url, {
      credentials: "include",
      headers: headers,
    }).then((data) => data.json());
  };
  checkStripeStatus = async () => {
    const currentMerchant = new Merchant(
      "localStorage",
      localStorage.getItem("merchant")
    );
    this.url =
      this.baseUrl +
      `/validate-merchant-stripe-account?stripe=${currentMerchant.stripeId}`;
    // will uncomment this when i have added menu for new businesses
    const response = await fetch(this.url, {});
    if (response.status === 200) {
      console.log("merchant stripe id good");
      return true;
    } else {
      console.log("merchant stripe id bad");
      return false;
    }
  };
  getBusinesses = async () => {
    this.url =
      this.baseUrl +
      "/business/" +
      JSON.parse(localStorage.getItem("sessionToken"));
    var headers = new Headers();
    const currentMerchant = new Merchant(
      "localStorage",
      localStorage.getItem("merchant")
    );
    // will uncomment this when i have added menu for new businesses
    console.log('currentMerchant in business',currentMerchant)
    headers.set("merchantId", currentMerchant.id);
    return fetch(this.url, {
      headers: headers,
    }).then((data) => data.json());
  };
}
export default new Client();
