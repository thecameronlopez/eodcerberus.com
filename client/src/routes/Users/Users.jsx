import styles from "./Users.module.css";
import React, { useState, useEffect } from "react";
import UserBar from "../../components/UserBar";
import Register from "../Auth/Register";
import ViewUsers from "./ViewUsers/ViewUsers";
import UserAnalytics from "./UserAnalytics/UserAnalytics";

const Components = {
  register_user: Register,
  view_users: ViewUsers,
  user_analytics: UserAnalytics,
};
const Users = () => {
  const [component, setComponent] = useState("view_users");
  const SelectedComponent = Components[component];
  const pages = ["view_users", "user_analytics", "register_user"];
  return (
    <section>
      <UserBar
        title={"Users"}
        pages={pages}
        component={component}
        setComponent={setComponent}
      />
      <div>
        <SelectedComponent />
      </div>
    </section>
  );
};

export default Users;
