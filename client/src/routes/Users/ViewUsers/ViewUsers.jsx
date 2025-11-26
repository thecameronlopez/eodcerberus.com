import styles from "./ViewUsers.module.css";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser } from "@fortawesome/free-solid-svg-icons";
import { formatCurrency, months } from "../../../utils/Helpers";

const ViewUsers = () => {
  const [usersWithTotals, setUsersWithTotals] = useState([]);
  const month = months[new Date().getMonth()];

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch users
        const usersResp = await fetch("/api/read/get_users");
        const usersData = await usersResp.json();
        if (!usersData.success) throw new Error(usersData.error);

        // Fetch totals
        const totalsResp = await fetch("/api/read/monthly_totals");
        const totalsData = await totalsResp.json();
        if (!totalsData.success) throw new Error(totalsData.message);

        // Merge users with their totals
        const merged = usersData.users.map((user) => {
          const userTotal = totalsData.totals.find((t) => t.id === user.id);
          return {
            ...user,
            total: userTotal?.total || 0,
          };
        });

        // Sort descending by total
        merged.sort((a, b) => b.total - a.total);

        setUsersWithTotals(merged);
      } catch (err) {
        toast.error(err.message);
      }
    };

    fetchData();
  }, []);

  return (
    <section>
      {usersWithTotals.length > 0 ? (
        <ul className={styles.userList}>
          {usersWithTotals.map(
            ({ id, first_name, last_name, email, department, total }) => (
              <li key={id}>
                <div>
                  <h2>
                    {first_name} {last_name}
                  </h2>
                  <FontAwesomeIcon icon={faUser} />
                </div>
                <div>
                  <p>Total for {month}</p>
                  <p>
                    <strong>{formatCurrency(total)}</strong>
                  </p>
                </div>
                <div>
                  <p>
                    {department.charAt(0).toUpperCase() + department.slice(1)}
                  </p>
                  {/* <p>{email}</p> */}
                </div>
              </li>
            )
          )}
        </ul>
      ) : (
        <h1>Users not found.</h1>
      )}
    </section>
  );
};

export default ViewUsers;
