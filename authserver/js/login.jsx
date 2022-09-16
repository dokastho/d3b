import React from 'react';
import { render } from 'react-dom';

render(
  <div>
		<h1>Log In</h1>
		<form action="/accounts/?target=/" method="post">
			<input type="hidden" name="operation" value="login" />
			<label htmlFor="username">Username</label><br />
			<input type="text" name="username" id="username" /><br />
			<label htmlFor="password">Password</label><br />
			<input type="password" name="password" id="password" /><br />
			<input type="submit" value="log in" /><br />
		</form>
	</div>,
	document.getElementById("reactEntry"),
);
