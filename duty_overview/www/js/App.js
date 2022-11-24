import { QueryClient, QueryClientProvider } from 'react-query'
import './App.css';
import Schedule from './components/schedule'
import { ChakraProvider } from '@chakra-ui/react'


const queryClient = new QueryClient()

function App() {
  return (
    <ChakraProvider>
      <QueryClientProvider client={queryClient}>
        <Schedule/>
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

      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;
