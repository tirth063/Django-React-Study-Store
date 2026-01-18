import { useState } from "react";
import api from "./api";
import { useNavigate } from "react-router-dom";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const register = async () => {
    try {
      setError("");

      const res = await api.post("register/", {
        username: username,
        email: email,
        password: password,
      });

      alert(res.data.message);
      navigate("/login");

    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError("Server error");
      }
    }
  };

  return (
    <div>
      <h2>Register</h2>

      {error && <p>{error}</p>}

      <input
        placeholder="username"
        value={username}
        onChange={e => setUsername(e.target.value)}
      />
      <br />

      <input
        placeholder="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      />
      <br />

      <input
        type="password"
        placeholder="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />
      <br />

      <button onClick={register}>Register</button>
    </div>
  );
}

export default Register;
