import React from 'react';
import { render } from 'react-dom';

render(
	<div>
		<h1>Create An Account</h1>
		<form action="/accounts/?target=create">
			<label htmlFor="username">Username</label>
			<input type="text" id="username" />
			<label htmlFor="username">Password</label>
			<input type="text" id="password" />
			<input type="hidden" id="operation" value="create" />
			<input type="submit" value="create" />
		</form>
	</div>,
	document.getElementById('titlecard'),
);
