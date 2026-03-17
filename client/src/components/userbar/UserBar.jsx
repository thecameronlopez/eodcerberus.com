import styles from "./UserBar.module.css";
import React, { useMemo, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown } from "@fortawesome/free-solid-svg-icons";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useTabRouter } from "../../context/TabRouterContext";

const UserBar = ({ pages, section }) => {
  const { user } = useAuth();
  const { tabs, setTab, icons } = useTabRouter();
  const navigate = useNavigate();
  const located = useLocation();
  const [tabsOpen, setTabsOpen] = useState(false);

  const activeTab = tabs[section];
  const orderedPages = useMemo(() => {
    if (!pages?.length) return [];
    return [...pages].sort((a, b) => {
      if (a === activeTab) return -1;
      if (b === activeTab) return 1;
      return 0;
    });
  }, [activeTab, pages]);

  const handlePathNav = (path) => {
    navigate(path);
  };

  const handleTabSelect = (page) => {
    setTab(section, page);
    setTabsOpen(false);
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
              aria-label={path === "/" ? "home" : path.replace("/", "")}
            >
              <FontAwesomeIcon icon={icons[path]} />
            </button>
          ))}
        </div>
      </div>

      {/* ROUTE TABS */}
      <div
        className={`${styles.userBarTabs} ${tabsOpen ? styles.tabsOpen : ""}`}
      >
        <button
          type="button"
          className={styles.mobileTabToggle}
          onClick={() => setTabsOpen((prev) => !prev)}
          aria-expanded={tabsOpen}
          aria-label={`${tabsOpen ? "collapse" : "expand"} ${section} tabs`}
        >
          <span className={styles.mobileTabToggleLabel}>
            <FontAwesomeIcon icon={icons[activeTab]} />
            <span>{activeTab}</span>
          </span>
          <FontAwesomeIcon icon={faChevronDown} className={styles.chevron} />
        </button>

        <div className={styles.userBarButtonBlock}>
          {orderedPages.map((page, index) => (
            <button
              key={index}
              className={activeTab === page ? styles.activeButton : ""}
              onClick={() => handleTabSelect(page)}
              title={page}
              aria-label={page}
            >
              <FontAwesomeIcon icon={icons[page]} />
              <span className={styles.buttonLabel}>{page}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default UserBar;
