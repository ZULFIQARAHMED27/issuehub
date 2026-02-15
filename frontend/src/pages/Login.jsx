import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import logo from "../assets/logo.png";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const response = await api.post(
        "/auth/login",
        new URLSearchParams({
          username: form.email,
          password: form.password,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );

      // Save token
      localStorage.setItem("token", response.data.access_token);

      // Navigate to dashboard
      navigate("/dashboard");

    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) {
        setError("Invalid email or password.");
      } else if (!err.response) {
        setError("Server unreachable. Please try again shortly.");
      } else if (err.response?.status >= 500) {
        setError("Server error. Please try again shortly.");
      } else {
        setError(err.response?.data?.error?.message || "Login failed.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px"
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "420px",
          background: "#fff",
          padding: "28px",
          borderRadius: "12px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.08)"
        }}
      >
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
        <img
          src={logo}
          alt="IssueHub logo"
          style={{ width: "44px", height: "44px", objectFit: "contain" }}
        />
        <h1 style={{ margin: 0, fontSize: "42px", lineHeight: 1.1 }}>IssueHub</h1>
      </div>
      <p style={{ margin: "6px 0 20px 0", color: "#6b7280" }}>
        Lightweight Issue Tracker
      </p>
      <h2 style={{ marginTop: 0 }}>Login</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <br /><br />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />
        <br /><br />

        <button type="submit" disabled={submitting}>
          {submitting ? "Logging in..." : "Login"}
        </button>
      </form>

      {error && <p style={{ color: "red", marginBottom: 0 }}>{error}</p>}
      </div>
    </div>
  );
}
