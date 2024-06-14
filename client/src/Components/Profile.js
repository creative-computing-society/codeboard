import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Profile = () => {
  const [profile, setProfile] = useState(null);
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

    fetchProfile();
  }, []);

  if (loading) {
    console.log('Loading...');
    return <div className="loading">Loading...</div>;
  }
  if (error) {
    console.error('Error:', error.message);
    return <div className="error">Error: {error.message}</div>;
  }

  console.log('Rendering profile:', profile);

  return (
    <div className="profile-container">
      <img src={profile.photo_url} alt="Profile" />
      <h1>{profile.name}</h1>
      <p>LeetCode Username: <span>{profile.leetcode_name}</span></p>
      <p>LeetCode Rank: <span>{profile.leetcode_rank}</span></p>
      <p>CCS Rank: <span>{profile.ccs_rank}</span></p>
      <p>Questions Solved on LeetCode: <span>{profile.total_solved}</span></p>
    </div>
  );
};

export default Profile;
