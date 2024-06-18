import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      console.log('Fetching profile...');
      try {
        const response = await axios.get('http://127.0.0.1:8000/get_user/?username=gurmankd');
        console.log('Response received:', response);
        setProfile(response.data);
        console.log('Profile data set:', response.data);
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
      try {
        const response = await axios.get('http://127.0.0.1:8000/today_questions/');
        console.log('Questions response received:', response);
        setQuestions(response.data);
        console.log('Questions data set:', response.data);
      } catch (err) {
        console.error('Error occurred:', err);
        setError(err);
      }
    };

    fetchProfile();
    fetchQuestions();
  }, []);

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
        <p>LeetCode Rank: <span>{profile.leetcode_rank}</span></p>
        <p>Today's Rank: <span>{profile.daily_rank}</span></p>
        <p>Weekly Rank: <span>{profile.weekly_rank}</span></p>
        <p>Monthly Rank: <span>{profile.monthly_rank}</span></p>
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
