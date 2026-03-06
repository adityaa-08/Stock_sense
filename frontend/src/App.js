import { useState } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import './index.css';

function App() {
  const [page, setPage] = useState('home');

  return (
    <div>
      <Navbar page={page} setPage={setPage} />
      {page === 'home'
        ? <HomePage setPage={setPage} />
        : <AnalysisPage />
      }
    </div>
  );
}

export default App;
