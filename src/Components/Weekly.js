import React, { useEffect, useState } from 'react';
import axios from 'axios';
import defaultImage from '../assets/default_file.svg';
import SERVER_URL from "../config.js";

const BASE_URL = SERVER_URL + 'api/leaderboard';

const Weekly = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${BASE_URL}/weekly/`)
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

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error loading data: {error.message}</div>;

  return (
    <div className="leaderboard-container">
      <h2 className="leaderboard-title-heading">CCS Ranking</h2>
      <h1 className="leaderboard-title">Weekly Leaderboard</h1>
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
                {index === 0 && <span style={{ fontSize: '2rem', color: 'rgba(255, 215, 0, 1)', textDecoration:'underline', textDecorationColor: 'rgba(255, 215, 0, 1)', textDecorationThickness:'2px' }}>1</span>}
                {index === 1 && <span style={{ fontSize: '2rem', color: ' rgba(220, 220, 220, 1)', textDecoration:'underline', textDecorationColor: 'rgba(220, 220, 220, 1)', textDecorationThickness:'2px' }}>2</span>}
                {index === 2 && <span style={{ fontSize: '2rem', color: 'rgba(205, 127, 50, 1)',textDecoration:'underline', textDecorationColor: 'rgba(205, 127, 50, 1)', textDecorationThickness:'2px' }}>3</span>}
                {index >= 3 && <span className="rank-number">{index + 1}</span>}
              </td>
              <td>
                {!item.photo_url ? (
                  <img src={defaultImage} alt={item.username} className="profile" />
                ) : (
                  <img 
                    src={item.photo_url} 
                    alt={item.username} 
                    className="profile" 
                    onError={(e) => { e.target.src = defaultImage }}
                  />
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

export default Weekly;
