import styles from "./EOD.module.css";
import React, { useRef } from "react";
import LOGO from "../../assets/cerberus-logo-blue.png";
import { formatCurrency, formatDate } from "../../utils/tools";
import { PAYMENT_TYPE, SALES_CATEGORY } from "../../utils/enums";

//How i want the EOD ordered in UI
const Order = {
  categories: [
    "new_appliance",
    "used_appliance",
    "extended_warranty",
    "delivery",
    "diagnostic_fee",
    "in_shop_repair",
    "labor",
    "parts",
    "ebay_sale",
  ],
  payments: [
    "cash",
    "card",
    "check",
    "acima",
    "tower_loan",
    "stripe_payment",
    "snap",
    "ebay_payment",
  ],
};

const EOD = ({ report, meta, ref }) => {
  const setTitle = (rtype) => {
    switch (rtype) {
      case "user_eod":
        return (
          <p className={styles.userTitle}>
            {meta.users[0].first_name} {meta.users[0].last_name}
          </p>
        );

      case "multi_user":
        return (
          <ul className={styles.multiUserTitle}>
            {meta.users.map((u, i) => (
              <li key={i}>
                {u.first_name} {u.last_name}
              </li>
            ))}
          </ul>
        );

      case "location":
        return <p className={styles.locationTitle}>{meta.locations[0].name}</p>;

      case "multi_location":
        return (
          <ul className={styles.multiLocationTitle}>
            {meta.locations.map((loc, i) => (
              <li key={i}>{loc.name}</li>
            ))}
          </ul>
        );

      case "master":
        return <p className={styles.masterTitle}>Master</p>;

      default:
        return null;
    }
  };

  const dater = () => {
    return meta.report_type === "user_eod"
      ? formatDate(meta.start).toString()
      : `${formatDate(meta.start)} - ${formatDate(meta.end)}`;
  };

  if (!report || !meta) return null;
  return (
    <div className={styles.eodPage} ref={ref}>
      <div className={styles.eodHeader}>
        <div className={styles.headerTop}>
          <div className={styles.headerBrand}>
            <img src={LOGO} className={styles.eodLogo} alt="Cerberus logo" />
            <p className={styles.brandLabel}>Cerberus Report</p>
          </div>
          <div className={styles.titleBlock}>
            {setTitle(meta.report_type)}
            <p className={styles.eodDate}>
              {`${formatDate(meta.start)} - ${formatDate(meta.end)}`}
            </p>
          </div>
        </div>
        <div className={styles.grandTotals}>
          <p>
            Grand Subtotal
            <span>{formatCurrency(report.grand.subtotal)}</span>
          </p>
          <p>
            Grand Total
            <span>{formatCurrency(report.grand.total)}</span>
          </p>
        </div>
      </div>
      <div className={styles.eodData}>
        <details open className={styles.reportSection}>
          <summary>Sales Category</summary>
          <ul>
            {Order.categories
              .map((key) => [key, report.categories[key]])
              .map(([key, value], index) => (
                <li key={index}>
                  <h4>{SALES_CATEGORY[key]}</h4>
                  <div className={styles.metricGroup}>
                    <p>
                      Subtotal
                      <span>{formatCurrency(value.subtotal)}</span>
                    </p>
                    <p className={styles.taxAdded}>
                      Tax
                      <span>{formatCurrency(value.tax)}</span>
                    </p>
                    <p>
                      Total
                      <span>{formatCurrency(value.total)}</span>
                    </p>
                  </div>
                </li>
              ))}
          </ul>
        </details>
        <details open className={styles.reportSection}>
          <summary>Payment Methods</summary>
          <ul>
            {Order.payments
              .map((key) => [key, report.payments[key]])
              .map(([key, value], index) => {
                const isCash = key === "cash";
                const deductionApplied = isCash ? report.deductions || 0 : 0;
                const totalBeforeDeduction =
                  (value.subtotal || 0) + (value.tax || 0);
                return (
                  <li key={index}>
                    <h4>{PAYMENT_TYPE[key]}</h4>
                    <div className={styles.metricGroup}>
                      <p>
                        Subtotal
                        <span>{formatCurrency(value.subtotal)}</span>
                      </p>
                      <p className={styles.taxAdded}>
                        Tax
                        <span>{formatCurrency(value.tax)}</span>
                      </p>
                      {isCash && deductionApplied > 0 && (
                        <p className={styles.deductionApplied}>
                          Deductions
                          <span>-{formatCurrency(deductionApplied)}</span>
                        </p>
                      )}
                      <p>
                        Total
                        <span>{formatCurrency(value.total)}</span>
                      </p>
                    </div>
                  </li>
                );
              })}
          </ul>
        </details>
      </div>
    </div>
  );
};

export default EOD;
