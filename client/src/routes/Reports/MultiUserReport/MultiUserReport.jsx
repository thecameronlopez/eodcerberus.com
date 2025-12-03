import styles from "./MultiUserReport.module.css";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getToday } from "../../../utils/Helpers";
import DailyReport from "../../../components/DailyReport";

const MultiUserReport = () => {
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const today = new Date().toISOString().split("T")[0];
  const [dates, setDates] = useState({
    start_date: getToday(),
    end_date: getToday(),
  });
  const [report, setReport] = useState(null);

  useEffect(() => {
    const getUsers = async () => {
      const response = await fetch("/api/read/get_users");
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message);
        setUsers(null);
        return;
      }
      setUsers(data.users);
    };
    getUsers();
  }, []);

  useEffect(() => {
    console.log(selectedUsers);
  }, [selectedUsers]);

  useEffect(() => {
    setReport(null);
  }, [selectedUsers, dates]);

  const runDat = async () => {
    if (selectedUsers.length === 0) {
      toast.error("Select at least 1 user");
      return;
    }
    const params = new URLSearchParams();
    selectedUsers.forEach((id) => params.append("users", id));
    try {
      const response = await fetch(
        `/api/read/multi_user_report?${params.toString()}&start_date=${
          dates.start_date
        }&end_date=${dates.end_date}`
      );
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      setReport(data.totals);
    } catch (error) {
      console.error("[ERROR]: ", error);
      toast.error(error.message);
    }
  };

  return (
    <div className={styles.muMasterBlock}>
      <div className={styles.muTopBar}>
        <div className={styles.selectUsers}>
          {users?.map(({ id, first_name, last_name }) => (
            <label key={id}>
              <input
                type="checkbox"
                value={id}
                onChange={(e) => {
                  const id = Number(e.target.value);
                  const checked = e.target.checked;

                  setSelectedUsers((prev) =>
                    checked ? [...prev, id] : prev.filter((u) => u !== id)
                  );
                }}
              />
              {first_name} {last_name}
            </label>
          ))}
        </div>
        <div className={styles.selectDates}>
          <label htmlFor="start_date">
            Start Date
            <input
              type="date"
              name="start_date"
              value={dates.start_date}
              onChange={(e) =>
                setDates({ ...dates, start_date: e.target.value })
              }
            />
          </label>
          <label htmlFor="end_date">
            End Date
            <input
              type="date"
              name="end_date"
              value={dates.end_date}
              onChange={(e) => setDates({ ...dates, end_date: e.target.value })}
            />
          </label>
          <button
            className={styles.runReport}
            disabled={selectedUsers.length === 0}
            onClick={runDat}
          >
            Run Report
          </button>
        </div>
      </div>
      {report && (
        <div className={styles.muReportData}>
          <DailyReport
            report={report}
            start_date={dates.start_date}
            end_date={dates.end_date}
            master={false}
            multi={users.filter((u) => selectedUsers.includes(u.id))}
          />
        </div>
      )}
    </div>
  );
};

export default MultiUserReport;
