import { Merchant } from "../Models.js";

class Client {
  constructor() {
    this.baseUrl = "http://0.0.0.0:5000";
    this.url = "";
  }
  async makeRequest(method, path, data, headersParam = false, isForm = false) {
    console.log("method", method);
    let requestData = data || {};
    console.log("data", data);
    try {
      this.url = this.baseUrl + path;
      console.log("baseUrl", this.url);
      var requestHeaders = false;
      if (headersParam) {
        requestHeaders = new Headers();
        for (const [key, value] of Object.entries(headersParam)) {
          console.log(`headers key and value: ${key}: ${value}`);
          requestHeaders.set(key, value);
        }
      }
      const response = await fetch(this.url, {
        method: method,
        body:
          method === "POST" && !isForm
            ? JSON.stringify(requestData)
            : method === "POST" && isForm
            ? requestData
            : null,
        headers: headersParam ? requestHeaders : {},
      });

      if (response.ok) {
        let responseContent = await response.json();
        console.log("response", response);
        return responseContent;
      } else {
        let body = await response.text();
        console.log(
          "APIclient.makeRequest.response.notOkay",
          response.statusText,
          body
        );
        return false;
      }
    } catch (err) {
      console.log("APIclient.makeRequest.error", err);
    }
  }
  getOrders = async () => {
    this.url = this.baseUrl + "/order";
    var headers = new Headers();
    const currentMerchant = new Merchant(
      "localStorage",
      localStorage.getItem("merchant")
    );
    console.log("currentMerchant", currentMerchant);
    // headers.set(
    //   "Authorization",
    //   "Basic " + btoa(currentMerchant.id + ":" + currentMerchant.password)
    // );
    headers.set(
      "Authorization",
      "Basic " + btoa("a:" + currentMerchant.password)
    );
    return fetch(this.url, {
      credentials: "include",
      headers: headers,
    }).then((data) => data.json());
  };
  getCustomers = async () => {
    this.url = this.baseUrl + "/customer";
    var headers = new Headers();
    const currentMerchant = new Merchant(
      "localStorage",
      localStorage.getItem("merchant")
    );
    // will uncomment this when i have added menu for new businesses
    // headers.set("Authorization", "Basic " + btoa(currentMerchant.id));
    headers.set("Authorization", "Basic " + btoa("a"));

    return fetch(this.url, {
      credentials: "include",
      headers: headers,
    }).then((data) => data.json());
  };
}
export default new Client();
