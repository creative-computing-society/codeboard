import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './Components/Navbar';
import Profile from './Components/Profile';
import Daily from './Components/Daily';
import Weekly from './Components/Weekly';
import Monthly from './Components/Monthly';
import Login from './Components/Login';
import UsernameEntry from './Components/UsernameEntry';
import './App.css';
import AuthVerify from './Components/AuthVerify';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isNewUser, setIsNewUser] = useState(false);

  const handleLogin = () => {
    if(localStorage.getItem('token'))
    setIsAuthenticated(true);
  //test commit
  };

useEffect(() => {
  handleLogin();
}, []);

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
              </Routes>
            </div>
          </>
        ) : (
          <Routes>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="/authverify" element={<AuthVerify onVerify={handleLogin} setIsNewUser={setIsNewUser} />} />
            {isNewUser && <Route path="/username" element={<UsernameEntry />} />}
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        )}
      </div>
    </Router>
  );
}

export default App;
