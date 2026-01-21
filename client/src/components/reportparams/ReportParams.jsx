import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { UserList, LocationList } from "../../utils/api";
import { renderOptions, formatDate } from "../../utils/tools";
import { useAuth } from "../../context/AuthContext";

const REPORT_TYPES = {
  user_eod: "User Report",
  multi_user: "Multi-User Report",
  location: "Location Report",
  multi_location: "Multi-Location Report",
  master: "Master Report",
};

const ReportParams = ({ reportType, userState, locationState, styles }) => {
  const { user } = useAuth();
  //User filter state
  const [users, setUsers] = useState(null);
  const { selectedUser, setSelectedUser, selectedUsers, setSelectedUsers } =
    userState;
  //Location filter state
  const [locations, setLocations] = useState(null);
  const {
    selectedLocation,
    setSelectedLocation,
    selectedLocations,
    setSelectedLocations,
  } = locationState;

  //get/set users
  useEffect(() => {
    const userList = async () => {
      const res = await UserList();
      if (!res.success) {
        toast.error(res.message);
        return;
      }
      setUsers(res.users);
    };
    userList();
  }, [reportType]);
  //get/set locations
  useEffect(() => {
    const locationList = async () => {
      const res = await LocationList();
      if (!res.success) {
        toast.error(res.message);
        return;
      }
      setLocations(res.locations);
    };
    locationList();
  }, [reportType]);

  const userEOD = () => {
    return (
      <select
        name="user_id"
        value={selectedUser}
        onChange={(e) => setSelectedUser(e.target.value)}
        className={styles.userSelect}
      >
        <option value="">--select a user--</option>
        {users?.map((u, index) => (
          <option value={u.id} key={index}>
            {u.first_name} {u.last_name}
          </option>
        ))}
      </select>
    );
  };

  const locationReport = () => {
    return (
      <select
        name="location_id"
        value={selectedLocation}
        onChange={(e) => setSelectedLocation(e.target.value)}
        className={styles.locationSelect}
      >
        <option value="">--select a location--</option>
        {locations?.map((l, index) => (
          <option value={l.id} key={index}>
            {l.name}
          </option>
        ))}
      </select>
    );
  };

  const multiLocationReport = () => {
    return (
      <ul className={styles.paramList}>
        {locations?.map((l, index) => (
          <li key={index}>
            <input
              type="checkbox"
              name="location_id"
              id={`${l.id}_location_id`}
              value={l.id}
              checked={selectedLocations.includes(l.id)}
              onChange={(e) => {
                const value = Number(e.target.value);
                setSelectedLocations((prev) =>
                  e.target.checked
                    ? [...prev, value]
                    : prev.filter((v) => v !== value)
                );
              }}
            />
            <label htmlFor={`${l.id}_location_id`}>{l.name}</label>
          </li>
        ))}
      </ul>
    );
  };

  const multiUserReport = () => {
    return (
      <ul className={styles.paramList}>
        {users?.map((u, index) => (
          <li key={index}>
            <input
              type="checkbox"
              name="user_id"
              id={`${u.id}_user_id`}
              value={u.id}
              checked={selectedUsers.includes(u.id)}
              onChange={(e) => {
                const value = Number(e.target.value);
                setSelectedUsers((prev) =>
                  e.target.checked
                    ? [...prev, value]
                    : prev.filter((v) => v !== value)
                );
              }}
            />
            <label htmlFor={`${u.id}_user_id`}>
              {u.first_name} {u.last_name}
            </label>
          </li>
        ))}
      </ul>
    );
  };

  const renderInputs = (rtype) => {
    const inputs = {
      user_eod: userEOD(),
      location: locationReport(),
      multi_location: multiLocationReport(),
      multi_user: multiUserReport(),
    };
    return inputs[rtype];
  };

  if (reportType === "master") return null;

  return <div>{renderInputs(reportType)}</div>;
};

export default ReportParams;
