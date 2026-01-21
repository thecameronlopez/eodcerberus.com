import styles from "./TicketList.module.css";
import React, { useEffect, useState } from "react";
import {
  formatDateObj,
  formatDate,
  getTodayLocalDate,
  renderOptions,
  formatCurrency,
} from "../../../../utils/tools";
import { useAuth } from "../../../../context/AuthContext";
import { MONTHS, SALES_CATEGORY, PAYMENT_TYPE } from "../../../../utils/enums";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBackwardStep,
  faEye,
  faForwardStep,
} from "@fortawesome/free-solid-svg-icons";
import { useNavigate } from "react-router-dom";
import { useTicket } from "../../../../context/TicketContext";
import { useTabRouter } from "../../../../context/TabRouterContext";

const TicketList = ({ setComponent }) => {
  const today = new Date();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { setSelectedTicketNumber } = useTicket();
  const { setTab } = useTabRouter();
  const [tickets, setTickets] = useState(null);
  const [date, setDate] = useState({
    start_date: getTodayLocalDate(),
    end_date: getTodayLocalDate(),
  });
  const [selectedMonth, setSelectedMonth] = useState("");

  const dateToISO = (date) => date.toISOString().split("T")[0];
  const startOfMonth = (year, month) => dateToISO(new Date(year, month, 1));
  const endOfMonth = (year, month) => dateToISO(new Date(year, month + 1, 0));

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const response = await fetch(
          `/api/read/tickets?start_date=${date.start_date}&end_date=${date.end_date}`,
        );

        const data = await response.json();
        if (data.success) {
          setTickets(data.tickets);
          console.log("Fetched tickets:", data.tickets);
        } else {
          console.error("Failed to fetch tickets:", data.message);
        }
      } catch (error) {
        console.error("Error fetching tickets:", error);
      }
    };

    fetchTickets();
  }, [date]);

  const openInSearch = (ticket_number) => {
    setSelectedTicketNumber(ticket_number);
    setTab("home", "search");
    navigate("/");
  };

  const handleControls = (action, value = null) => {
    const today = getTodayLocalDate();

    let { start_date, end_date } = date;

    switch (action) {
      case "today":
        setSelectedMonth("");
        setDate({ start_date: today, end_date: today });
        break;

      case "month":
        if (value === "") return;
        const year = new Date().getFullYear();
        const monthIndex = Number(value);

        setSelectedMonth(value);
        setDate({
          start_date: startOfMonth(year, monthIndex),
          end_date: endOfMonth(year, monthIndex),
        });
        break;
      case "prev":
      case "next":
        setSelectedMonth("");
        const baseDate =
          start_date !== end_date ? new Date(today) : new Date(start_date);

        baseDate.setDate(baseDate.getDate() + (action === "next" ? 1 : -1));

        const newDate = dateToISO(baseDate);
        setDate({ start_date: newDate, end_date: newDate });
        break;

      default:
        break;
    }
  };

  return (
    <div className={styles.ticketListPage}>
      <div className={styles.ticketControls}>
        <div className={styles.autoDate}>
          {/* <div className={styles.autoDateSelect}>
            <label htmlFor="month_of">
              <select
                value={selectedMonth}
                onChange={(e) => handleControls("month", e.target.value)}
              >
                <option value="">--select a month--</option>
                {renderOptions(MONTHS)}
              </select>
            </label>
          </div> */}
          <div className={styles.autoDateButtons}>
            <button onClick={() => handleControls("prev")}>
              <FontAwesomeIcon icon={faBackwardStep} />
            </button>
            <button onClick={() => handleControls("today")}>Today</button>
            <button onClick={() => handleControls("next")}>
              <FontAwesomeIcon icon={faForwardStep} />
            </button>
          </div>
        </div>
        <div className={styles.ticketListDatePicker}>
          <label htmlFor="start_date">
            Start Date
            <input
              type="date"
              name="start_date"
              id="start_date"
              value={date.start_date}
              onChange={(e) => setDate({ ...date, start_date: e.target.value })}
            />
          </label>
          <label htmlFor="end_date">
            End Date
            <input
              type="date"
              name="end_date"
              id="end_date"
              value={date.end_date}
              onChange={(e) => setDate({ ...date, end_date: e.target.value })}
            />
          </label>
        </div>
      </div>
      <div className={styles.listOfTickets}>
        <h2>
          {formatDate(date.start_date)} - {formatDate(date.end_date)}
        </h2>
        {tickets && tickets.length > 0 ? (
          <ul>
            {tickets.map((ticket) => (
              <li key={ticket.id} className={styles.ticketItem}>
                <div className={styles.ticketMetaData}>
                  <button
                    className={styles.viewThisTicket}
                    onClick={() => openInSearch(ticket.ticket_number)}
                  >
                    {/* <FontAwesomeIcon icon={faEye} /> */}
                    Manage Ticket
                  </button>
                  <p>Ticket #{ticket.ticket_number}</p>
                  <p>
                    User:{" "}
                    <span>
                      {ticket.user.first_name} {ticket.user.last_name[0]}.
                    </span>
                  </p>
                  <p>
                    Date: <span>{formatDate(ticket.ticket_date)}</span>
                  </p>
                  <p>
                    Subtotal: <span>{formatCurrency(ticket.subtotal)}</span>
                  </p>
                  <p>
                    Total: <span>{formatCurrency(ticket.total)}</span>
                  </p>
                </div>
                <div className={styles.ticketTransactions}>
                  {ticket.transactions.map((tx, txIndex) => (
                    <div key={txIndex} className={styles.ticketTransaction}>
                      <p className={styles.transactionHeader}>
                        Transaction Date{" "}
                        <span>{formatDate(tx.posted_date)}</span>
                      </p>
                      {tx.line_items.map((li, liIndex) => (
                        <div
                          key={liIndex}
                          className={styles.transactionLineItem}
                        >
                          <p>
                            Category: <span>{SALES_CATEGORY[li.category]}</span>
                          </p>
                          <p>
                            Payment Type:{" "}
                            <span>{PAYMENT_TYPE[li.payment_type]}</span>
                          </p>
                          <p>
                            Subtotal:{" "}
                            <span>{formatCurrency(li.unit_price)}</span>
                          </p>
                          <p>
                            Tax: <span>{formatCurrency(li.tax_amount)}</span>
                          </p>
                          <p>
                            Total: <span>{formatCurrency(li.total)}</span>
                          </p>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.noTickets}>No Tickets for this date range</p>
        )}
      </div>
    </div>
  );
};

export default TicketList;
