import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SERVER_URL from "../config.js";
const API_URL = SERVER_URL+'api/auth';
const AuthVerify = ({ onVerify, setIsNewUser }) => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    const jwtToken = query.get('token');

    if (jwtToken) {
      console.log('JWT Token:', jwtToken);

      const requestBody = {
        token: jwtToken,
      };

      console.log('Request Body:', requestBody);

      fetch(`${API_URL}/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })
        .then(response => {
          console.log('Response Status:', response.status);
          return response.json().then(data => ({ status: response.status, data }));
        })
        .then(({ status, data }) => {
          console.log('Response Data:', data);
          if (status === 400) {
            if (data.leetcode === false) {
              setIsNewUser(true);
              navigate('/username', { state: { jwtToken } }); // Pass the JWT token as state
            } else {
              throw new Error('Unexpected error format');
            }
          } else if (status === 200) {
            if (data && data.token) {
              localStorage.setItem('token', data.token); // Save token locally
              console.log('Token stored in localStorage:', localStorage.getItem('token'));
               // Log the stored token
              onVerify();
              navigate('/profile');
            } else {
              throw new Error('Token not found in response');
            }
          } else {
            throw new Error(`Unexpected response status: ${status}`);
          }
        })
        .catch(error => {
          console.error('Error checking user:', error);
          // Handle error (e.g., show a notification)
          navigate('/login'); // Navigate to login page on error
        });
    } else {
      navigate('/login'); // Navigate to login page if no token found
    }
  }, [navigate, location, onVerify, setIsNewUser]);

  return <div>Loading...</div>;
};

export default AuthVerify;
