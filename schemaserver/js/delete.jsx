import React from 'react';
import { render } from 'react-dom';

render(
  <form action="/accounts/?target=/" method="post">
    <input type="hidden" name="operation" value="delete" />
    <label htmlFor='deleteacct'>Are You Sure?</label>
    <input id="deleteacct" type="submit" value="Confirm" />
  </form>,
  document.getElementById('reactEntry'),
);
