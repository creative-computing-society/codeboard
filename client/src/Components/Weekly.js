import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Weekly = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/weekly_leaderboard/?username=gurmankd')
      .then(response => {
        // Convert object to array of objects
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
    <div>
      <h1>Weekly Leaderboard</h1>
      <table border="1">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Username</th>
            <th>Last Solved</th>
            <th>Questions Solved</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={item.id}>
              <td>{index + 1}</td>
              <td>{item.Username}</td>
              <td>{item["Last Solved"]}</td>
              <td>{item["Questions Solved"]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Weekly;
