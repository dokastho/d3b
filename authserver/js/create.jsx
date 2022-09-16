import React from 'react';
import { render } from 'react-dom';

render(
	<div>
		<h1>Create An Account</h1>
		<form action="/accounts/?target=/" method="post">
			<label htmlFor="username">Username</label><br />
			<input type="text" name="username" id="username" /><br />
			<label htmlFor="username">email</label><br />
			<input type="text" name="email" id="email" /><br />
			<label htmlFor="username">Password</label><br />
			<input type="password" name="password" id="password" /><br />
			<input type="hidden" name="operation" value="create" />
			<input type="submit" value="create" />
		</form>
	</div>,
	document.getElementById('reactEntry'),
);
