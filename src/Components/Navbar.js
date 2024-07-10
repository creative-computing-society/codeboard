import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaCalendarDay, FaCalendarWeek, FaCalendarAlt } from 'react-icons/fa';
import { MdAccountCircle } from 'react-icons/md';
import ccsLogo from '../assets/ccs_logo.png';

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // For testing purposes, you can hardcode a token here
    //const token = '8b0a868c328aa002033e90a5dc7089936be8f8b0'; // Replace with your hardcoded token

    // Uncomment the following line to switch back to using the token from localStorage
     const token = localStorage.getItem('token');

    console.log('Stored Token:', token); // Log the stored token for debugging

    fetch('https://api.knowishan.fun/api/auth/logout/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`,
      },
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Logout request failed');
      }
      return response.json();
    })
    .then(data => {
      console.log('Logout Response:', data); // Log the response for debugging
      if (data.message.toLowerCase() === 'logged out successfully') { // Adjusted to match server response case
        localStorage.removeItem('token'); // Remove token from local storage
        navigate('/login'); // Navigate to login page after logout
      } else {
        throw new Error('Logout failed');
      }
    })
    .catch(error => {
      console.error('Error logging out:', error);
    });
  };

  return (
    <div className="NavBar">
      <img src={ccsLogo} alt="ccs_logo" className='ccsLogo'/>
      <ul>
        <li className="divider">DASHBOARD</li>
        <li className="nav-link">
          <Link to="/">
            <MdAccountCircle className="nav-icon" />
            <span className="nav-Text">Profile</span>
          </Link>
        </li>
        
        <li className="divider">LEADERBOARD</li>
        <li className="nav-link">
          <Link to="/daily">
            <FaCalendarDay className="nav-icon" /> 
            <span className="nav-Text">Daily</span>
          </Link>
        </li>
        <li className="nav-link">
          <Link to="/weekly">
            <FaCalendarWeek className="nav-icon" /> 
            <span className="nav-Text">Weekly</span>
          </Link>
        </li>
        <li className="nav-link">
          <Link to="/monthly">
            <FaCalendarAlt className="nav-icon" /> 
            <span className="nav-Text">Monthly</span>
          </Link>
        </li>
        <li className="nav-link">
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </li>
      </ul>
    </div>
  );
}
