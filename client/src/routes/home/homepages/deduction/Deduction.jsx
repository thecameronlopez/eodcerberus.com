import styles from "./Deduction.module.css";
import { useAuth } from "../../../../context/AuthContext";
import React, { useEffect, useState } from "react";
import { formatCurrency, formatDate } from "../../../../utils/tools";
import { list } from "../../../../utils/api";
import toast from "react-hot-toast";
import MoneyField from "../../../../components/MoneyField";

const Deduction = () => {
  const { user, setLoading } = useAuth();
  const [amount, setAmount] = useState("");
  const [reason, setReason] = useState("");
  const [myDeductions, setMyDeductions] = useState([]);

  const fetchMyDeductions = async () => {
    const deductionsRes = await list("deductions");
    if (!deductionsRes.success) {
      toast.error(deductionsRes.message);
      setMyDeductions([]);
      return;
    }
    const filtered = (deductionsRes.items || []).filter(
      (deduction) => Number(deduction.user?.id) === Number(user.id),
    );
    setMyDeductions(filtered);
  };

  useEffect(() => {
    fetchMyDeductions();
  }, [user.id]);

  const deleteDeduction = async (did) => {
    if (!confirm("Delete this deduction?")) return;

    try {
      const response = await fetch(`/api/deductions/${did}`, {
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
    if (!confirm("Submit deduction?")) return;
    const amountCents = Number(amount);
    if (Number.isNaN(amountCents) || amountCents < 1) {
      toast.error("Enter a valid deduction amount");
      return;
    }

    const payload = {
      user_id: Number(user.id),
      amount: amountCents,
      reason: reason,
    };

    try {
      setLoading(true);
      const response = await fetch("/api/deductions", {
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
          {myDeductions?.map(({ id, amount, reason, date }) => (
            <li
              key={id}
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
