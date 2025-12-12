import React from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import ccsLogo from '../assets/ccs_logo.png';
import SERVER_URL from '../config.js';
import completeLogin from '../utils/completeLogin.js';
import '../Login.css';

const API_URL = `${SERVER_URL}api/auth`;

const Login = ({ onLogin, setIsNewUser, setIsAuthenticated }) => {
  // const clientId = process.env.REACT_APP_CLIENT_ID;
  const clientId = '667465f49c13fa9047715311';

  const callbackUrl = 'https://codeboard.ccstiet.com/authverify';
  // const callbackUrl = 'http://localhost:3000/authverify';
  const navigate = useNavigate();

  const handleLogin = () => {
    const authUrl = `https://auth.ccstiet.com/auth/google?clientid=${clientId}&callback=${callbackUrl}`;
    window.location.href = authUrl;
  };

  const handleGoogleLogin = async (credentialResponse) => {
    try {
      const response = await fetch(`${API_URL}/google-login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: credentialResponse.credential }),
      });

      const data = await response.json();
      completeLogin(data, response.status, { navigate, onVerify: onLogin, setIsNewUser, setIsAuthenticated });
    } catch (error) {
      console.error('Google login failed:', error);
    }
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
          <div className="google-login-wrapper">
            <GoogleLogin
              onSuccess={handleGoogleLogin}
              onError={() => console.error('Google login failed')}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
