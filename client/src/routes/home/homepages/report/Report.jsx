import styles from "./Report.module.css";
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
  formatLocationName,
  formatCurrency,
  formatDate,
} from "../../../../utils/tools";
import { UserList } from "../../../../utils/api";
import toast from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faPrint,
  faSquareMinus,
  faSquarePlus,
} from "@fortawesome/free-solid-svg-icons";
import MoneyField from "../../../../components/MoneyField";
import EOD from "../../../../components/report/EOD";
import { useReactToPrint } from "react-to-print";
import { useRef } from "react";

const Report = () => {
  const { user, location, setLoading } = useAuth();
  const [users, setUsers] = useState(null);
  const [selectedUser, setSelectedUser] = useState(user.id || null);
  const [reportDate, setReportDate] = useState(getTodayLocalDate());
  const [report, setReport] = useState(null);
  const [meta, setMeta] = useState(null);
  const contentRef = useRef(null);
  const printFn = useReactToPrint({ contentRef });

  useEffect(() => {
    const ulist = async () => {
      const u = await UserList();
      if (!u.success) {
        toast.error(u.message);
        setUsers(null);
      }
      setUsers(u.users);
    };
    ulist();
  }, []);

  useEffect(() => {
    setReport(null);
    setMeta(null);
  }, [reportDate]);

  const runReport = async () => {
    try {
      const response = await fetch(
        `/api/reports/summary?start=${reportDate}&users=${selectedUser}&type=user_eod`
      );
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      setReport(data.report);
      setMeta(data.meta);
    } catch (error) {
      console.error("[EOD FETCH ERROR]: ", error);
      toast.error(error.message);
    }
  };

  if (!users) return null;

  return (
    <div className={styles.reportPage}>
      <div className={styles.reportHeader}>
        <div>
          {user.is_admin && (
            <select
              name="user_id"
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
            >
              <option value="">--select user--</option>
              {users.map((u, index) => (
                <option value={u.id} key={index}>
                  {u.first_name} {u.last_name}
                </option>
              ))}
            </select>
          )}
          <input
            type="date"
            name="date"
            id="date"
            value={reportDate}
            onChange={(e) => setReportDate(e.target.value)}
          />
        </div>
        <div className={styles.headerControls}>
          <button onClick={printFn}>
            <FontAwesomeIcon icon={faPrint} />
          </button>
          <button className={styles.runReport} onClick={runReport}>
            Run Report
          </button>
        </div>
      </div>
      {report && <EOD report={report} meta={meta} ref={contentRef} />}
    </div>
  );
};

export default Report;
