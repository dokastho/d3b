import React from 'react';
import { render } from 'react-dom';

class Index extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      logname: "",
      schemas: []
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
          schemas: data.schemas
        });
      })
      .catch((error) => console.log(error));
  }


  deleteSchema(id) {
    fetch(`/schema/delete/${id}/`, { credentials: 'same-origin', method: 'POST' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        // return response.json();
      })
      .then(() => {
        const { schemas } = this.state;
        this.setState({
          schemas: schemas.filter(function(s) { 
            return s.id !== id 
        })});
      })
      .catch((error) => console.log(error));
  }


  render() {
    const { logname, schemas } = this.state;
    return (
      <div>
        <h1>Dokasfam Auth Services</h1>
        <a href={`/user/${logname}/`}>signed in as {logname}</a>
        <hr />
        <br />


        <br />
        <a href="/accounts/create/">Create a new account</a>
        <br />
        <h3>Upload DB Schema</h3>
        <form action="/schema/?target=/" method="post" enctype="multipart/form-data">
          <input type="hidden" name="operation" value="create" />
          <label htmlFor="file">DB Schema .sqlite3 file</label><br />
          <input type="file" id="file" name="file" required /><br />
          <label htmlFor="dbname">DB Name</label><br />
          <input type="text" id="dbname" name="dbname" required /><br />
          <input type="submit" />
        </form>

        <br />

        {
          schemas.map((s) => (
            <div className="row" key={s.id}>
              <span>
                {s.name}&#9;{s.created}&#9;
              </span>
              <button className="deletebtn" onClick={() => this.deleteSchema(s.id)}>x</button>
            </div>
          ))
        }

      </div>
    )
  }
}

render(
  <Index />,
  document.getElementById('reactEntry')
)