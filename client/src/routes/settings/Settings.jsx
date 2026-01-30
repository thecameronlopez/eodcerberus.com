import UserBar from "../../components/userbar/UserBar";
import { useAuth } from "../../context/AuthContext";
import Locations from "./settingspages/locations/Locations";
import Users from "./settingspages/users/Users";
import Categories from "./settingspages/categories/Categories";
import React, { useState } from "react";
import { useTabRouter } from "../../context/TabRouterContext";

const PAGES = {
  locations: Locations,
  users: Users,
  categories: Categories,
};

const Settings = () => {
  const { tabs } = useTabRouter();
  const activeTab = tabs.settings;

  const SelectedComponent = PAGES[activeTab];

  return (
    <div>
      <UserBar pages={Object.keys(PAGES)} section={"settings"} />
      <SelectedComponent />
    </div>
  );
};

export default Settings;
