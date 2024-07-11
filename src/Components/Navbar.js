import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaCalendarDay, FaCalendarWeek, FaCalendarAlt } from 'react-icons/fa';
import { MdAccountCircle } from 'react-icons/md';
import ccsLogo from '../assets/ccs_logo.png';
import SERVER_URL from "../config.js";

const API_URL = `${SERVER_URL}api/auth`;

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    const token = localStorage.getItem('token');

    try {
      console.log('Stored Token:', token);

      const response = await fetch(API_URL + '/logout/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Logout request failed');
      }

      const data = await response.json();
      console.log('Logout Response:', data);

      if (data.message.toLowerCase() === 'logged out successfully') {
        localStorage.removeItem('token');
        localStorage.removeItem('isNewUser')
        navigate('/login');
      } else {
        throw new Error('Logout failed');
      }
    } catch (error) {
      console.error('Error logging out:', error);
      // Optionally, you can navigate to login or show a user-friendly message
      navigate('/login');
    }
  };

  return (
    <div className="NavBar">
      <img src={ccsLogo} alt="ccs_logo" className="ccsLogo" />
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
      </ul>
      <div className="logout-button-container">
        
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>
    </div>
  );
}
