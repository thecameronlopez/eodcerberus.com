import styles from "./Reports.module.css";
import React, { useState } from "react";
import UserBar from "../../components/userbar/UserBar";
import { useAuth } from "../../context/AuthContext";
import RunReports from "./reportpages/run_reports/RunReports";
import TicketList from "./reportpages/ticket_list/TicketList";
import { useTabRouter } from "../../context/TabRouterContext";

const PAGES = {
  run_reports: RunReports,
  ticket_list: TicketList,
};

const Reports = () => {
  const { tabs } = useTabRouter();
  const activeTab = tabs.reports;

  const SelectedComponent = PAGES[activeTab];
  return (
    <div>
      <UserBar pages={Object.keys(PAGES)} section={"reports"} />
      <SelectedComponent />
    </div>
  );
};

export default Reports;
