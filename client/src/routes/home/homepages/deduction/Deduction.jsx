import styles from "./Deduction.module.css";
import { useAuth } from "../../../../context/AuthContext";
import React, { useEffect, useState } from "react";
import {
  SALES_CATEGORY,
  DEPARTMENTS,
  LOCATIONS,
  PAYMENT_TYPE,
} from "../../../../utils/enums";
import {
  getTodayLocalDate,
  renderOptions,
  formatCurrency,
  formatDate,
} from "../../../../utils/tools";
import { UserList } from "../../../../utils/api";
import toast from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquarePlus } from "@fortawesome/free-solid-svg-icons";
import MoneyField from "../../../../components/MoneyField";

const Deduction = () => {
  const today = new Date();
  const { user, location, setLoading } = useAuth();
  const [amount, setAmount] = useState("");
  const [reason, setReason] = useState("");
  const [date, setDate] = useState({
    start: getTodayLocalDate(),
    end: getTodayLocalDate(),
  });
  const [myDeductions, setMyDeductions] = useState([]);

  useEffect(() => {
    const get = async () => {
      const response = await fetch(`/api/read/deductions/user/${user.id}/all`);
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message);
        setMyDeductions(null);
      }
      console.log("DEDUCTIONS DATA: ", data.deductions);
      setMyDeductions(data.deductions);
    };
    get();
  }, []);

  const deleteDeduction = async (did) => {
    if (!confirm("Delete this deduction?")) return;

    try {
      const response = await fetch(`/api/delete/deduction/${did}`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      setMyDeductions((prev) => prev.filter((d) => d.id !== did));
      toast.success(data.message);
    } catch (error) {
      console.error("[DEDUCTION DELETION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!confirm(`Submit deduction for ${date.start}`)) return;
    console.log(amount);
    const payload = {
      amount: Number(amount),
      reason: reason,
      date: date.start,
    };

    try {
      setLoading(true);
      const response = await fetch("/api/create/deduction", {
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
      setAmount("");
      setReason("");
      setDate(getTodayLocalDate());
      setMyDeductions((prev) => [data.deduction, ...prev]);
    } catch (error) {
      console.error("[DEDUCTION ERROR]: ", error);
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.deductionsPage}>
      <div>
        <h3>Deductions</h3>
        <input
          type="date"
          name="date"
          id="date"
          value={date.start}
          onChange={(e) => setDate({ ...date, start: e.target.value })}
          className={styles.deductionsDateSet}
        />
        <form className={styles.deductionForm} onSubmit={handleSubmit}>
          <div>
            <label htmlFor="amount">Amount</label>
            <MoneyField
              name={"amount"}
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder={"$0.00"}
            />
          </div>
          <div>
            <label htmlFor="reason">Reason</label>
            <input
              type="text"
              name="reason"
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              required
            />
          </div>
          <button type="submit">Submit Deduction</button>
        </form>
      </div>
      <div className={styles.deductionsList}>
        <h4>My Deductions</h4>
        <ul>
          {myDeductions?.map(({ id, amount, reason, date }, index) => (
            <li
              key={index}
              onClick={() => deleteDeduction(id)}
              title="click to delete"
            >
              <p>{formatCurrency(amount)}</p>
              <p>{formatDate(date)}</p>
              <p className={styles.reasonForDeduction}>{reason}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Deduction;
