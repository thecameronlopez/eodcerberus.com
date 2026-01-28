import toast from "react-hot-toast";
import styles from "./Locations.module.css";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBan,
  faPenToSquare,
  faTrash,
} from "@fortawesome/free-solid-svg-icons";

const Locations = () => {
  const { user, setUser } = useAuth();
  const [locations, setLocations] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    address: "",
    current_tax_rate: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  useEffect(() => {
    const getLoc = async () => {
      const response = await fetch("/api/read/locations");
      const data = await response.json();
      if (!data.success) {
        toast.error(data.message);
        setLocations(null);
      }
      setLocations(data.locations);
    };
    getLoc();
  }, [user]);

  useEffect(() => {
    if (!editingId) {
      setFormData({
        name: "",
        code: "",
        address: "",
        current_tax_rate: "",
      });
    }
  }, [editingId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!confirm("Submit new location?")) return;

    const rate = Number(formData.current_tax_rate);

    if (isNaN(rate) || rate < 0 || rate > 20) {
      toast.error("Enter a valid tax rate (0–20%)");
      return;
    }

    const payload = {
      ...formData,
      current_tax_rate: rate / 100,
    };

    try {
      const response = await fetch("/api/create/location", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      setLocations((prev) => [...prev, data.new_location]);
      setFormData({
        name: "",
        code: "",
        address: "",
        current_tax_rate: "",
      });
      toast.success("Location added");
    } catch (error) {
      console.error("[NEW LOCATION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  const handleUpdateLocation = async (e) => {
    e.preventDefault();
    if (!confirm("Update location?")) return;
    const payload = {
      ...formData,
      current_tax_rate: Number(formData.current_tax_rate) / 100,
    };
    try {
      const response = await fetch(`/api/update/location/${editingId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        credentials: "include",
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      setLocations((prev) =>
        prev.map((loc) => (loc.id === editingId ? data.new_location : loc))
      );
      setFormData({
        name: "",
        code: "",
        address: "",
        current_tax_rate: "",
      });
      setEditingId(null);
      toast.success(data.message);
    } catch (error) {
      console.error("[UPDATE LOCATION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  const updateDefault = async (location_id) => {
    if (!confirm("Update default location?")) return;
    try {
      const response = await fetch(
        `/api/update/user/location/${user.id}?location_id=${location_id}`,
        {
          method: "PATCH",
          credentials: "include",
        }
      );
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      setUser((prev) => ({ ...prev, location_id: location_id }));
      toast.success(data.message);
    } catch (error) {
      console.error("[DEFAULT LOCATION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  const sendLocationDataToForm = (index) => {
    setFormData({
      name: locations[index].name || "",
      code: locations[index].code || "",
      address: locations[index].address || "",
      current_tax_rate:
        Number(locations[index].current_tax_rate * 100).toFixed(2) || 0.0,
    });
  };

  return (
    <div className={styles.locationsPage}>
      <h1>Locations </h1>
      <div className={styles.locationDataBlock}>
        <div className={styles.locations}>
          {locations?.map(
            ({ id, name, code, address, current_tax_rate }, index) => (
              <div key={index} className={styles.location}>
                <div className={styles.locationControls}>
                  {user.location_id !== id ? (
                    <button
                      className={styles.setDefault}
                      onClick={() => updateDefault(id)}
                    >
                      Set as default
                    </button>
                  ) : (
                    <p className={styles.defaultTag}>Default Location</p>
                  )}
                  {user.is_admin && (
                    <>
                      <button
                        onClick={() => {
                          sendLocationDataToForm(index);
                          setEditingId(editingId === id ? null : id);
                        }}
                      >
                        <FontAwesomeIcon
                          icon={editingId === id ? faBan : faPenToSquare}
                        />
                      </button>
                      <button className={styles.deleteLocationButton}>
                        <FontAwesomeIcon icon={faTrash} />
                      </button>
                    </>
                  )}
                </div>
                <h3>{name}</h3>
                <p>
                  Address: <span>{address}</span>
                </p>
                <p>
                  Code: <span>{code}</span>
                </p>

                <p>
                  Current Tax Rate:{" "}
                  <span>{(Number(current_tax_rate) * 100).toFixed(2)}%</span>
                </p>
              </div>
            )
          )}
        </div>
        {user.is_admin && (
          <div className={styles.addLocationForm}>
            <h3>{editingId ? "Update" : "Add"} Location</h3>
            <form onSubmit={editingId ? handleUpdateLocation : handleSubmit}>
              <div>
                <label htmlFor="name">Location Name</label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>
              <div>
                <label htmlFor="code">Location Code</label>
                <input
                  type="text"
                  name="code"
                  id="code"
                  value={formData.code}
                  onChange={handleChange}
                  required
                />
              </div>
              <div>
                <label htmlFor="address">Address</label>
                <input
                  type="text"
                  name="address"
                  id="address"
                  value={formData.address}
                  onChange={handleChange}
                  required
                />
              </div>
              <div>
                <label htmlFor="current_tax_rate">Current Tax Rate (%)</label>
                <input
                  type="number"
                  step={"0.01"}
                  placeholder="0.00"
                  name="current_tax_rate"
                  id="current_tax_rate"
                  value={formData.current_tax_rate}
                  onChange={handleChange}
                  required
                />
              </div>
              <button type="submit">
                {editingId ? "Update" : "Add New"} Location
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default Locations;
