import styles from "./Toggler.module.css";
import React from "react";
import { formatLocationName } from "../../utils/Helpers";

const Toggler = ({ val, setVal, location }) => {
  return (
    <div className={styles.reportTypeToggler}>
      <span className={val ? styles.masterInactive : ""}>
        {formatLocationName(location)}
      </span>

      <label className={styles.masterToggle}>
        <input type="checkbox" checked={val} onChange={() => setVal(!val)} />
        <span className={styles.masterSlider}></span>
      </label>

      <span className={!val ? styles.masterInactive : ""}>Master</span>
    </div>
  );
};

export default Toggler;
