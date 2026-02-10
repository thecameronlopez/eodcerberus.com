import styles from "./Register.module.css";
import toast from "react-hot-toast";
import React, { useState, useEffect } from "react";
import { DepartmentList, LocationList } from "../../../utils/api";

const Register = () => {
  const [departments, setDepartments] = useState([]);
  const [locations, setLocations] = useState([]);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    pw: "",
    pw2: "",
    department: "",
    location_code: "",
    is_admin: false,
  });

  useEffect(() => {
    const loadLookups = async () => {
      const [departmentsRes, locationsRes] = await Promise.all([
        DepartmentList(),
        LocationList(),
      ]);
      if (!departmentsRes.success) {
        toast.error(departmentsRes.message);
      } else {
        setDepartments(departmentsRes.departments || []);
      }
      if (!locationsRes.success) {
        toast.error(locationsRes.message);
      } else {
        setLocations(locationsRes.locations || []);
      }
    };

    loadLookups();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.pw !== formData.pw2) {
      toast.error("Passwords do not match!");
      return;
    }
    try {
      const response = await fetch("/api/users", {
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
      setFormData({
        first_name: "",
        last_name: "",
        email: "",
        pw: "",
        pw2: "",
        department: "",
        location_code: "",
        is_admin: false,
      });
    } catch (error) {
      console.error("[ERROR]: ", error);
      toast.error(error.message);
    }
  };
  return (
    <div className={styles.registerContainer}>
      <form className={styles.registrationForm} onSubmit={handleSubmit}>
        <h2 style={{ color: "var(--linkText)" }}>Register New User</h2>
        <div className={styles.adminCheck}>
          <label htmlFor="is_admin">
            Admin
            <input
              type="checkbox"
              name="is_admin"
              id="is_admin"
              checked={formData.is_admin}
              onChange={handleChange}
            />
          </label>
        </div>
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
            {departments.map((department) => (
              <option key={department.id} value={department.name}>
                {department.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="location_code">Location</label>
          <select
            name="location_code"
            id="location_code"
            value={formData.location_code}
            onChange={handleChange}
          >
            <option value="">--select a location--</option>
            {locations.map((location) => (
              <option key={location.id} value={location.code}>
                {location.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="pw">Password</label>
          <input
            type="password"
            name="pw"
            id="pw"
            value={formData.pw}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="pw2">Enter Password Again</label>
          <input
            type="password"
            name="pw2"
            id="pw2"
            value={formData.pw2}
            onChange={handleChange}
          />
        </div>
        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default Register;
