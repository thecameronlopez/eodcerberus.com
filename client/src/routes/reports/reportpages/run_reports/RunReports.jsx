import styles from "./RunReports.module.css";
import React, { useRef, useState, useEffect } from "react";
import { useAuth } from "../../../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import EOD from "../../../../components/report/EOD";
import { useReactToPrint } from "react-to-print";
import { UserList, LocationList } from "../../../../utils/api";
import ReportParams from "../../../../components/reportparams/ReportParams";
import { getTodayLocalDate } from "../../../../utils/tools";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPrint } from "@fortawesome/free-solid-svg-icons";

const REPORT_TYPES = {
  user_eod: "User Report",
  multi_user: "Multi-User Report",
  location: "Location Report",
  multi_location: "Multi-Location Report",
  master: "Master Report",
};

/*
if report_type = user_od
params = start, user_id, report_type

if report_type = multi_user_eod
params = start, end, [user_ids], report_type

if report_type = location
params = start, end, location_id, report_type

if report_type = multi_location
paramas = start, end, [location_ids], report_type


*/

const RunReports = () => {
  const { user } = useAuth();
  const today = new Date();
  //Report Type filter state
  const [reportType, setReportType] = useState("user_eod");
  //Date filter state
  const [reportDate, setReportDate] = useState({
    start: getTodayLocalDate(),
    end: getTodayLocalDate(),
  });
  //location paramas
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(user.location_id);
  //user params
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(user.id);
  //Errors
  const [error, setError] = useState("");

  //printing
  const contentRef = useRef(null);
  const printFn = useReactToPrint({ contentRef });
  //report data
  const [report, setReport] = useState(null);
  const [meta, setMeta] = useState(null);

  useEffect(() => {
    setReport(null);
    setMeta(null);
  }, [reportType]);

  const setURL = (rtype) => {
    const params = new URLSearchParams({
      start: reportDate.start,
      end: reportDate.end,
      type: rtype,
    });
    if (rtype === "user_eod") {
      params.set("users", selectedUser);
    }
    if (rtype === "multi_user") {
      params.set("users", selectedUsers.join(","));
    }
    if (rtype === "location") {
      params.set("locations", selectedLocation);
    }
    if (rtype === "multi_location") {
      params.set("locations", selectedLocations.join(","));
    }

    return `/api/reports/summary?${params.toString()}`;
  };

  //Run Report
  const runReport = async () => {
    if (
      (reportType === "multi_user" && selectedUsers.length === 0) ||
      (reportType === "multi_location" && selectedLocations.length === 0)
    ) {
      toast.error("Must select at least 1 parameter");
      return;
    }
    try {
      const response = await fetch(setURL(reportType), {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      if (!data.success) {
        setError(data.message);
        throw new Error(data.message);
      }
      setReport(data.report);
      setMeta(data.meta);
    } catch (error) {
      console.error("[REPORT ERROR]: ", error);
      toast.error(error.message);
    }
  };

  return (
    <div className={styles.reportsPage}>
      <div className={styles.reportFilters}>
        <div>
          <button
            className={styles.prinnit}
            onClick={printFn}
            disabled={!report}
          >
            <FontAwesomeIcon icon={faPrint} />
          </button>
          <div className={styles.reportType}>
            <label htmlFor="report_type">Select Report Type</label>
            <select
              name="report_type"
              id="report_type"
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
            >
              {Object.entries(REPORT_TYPES).map(([key, value], index) => (
                <option value={key} key={index}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div className={styles.reportDate}>
            <label htmlFor="start">
              Start
              <input
                type="date"
                name="start"
                id="start"
                value={reportDate.start}
                onChange={(e) =>
                  setReportDate({ ...reportDate, start: e.target.value })
                }
              />
            </label>
            <label htmlFor="end">
              End
              <input
                type="date"
                name="end"
                id="end"
                value={reportDate.end}
                onChange={(e) =>
                  setReportDate({ ...reportDate, end: e.target.value })
                }
              />
            </label>
          </div>
        </div>
        <ReportParams
          reportType={reportType}
          userState={{
            selectedUser,
            setSelectedUser,
            selectedUsers,
            setSelectedUsers,
          }}
          locationState={{
            selectedLocation,
            setSelectedLocation,
            selectedLocations,
            setSelectedLocations,
          }}
          styles={styles}
        />
        <button className={styles.runnit} onClick={runReport}>
          Run Report
        </button>
      </div>
      <div className={styles.reported}>
        {report && <EOD report={report} meta={meta} ref={contentRef} />}
      </div>
    </div>
  );
};

export default RunReports;
