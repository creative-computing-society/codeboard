import { Link } from 'react-router-dom';
import { FaCode } from 'react-icons/fa'; // Using FaCode for the Leetcode icon
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
            <MdAccountCircle className="nav-icon" /> {/* Using FaUserCircle for the user profile icon */}
            Profile
          </Link>
        </li>
        
        <li className="divider">LEADERBOARD</li>
        <li className="nav-link">
          <Link to="/leetcode">
            <FaCode className="nav-icon" /> {/* Using FaCode for the Leetcode icon */}
            Leetcode
          </Link>
        </li>
      </ul>
    </div>
  );
}
