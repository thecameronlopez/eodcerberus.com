import styles from "./Login.module.css";
import toast from "react-hot-toast";
import React, { useState } from "react";
import { useAuth } from "../../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import LOGO from "../../../assets/cerberus-logo-blue.png";

const Login = () => {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setSubmitting(true);
      const response = await fetch("/api/auth/login", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success(data.message);
      setUser(data.user);
      navigate("/");
    } catch (error) {
      console.error("[ERROR]: ", error);
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className={styles.loginShell}>
      <div className={styles.loginIntro}>
        <div className={styles.brandBadge}>
          <img src={LOGO} alt="Cerberus" className={styles.brandLogo} />
          <div>
            <p className={styles.eyebrow}>Operations Portal</p>
            <h1 className={styles.loginHeader}>Cerberus Access</h1>
          </div>
        </div>
        <p className={styles.loginCopy}>
          Sign in to manage tickets, reporting, deductions, and daily store
          operations from one place.
        </p>
        <div className={styles.featureGrid}>
          <div className={styles.featureCard}>
            <span>Live Workflow</span>
            <p>Tickets, transactions, and adjustments stay inside one system.</p>
          </div>
          <div className={styles.featureCard}>
            <span>Store Controls</span>
            <p>Built for front-line teams, admin users, and reporting staff.</p>
          </div>
        </div>
      </div>

      <div className={styles.loginContainer}>
        <div className={styles.formHeader}>
          <p className={styles.formEyebrow}>Secure Sign-In</p>
          <h2>Welcome back</h2>
          <p>Use your company email and password to continue.</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.loginForm}>
          <div>
            <label htmlFor="email">Email</label>
            <input
              type="email"
              name="email"
              id="email"
              value={formData.email}
              onChange={handleChange}
              autoComplete="email"
              required
            />
          </div>
          <div>
            <label htmlFor="password">Password</label>
            <div className={styles.passwordField}>
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                id="password"
                value={formData.password}
                onChange={handleChange}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className={styles.passwordToggle}
                onClick={() => setShowPassword((current) => !current)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                aria-pressed={showPassword}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>
          <button type="submit" disabled={submitting}>
            {submitting ? "Signing In..." : "Login"}
          </button>
        </form>
      </div>
    </section>
  );
};

export default Login;
