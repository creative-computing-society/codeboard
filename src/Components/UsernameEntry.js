/* Steps to implement the UsernameEntry component:
1.login the user after ccs login
2.store the django token in local storage, and redirect to profile if leetcode is true, otherwise keep redirecting to username entry page
3.if token is not present, redirect to login page
4.pass the django token as authorization header in the request to the backend
5.first request should be to /verify-leetcode/ endpoint
6.if any error, show it to the user
7.if success, show the confirmation popup
8.if user clicks on confirm, send the request to /register-leetcode/ endpoint
9.don't forget to pass the django token in the request header
10.if success, redirect to the profile page
11.if error, tell the user an error occurred and try again, or redirect to login and tell the user that an error occurred*/

// Also do fix the ui basic maine krdia, iski css is located in usernameform.css
// ek baar css test krne ke liye copy it's content at the end of app.css and open this username entry page
// lastly css-bulb png is inside assets folder
// Regards, Ishan ✌️
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import SERVER_URL from "../config.js";

const API_URL = SERVER_URL + 'api/auth';

const UsernameEntry = () => {
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { jwtToken: stateJwtToken } = location.state || {}; // Retrieve the JWT token from the location state
  const [jwtToken, setJwtToken] = useState(stateJwtToken);

  useEffect(() => {
    if (!stateJwtToken) {
      console.error('JWT token is missing from state');
      navigate('/login'); // Navigate to login page if JWT token is missing from state
    } else {
      setJwtToken(stateJwtToken);
    }
  }, [navigate, stateJwtToken]);

  const handleUsernameChange = (e) => {
    setLeetcodeUsername(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!jwtToken) {
      console.error('JWT token is missing');
      navigate('/login'); // Navigate to login page if JWT token is missing
      return;
    }

    // Define the request payload
    const payload = {
      leetcode_username: leetcodeUsername,
      token: jwtToken
    };

    // Define the request options
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwtToken}`
      },
      body: JSON.stringify(payload)
    };

    // Make the API call
    fetch(`${API_URL}/verify-leetcode/`, requestOptions)   //CHANGE THIS ABCK TO fetch(`${API_URL}/login/`, requestOptions) 
      .then(response => response.json())
      .then(data => {
        // Handle response
        console.log('Success:', data);
        // Navigate to the desired page
        navigate('/profile');
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  // return (
  //   <div>
  //     <h2>Enter Username</h2>
  //     <form onSubmit={handleSubmit}>
  //       <label>
  //         Username:
  //         <input type="text" value={leetcodeUsername} onChange={handleUsernameChange} />
  //       </label>
  //       <button type="submit">Submit</button>
  //     </form>
  //   </div>
    
  // );
  const [formData, setFormData] = useState({
    profileImg: '/default-profile-img.png',
    userName: 'John Doe',
    rollNumber: '2783742',
    phone: '123456789',
    email: 'hello@gmail.com',
    branch: 'RAI',
    passingYear: '2027',
    policy: true
});

const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prevState => ({
        ...prevState,
        [name]: type === 'checkbox' ? checked : value
    }));
};


return (
    <div>
        <div className="container">
            {/* Left side content */}
            <div className="left">
                <div className="left-top">
                    <div className="logo">
                        <img src="./assets/ccs-bulb.png" alt="CCS Logo" />
                    </div>
                    <div>
                        <h1>Single Sign On</h1>
                        <h2>Simplifying access across CCS</h2>
                    </div>
                </div>

                <div className="left-bottom">
                    <div className="content">
                        <img className="profile" src={formData.profileImg} />
                        <div className="content-left">
                            <h4>Welcome, {formData.userName}!</h4>
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
                            <input type="text" id="roll-number" name="rollNumber" value={formData.rollNumber} onChange={handleChange} placeholder=" " disabled/>
                            <label htmlFor="roll-number">Roll Number</label>
                        </div>

                        <div className="input-group">
                            <input type="tel" id="phone" name="phone" value={formData.phone} onChange={handleChange} placeholder=" " disabled/>
                            <label htmlFor="phone">Phone Number</label>
                        </div>
                    </div>

                    <div className="input-group">
                        <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} placeholder=" " disabled/>
                        <label htmlFor="email">Personal Email</label>
                    </div>

                    <div className="input-group">
                        <select id="branch" name="branch" value={formData.branch} onChange={handleChange} disabled>
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
                        <label htmlFor="branch" className={formData.branch ? 'active' : ''}>Branch</label>
                    </div>

                    <div className="input-group">
                        <input type="number" id="passing-year" name="passingYear" value={formData.passingYear} onChange={handleChange} min="1900" max="2100" placeholder=" " disabled/>
                        <label htmlFor="passing-year">Passing Year</label>
                    </div>
                  
                    <div className="input-group">
                            <input type="text" id="roll-number" name="rollNumber" value={leetcodeUsername} onChange={handleUsernameChange} required placeholder=" " />
                            <label htmlFor="roll-number">Leetcode-username</label>
                    </div>

                    <div className="policy">
                        <label htmlFor="policy">
                            <input type="checkbox" id="policy" name="policy" checked={formData.policy} onChange={handleChange} disabled /> <span>I accept the OAuth policy</span>
                        </label>
                    </div>

                    <button type="submit">Submit</button>
                </form>
            </div>
        </div>
    </div>
);
}
export default UsernameEntry;
// on click submit, if error, toast error ...if ok, pop up
//logout -> get request with token then show msg log out success -> delete token