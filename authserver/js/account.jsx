import React from 'react';
import { render } from 'react-dom';

render(
  <div>
    <h1>Account Settings</h1>
    <form target="/accounts/logout/" method="post">
      <input type="submit" value="logout" />
    </form>
    <a href="/accounts/?target=password">Change password</a><br />
    <a href="/accounts/?target=delete">Delete account</a><br />
  </div>
)