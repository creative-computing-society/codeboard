import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SERVER_URL from "../config.js";
import '../usernameform.css';
import ccsLogoBulb from '../assets/ccs-bulb.png';

const API_URL = SERVER_URL + 'api/auth';

const UsernameEntry = ({setIsNewUser}) => {
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const navigate = useNavigate();

  // Function to get the token from localStorage
  const getToken = () => localStorage.getItem('token');

  const handleUsernameChange = (e) => {
    setLeetcodeUsername(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const token = getToken(); // Retrieve token from localStorage

    if (!token) {
      console.error('Token is missing');
      navigate('/login'); // Navigate to login page if token is missing
      return;
    }

    // Define the request payload
    const payload = {
      leetcode_username: leetcodeUsername,
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
          return response.json().then(body => {
            throw new Error(body.error || 'Verification failed');
          });
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
                return response.json().then(body => {
                  throw new Error(body.error || 'Registration failed');
                });
              }
              if (response.status === 201) {
              }
              // setIsNewUser(false);
              localStorage.setItem('isNewUser', false);
              navigate('/profile'); // Redirect to profile page on success
            })
            .catch(error => {
              console.error('Error registering:', error);
              alert(`An error occurred while registering. Please try again. ${error.message}`);
            });
        }
      })
      .catch(error => {
        // Directly handle the error object
        console.error('Error verifying:', error);
        alert(`Verification failed. ${error.message}`);
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
              <img className="profile" src="/default-profile-img.png" alt="Profile" />
              <div className="content-left">
                <h4>Welcome, John Doe!</h4>
                <p>Please accept the OAuth policy and provide additional information.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right side form */}
        <div className="right">
          <form onSubmit={handleSubmit} className="user-form">
            <div className="input-group-row">
              <div className="input-group">
                <input
                  type="text"
                  id="roll-number"
                  name="rollNumber"
                  value="2783742"
                  placeholder=" "
                  disabled
                />
                <label htmlFor="roll-number">Roll Number</label>
              </div>

              <div className="input-group">
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value="123456789"
                  placeholder=" "
                  disabled
                />
                <label htmlFor="phone">Phone Number</label>
              </div>
            </div>

            <div className="input-group">
              <input
                type="email"
                id="email"
                name="email"
                value="hello@gmail.com"
                placeholder=" "
                disabled
              />
              <label htmlFor="email">Personal Email</label>
            </div>

            <div className="input-group">
              <select id="branch" name="branch" value="RAI" disabled>
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
                type="number"
                id="passing-year"
                name="passingYear"
                value="2027"
                placeholder=" "
                disabled
              />
              <label htmlFor="passing-year">Passing Year</label>
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
