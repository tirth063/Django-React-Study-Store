
import { useState} from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Cookies } from 'react-cookie';
import api from './api';

function Register() {
  const cookies = new Cookies();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [balance, setBalance] = useState('');
  const [usernameError, setUsernameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [balanceError, setBalanceError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setUsernameError('');
    setEmailError('');
    setPasswordError('');
    setBalanceError('');

    try {
      const res = await api.post(`register/`, {
        username,
        email,
        password,
        balance: parseFloat(balance)
      });
      cookies.set('token', res.data.access, { path: '/' });
      cookies.set('user', JSON.stringify(res.data.user), { path: '/' });
      navigate('/');
    } catch (err) {
      const errors = err.response?.data;
      if (errors?.username) setUsernameError(errors.username[0]);
      if (errors?.email) setEmailError(errors.email[0]);
      if (errors?.password) setPasswordError(errors.password[0]);
      if (errors?.balance) setBalanceError(errors.balance[0]);
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-5">
          <div className="card shadow">
            <div className="card-body p-4">
              <h3 className="text-center mb-4">Register</h3>
              <form onSubmit={handleRegister}>
                <div className="mb-3">
                  <label className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-control"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                  {usernameError && <small className="text-danger">{usernameError}</small>}
                </div>
                <div className="mb-3">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  {emailError && <small className="text-danger">{emailError}</small>}
                </div>
                <div className="mb-3">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    className="form-control"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                  {passwordError && <small className="text-danger">{passwordError}</small>}
                </div>
                <div className="mb-3">
                  <label className="form-label">Initial Balance</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-control"
                    value={balance}
                    onChange={(e) => setBalance(e.target.value)}
                    required
                  />
                  {balanceError && <small className="text-danger">{balanceError}</small>}
                </div>
                <button type="submit" className="btn btn-primary w-100">Register</button>
              </form>
              <p className="text-center mt-3">
                Already have an account? <Link to="/login">Login</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;