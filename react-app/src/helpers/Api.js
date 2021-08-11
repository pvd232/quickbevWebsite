import { Merchant, LocalStorageManager } from "../Models.js";

class Client {
  constructor() {
    this.baseUrl = "https://quickbev.us";
    // this.mode = "cors";
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
      const request = new Request(this.url);
      var requestHeaders = false;
      if (headersParam) {
        console.log('headersParam',headersParam)
        requestHeaders = new Headers();
        for (const [key, value] of Object.entries(headersParam)) {
          requestHeaders.set(key, value);
        }
      }
      const response = await fetch(request, {
        method: method,
        body:
          method === "POST" && !isForm && data
            ? JSON.stringify(requestData)
            : method === "PUT" && !isForm && data
            ? JSON.stringify(requestData)
            : method === "POST" && isForm && data
            ? requestData
            : null,
        headers: headersParam ? requestHeaders : {},
        mode: this.mode,
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
    const requestUrl = this.baseUrl + "/merchant";
    const requestHeaders = new Headers();
    for (const [key, value] of Object.entries(credentials)) {
      requestHeaders.set(key, value);
    }
    const request = new Request(requestUrl);
    const requestParams = {
      method: "GET",
      headers: requestHeaders,
      mode: this.mode,
      cache: "default",
    };
    const response = await fetch(request, requestParams);

    const headers = {};
    for (const [key, value] of response.headers.entries()) {
      headers[key] = value;
    }
    if (response.status === 204) {
      return false;
    } else {
      const loggedInMerchant = new Merchant("json", await response.json());
      LocalStorageManager.shared.setLocalStorage("merchant", loggedInMerchant);
      LocalStorageManager.shared.setLocalStorage(
        "session_token",
        headers.jwt_token
      );
      return true;
    }
  };
  getOrders = async () => {
    this.url =
      this.baseUrl + "/order/" + LocalStorageManager.shared.sessionToken;

    const headers = new Headers();
    headers.set(
      "Authorization",
      "Basic " +
        btoa(
          LocalStorageManager.shared.currentMerchant.id +
            ":" +
            LocalStorageManager.shared.currentMerchant.password
        )
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
      "/customer?session_token=" +
      LocalStorageManager.shared.sessionToken;
    console.log("this.url", this.url);

    const headers = new Headers();
    // will uncomment this when i have added menu for new businesses
    headers.set(
      "Authorization",
      "Basic " + btoa(LocalStorageManager.shared.currentMerchant.id)
    );
    return fetch(this.url, {
      credentials: "include",
      headers: headers,
    }).then((data) => data.json());
  };
  getMerchantEmployees = async () => {
    this.url =
      this.baseUrl +
      "/merchant_employee/" +
      LocalStorageManager.shared.sessionToken;

    const requestHeaders = new Headers();
    const myRequest = new Request(this.url);
    requestHeaders.set(
      "merchant-id",
      LocalStorageManager.shared.currentMerchant.id
    );

    const requestParams = {
      method: "GET",
      headers: requestHeaders,
      mode: this.mode,
      cache: "default",
    };
    return fetch(myRequest, requestParams).then((data) => data.json());
  };
  getQuickPasses = async (businessId) => {
    this.url =
      this.baseUrl +
      "/quick_pass/bouncer"

    const requestHeaders = new Headers();
    const myRequest = new Request(this.url);
    requestHeaders.set(
      "business-id",
      businessId
    );

    const requestParams = {
      method: "GET",
      headers: requestHeaders,
      mode: this.mode,
      cache: "default",
    };
    return fetch(myRequest, requestParams).then((data) => data.json());
  };
  getBouncers = async () => {
    this.url =
      this.baseUrl + "/bouncer/" + LocalStorageManager.shared.sessionToken;

    const requestHeaders = new Headers();
    const myRequest = new Request(this.url);
    requestHeaders.set(
      "merchant-id",
      LocalStorageManager.shared.currentMerchant.id
    );

    const requestParams = {
      method: "GET",
      headers: requestHeaders,
      mode: this.mode,
      cache: "default",
    };
    return fetch(myRequest, requestParams).then((data) => data.json());
  };
  checkStripeStatus = async () => {
    this.url =
      this.baseUrl +
      `/validate-merchant-stripe-account?stripe=${LocalStorageManager.shared.currentMerchant.stripeId}`;

    const requestParams = {
      method: "GET",
      mode: this.mode,
      cache: "default",
    };
    // will uncomment this when i have added menu for new businesses
    const response = await fetch(this.url, requestParams);
    if (response.status === 200) {
      return true;
    } else {
      return false;
    }
  };
  checkTokenStatus = async (sessionToken) => {
    this.url =
      this.baseUrl + `/bouncer/verify_jwt?session_token=${sessionToken}`;

    const requestParams = {
      method: "GET",
      mode: this.mode,
      cache: "default",
    };
    // will uncomment this when i have added menu for new businesses
    const response = await fetch(this.url, requestParams);
    if (response.status === 200) {
      return true;
    } else {
      return false;
    }
  };
  getBusinesses = async () => {
    this.url =
      this.baseUrl + "/business/" + LocalStorageManager.shared.sessionToken;
    const headers = new Headers();
    // will uncomment this when i have added menu for new businesses
    headers.set("merchant-id", LocalStorageManager.shared.currentMerchant.id);

    return fetch(this.url, {
      headers: headers,
      mode: this.mode,
    }).then((data) => data.json());
  };
}
export default new Client();
