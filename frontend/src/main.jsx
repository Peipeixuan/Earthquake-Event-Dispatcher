import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { BrowserRouter, Routes, Route } from 'react-router';
import Simulation from './pages/simulation.jsx';
import AlertReport from './pages/alert-report.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/simulation" element={<Simulation />} />
        <Route path="/alert" element={<AlertReport />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
