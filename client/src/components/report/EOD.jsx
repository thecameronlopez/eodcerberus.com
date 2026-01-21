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
    "ebay_payment",
  ],
};

const EOD = ({ report, meta, ref }) => {
  console.log("[REPORT]: ", report);
  console.log("[META]: ", meta);

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
        <img src={LOGO} className={styles.eodLogo} />
        <div className={styles.eodTitle}>
          <div>
            {setTitle(meta.report_type)}
            <p className={styles.eodDate}>{`${formatDate(
              meta.start,
            )} - ${formatDate(meta.end)}`}</p>
          </div>
          <div className={styles.grandTotals}>
            <h4>Grand Subtotal: {formatCurrency(report.grand.subtotal)}</h4>
            <h4>Grand Total: {formatCurrency(report.grand.total)}</h4>
          </div>
        </div>
      </div>
      <div className={styles.eodData}>
        <details open>
          <summary>Sales Category</summary>
          <ul>
            {Order.categories
              .map((key) => [key, report.categories[key]])
              .map(([key, value], index) => (
                <li key={index}>
                  <h4>{SALES_CATEGORY[key]}</h4>
                  <div>
                    <p>
                      Subtotal: <span>{formatCurrency(value.subtotal)}</span>
                    </p>
                    <p className={styles.taxAdded}>
                      Tax: <span>{formatCurrency(value.tax)}</span>
                    </p>
                    <p>
                      Total: <span>{formatCurrency(value.total)}</span>
                    </p>
                  </div>
                </li>
              ))}
          </ul>
        </details>
        <details open>
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
                    <div>
                      <p>
                        Subtotal: <span>{formatCurrency(value.subtotal)}</span>
                      </p>
                      <p className={styles.taxAdded}>
                        Tax: <span>{formatCurrency(value.tax)}</span>
                      </p>
                      {isCash && deductionApplied > 0 && (
                        <p className={styles.deductionApplied}>
                          Deductions:{" "}
                          <span>-{formatCurrency(deductionApplied)}</span>
                        </p>
                      )}
                      <p>
                        Total: <span>{formatCurrency(value.total)}</span>
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
