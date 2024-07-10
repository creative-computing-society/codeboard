import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SERVER_URL from "../config.js";
const API_URL = SERVER_URL + 'api/auth';

const UsernameEntry = () => {
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { jwtToken: stateJwtToken } = location.state || {}; // Retrieve the JWT token from the location state
  const [jwtToken, setJwtToken] = useState(stateJwtToken);

  useEffect(() => {
    if (!stateJwtToken) {
      console.error('JWT token is missing from state');
      navigate('/login'); // Navigate to login page if JWT token is missing from state
    } else {
      setJwtToken(stateJwtToken);
    }
  }, [navigate, stateJwtToken]);

  const handleUsernameChange = (e) => {
    setLeetcodeUsername(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!jwtToken) {
      console.error('JWT token is missing');
      navigate('/login'); // Navigate to login page if JWT token is missing
      return;
    }

    // Define the request payload
    const payload = {
      leetcode_username: leetcodeUsername,
      token: jwtToken
    };

    // Define the request options
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwtToken}`
      },
      body: JSON.stringify(payload)
    };

    // Make the API call
    fetch(`${API_URL}/login/`, requestOptions)   //CHANGE THIS ABCK TO fetch(`${API_URL}/login/`, requestOptions) 
      .then(response => response.json())
      .then(data => {
        // Handle response
        console.log('Success:', data);
        // Navigate to the desired page
        navigate('/profile');
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  return (
    <div>
      <h2>Enter Username</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Username:
          <input type="text" value={leetcodeUsername} onChange={handleUsernameChange} />
        </label>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default UsernameEntry;
// on click submit, if error, toast error ...if ok, pop up
//logout -> get request with token then show msg log out success -> delete token