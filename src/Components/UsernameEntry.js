import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SERVER_URL from "../config.js";
import '../usernameform.css';
import ccsLogoBulb from '../assets/ccs-bulb.png';

const API_URL = SERVER_URL + 'api/auth';

const UsernameEntry = () => {
  const location = useLocation();
  const { userData } = location.state || {};
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const navigate = useNavigate();

  const handleUsernameChange = (e) => {
    setLeetcodeUsername(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const token = localStorage.getItem('token'); // Retrieve token from localStorage

    if (!token) {
      console.error('Token is missing');
      navigate('/login'); // Navigate to login page if token is missing
      return;
    }

    // Define the request payload
    const payload = {
      leetcode_username: leetcodeUsername,
      token: token // Use the stored token here
    };

    // Define the request options
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
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
        // Handle success
        if (window.confirm('Verification successful. Proceed to register?')) {
          // Send request to register leetcode username
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
    <div>
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
              <input
                type="email"
                id="email"
                name="email"
                value={userData ? userData.email : ''}
                placeholder=" "
                disabled
              />
              <label htmlFor="email">Personal Email</label>
            </div>
            

            <div className="input-group">
              <select id="branch" name="branch" value="COE" disabled>
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
              />
              <label htmlFor="leetcode-username">Leetcode-username</label>
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
