import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SERVER_URL from "../config.js";

const API_URL = `${SERVER_URL}api/auth`;

const AuthVerify = ({ onVerify, setIsNewUser, setIsAuthenticated }) => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const verifyUser = async () => {
      const query = new URLSearchParams(location.search);
      const jwtToken = query.get('token');

      if (jwtToken) {
        console.log('JWT Token:', jwtToken);

        const requestBody = { token: jwtToken };

        try {
          const response = await fetch(`${API_URL}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody),
          });

          const data = await response.json();
          const status = response.status;

          console.log('Response Status:', status);
          console.log('Response Data:', data);

          if (data.leetcode === false) {
            setIsNewUser(true);
            onVerify();
            const userData = {
              rollNo: data.user.roll_no,
              email: data.user.email,
              branch: data.user.branch,
              fullName: `${data.user.first_name} ${data.user.last_name}`
            };
            setIsAuthenticated(true); // Set isAuthenticated to true
            navigate('/username', { state: { jwtToken, userData, token: data.token } });
            console.log('Navigated to /username');
          } else if (status === 200 && data.token) {
            localStorage.setItem('token', data.token);
            console.log('Token stored in localStorage:', localStorage.getItem('token'));
            onVerify();
            setIsAuthenticated(true); // Set isAuthenticated to true
            navigate('/profile');
            console.log('Navigated to /profile');
          } else {
            console.error(`Unexpected response: ${JSON.stringify(data)}`);
            navigate('/login');
            console.log('Navigated to /login1');
          }
        } catch (error) {
          console.error('Error checking user:', error);
          navigate('/login');
          console.log('Navigated to /login2');
        }
      } else {
        navigate('/login');
        console.log('Navigated to /login3');
      }
    };

    verifyUser();
  }, [navigate, location, onVerify, setIsNewUser, setIsAuthenticated]);

  return <div>Loading...</div>;
};

export default AuthVerify;
