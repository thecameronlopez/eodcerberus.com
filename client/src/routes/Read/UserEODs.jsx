import toast from "react-hot-toast";
import { useAuth } from "../../context/AuthContext";
import styles from "./UserEODs.module.css";
import React, { useEffect, useState } from "react";
import { formatCurrency, formatDate } from "../../utils/Helpers";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFileInvoiceDollar } from "@fortawesome/free-solid-svg-icons";
import DailyReport from "../../components/DailyReport";

const UserEODs = ({ setComponent, setTicket }) => {
  const [eods, setEods] = useState([]);
  const { user } = useAuth();
  const today = new Date().toISOString().split("T")[0];
  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState(today);
  const [reportDate, setReportDate] = useState(today);
  const [users, setUsers] = useState([]);
  const [userId, setUserId] = useState(user.id);
  const [totals, setTotals] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch(`/api/read/get_users`, {
          method: "GET",
          credentials: "include",
        });
        const data = await response.json();
        if (!data.success) {
          throw new Error(data.message);
        }
        setUsers(data.users);
      } catch (error) {
        console.error("[ERROR]:", error);
        toast.error(`Error fetching employees: ${error.message}`);
      }
    };
    fetchUsers();
  }, []);

  useEffect(() => {
    setTotals(null);
    const fetchEODs = async () => {
      try {
        const response = await fetch(
          `/api/read/eod_by_date_range?start_date=${startDate}&end_date=${endDate}&user_id=${
            userId || null
          }`
        );
        const data = await response.json();
        if (!data.success) {
          throw new Error(data.message);
        }
        setEods(data.eods);
      } catch (error) {
        console.error("[ERROR]:", error);
        toast.error(error.message);
      }
    };
    fetchEODs();
  }, [userId, startDate, endDate]);

  const handleMonthChange = (month) => {
    if (month === "") {
      setStartDate(today);
      setEndDate(today);
      return;
    }

    const year = new Date().getFullYear();

    const start = `${year}-${month}-01`;
    const endDay = new Date(year, month, 0).getDate();
    const end = `${year}-${month}-${String(endDay).padStart(2, "0")}`;

    setStartDate(start);
    setEndDate(end);
  };

  const runReport = async (id) => {
    try {
      const response = await fetch(`/api/read/run_report/${id}/${reportDate}`);
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      console.log(data.totals);
      setTotals(data.totals);
    } catch (error) {
      console.error("[ERROR]: ", error);
      toast.error(error.message);
    }
  };

  return (
    <section>
      <div className={styles.searchBar}>
        <div className={styles.dateSearchBlock}>
          <div>
            <label htmlFor="month">Month</label>
            <select
              name="month"
              id="month"
              onChange={(e) => handleMonthChange(e.target.value)}
            >
              <option value="">--Select a month--</option>
              <option value="01">January</option>
              <option value="02">February</option>
              <option value="03">March</option>
              <option value="04">April</option>
              <option value="05">May</option>
              <option value="06">June</option>
              <option value="07">July</option>
              <option value="08">August</option>
              <option value="09">September</option>
              <option value="10">October</option>
              <option value="11">November</option>
              <option value="12">December</option>
            </select>
          </div>
          <div>
            <label htmlFor="employee">Employee</label>
            <select
              name="employee"
              id="employee"
              onChange={(e) => setUserId(e.target.value)}
              value={userId}
            >
              <option value="">--Select an employee--</option>
              {users.map(({ id, first_name, last_name }) => (
                <option key={id} value={id}>
                  {first_name} {last_name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className={styles.reportBlock}>
          <div>
            <label htmlFor="report_date">select a date</label>
            <input
              type="date"
              name="report_date"
              id="report_date"
              value={reportDate}
              onChange={(e) => {
                setStartDate(e.target.value);
                setEndDate(e.target.value);
                setReportDate(e.target.value);
              }}
            />
          </div>
          <button
            className={styles.runReportButton}
            onClick={() => runReport(userId)}
          >
            Run Report
            <FontAwesomeIcon icon={faFileInvoiceDollar} />
          </button>
        </div>
      </div>

      <div className={styles.eodListBox}>
        {totals ? (
          <DailyReport report={totals} date={reportDate} />
        ) : (
          <ul>
            {eods.map(
              ({
                id,
                ticket_number,
                date,
                sub_total,
                card,
                cash,
                checks,
                acima,
                tower_loan,
                extended_warranty,
                salesman,
              }) => (
                <li
                  key={id}
                  onClick={() => {
                    setTicket(ticket_number);
                    setComponent("read_eod");
                  }}
                >
                  <div>
                    <p>{formatDate(date)}</p>
                    <h3>{ticket_number}</h3>
                    <p className={styles.subTotal}>
                      Subtotal: {formatCurrency(sub_total)}
                    </p>
                    <small>
                      {salesman.first_name} {salesman.last_name[0]}.
                    </small>
                  </div>
                  <div>
                    <p>Card: {formatCurrency(card)}</p>
                    <p>Cash: {formatCurrency(cash)}</p>
                    <p>Checks: {formatCurrency(checks)}</p>
                    <p>Acima: {formatCurrency(acima)}</p>
                    <p>Tower Load: {formatCurrency(tower_loan)}</p>
                    <p>
                      Extended Warranty: {formatCurrency(extended_warranty)}
                    </p>
                  </div>
                </li>
              )
            )}
          </ul>
        )}
      </div>
    </section>
  );
};

export default UserEODs;
