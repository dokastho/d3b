import React from 'react';
import { render } from 'react-dom';

render(
  <div>
    <h1>Account Settings</h1>
    <form action="/accounts/logout/" method="post">
      <input type="submit" value="logout" />
    </form>
    <br />
    <a href="/accounts/password/">Change password</a><br />
    <a href="/accounts/delete/">Delete account</a><br />
  </div>,
  document.getElementById("reactEntry"),
);