import styles from "./EditUser.module.css";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../context/AuthContext";
import { UserList } from "../../../utils/api";
import toast from "react-hot-toast";

const EditUser = ({ userId, closeEdit }) => {
  const { user } = useAuth();
  const [userData, setUserData] = useState(null);

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    is_admin: false,
    terminated: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  useEffect(() => {
    const gitem = async () => {
      const ulist = await UserList();
      if (!ulist.success) {
        toast.error(ulist.message);
        setUserData(null);
        return;
      }
      const foundUser = ulist.users.find((u) => u.id === parseInt(userId, 10));
      if (foundUser) {
        setUserData(foundUser);
        setFormData({
          first_name: foundUser.first_name,
          last_name: foundUser.last_name,
          email: foundUser.email,
          is_admin: foundUser.is_admin,
          terminated: !!foundUser.terminated,
        });
      } else {
        toast.error("User not found");
        setUserData(null);
      }
    };
    gitem();
  }, [userId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      email: formData.email,
    };
    if (user?.is_admin) {
      payload.is_admin = !!formData.is_admin;
      payload.terminated = !!formData.terminated;
    }

    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success("User updated successfully");
      closeEdit();
    } catch (error) {
      console.error("Error updating user:", error);
      toast.error(`Error updating user: ${error.message}`);
    }
  };

  if (!userData) return null;
  return (
    <form className={styles.editUserForm} onSubmit={handleSubmit}>
      <div>
        <label htmlFor="first_name">First Name</label>
        <input
          type="text"
          name="first_name"
          id="first_name"
          value={formData.first_name}
          onChange={handleChange}
        />
      </div>
      <div>
        <label htmlFor="last_name">Last Name</label>
        <input
          type="text"
          name="last_name"
          id="last_name"
          value={formData.last_name}
          onChange={handleChange}
        />
      </div>
      <div>
        <label htmlFor="email">Email</label>
        <input
          type="email"
          name="email"
          id="email"
          value={formData.email}
          onChange={handleChange}
        />
      </div>
      {user?.is_admin && (
        <>
          <div>
            <label htmlFor="is_admin">
              Admin
              <input
                type="checkbox"
                name="is_admin"
                id="is_admin"
                checked={!!formData.is_admin}
                onChange={handleChange}
              />
            </label>
          </div>
          <div>
            <label htmlFor="terminated">
              Terminated
              <input
                type="checkbox"
                name="terminated"
                id="terminated"
                checked={!!formData.terminated}
                onChange={handleChange}
              />
            </label>
          </div>
        </>
      )}
      <button type="submit">Save Changes</button>
    </form>
  );
};

export default EditUser;
