import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const UsernameEntry = () => {
  const [username, setUsername] = useState('');
  const navigate = useNavigate();

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Add logic to handle username submission, e.g., call an API to update the username
    // After successful submission, navigate to the desired page
    // Placeholder for API call
    // fetch('http://localhost:8000/api/auth/login/', { method: 'POST', body: JSON.stringify({ username }) })
    //   .then(response => response.json())
    //   .then(data => { leetcode_username
    //     // handle response
    //   });

    navigate('/profile');
  };

  return (
    <div>
      <h2>Enter Username</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Username:
          <input type="text" value={username} onChange={handleUsernameChange} />
        </label>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default UsernameEntry;
