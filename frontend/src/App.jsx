import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import VibePage from './pages/VibePage';
import AboutPage from './pages/AboutPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-900 text-white font-sans selection:bg-purple-500 selection:text-white">
        <Routes>
          <Route path="/" element={<AboutPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/vibe" element={<VibePage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
