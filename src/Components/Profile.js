import React, { useState, useEffect } from 'react';
import SERVER_URL from "../config.js";
const BASE_URL = SERVER_URL + 'api/leaderboard';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [rankPeriod, setRankPeriod] = useState('today');

  useEffect(() => {
    const fetchProfile = async () => {
      // console.log('Fetching profile...');
      const token = localStorage.getItem('token');
      // console.log('Token:', token);
      if (!token) {
        setError('Token is missing');
        setLoading(false);
        window.location.href = "/login";
        return;
      }

      try {
        const response = await fetch(`${BASE_URL}/user/profile/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
          }
        });

        if (response.status === 401 || response.status === 404 || response.status === 400) {
          window.location.href = "/login";
          localStorage.removeItem('token');
          return;
        }
        else if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        // console.log('Profile response received:', data);
        setProfile(data);
      } catch (err) {
        console.error('Error occurred:', err);
        setError(err.message);
      } finally {
        setLoading(false);
        // console.log('Loading state set to false');
      }
    };

    const fetchQuestions = async () => {
      // console.log('Fetching questions...');
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Token is missing');
        return;
      }

      try {
        const response = await fetch(`${BASE_URL}/questions/today/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
          }
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        // console.log('Questions response received:', data);
        setQuestions(data);
      } catch (err) {
        console.error('Error occurred:', err);
        setError(err.message);
      }
    };

    fetchProfile();
    fetchQuestions();
  }, []); // Fetch profile and questions only once on component mount

  const showRank = (period) => {
    setRankPeriod(period);
  };

  if (loading) {
    // console.log('Loading...');
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    console.error('Error:', error);
    return <div className="error">Error: {error}</div>;
  }

  if (!profile) {
    // console.log('No profile data available');
    return <div className="no-data">No profile data available</div>;
  }

  /* console.log('Rendering profile:', profile);
  console.log('Rendering questions:', questions); */

  return (
    <div className="profile-container">
      <div className="detail-container">
        {profile.photo_url && <img src={profile.photo_url} alt="Profile" />}
        <h1>{profile.name}</h1>
        <p>Username: <span>{profile.username}</span></p>
        
        {rankPeriod === 'today' && <p>Today's Rank: <span>{profile.daily_rank}</span></p>}
        {rankPeriod === 'weekly' && <p>Weekly Rank: <span>{profile.weekly_rank}</span></p>}
        {rankPeriod === 'monthly' && <p>Monthly Rank: <span>{profile.monthly_rank}</span></p>}
        <div className="rank-slider">
          <button className={`tab ${rankPeriod === 'today' ? 'active' : ''}`} onClick={() => showRank('today')}>Today's</button>
          <button className={`tab ${rankPeriod === 'weekly' ? 'active' : ''}`} onClick={() => showRank('weekly')}>Weekly</button>
          <button className={`tab ${rankPeriod === 'monthly' ? 'active' : ''}`} onClick={() => showRank('monthly')}>Monthly</button>
        </div>
      </div>

      <div className="question-container">
        <h2>Today's Questions</h2>
        <table className="questions-table">
          <thead>
            <tr>
              <th>Question</th>
              <th>Difficulty</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {questions.length > 0 ? questions.map((question, index) => (
              <tr key={index}>
                <td><a href={question.leetcode_link} target="_blank" rel="noopener noreferrer">{question.title}</a></td>
                <td>{question.difficulty}</td>
                <td>{question.status}</td>
              </tr>
            )) : (
              <tr>
                <td colSpan="3">No questions available</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Profile;
