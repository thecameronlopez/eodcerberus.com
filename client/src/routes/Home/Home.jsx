import { useAuth } from "../../context/AuthContext";
import styles from "./Home.module.css";
import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEllipsisVertical,
  faEye,
  faList,
  faSquarePlus,
} from "@fortawesome/free-solid-svg-icons";
import { useNavigate } from "react-router-dom";
import AddEOD from "../Create/AddEOD";
import ReadEOD from "../Read/ReadEOD";
import clsx from "clsx";

const Components = {
  add_eod: <AddEOD />,
  read_eod: <ReadEOD />,
};

const Home = () => {
  const { user } = useAuth();
  const [eods, setEods] = useState([]);
  const [component, setComponent] = useState("add_eod");
  const [activeButton, setActiveButton] = useState(0);
  const navigate = useNavigate();

  const handleClick = (index, componentName) => {
    setActiveButton(index);
    setComponent(componentName);
  };

  return (
    <section>
      <div className={styles.userBar}>
        <h2 className={styles.homeUser}>
          {user.first_name} {user.last_name}
        </h2>
        <div className={styles.userBarButtonBlock}>
          <button
            className={activeButton === 0 ? styles.activeButton : ""}
            onClick={() => handleClick(0, "add_eod")}
          >
            <FontAwesomeIcon icon={faSquarePlus} />
          </button>
          <button
            className={activeButton === 1 ? styles.activeButton : ""}
            onClick={() => handleClick(1, "read_eod")}
          >
            <FontAwesomeIcon icon={faEye} />
          </button>
          <button className={activeButton === 2 ? styles.activeButton : ""}>
            <FontAwesomeIcon icon={faList} />
          </button>
          <button className={activeButton === 3 ? styles.activeButton : ""}>
            <FontAwesomeIcon icon={faEllipsisVertical} />
          </button>
        </div>
      </div>
      <div>{Components[component]}</div>
    </section>
  );
};

export default Home;
