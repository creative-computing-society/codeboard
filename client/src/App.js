import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Leetcode from './Components/Leetcode';
import Navbar from './Components/Navbar';
import Profile from './Components/Profile';
import './App.css'
function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <div className="content">
          <Routes>
            <Route path="/" element={<Profile />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/leetcode" element={<Leetcode />} />
            
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
