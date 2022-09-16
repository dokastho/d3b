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
        <h1>Dokasfam Auth Services</h1>
        <a href={`/accounts/${logname}/`}>signed in as {logname}</a>
        <hr />
        <br />
        

        <br />
        <a href="/accounts/create/">Create a new account</a>
        <br />
        <h3>Upload DB Schema</h3>
        <form action="/schema/?target=/" method="post" enctype="multipart/form-data">
          <label htmlFor="file">DB Schema .sqlite3 file</label><br/>
          <input type="file" id="file" name="file" required /><br/>
          <label htmlFor="dbname">DB Name</label><br/>
          <input type="text" id="dbname" name="dbname" required /><br/>
        </form>

      </div>
    )
  }
}

render(
  <Index />,
  document.getElementById('reactEntry')
)