import { UserList } from "../../../../utils/api";
import styles from "./Users.module.css";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import Register from "../../../auth/register/Register";
import EditUser from "../../../auth/edit/EditUser";
import { useAuth } from "../../../../context/AuthContext";
import { DEPARTMENTS } from "../../../../utils/enums";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEraser,
  faRotateLeft,
  faTrashCan,
  faUserPen,
  faUserSlash,
} from "@fortawesome/free-solid-svg-icons";

const Users = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState(null);
  const [editingID, setEditingID] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      const ulist = await UserList();
      if (!ulist.success) {
        toast.error(ulist.message);
        setUsers(null);
      }
      setUsers(ulist.users);
    };
    fetchUsers();
  }, []);

  const handleUser = async (userID, action) => {
    if (!confirm(`Are you sure you want to ${action} this user?`)) return;
    const URL = {
      terminate: `/api/update/user/${userID}/terminate`,
      delete: `/api/delete/user/${userID}`,
    };

    const METHOD = {
      terminate: "PUT",
      delete: "DELETE",
    };

    try {
      const response = await fetch(URL[action], {
        method: METHOD[action],
        credentials: "include",
      });
      const data = await response.json();
      if (data.success) {
        toast.success(data.message);
        const updatedUsers = users.filter((u) => u.id !== userID);
        setUsers(updatedUsers);
      } else {
        toast.error(data.message);
      }
    } catch (error) {
      toast.error("Error processing request.");
    }
  };

  if (!users) return null;

  return (
    <div className={styles.userSettingsPage}>
      <div className={styles.userListInSettings}>
        <h2>Users</h2>
        <ul>
          {users.map((u, index) => (
            <li key={index}>
              <div>
                <p>
                  <b>
                    {u.first_name} {u.last_name}
                  </b>
                </p>
                <p>
                  {u.location.name} {DEPARTMENTS[u.department]}
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
                    <button onClick={() => handleUser(u.id, "terminate")}>
                      Terminate
                      <FontAwesomeIcon
                        className={styles.terminateUser}
                        icon={faUserSlash}
                      />
                    </button>
                    <button onClick={() => handleUser(u.id, "delete")}>
                      Delete
                      <FontAwesomeIcon
                        className={styles.deleteUser}
                        icon={faTrashCan}
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
