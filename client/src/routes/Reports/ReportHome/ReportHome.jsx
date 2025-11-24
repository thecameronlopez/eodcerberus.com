import styles from "./ReportHome.module.css";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../context/AuthContext";
import {
  formatLocationName,
  getToday,
  shiftDate,
} from "../../../utils/Helpers";
import toast from "react-hot-toast";
import DailyReport from "../../../components/DailyReport";
import Toggler from "../../../components/toggler/Toggler";

const ReportHome = () => {
  const { location } = useAuth();
  const [date, setDate] = useState(getToday());
  const [report, setReport] = useState(null);
  const [master, setMaster] = useState(false);

  useEffect(() => {
    const runReport = async () => {
      const URL = master
        ? `/api/read/run_master_by_date?date=${date}`
        : `/api/read/run_location_report_by_date/${location}?date=${date}`;
      const response = await fetch(URL);
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message || "Something went wrong.");
        return;
      }
      setReport(data.totals);
    };
    runReport();
  }, [date, location, master]);

  return (
    <>
      <div className={styles.reportHomeContainer}>
        <div className={styles.reportHomeDatePicker}>
          <div>
            <button
              onClick={() => {
                const prev = shiftDate(date, -1);
                setDate(prev);
              }}
            >
              prev
            </button>
            <button onClick={() => setDate(getToday())}>today</button>
            <button
              onClick={() => {
                const next = shiftDate(date, 1);
                setDate(next);
              }}
              disabled={date === getToday()}
            >
              next
            </button>
          </div>
          <input
            type="date"
            name="date"
            id="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>
        <Toggler val={master} setVal={setMaster} location={location} />
      </div>
      {report && (
        <div className={styles.singleDateReportContainer}>
          <DailyReport report={report} date={date} master={master} />
        </div>
      )}
    </>
  );
};

export default ReportHome;
