import styles from "./DailyReport.module.css";
import React, { useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import {
  formatCurrency,
  formatDate,
  formatLocationName,
} from "../utils/Helpers";
import { faPrint } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const DailyReport = ({ report, date, start_date, end_date, master }) => {
  if (!report) return null;

  const title = report.salesman
    ? `${report.salesman.first_name} ${report.salesman.last_name}`
    : formatLocationName(report.location);

  const displayDate = date
    ? formatDate(date)
    : `${formatDate(start_date)} - ${formatDate(end_date)}`;

  const printPage = () => {
    window.print();
  };

  // useEffect(() => {
  //   console.log(report);
  //   console.log(title);
  // });
  return (
    <div className={styles.reportPage}>
      <div className={styles.reportHeader}>
        <div>
          <img
            src="/cerberus-logo.svg"
            style={{ width: "80px", alignSelf: "center" }}
            alt=""
          />
          <div>
            <h2>{master ? "Master" : title}</h2>
            <p className={styles.reportHeaderDate}>{displayDate}</p>
          </div>
        </div>
        <button className={styles.printPageButton} onClick={printPage}>
          <FontAwesomeIcon icon={faPrint} />
        </button>
      </div>
      <ul className={styles.reportData}>
        <li>
          <strong>Total Sales</strong>{" "}
          <span>{formatCurrency(report.total_sales)}</span>
        </li>
        <li>
          <strong>Total Units</strong>
          <span>{report.total_units}</span>
        </li>
        <li>
          <strong>New Appliance Sales</strong>{" "}
          <span>{formatCurrency(report.new_appliance_sales)}</span>
        </li>
        <li>
          <strong>Used Appliance Sales</strong>{" "}
          <span>{formatCurrency(report.used_appliance_sales)}</span>
        </li>
        <li>
          <strong>Extended Warranty Sales</strong>
          <span>{formatCurrency(report.extended_warranty_sales)}</span>
        </li>
        <li>
          <strong>Diagnostic Fees</strong>
          <span>{formatCurrency(report.diagnostic_fees)}</span>
        </li>
        <li>
          <strong>In-Shop Repairs</strong>
          <span>{formatCurrency(report.in_shop_repairs)}</span>
        </li>
        <li>
          <strong>Service Sales</strong>
          <span>{formatCurrency(report.service_sales)}</span>
        </li>
        <li>
          <strong>Parts Sales</strong>
          <span>{formatCurrency(report.parts_sales)}</span>
        </li>
        <li>
          <strong>Ebay Sales</strong>
          <span>{formatCurrency(report.ebay_sales)}</span>
        </li>
        <li>
          <strong>Delivery Sales</strong>
          <span>{formatCurrency(report.delivery)}</span>
        </li>
        <li>
          <strong>Total Card</strong>
          <span>{formatCurrency(report.card)}</span>
        </li>
        <li>
          <strong>Total Cash</strong>
          <span>{formatCurrency(report.cash)}</span>
        </li>
        <li>
          <strong>Total Checks</strong>
          <span>{formatCurrency(report.checks)}</span>
        </li>
        <li>
          <strong>Total Acima</strong>
          <span>{formatCurrency(report.acima)}</span>
        </li>
        <li>
          <strong>Total Tower Loan</strong>
          <span>{formatCurrency(report.tower_loan)}</span>
        </li>
        <li>
          <strong>Misc. Deductions</strong>
          <span>{formatCurrency(report.misc_deductions)}</span>
        </li>
        <li>
          <strong>Cash Deposits</strong>
          <span>{formatCurrency(report.cash_deposits)}</span>
        </li>
        <li>
          <strong>Total Refunds</strong>
          <span>{formatCurrency(report.refunds)}</span>
        </li>
        <li>
          <strong>Total Ebay Returns</strong>
          <span>{formatCurrency(report.ebay_returns)}</span>
        </li>
      </ul>
    </div>
  );
};

export default DailyReport;
