import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SERVER_URL from "../config.js";
import ccsLogoBulb from '../assets/ccs-bulb.png';
const API_URL = SERVER_URL + 'api/auth';

const UsernameEntry = () => {
  const location = useLocation();
  const { userData, token } = location.state || {}; // Retrieve token from location state
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Add the class to the body element when the component mounts
    document.body.classList.add('username-entry-body');
    
    // Remove the class from the body element when the component unmounts
    return () => {
      document.body.classList.remove('username-entry-body');
    };
  }, []);

  const handleUsernameChange = (e) => {
    setLeetcodeUsername(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!token) {
      console.error('Token is missing');
      navigate('/login'); // Navigate to login page if token is missing
      return;
    }

    // Define the request payload
    const payload = {
      leetcode_username: leetcodeUsername,
      token: token // Use the token passed from AuthVerify
    };

    // Define the request options
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      },
      body: JSON.stringify(payload)
    };

    // Make the API call to verify leetcode username
    fetch(`${API_URL}/verify-leetcode/`, requestOptions)
      .then(response => {
        if (!response.ok) {
          throw new Error('Verification failed');
        }
        return response.json();
      })
      .then(data => {
        if (window.confirm('Verification successful. Proceed to register?')) {
          fetch(`${API_URL}/register-leetcode/`, requestOptions)
            .then(response => {
              if (!response.ok) {
                throw new Error('Registration failed');
              }
              navigate('/profile'); // Redirect to profile page on success
            })
            .catch(error => {
              console.error('Error registering:', error);
              alert('An error occurred while registering. Please try again.');
            });
        }
      })
      .catch(error => {
        console.error('Error verifying:', error);
        alert('Verification failed. Please check your username and try again.');
      });
  };

  return (
    <div className="outer-container">
      <div className="container">
        {/* Left side content */}
        <div className="left">
          <div className="left-top">
            <div className="logo">
              <img src={ccsLogoBulb} alt="CCS Logo" />
            </div>
            <div>
              <h1>Single Sign On</h1>
              <h2>Simplifying access across CCS</h2>
            </div>
          </div>

          <div className="left-bottom">
            <div className="content">
              <div className="content-left">
                <h4>Welcome, {userData ? userData.fullName : 'User'}!</h4>
                <p>Please accept the OAuth policy and provide additional information.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right side form */}
        <div className="right">
          <form onSubmit={handleSubmit} className="user-form">
            <div className="input-group">
              <input
                type="email"
                id="email"
                name="email"
                value={userData ? userData.email : ''}
                placeholder=" "
                disabled
              />
              <label htmlFor="email">Email</label>
            </div>
            <div className="input-group">
              <input
                type="text"
                id="roll-number"
                name="rollNumber"
                value={userData ? userData.rollNo : ''}
                placeholder=" "
                disabled
              />
              <label htmlFor="roll-number">Roll Number</label>
            </div>
            <div className="input-group">
              <select id="branch" name="branch" value={userData ? userData.branch : ''} disabled>
                <option value="" disabled>Select your branch</option>
                <option value="BT">BioTechnology</option>
                <option value="BM">Biomedical</option>
                <option value="CE">Civil Engineering</option>
                <option value="CHE">Chemical Engineering</option>
                <option value="COE">Computer Engineering</option>
                <option value="COPC">Computer Science & Engineering (Patiala Campus)</option>
                <option value="COSE">Computer Science & Engineering (Derabassi Campus)</option>
                <option value="COBS">Computer Science and Business Systems</option>
                <option value="ELE">Electrical Engineering</option>
                <option value="ECE">Electronics and Communication Engineering</option>
                <option value="ENC">Electronics and Computer Engineering</option>
                <option value="EEC">Electrical and Computer Engineering</option>
                <option value="EVD">Electronics Engineering (VLSI Design and Technology)</option>
                <option value="RAI">Robotics and Artificial Intelligence</option>
              </select>
              <label htmlFor="branch" className="active">Branch</label>
            </div>
            <div className="input-group">
              <input
                type="text"
                id="leetcode-username"
                name="leetcodeUsername"
                value={leetcodeUsername}
                onChange={handleUsernameChange}
                required
                placeholder=" "
                autoComplete="off"
              />
              <label htmlFor="leetcode-username">Leetcode Username</label>
            </div>
            <div className="policy">
              <label htmlFor="policy">
                <input
                  type="checkbox"
                  id="policy"
                  name="policy"
                  checked
                  onChange={() => {}}
                  required
                />{' '}
                <span>I accept the OAuth policy</span>
              </label>
            </div>

            <button type="submit">Submit</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UsernameEntry;
