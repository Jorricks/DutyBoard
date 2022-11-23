import './App.css';
import { useGetSchedule } from "./api";

function App() {

  const { data: { calendars, persons } } = useGetSchedule();
  console.log(calendars);
  console.log(persons);
  return (
    <div className="App">
      <header className="App-header">
        <img src="/logo512.png" className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
