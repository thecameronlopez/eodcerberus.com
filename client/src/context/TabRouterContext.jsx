import { useContext, useState, createContext } from "react";
import {
  faHouse,
  faGears,
  faClipboard,
  faSquarePlus,
  faMoneyBillTransfer,
  faMagnifyingGlass,
  faArrowTrendUp,
  faRankingStar,
  faLocationCrosshairs,
  faUsers,
  faPersonRunning,
  faLayerGroup,
  faList,
} from "@fortawesome/free-solid-svg-icons";

const TabRouterContext = createContext();

export const TabRouterProvider = ({ children }) => {
  const [tabs, setTabs] = useState({
    home: "ticket",
    settings: "locations",
    reports: "run_reports",
  });

  const setTab = (section, tab) => {
    setTabs((prev) => ({ ...prev, [section]: tab }));
  };

  const icons = {
    //main routes
    "/": faHouse,
    "/settings": faGears,
    "/reports": faClipboard,

    // Home tabs
    ticket: faSquarePlus,
    deduction: faMoneyBillTransfer,
    search: faMagnifyingGlass,
    report: faArrowTrendUp,
    ranking: faRankingStar,

    //Settings tabs
    locations: faLocationCrosshairs,
    users: faUsers,
    categories: faList,

    //Reports tabs
    run_reports: faPersonRunning,
    ticket_list: faLayerGroup,
  };

  return (
    <TabRouterContext.Provider value={{ tabs, setTab, icons }}>
      {children}
    </TabRouterContext.Provider>
  );
};

export const useTabRouter = () => useContext(TabRouterContext);
