import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SERVER_URL from "../config.js";
import completeLogin from '../utils/completeLogin.js';

const API_URL = `${SERVER_URL}api/auth`;

const AuthVerify = ({ onVerify, setIsNewUser, setIsAuthenticated }) => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const verifyUser = async () => {
      const query = new URLSearchParams(location.search);
      const jwtToken = query.get('token');

      if (jwtToken) {
        // console.log('JWT Token:', jwtToken);

        const requestBody = { token: jwtToken };

        try {
          const response = await fetch(`${API_URL}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody),
          });

          const data = await response.json();
          const status = response.status;

          completeLogin(data, status, { navigate, onVerify, setIsNewUser, setIsAuthenticated, jwtToken });
        } catch (error) {
          console.error('Error checking user:', error);
          navigate('/login');
          // console.log('Navigated to /login2');
        }
      } else {
        navigate('/login');
        // console.log('Navigated to /login3');
      }
    };

    verifyUser();
  }, [navigate, location, onVerify, setIsNewUser, setIsAuthenticated]);

  return <div>Loading...</div>;
};

export default AuthVerify;
