import styles from "./DateRangeReport.module.css";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../context/AuthContext";
import { formatLocationName, getToday } from "../../../utils/Helpers";
import DailyReport from "../../../components/DailyReport";
import toast from "react-hot-toast";
import Toggler from "../../../components/toggler/Toggler";

const DateRangeReport = () => {
  const { location } = useAuth();
  const today = new Date().toISOString().split("T")[0];
  const [dates, setDates] = useState({
    start_date: getToday(),
    end_date: getToday(),
  });
  const [report, setReport] = useState(null);
  const [master, setMaster] = useState(false);

  useEffect(() => {
    const fetchReport = async () => {
      const URL = master
        ? `/api/read/run_master_by_date_range?start_date=${dates.start_date}&end_date=${dates.end_date}`
        : `/api/read/run_location_report_by_date_range/${location}?start_date=${dates.start_date}&end_date=${dates.end_date}`;
      const response = await fetch(URL);
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message || "Something went wrong");
      }
      setReport(data.totals);
    };
    fetchReport();
  }, [dates, location, master]);

  return (
    <>
      <div className={styles.dateRangeContainer}>
        <div className={styles.dateInputContainer}>
          <div className={styles.dateInput}>
            <label htmlFor="start_date">Start Date</label>
            <input
              type="date"
              name="start_date"
              id="start_date"
              value={dates.start_date}
              onChange={(e) =>
                setDates({ ...dates, start_date: e.target.value })
              }
            />
          </div>
          <div className={styles.dateInput}>
            <label htmlFor="end_date">End Date</label>
            <input
              type="date"
              name="end_date"
              id="end_date"
              value={dates.end_date}
              onChange={(e) => setDates({ ...dates, end_date: e.target.value })}
            />
          </div>
        </div>
        <Toggler val={master} setVal={setMaster} location={location} />
      </div>
      {report && (
        <div className={styles.dateRangeReportData}>
          <DailyReport
            report={report}
            start_date={dates.start_date}
            end_date={dates.end_date}
            master={master}
          />
        </div>
      )}
    </>
  );
};

export default DateRangeReport;
