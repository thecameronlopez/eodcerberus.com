import styles from "./UserBar.module.css";
import React, { useRef, useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCaretDown,
  faChartSimple,
  faClipboardList,
  faClipboardUser,
  faEllipsisVertical,
  faFileContract,
  faFileInvoiceDollar,
  faMagnifyingGlass,
  faMoneyBillTransfer,
  faRankingStar,
  faUserPlus,
  faUsers,
} from "@fortawesome/free-solid-svg-icons";
import {
  faCalendarDays,
  faSquarePlus,
} from "@fortawesome/free-regular-svg-icons";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const paths = {
  add_eod: {
    icon: faSquarePlus,
  },
  read_eod: {
    icon: faMagnifyingGlass,
  },
  user_eods: {
    icon: faClipboardList,
  },
  view_users: {
    icon: faUsers,
  },
  register_user: {
    icon: faUserPlus,
  },
  user_analytics: {
    icon: faChartSimple,
  },
  deductions: {
    icon: faMoneyBillTransfer,
  },
  view_deductions: {
    icon: faFileInvoiceDollar,
  },
  date_range_report: {
    icon: faCalendarDays,
  },
  report_home: {
    icon: faFileContract,
  },
  user_reports: {
    icon: faClipboardUser,
  },
  user_rankings: {
    icon: faRankingStar,
  },
};

const UserBar = ({ setComponent, component, title, pages }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const { user, location } = useAuth();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);
  return (
    <div className={styles.userBar}>
      <h2 className={styles.homeUser}>{title}</h2>
      <div className={styles.userBarButtonBlock}>
        {pages?.map((page, index) => (
          <button
            key={index}
            className={component === page ? styles.activeButton : ""}
            onClick={() => setComponent(page)}
          >
            <FontAwesomeIcon icon={paths[page].icon} />
          </button>
        ))}
        <button
          className={menuOpen ? styles.activeButton : ""}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? (
            <FontAwesomeIcon icon={faCaretDown} />
          ) : (
            <FontAwesomeIcon icon={faEllipsisVertical} />
          )}
        </button>
      </div>
      {menuOpen && (
        <div className={styles.userMenu} ref={menuRef}>
          <Link to={"/"}>Home</Link>
          <Link to="/reports">Reports</Link>
          <Link to="/settings">Settings</Link>
          {user.is_admin && <Link to="/users">Users</Link>}
        </div>
      )}
    </div>
  );
};

export default UserBar;
