import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
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

  const handleLogin = () => {
    if (localStorage.getItem('token')) {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    const savedIsNewUser = localStorage.getItem('isNewUser');
    if (savedIsNewUser) {
      setIsNewUser(JSON.parse(savedIsNewUser));
    }
    handleLogin();
  }, []);

  useEffect(() => {
    localStorage.setItem('isNewUser', JSON.stringify(isNewUser));
  }, [isNewUser]);

  console.log('Is Authenticated:', isAuthenticated);

  return (
    <Router>
      <div className="app-container">
        {isAuthenticated ? (
          <>
            <Navbar />
            <div className="content">
              <Routes>
                {isNewUser ? (
                  <Route path="/username" element={<UsernameEntry />} />
                ) : (
                  <>
                    <Route path="/" element={<Profile />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/daily" element={<Daily />} />
                    <Route path="/weekly" element={<Weekly />} />
                    <Route path="/monthly" element={<Monthly />} />
                  </>
                )}
                <Route path="*" element={<Navigate to={isNewUser ? "/username" : "/profile"} />} />
              </Routes>
            </div>
          </>
        ) : (
          <Routes>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="/authverify" element={<AuthVerify onVerify={handleLogin} setIsNewUser={setIsNewUser} />} />
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        )}
      </div>
    </Router>
  );
}

export default App;
