import React, { useState, useEffect } from 'react';
import SERVER_URL from "../config.js";
const BASE_URL = SERVER_URL+'api/leaderboard';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [rankPeriod, setRankPeriod] = useState('today');

  useEffect(() => {
    const fetchProfile = async () => {
      console.log('Fetching profile...');
      const token = localStorage.getItem('token');
      console.log(token);
      if (!token) {
        setError('Token is missing');
        setLoading(false);
        window.location.href="/login";
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

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response received:', data);
        setProfile(data);
        console.log('Profile data set:', data);
      } catch (err) {
        console.error('Error occurred:', err);
        setError(err);
      } finally {
        setLoading(false);
        console.log('Loading state set to false');
      }
    };

    const fetchQuestions = async () => {
      console.log('Fetching questions...');
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
        console.log('Questions response received:', data);
        setQuestions(data);
        console.log('Questions data set:', data);
      } catch (err) {
        console.error('Error occurred:', err);
        setError(err);
      }
    };

    fetchProfile();
    fetchQuestions();
  }, []);

  const showRank = (period) => {
    setRankPeriod(period);
  };

  if (loading) {
    console.log('Loading...');
    return <div className="loading">Loading...</div>;
  }
  if (error) {
    console.error('Error:', error.message);
    return <div className="error">Error: {error.message}</div>;
  }
  if (!profile) {
    console.log('No profile data available');
    return <div className="no-data">No profile data available</div>;
  }

  console.log('Rendering profile:', profile);
  console.log('Rendering questions:', questions);

  return (
    <div className="profile-container">
      <div className="detail-container">
        <img src={profile.photo_url} alt="Profile" />
        <h1>{profile.name}</h1>
        <p>LeetCode Username: <span>{profile.username}</span></p>
        
        <div className="rank-slider">
          <button className={`tab ${rankPeriod === 'today' ? 'active' : ''}`} onClick={() => showRank('today')}>Today's</button>
          <button className={`tab ${rankPeriod === 'weekly' ? 'active' : ''}`} onClick={() => showRank('weekly')}>Weekly</button>
          <button className={`tab ${rankPeriod === 'monthly' ? 'active' : ''}`} onClick={() => showRank('monthly')}>Monthly</button>
        </div>

        {rankPeriod === 'today' && <p>Today's Rank: <span>{profile.daily_rank}</span></p>}
        {rankPeriod === 'weekly' && <p>Weekly Rank: <span>{profile.weekly_rank}</span></p>}
        {rankPeriod === 'monthly' && <p>Monthly Rank: <span>{profile.monthly_rank}</span></p>}
      </div>

      <div className="question-container">
        <h2>Today's Questions</h2>
        <table className="questions-table">
          <thead>
            <tr>
              <th>Question</th>
              <th>Difficulty</th>
              <th>Status</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {questions.map((question, index) => (
              <tr key={index}>
                <td>{question.title}</td>
                <td>{question.difficulty}</td>
                <td>{question.status}</td>
                <td><a href={question.leetcode_link} target="_blank" rel="noopener noreferrer">View</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Profile;
