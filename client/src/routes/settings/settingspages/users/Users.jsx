import { UserList } from "../../../../utils/api";
import styles from "./Users.module.css";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import Register from "../../../auth/register/Register";
import EditUser from "../../../auth/edit/EditUser";
import { useAuth } from "../../../../context/AuthContext";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faRotateLeft,
  faUserPen,
  faUserSlash,
} from "@fortawesome/free-solid-svg-icons";

const Users = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState(null);
  const [editingID, setEditingID] = useState(null);

  const fetchUsers = async () => {
    const ulist = await UserList();
    if (!ulist.success) {
      toast.error(ulist.message);
      setUsers(null);
      return;
    }
    setUsers(ulist.users);
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleTerminateToggle = async (targetUser) => {
    const nextTerminated = !targetUser.terminated;
    const actionWord = nextTerminated ? "terminate" : "restore";
    if (!confirm(`Are you sure you want to ${actionWord} this user?`)) return;

    try {
      const response = await fetch(`/api/users/${targetUser.id}`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ terminated: nextTerminated }),
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success(data.message || "User updated");
      setUsers((prev) =>
        (prev || []).map((u) => (u.id === targetUser.id ? { ...u, ...data.user } : u)),
      );
    } catch (error) {
      toast.error(error.message || "Error processing request.");
    }
  };

  if (!users) return null;

  return (
    <div className={styles.userSettingsPage}>
      <div className={styles.userListInSettings}>
        <h2>Users</h2>
        <ul>
          {users.map((u) => (
            <li key={u.id}>
              <div>
                <p>
                  <b>
                    {u.first_name} {u.last_name}
                  </b>
                </p>
                <p>
                  {u.location?.name} {u.department?.name}
                </p>
                {user.is_admin && (
                  <div className={styles.userControls}>
                    <button
                      onClick={() =>
                        editingID === null
                          ? setEditingID(u.id)
                          : setEditingID(null)
                      }
                    >
                      Edit
                      <FontAwesomeIcon
                        icon={editingID === u.id ? faRotateLeft : faUserPen}
                      />
                    </button>
                    <button onClick={() => handleTerminateToggle(u)}>
                      {u.terminated ? "Restore" : "Terminate"}
                      <FontAwesomeIcon
                        className={styles.terminateUser}
                        icon={faUserSlash}
                      />
                    </button>
                  </div>
                )}
              </div>
              {editingID === u.id && (
                <div className={styles.editForm}>
                  <EditUser
                    userId={u.id}
                    closeEdit={() => setEditingID(null)}
                  />
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
      <div className={styles.registerFormInSettings}>
        {user.is_admin && <Register />}
      </div>
    </div>
  );
};

export default Users;
