import React from 'react';
import { render } from 'react-dom';

class Index extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      logname: ""
    }
  }

  componentDidMount() {
    fetch('/api/v1/whoami/', { credentials: 'same-origin', method: 'POST' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(data);
        this.setState({
          logname: data.logname,
        });
      })
      .catch((error) => console.log(error));
  }


  render() {
    const { logname } = this.state;
    return (
      <div>
        {logname === "" ? <a href="/accounts/login/">log in</a>
          : <a href={`/accounts/${logname}/`}>signed in as {logname}</a>}

        <br />
        <a href="/accounts/create/">Create a new account</a>
        <br />
        <form action="/upload/?target=/" method="post" enctype="multipart/form-data">
          <label htmlFor="schema">DB Schema .sqlite3 file</label><br/>
          <input type="file" id="schema" name="file" required /><br/>
          <label htmlFor="dbfile">DB Name</label><br/>
          <input type="text" id="dbfile" name="dbname" required /><br/>
        </form>

      </div>
    )
  }
}

render(
  <Index />,
  document.getElementById('reactEntry')
)