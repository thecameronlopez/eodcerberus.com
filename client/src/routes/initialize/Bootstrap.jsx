import toast from "react-hot-toast";
import styles from "./Bootstrap.module.css";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { renderOptions } from "../../utils/tools";
import { DEPARTMENTS } from "../../utils/enums";
import { useAuth } from "../../context/AuthContext";

const Bootstrap = () => {
  const { setBootstrapped } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    department: "",
    password: "",
    name: "",
    code: "",
    current_tax_rate: "",
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
    if (!confirm("Initialize application?")) return;
    const ratePercent = Number(formData.current_tax_rate);
    if (Number.isNaN(ratePercent) || ratePercent < 0 || ratePercent > 20) {
      toast.error("Enter a valid tax rate between 0 and 20");
      return;
    }

    const payload = {
      user: {
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        pw: formData.password,
        pw2: formData.password,
      },
      location: {
        name: formData.name,
        code: formData.code,
        current_tax_rate: ratePercent / 100,
      },
      department: {
        name: formData.department,
      },
    };

    try {
      const response = await fetch("/api/bootstrap", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success(data.message);
      setBootstrapped(true);
      navigate("/");
    } catch (error) {
      console.error("[BOOTSTRAP ERROR]: ", error);
      toast.error(error.message);
      return;
    }
  };

  return (
    <div className={styles.bootstrapPage}>
      <h1>Cerberus Initialization</h1>
      <form onSubmit={handleSubmit} className={styles.bootstrapForm}>
        <fieldset>
          <legend>Admin User Initialization</legend>
          <div>
            <label htmlFor="first_name">First Name</label>
            <input
              type="text"
              name="first_name"
              id="first_name"
              value={formData.first_name}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="last_name">Last Name</label>
            <input
              type="text"
              name="last_name"
              id="last_name"
              value={formData.last_name}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="email">Email</label>
            <input
              type="email"
              name="email"
              id="email"
              value={formData.email}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="department">Department</label>
            <select
              name="department"
              id="department"
              value={formData.department}
              onChange={handleChange}
            >
              <option value="">--select department--</option>
              {renderOptions(DEPARTMENTS)}
            </select>
          </div>
          <div>
            <label htmlFor="password">Password</label>
            <input
              type="text"
              name="password"
              id="password"
              value={formData.password}
              onChange={handleChange}
            />
          </div>
        </fieldset>
        <fieldset>
          <legend>Location Initialization</legend>
          <div>
            <label htmlFor="locationName">Location Name</label>
            <input
              type="text"
              name="name"
              id="name"
              value={formData.name}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="code">Location Code</label>
            <input
              type="text"
              name="code"
              id="code"
              value={formData.code}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="current_tax_rate">Tax Rate (%)</label>
            <input
              type="number"
              name="current_tax_rate"
              id="current_tax_rate"
              min="0"
              max="20"
              step="0.01"
              value={formData.current_tax_rate}
              onChange={handleChange}
            />
          </div>
        </fieldset>
        <button type="submit">Initialize</button>
      </form>
    </div>
  );
};

export default Bootstrap;
