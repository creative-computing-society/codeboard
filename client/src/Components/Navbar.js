import { Link } from 'react-router-dom';
import { FaCalendarDay, FaCalendarWeek, FaCalendarAlt } from 'react-icons/fa';
import { MdAccountCircle } from 'react-icons/md';
import ccsLogo from '../assets/ccs_logo.png';

export default function Navbar() {
  return (
    <div className="NavBar">
      <img src={ccsLogo} alt="ccs_logo" className='ccsLogo'/>
      <ul>
        <li className="divider">DASHBOARD</li>
        <li className="nav-link">
          <Link to="/">
            <MdAccountCircle className="nav-icon" />
            <span class="nav-Text">Profile</span>
          </Link>
        </li>
        
        <li className="divider">LEADERBOARD</li>
        <li className="nav-link">
          <Link to="/daily">
            <FaCalendarDay className="nav-icon" /> 
            <span class="nav-Text">Daily</span>
          </Link>
        </li>
        <li className="nav-link">
          <Link to="/weekly">
            <FaCalendarWeek className="nav-icon" /> 
            <span class="nav-Text">Weekly</span>
          </Link>
        </li>
        <li className="nav-link">
          <Link to="/monthly">
            <FaCalendarAlt className="nav-icon" /> 
            <span class="nav-Text">Monthly</span>
          </Link>
        </li>
      </ul>-
    </div>
  );
}
