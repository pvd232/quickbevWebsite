import { Merchant } from '../Models.js';

class Client {
	constructor() {
		this.baseUrl = 'http://localhost:8080';
		this.url = '';
	}
	async makeRequest(method, path, data = false, headersParam = false, isForm = false) {
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
					method === 'POST' && !isForm && data
						? JSON.stringify(requestData)
						: method === 'POST' && isForm && data
						? requestData
						: null,
				headers: headersParam ? requestHeaders : {},
			});

			if (response.ok) {
				var responseContent = {};
				if (response.body) {
					try {
						responseContent = await response.json();
					} catch (err) {
						console.log('error turning response content into json', err);
					}
				}
				const headers = {};
				for (const [key, value] of response.headers.entries()) {
					headers[key] = value;
				}
				responseContent.headers = headers;
				return responseContent;
			} else {
				let body = await response.text();
				console.log('APIclient.makeRequest.response.notOkay', response.statusText, body);
				return false;
			}
		} catch (err) {
			console.log(
				'APIclient.makeRequest.error, the response probably didnt have a body so it failed in turning it into JSON so ignore this',
				err
			);
		}
	}
	getOrders = async () => {
		this.url = this.baseUrl + '/order/' + JSON.parse(localStorage.getItem('sessionToken'));
		console.log('this.url', this.url);

		var headers = new Headers();
		const currentMerchant = new Merchant('localStorage', localStorage.getItem('merchant'));
		console.log('currentMerchant', currentMerchant);
		headers.set('Authorization', 'Basic ' + btoa(currentMerchant.id + ':' + currentMerchant.password));
		return fetch(this.url, {
			credentials: 'include',
			headers: headers,
		}).then((data) => data.json());
	};
	getCustomers = async () => {
		this.url = this.baseUrl + '/customer/' + JSON.parse(localStorage.getItem('sessionToken'));
		console.log('this.url', this.url);

		var headers = new Headers();
		const currentMerchant = new Merchant('localStorage', localStorage.getItem('merchant'));
		// will uncomment this when i have added menu for new businesses
		headers.set('Authorization', 'Basic ' + btoa(currentMerchant.id));
		return fetch(this.url, {
			credentials: 'include',
			headers: headers,
		}).then((data) => data.json());
	};
}
export default new Client();
