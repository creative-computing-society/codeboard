export default function completeLogin(data, status, { navigate, onVerify, setIsNewUser, setIsAuthenticated, jwtToken }) {
  if (data.leetcode === false) {
    setIsNewUser(true);
    onVerify();
    const userData = {
      rollNo: data.user.roll_no,
      email: data.user.email,
      branch: data.user.branch,
      fullName: `${data.user.first_name} ${data.user.last_name}`
    };
    setIsAuthenticated(true);
    navigate('/username', { state: { jwtToken, userData, token: data.token } });
  } else if (status === 200 && data.token) {
    localStorage.setItem('token', data.token);
    onVerify();
    setIsAuthenticated(true);
    navigate('/profile');
  } else {
    console.error(`Unexpected response: ${JSON.stringify(data)}`);
    navigate('/login');
  }
}
