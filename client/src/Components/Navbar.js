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
            Profile
          </Link>
        </li>
        
        <li className="divider">LEADERBOARD</li>
        <li className="nav-link">
          <Link to="/daily">
            <FaCalendarDay className="nav-icon" /> 
            Daily
          </Link>
        </li>
        <li className="nav-link">
          <Link to="/weekly">
            <FaCalendarWeek className="nav-icon" /> 
            Weekly
          </Link>
        </li>
        <li className="nav-link">
          <Link to="/monthly">
            <FaCalendarAlt className="nav-icon" /> 
            Monthly
          </Link>
        </li>
      </ul>
    </div>
  );
}
