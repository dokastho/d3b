import React from 'react';
import { render } from 'react-dom';

render(
  <form action="/accounts/target=delete">
    <label htmlFor='deleteacct'>Are You Sure?</label>
    <input id="deleteacct" type="submit" value="Confirm" />
  </form>,
  document.getElementById('titlecard'),
);
