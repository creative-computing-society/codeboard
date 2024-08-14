import React from 'react';
import ccsLogo from '../assets/ccs_logo.png';
import '../Login.css';

const Login = ({ onLogin }) => {
  // const clientId = process.env.REACT_APP_CLIENT_ID;
  const clientId = '667465f49c13fa9047715311'; // Replace with your actual client ID

  const callbackUrl = 'https://codeboard.ccstiet.com/authverify'; // Replace with your actual callback URL if needed
  // const callbackUrl = 'http://localhost:3000/authverify';
  const handleLogin = () => {
    const authUrl = `https://auth.ccstiet.com/auth/google?clientid=${clientId}&callback=${callbackUrl}`;
    window.location.href = authUrl;
  };

  return (
    <div className="login-outer-container">
      <div className="login-container">
        <div className="logo-section">
          <img src={ccsLogo} alt="CCS Logo" className="ccs-logo" />
        </div>
        <div className="form-section">
          <h2>CCS Codeboard</h2>
          <button type="button" className="form-button ccs-login" onClick={handleLogin}>
            Login with CCS
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
