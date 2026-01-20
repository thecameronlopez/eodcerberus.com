import styles from "./UserBar.module.css";
import React, { useRef, useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useTabRouter } from "../../context/TabRouterContext";

const UserBar = ({ pages, section }) => {
  const { user } = useAuth();
  const { tabs, setTab, icons } = useTabRouter();
  const navigate = useNavigate();
  const located = useLocation();

  const activeTab = tabs[section];

  const handlePathNav = (path) => {
    navigate(path);
  };

  const MAIN_PATHS = ["/", "/reports", "/settings"];

  return (
    <div className={styles.userBar}>
      {/* MAIN ROUTES */}
      <div className={styles.userBarPath}>
        <h2 className={styles.homeUser}>
          {user.first_name} {user.last_name}
        </h2>
        <div className={styles.pathButtons}>
          {MAIN_PATHS.map((path, index) => (
            <button
              key={index}
              onClick={() => handlePathNav(path)}
              className={located.pathname === path ? styles.activePath : ""}
            >
              <FontAwesomeIcon icon={icons[path]} />
            </button>
          ))}
        </div>
      </div>

      {/* ROUTE TABS */}
      <div className={styles.userBarButtonBlock}>
        {pages?.map((page, index) => (
          <button
            key={index}
            className={activeTab === page ? styles.activeButton : ""}
            onClick={() => setTab(section, page)}
            title={page}
          >
            <FontAwesomeIcon icon={icons[page]} />
          </button>
        ))}
      </div>
    </div>
  );
};

export default UserBar;
