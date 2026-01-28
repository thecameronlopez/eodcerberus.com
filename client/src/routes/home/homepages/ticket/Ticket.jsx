import styles from "./Ticket.module.css";
import { useAuth } from "../../../../context/AuthContext";
import React, { useEffect, useState } from "react";
import {
  SALES_CATEGORY,
  DEPARTMENTS,
  LOCATIONS,
  PAYMENT_TYPE,
} from "../../../../utils/enums";
import {
  getTodayLocalDate,
  renderOptions,
  formatLocationName,
} from "../../../../utils/tools";
import { UserList } from "../../../../utils/api";
import toast from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquarePlus } from "@fortawesome/free-solid-svg-icons";
import MoneyField from "../../../../components/MoneyField";

const Ticket = () => {
  const { user, location, setLoading } = useAuth();
  const [users, setUsers] = useState([]);
  const [formData, setFormData] = useState({
    ticket_number: "",
    date: getTodayLocalDate(),
    location_id: user.location_id,
    user_id: user.id,
    line_items: [],
  });

  useEffect(() => {
    const response = async () => {
      const listing = await UserList();
      if (!listing.success) {
        toast.error(listing.message);
        return;
      }
      setUsers(listing.users);
    };
    response();
  }, []);

  /* ------------------ handle line items ------------------ */
  const addLineItem = () => {
    setFormData((prev) => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        {
          category: "",
          payment_type: "",
          unit_price: "",
          is_return: false,
        },
      ],
    }));
  };

  const updateLineItem = (index, field, value) => {
    setFormData((prev) => {
      const items = [...prev.line_items];
      items[index] = { ...items[index], [field]: value };
      return { ...prev, line_items: items };
    });
  };

  const removeLineItem = (index) => {
    setFormData((prev) => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index),
    }));
  };

  /* ------------------ submit ticket ------------------ */
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!confirm("Submit Ticket?")) return;
    if (!formData.line_items.length) {
      toast.error("At least one line item is required");
      return;
    }
    if (!formData.ticket_number) {
      toast.error("Ticket number is required");
      return;
    }

    const payload = {
      ticket_number: Number(formData.ticket_number),
      location_id: Number(user.location_id),
      user_id: Number(formData.user_id),
      date: formData.date,
      line_items: formData.line_items.map((li) => ({
        category: li.category,
        payment_type: li.payment_type,
        unit_price: Number(li.unit_price),
        is_return: li.is_return,
      })),
    };
    setLoading(true);
    try {
      const response = await fetch("/api/create/ticket", {
        method: "POST",
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
      setFormData({
        ticket_number: "",
        user_id: user.id,
        location_id: user.location_id,
        date: getTodayLocalDate(),
        line_items: [],
      });
      toast.success(data.message);
    } catch (error) {
      console.error("[TICKET SUBMISSION ERROR]: ", error);
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.ticketContainer}>
      <form className={styles.ticketForm} onSubmit={handleSubmit}>
        <div className={styles.formTopBar}>
          {user.is_admin && (
            <div>
              <label htmlFor="user_id">Submit As</label>
              <select
                name="user_id"
                id="user_id"
                value={formData.user_id}
                onChange={(e) => {
                  setFormData({ ...formData, user_id: e.target.value });
                }}
                className={styles.adminUserSelect}
              >
                {users?.map(({ id, first_name, last_name }, index) => (
                  <option value={id} key={index}>
                    {first_name} {last_name}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div>
            <label htmlFor="date">Date</label>
            <input
              type="date"
              name="date"
              id="date"
              value={formData.date}
              onChange={(e) =>
                setFormData({ ...formData, date: e.target.value })
              }
            />
          </div>
          <div>
            <label htmlFor="ticket_number">Ticket Number</label>
            <input
              type="text"
              name="ticket_number"
              id="ticket_number"
              value={formData.ticket_number}
              onChange={(e) => {
                setFormData({ ...formData, ticket_number: e.target.value });
              }}
            />
          </div>
          <div className={styles.unitCount}>
            <label htmlFor="units">Units: </label>
            <p>{formData.line_items.length}</p>
          </div>
          <div className={styles.locale}>
            <label htmlFor="location">Location:</label>
            <p>{user.location.name}</p>
          </div>
        </div>
        <div className={styles.lineItems}>
          <h3>
            Line Items{" "}
            <button type="button" onClick={addLineItem}>
              <FontAwesomeIcon icon={faSquarePlus} />
            </button>
          </h3>
          {formData.line_items.map((li, index) => (
            <div key={index} className={styles.lineItem}>
              <div>
                <label htmlFor="category">Sales Category</label>
                <select
                  value={li.category}
                  onChange={(e) =>
                    updateLineItem(index, "category", e.target.value)
                  }
                  required
                >
                  <option value="">--select a sales category--</option>
                  {renderOptions(SALES_CATEGORY)}
                </select>
              </div>
              <div>
                <label htmlFor="payment_type">Payment Type</label>
                <select
                  name="payment_type"
                  value={li.payment_type}
                  onChange={(e) =>
                    updateLineItem(index, "payment_type", e.target.value)
                  }
                  required
                >
                  <option value="">--select payment type--</option>
                  {renderOptions(PAYMENT_TYPE)}
                </select>
              </div>
              <div>
                <label htmlFor="unit_price">Unit Price</label>
                <MoneyField
                  name={"unit_price"}
                  value={li.unit_price || 0}
                  onChange={(e) =>
                    updateLineItem(index, "unit_price", e.target.value)
                  }
                  placeholder={"$0.00"}
                  className={styles.unitPriceInput}
                />
              </div>
              <div className={styles.returnBox}>
                <label htmlFor="is_return">Return</label>
                <input
                  type="checkbox"
                  name="is_return"
                  checked={li.is_return}
                  onChange={(e) =>
                    updateLineItem(index, "is_return", e.target.checked)
                  }
                />
              </div>

              <button
                className={styles.removeLiButton}
                type="button"
                onClick={() => removeLineItem(index)}
              >
                X
              </button>
            </div>
          ))}
        </div>
        <button type="submit" disabled={formData.line_items.length === 0}>
          Submit Ticket
        </button>
      </form>
    </div>
  );
};

export default Ticket;
