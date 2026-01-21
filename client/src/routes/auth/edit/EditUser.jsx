import styles from "./EditUser.module.css";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";
import { UserList } from "../../../utils/api";
import toast from "react-hot-toast";
import { DEPARTMENTS } from "../../../utils/enums";
import { renderOptions } from "../../../utils/tools";

const EditUser = ({ userId, closeEdit }) => {
  const { user } = useAuth();
  const [userData, setUserData] = useState(null);

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    department: "",
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
      }
      const foundUser = ulist.users.find((u) => u.id === parseInt(userId));
      if (foundUser) {
        setUserData(foundUser);
        setFormData({
          first_name: foundUser.first_name,
          last_name: foundUser.last_name,
          email: foundUser.email,
          department: foundUser.department,
          is_admin: foundUser.is_admin,
        });
      } else {
        toast.error("User not found");
        setUserData(null);
      }
    };
    gitem();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/update/user/${userId}`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
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
      <div>
        <label htmlFor="department">Department</label>
        <select
          name="department"
          id="department"
          value={formData.department}
          onChange={handleChange}
        >
          {renderOptions(DEPARTMENTS)}
        </select>
      </div>
      <button type="submit">Save Changes</button>
    </form>
  );
};

export default EditUser;
