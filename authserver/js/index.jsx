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

      </div>
    )
  }
}

render(
  <Index />,
  document.getElementById('reactEntry')
)