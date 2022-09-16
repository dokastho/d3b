import React from 'react';
import { render } from 'react-dom';

render(
  <div>
		<h1>Log In</h1>
		<form action="/accounts/target=/" method="post">
			<input type="hidden" name="operation" value="login" />
			<label htmlFor="uname">Username</label><br />
			<input type="text" name="uname" id="uname" /><br />
			<label htmlFor="pword">Password</label><br />
			<input type="password" name="pword" id="pword" /><br />
			<input type="submit" value="log in" /><br />
		</form>
	</div>,
	document.getElementById("reactEntry"),
);
