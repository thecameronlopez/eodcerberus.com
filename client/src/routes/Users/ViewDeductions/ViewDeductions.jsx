import { useEffect, useState } from "react";
import styles from "./ViewDeductions.module.css";
import { useAuth } from "../../../context/AuthContext";
import toast from "react-hot-toast";
import { formatCurrency, formatDate } from "../../../utils/Helpers";
const ViewDeductions = () => {
  const { user } = useAuth();
  const [deductions, setDeductions] = useState([]);
  const [users, setUsers] = useState([]);
  const today = new Date().toISOString().split("T")[0];
  const [params, setParams] = useState({
    date: today,
    user_id: user.id,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setParams({
      ...params,
      [name]: value,
    });
  };

  useEffect(() => {
    const fetchDeductions = async () => {
      const url = params.date
        ? `/api/read/get_deductions_by_user/${params.user_id}/${params.date}`
        : `/api/read/get_deductions_by_user/${params.user_id}`;
      const response = await fetch(url);
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message);
        return;
      }
      setDeductions(data.deductions);
    };
    fetchDeductions();
  }, [params]);

  useEffect(() => {
    const fetchUsers = async () => {
      const response = await fetch("/api/read/get_users");
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message);
        return;
      }
      setUsers(data.users);
    };
    fetchUsers();
  }, []);

  return (
    <div className={styles.deductionContainer}>
      <div className={styles.deductionSearchBar}>
        <div>
          <input
            type="date"
            name="date"
            id="date"
            value={params.date}
            onChange={handleChange}
          />
          <button onClick={() => setParams({ ...params, date: null })}>
            All
          </button>
        </div>
        <select
          name="user_id"
          id="user_id"
          value={params.user_id}
          onChange={handleChange}
        >
          <option value="">--Select Salesman--</option>
          {users.map(({ id, first_name, last_name }) => (
            <option value={id} key={id}>
              {first_name} {last_name}
            </option>
          ))}
        </select>
      </div>
      <ul className={styles.deductionList}>
        {deductions.map(({ id, amount, date, reason, salesman }) => (
          <li key={id}>
            <div>
              <p>{formatDate(date)}</p>
              <h3>
                {salesman.first_name} {salesman.last_name}
              </h3>
            </div>
            <div>
              <p
                style={{
                  color: "var(--bannerBackground)",
                  fontWeight: "800",
                  textDecoration: "underline",
                }}
              >
                <b>{formatCurrency(amount)}</b>
              </p>
              <small>{reason}</small>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ViewDeductions;
