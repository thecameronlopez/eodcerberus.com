import styles from "./Ranking.module.css";
import React, { useEffect, useState } from "react";
import {
  formatCurrency,
  getTodayLocalDate,
  renderOptions,
} from "../../../../utils/tools";
import { DEPARTMENTS, MONTHS } from "../../../../utils/enums";
import toast from "react-hot-toast";
import { useAuth } from "../../../../context/AuthContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBackwardStep,
  faCrown,
  faForwardStep,
} from "@fortawesome/free-solid-svg-icons";

{
  /* <FontAwesomeIcon icon={faCrown} /> */
}

const Ranking = () => {
  const today = new Date();
  const { user } = useAuth();
  const [totals, setTotals] = useState(null);
  const [chosenDepartment, setChosenDepartment] = useState(
    user.department || "all"
  );
  const [date, setDate] = useState({
    year: today.getFullYear(),
    month: today.getMonth(),
  });

  useEffect(() => {
    const fetchTotals = async () => {
      try {
        const response = await fetch(
          `/api/read/monthly_totals?year=${date.year}&month=${
            date.month + 1
          }&department=${chosenDepartment}`
        );
        const data = await response.json();
        if (!data.success) {
          throw new Error(data.message);
        }
        setTotals(data.totals);
        // console.log(data.totals);
      } catch (error) {
        console.error("[TOTALS FETCH ERROR]: ", error);
        toast.error(error.message);
      }
    };

    fetchTotals();
  }, [date, chosenDepartment]);

  const moveMonth = (direction) => {
    setDate((prev) => {
      let newMonth = prev.month + direction;
      let newYear = prev.year;

      if (newMonth > 11) {
        newMonth = 0;
        newYear += 1;
      } else if (newMonth < 0) {
        newMonth = 11;
        newYear -= 1;
      }

      return { year: newYear, month: newMonth };
    });
  };

  if (!totals) return null;

  return (
    <div className={styles.rankingsPage}>
      <div className={styles.monthPicker}>
        <button onClick={() => moveMonth(-1)}>
          <FontAwesomeIcon icon={faBackwardStep} />
        </button>
        <span>
          {MONTHS[date.month]}, {date.year}
        </span>
        <button onClick={() => moveMonth(1)}>
          <FontAwesomeIcon icon={faForwardStep} />
        </button>
      </div>
      <div className={styles.userRank}>
        <select
          name="department"
          value={chosenDepartment}
          onChange={(e) => setChosenDepartment(e.target.value)}
        >
          <option value="all">All Departments</option>
          {renderOptions(DEPARTMENTS)}
        </select>
        <ul className={styles.rankingsBoard}>
          {totals
            .filter((u) => u.department === chosenDepartment || "all")
            .map((u, index) => (
              <li key={index}>
                {index === 0 && u.total !== 0 && (
                  <FontAwesomeIcon icon={faCrown} className={styles.theKing} />
                )}
                <h4>
                  {u.first_name} {u.last_name}
                </h4>
                <p>Total: {formatCurrency(u.total)}</p>
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
};

export default Ranking;
