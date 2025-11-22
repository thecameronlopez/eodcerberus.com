import styles from "./UserAnalytics.module.css";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../context/AuthContext";
import toast from "react-hot-toast";
import { formatDate } from "../../../utils/Helpers";

{
  /* <select name="user_id" id="user_id">
  <option value="">--Select User--</option>
  {users?.map(({ id, first_name, last_name }) => (
    <option value={id} key={id}>
      {first_name} {last_name}
    </option>
  ))}
</select>; */
}

const UserAnalytics = () => {
  const { user } = useAuth();
  const today = new Date().toLocaleDateString("en-CA");
  const [users, setUsers] = useState([]);
  const [userID, setUserID] = useState(user.id);
  const [dates, setDates] = useState({
    start_date: today,
    end_date: today,
  });

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
    const fetchReport = async () => {
      const response = await fetch(``);
    };
    fetchUsers();
  }, []);

  const shiftDate = (dateStr, amount) => {
    const d = new Date(dateStr + "T00:00");
    d.setDate(d.getDate() + amount);
    return d.toLocaleDateString("en-CA");
  };

  return (
    <div className={styles.userAnalyticsContainer}>
      <div className={styles.analyticsSelectionBar}>
        <select
          name="user_id"
          value={userID}
          onChange={(e) => setUserID(e.target.value)}
        >
          <option value="">--Select User--</option>
          {users.map(({ id, first_name, last_name }) => (
            <option value={id} key={id}>
              {first_name} {last_name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default UserAnalytics;
