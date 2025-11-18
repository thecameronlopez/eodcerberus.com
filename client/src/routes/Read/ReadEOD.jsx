import styles from "./ReadEOD.module.css";
import React, { useState } from "react";

const ReadEOD = () => {
  const [ticketNumber, setTicketNumber] = useState("");
  return (
    <section>
      <div className={styles.searchBar}>
        <div className={styles.ticketNumberSearch}>
          <label htmlFor="ticket_number">Enter Ticket Number</label>
          <input
            type="text"
            name="ticket_number"
            id="ticket_number"
            value={ticketNumber}
            onChange={(e) => setTicketNumber(e.target.value)}
          />
        </div>
        <div className={styles.monthSearch}>
          <label htmlFor="month">Month</label>
          <select name="month" id="month">
            <option value="">--Select a month--</option>
          </select>
        </div>
        <div className={styles.personSearch}>
          <label htmlFor="employee">Employee</label>
          <select name="employee" id="employee">
            <option value="">--Select a an employee--</option>
          </select>
        </div>
      </div>
    </section>
  );
};

export default ReadEOD;
