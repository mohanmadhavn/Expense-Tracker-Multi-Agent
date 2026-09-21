import { useState } from "react";
import { login } from "../services/api";

function Login({ onSwitch, onSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      setError("");
      const data = await login(email, password);
      localStorage.setItem("access_token", data.access_token);
      onSuccess();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>EP Tracker</h1>
        <p className="subtitle">Personal Finance Manager</p>

        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Login</button>
        </form>

        {error && <p className="error">{error}</p>}

        <p className="switch-link">
          Don't have an account?{" "}
          <span onClick={onSwitch}>Register</span>
        </p>
      </div>
    </div>
  );
}

export default Login;
