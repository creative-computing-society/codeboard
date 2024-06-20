import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Daily = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/daily_leaderboard/?username=gurnamkd')
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
    <h1 className="leaderboard-title">Daily Leaderboard</h1>
    <table className="leaderboard-table">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Username</th>
          <th></th>
          <th>Questions Solved</th>
        </tr>
      </thead>
      <tbody>
        {data.map((item, index) => (
          <tr key={item.id} className="leaderboard-row">
            <td>{index + 1}</td>
            <td><img src={item.photo_url} alt="Profile" /></td>
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
