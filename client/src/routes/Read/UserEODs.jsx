import toast from "react-hot-toast";
import { useAuth } from "../../context/AuthContext";
import styles from "./UserEODs.module.css";
import React, { useEffect, useState } from "react";
import { formatCurrency, formatDate, getToday } from "../../utils/Helpers";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faFileInvoiceDollar,
  faPenToSquare,
} from "@fortawesome/free-solid-svg-icons";
import DailyReport from "../../components/DailyReport";

const UserEODs = ({ setComponent, setTicket }) => {
  const [eods, setEods] = useState([]);
  const { user } = useAuth();
  const today = new Date().toISOString().split("T")[0];
  const [startDate, setStartDate] = useState(getToday());
  const [endDate, setEndDate] = useState(getToday());
  const [reportDate, setReportDate] = useState(getToday());
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
    setReportDate(start);
  };

  const runReport = async (id) => {
    try {
      const response = await fetch(`/api/read/run_report/${id}/${reportDate}`);
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
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
      {totals ? (
        <DailyReport report={totals} date={reportDate} />
      ) : (
        <ul className={styles.eodListBox}>
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
              used,
              ["new"]: new_appliances,
              diagnostic_fees,
              ebay_returns,
              refunds,
              ebay_sales,
              in_shop_repairs,
              parts,
              delivery,
              service,
            }) => (
              <li key={id}>
                <div>
                  <FontAwesomeIcon
                    icon={faPenToSquare}
                    onClick={() => {
                      setTicket(ticket_number);
                      setComponent("read_eod");
                    }}
                  />
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
                  <p>New: {formatCurrency(new_appliances)}</p>
                  <p>Used: {formatCurrency(used)}</p>
                  <p>Extended Warranty: {formatCurrency(extended_warranty)}</p>
                  <p>In Shop Repairs: {formatCurrency(in_shop_repairs)}</p>
                  <p>Ebay Sales: {formatCurrency(ebay_sales)}</p>
                  <p>Diagnostic Fees: {formatCurrency(diagnostic_fees)}</p>
                  <p>Delivery: {formatCurrency(delivery)}</p>
                  <p>Parts: {formatCurrency(parts)}</p>
                  <p>Service: {formatCurrency(service)}</p>
                  <p>Card: {formatCurrency(card)}</p>
                  <p>Cash: {formatCurrency(cash)}</p>
                  <p>Checks: {formatCurrency(checks)}</p>
                  <p>Acima: {formatCurrency(acima)}</p>
                  <p>Tower Load: {formatCurrency(tower_loan)}</p>
                  <p className={styles.redP}>
                    Refunds: {formatCurrency(refunds)}
                  </p>
                  <p className={styles.redP}>
                    Ebay Returns: {formatCurrency(ebay_returns)}
                  </p>
                </div>
              </li>
            )
          )}
        </ul>
      )}
    </section>
  );
};

export default UserEODs;
