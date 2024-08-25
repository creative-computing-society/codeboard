import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './Components/Navbar';
import Profile from './Components/Profile';
import Daily from './Components/Daily';
import Weekly from './Components/Weekly';
import Monthly from './Components/Monthly';
import Login from './Components/Login';
import AuthVerify from './Components/AuthVerify';
import UsernameEntry from './Components/UsernameEntry';
import './App.css';

function App() {
  const [isNewUser, setIsNewUser] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = async () => {
    if (localStorage.getItem('token')) {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    handleLogin();
  }, []);

  console.log('Is Authenticated:', isAuthenticated);

  return (
    <Router>
      <div className="app-container">
        {isAuthenticated ? (
          <>
            <Navbar />
            <div className="content">
              <Routes>
                <Route path="/" element={<Profile />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/daily" element={<Daily />} />
                <Route path="/weekly" element={<Weekly />} />
                <Route path="/monthly" element={<Monthly />} />
                <Route path="*" element={<Navigate to="/profile" />} />
                
                <Route path="/authverify" element={<AuthVerify onVerify={handleLogin} setIsNewUser={setIsNewUser} setIsAuthenticated={setIsAuthenticated} />} />
                {isNewUser && <Route path="/username" element={<UsernameEntry setIsAuthenticated={setIsAuthenticated} />} />}
              </Routes>
            </div>
          </>
        ) : (
          <Routes>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="/authverify" element={<AuthVerify onVerify={handleLogin} setIsNewUser={setIsNewUser} setIsAuthenticated={setIsAuthenticated} />} />
            {isNewUser && <Route path="/username" element={<UsernameEntry setIsAuthenticated={setIsAuthenticated} />} />}
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        )}
      </div>
    </Router>
  );
}

export default App;