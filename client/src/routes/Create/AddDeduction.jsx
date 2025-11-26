import MoneyField from "../../components/MoneyField";
import styles from "./AddDeduction.module.css";
import React, { useState } from "react";
import { formatDate, formatLocationName, getToday } from "../../utils/Helpers";
import toast from "react-hot-toast";
import { useAuth } from "../../context/AuthContext";

const AddDeduction = () => {
  const { location } = useAuth();
  const today = new Date().toISOString().split("T")[0];
  const [formData, setFormData] = useState({
    date: getToday(),
    amount: "",
    reason: "",
    location: location,
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
    if (!confirm("Submit deduction?")) return;

    try {
      const response = await fetch("/api/create/submit_deduction", {
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
        date: getToday(),
        amount: "",
        reason: "",
      });
    } catch (error) {
      toast.error(error.message);
      console.error("[ERROR]: ", error);
    }
  };

  return (
    <div className={styles.deductionContainer}>
      <form className={styles.deductionForm} onSubmit={handleSubmit}>
        <h2>Deductions</h2>
        <small style={{ fontWeight: "600", marginBottom: "10px" }}>
          Submitting deduction for {formatLocationName(location)}
        </small>
        <div>
          <label htmlFor="date">Date</label>
          <input
            type="date"
            name="date"
            id="date"
            value={formData.date}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="amount">Deduction Amount</label>
          <MoneyField
            name={"amount"}
            placeholder={"0.00"}
            value={formData.amount}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="reason">Reason for deduction</label>
          <textarea
            name="reason"
            id="reason"
            value={formData.reason}
            onChange={handleChange}
          ></textarea>
        </div>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default AddDeduction;
