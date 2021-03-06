import React, { useState, useReducer, useEffect } from 'react';
import { Merchant, Business, setLocalStorage } from '../Models.js';
import API from '../helpers/Api.js';
import Navbar from '../Navbar.js';

import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import '../css/Signup.css';

const Signin = () => {
	const [merchant, setMerchant] = useState(null);
	const [business, setBusiness] = useState(null);
	const [redirect, setRedirect] = useState(null);
	const [errorMsg, setErrorMsg] = useState(null);
	const [authorization, setAuthorization] = useReducer((state, newState) => ({ ...state, ...newState }), {
		email: '',
		password: '',
	});
	const formChangeHandler = (event) => {
		let name = event.target.name;
		let value = event.target.value;
		setAuthorization({ [name]: value });
	};
	const validate = (form) => {
		form.classList.add('was-validated');
		return form.checkValidity();
	};

	useEffect(() => {
		//had to do this because memory leak due to component not unmounting properly
		let mount = true;
		if (mount && redirect) {
			window.location.assign(redirect);
		}

		return () => (mount = false);
	}, [redirect]);

	const onSubmit = (event) => {
		event.preventDefault();
		const form = event.target;
		if (validate(form)) {
			API.makeRequest('GET', '/merchant', false, authorization).then((response) => {
				if (response) {
					// if the username is available the response from the API will be true
					const loggedInMerchant = new Merchant('json', response);
					setLocalStorage('merchant', loggedInMerchant);
					console.log('response.headers.jwt_token', response.headers.jwt_token);

					setLocalStorage('sessionToken', response.headers.jwt_token);
					setRedirect('/home');
					// return false;
				} else {
					const newErrorMsgState = {};
					// otherwise it will be false
					newErrorMsgState['errorMsg'] = 'Invalid username or password, please try again';
					newErrorMsgState['errorDisplay'] = 'inline-block';
					setErrorMsg(newErrorMsgState);
					return false;
				}
			});
		} else {
			return false;
		}
	};
	const errorMsgStyle = {
		display: errorMsg ? errorMsg.errorDisplay : 'none',
		textAlign: 'left',
		marginTop: '0',
	};
	return (
		<>
			<Navbar />
			<div className='signupBody'>
				<div id='msform' style={{ marginTop: '5vh' }}>
					<fieldset>
						<h2 className='fs-title'>Sign in</h2>
						<Row style={{ marginTop: '10%' }}>
							<Col xs={10}>
								<div className='invalid-feedback' style={errorMsgStyle}>
									{errorMsg ? errorMsg.errorMsg : ''}
								</div>
								<Form.Label>Email</Form.Label>
								<Form.Control
									type='text'
									name='email'
									required
									onChange={(e) => {
										formChangeHandler(e);
									}}
									value={authorization.email}
								/>
							</Col>
						</Row>
						<Row>
							<Col xs={10}>
								<Form.Label>Password</Form.Label>
								<Form.Control
									type='text'
									name='password'
									required
									onChange={(e) => {
										formChangeHandler(e);
									}}
									value={authorization.password}
								/>
							</Col>
						</Row>
						<Row>
							<Col>
								<Button
									className='btn btn-primary text-center'
									style={{ marginTop: '10%' }}
									onClick={(event) => {
										onSubmit(event);
									}}
								>
									Submit
								</Button>
							</Col>
						</Row>
					</fieldset>
				</div>
			</div>
		</>
	);
};
export default Signin;
