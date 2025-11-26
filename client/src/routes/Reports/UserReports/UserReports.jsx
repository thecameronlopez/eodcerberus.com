import styles from "./UserReports.module.css";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../context/AuthContext";
import {
  formatDate,
  formatLocationName,
  getToday,
  shiftDate,
} from "../../../utils/Helpers";
import toast from "react-hot-toast";
import DailyReport from "../../../components/DailyReport";

const UserReports = () => {
  const { user, location } = useAuth();
  const today = new Date().toISOString().split("T")[0];
  const [users, setUsers] = useState([]);
  const [params, setParams] = useState({
    start_date: getToday(),
    end_date: getToday(),
    user_id: user.id,
  });

  const [report, setReport] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setParams({
      ...params,
      [name]: value,
    });
  };

  useEffect(() => {
    const fetchUsers = async () => {
      const response = await fetch("/api/read/get_users");
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message);
      }
      setUsers(data.users);
    };
    fetchUsers();
  }, []);

  const setToday = () => {
    setParams({
      ...params,
      start_date: getToday(),
      end_date: getToday(),
    });
  };

  useEffect(() => {
    const runReport = async () => {
      const server =
        params.start_date === params.end_date
          ? `/api/read/run_report/${params.user_id}/${params.end_date}`
          : `/api/read/run_report_by_date_range/${params.user_id}?start_date=${params.start_date}&end_date=${params.end_date}`;

      try {
        const response = await fetch(server);
        const data = await response.json();
        if (!data.success) {
          throw new Error(data.message || "Something went wrong.");
        }
        setReport(data.totals);
      } catch (error) {
        console.error("[ERROR]: ", error);
        toast.error(error.message);
        setReport(null);
      }
    };
    runReport();
  }, [params]);

  return (
    <div className={styles.userReportsBlock}>
      <div className={styles.userReportsControlBar}>
        <div>
          <label
            htmlFor="user_id"
            style={{ fontSize: "14px", marginLeft: "4px" }}
          >
            User
          </label>
          <select
            name="user_id"
            id="user_id"
            value={params.user_id}
            onChange={handleChange}
          >
            <option value="">--Select User--</option>
            {users.map(({ id, first_name, last_name }) => (
              <option value={id} key={id}>
                {first_name} {last_name}
              </option>
            ))}
          </select>
        </div>
        <div className={styles.dayMover}>
          <button
            onClick={() => {
              const prev = shiftDate(params.start_date, -1);
              setParams({ ...params, start_date: prev, end_date: prev });
            }}
          >
            prev
          </button>
          <button onClick={setToday}>Today</button>
          <button
            onClick={() => {
              const next = shiftDate(params.end_date, 1);
              setParams({ ...params, start_date: next, end_date: next });
            }}
            disabled={params.end_date === today}
          >
            next
          </button>
        </div>
        <div className={styles.dateBlock}>
          <div>
            <label htmlFor="start_date">Start Date</label>
            <input
              type="date"
              name="start_date"
              value={params.start_date}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="end_date">End Date</label>
            <input
              type="date"
              name="end_date"
              value={params.end_date}
              onChange={handleChange}
            />
          </div>
        </div>
      </div>
      <div className={styles.reportBlock}>
        {report ? (
          <DailyReport
            report={report}
            start_date={params.start_date}
            end_date={params.end_date}
          />
        ) : (
          <h3>Choose to run report</h3>
        )}
      </div>
    </div>
  );
};

export default UserReports;
