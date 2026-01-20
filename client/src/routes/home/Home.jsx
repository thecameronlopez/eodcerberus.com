import styles from "./Home.module.css";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import UserBar from "../../components/userbar/UserBar";
import { useTicket } from "../../context/TicketContext";
import { useTabRouter } from "../../context/TabRouterContext";

//PAGES
import Ticket from "./homepages/ticket/Ticket";
import Deduction from "./homepages/deduction/Deduction";
import Search from "./homepages/search/Search";
import Report from "./homepages/report/Report";
import Ranking from "./homepages/ranking/Ranking";

const PAGES = {
  ticket: Ticket,
  deduction: Deduction,
  search: Search,
  report: Report,
  ranking: Ranking,
};

const Home = () => {
  const { selectedTicketNumber, setSelectedTicketNumber } = useTicket();
  const { tabs, setTab } = useTabRouter();
  const [ticket, setTicket] = useState(null);

  const activeTab = tabs.home;
  const [ticketNumber, setTicketNumber] = useState("");

  useEffect(() => {
    if (selectedTicketNumber) {
      setTicketNumber(selectedTicketNumber);
      setSelectedTicketNumber(null);
      setTab("home", "search");
    }
  }, [selectedTicketNumber, setSelectedTicketNumber, setTab]);

  const SelectedComponent = PAGES[activeTab];

  return (
    <div className={styles.homeContainer}>
      <UserBar pages={Object.keys(PAGES)} section={"home"} />
      <SelectedComponent
        setTicket={setTicket}
        ticket={ticket}
        ticketNumber={ticketNumber}
        setTicketNumber={setTicketNumber}
      />
    </div>
  );
};

export default Home;
