import { useAuth } from "../../context/AuthContext";
import styles from "./Home.module.css";
import React, { useState, useEffect, useRef } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useNavigate, useLocation, Link } from "react-router-dom";
import AddEOD from "../Create/AddEOD";
import ReadEOD from "../Read/ReadEOD";
import UserEODs from "../Read/UserEODs";
import clsx from "clsx";
import UserBar from "../../components/UserBar";
import AddDeduction from "../Create/AddDeduction";
import ViewDeductions from "../Users/ViewDeductions/ViewDeductions";
import ViewUsers from "../Users/ViewUsers/ViewUsers";

const Components = {
  add_eod: AddEOD,
  read_eod: (props) => <ReadEOD {...props} />,
  user_eods: (props) => <UserEODs {...props} />,
  deductions: AddDeduction,
  user_rankings: ViewUsers,
};

const Home = () => {
  const [component, setComponent] = useState("add_eod");
  const [ticket, setTicket] = useState(null);
  const { user } = useAuth();
  const title = `${user.first_name} ${user.last_name}`;
  const pages = [
    "add_eod",
    "deductions",
    "read_eod",
    "user_eods",
    "user_rankings",
  ];

  const SelectedComponent = Components[component];

  return (
    <section>
      <UserBar
        component={component}
        setComponent={setComponent}
        title={`${user.first_name} ${user.last_name}`}
        pages={pages}
      />
      <div className={styles.homeBox}>
        <SelectedComponent
          setComponent={setComponent}
          setTicket={setTicket}
          ticket={ticket}
        />
      </div>
    </section>
  );
};

export default Home;
