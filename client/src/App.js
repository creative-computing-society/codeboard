import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './Components/Navbar';
import Profile from './Components/Profile';
import Daily from './Components/Daily';
import Weekly from './Components/Weekly';
import Monthly from './Components/Monthly';
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
            <Route path="/daily" element={<Daily />} />
            <Route path="/weekly" element={<Weekly />} />
            <Route path="/monthly" element={<Monthly />} />
            
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
