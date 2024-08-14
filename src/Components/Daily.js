import React, { useEffect, useState } from 'react';
import axios from 'axios';
import defaultImage from '../assets/default_file.svg'; 
import badge1 from '../assets/badge1.png';
import badge2 from '../assets/badge2.png';
import badge3 from '../assets/badge3.png';

import SERVER_URL from "../config.js";

const BASE_URL = SERVER_URL + 'api/leaderboard';

const Daily = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${BASE_URL}/daily/`)
      .then(response => {
        const dataArray = Object.keys(response.data).map(key => ({
          id: key,
          ...response.data[key]
        }));
        setData(dataArray);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error loading data: {error.message}</p>;

  return (
    <div className="leaderboard-container">
      <h2 className="leaderboard-title-heading">CCS Ranking</h2>
      <h1 className="leaderboard-title">Daily Leaderboard</h1>
      <table className="leaderboard-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Profile</th>
            <th>Username</th>
            <th>Questions Solved</th>
          </tr>
        </thead>
        <tbody>
  {data.map((item, index) => (
    <tr key={item.id} className="leaderboard-row">
      <td>
        {index === 0 && <img src={badge1} alt="First Place"  className='badge' />}
        {index === 1 && <img src={badge2} alt="Second Place" className='badge' />}
        {index === 2 && <img src={badge3} alt="Third Place" className='badge' />}
        {index >= 3 && index + 1}
      </td>
      <td>
        {!item.photo_url ? (
          <img src={defaultImage} alt="Default Profile" />
        ) : (
          <img src={item.photo_url} alt="Profile" onError={(e) => { e.target.src = defaultImage }} />
        )}
      </td>
      <td>{item.username}</td>
      <td>{item.ques_solv}</td>
    </tr>
  ))}
</tbody>

      </table>
    </div>
  );
};

export default Daily;
