import styles from "./Search.module.css";
import { useAuth } from "../../../../context/AuthContext";
import { useNavigate } from "react-router-dom";
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
  formatCurrency,
  formatDate,
} from "../../../../utils/tools";
import { UserList } from "../../../../utils/api";
import toast from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faDeleteLeft,
  faMinus,
  faPenToSquare,
  faRotateLeft,
  faSquareMinus,
  faSquarePlus,
  faTrash,
  faXmark,
} from "@fortawesome/free-solid-svg-icons";
import MoneyField from "../../../../components/MoneyField";
import { useTicket } from "../../../../context/TicketContext";

const Search = ({ ticketNumber: initialTicketNumber }) => {
  const navigate = useNavigate();
  const { user, location, setLoading } = useAuth();
  const { selectedTicketNumber, setSelectedTicketNumber } = useTicket();
  const [users, setUsers] = useState([]);
  const [ticketNumber, setTicketNumber] = useState(initialTicketNumber || "");
  const [ticket, setTicket] = useState(null);
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    posted_date: getTodayLocalDate(),
    location_id: user.location_id,
    user_id: user.id,
    line_items: [
      {
        category: "",
        payment_type: "",
        amount: "",
        date: "",
        is_return: false,
      },
    ],
  });
  const [editData, setEditData] = useState({
    ticket_number: "",
    ticket_date: "",
    user_id: "",
  });

  useEffect(() => {
    if (initialTicketNumber) {
      setTicketNumber(initialTicketNumber);
    }
  }, [initialTicketNumber]);

  useEffect(() => {
    const fetchTicket = async (ticket_number) => {
      if (!ticket_number || ticket_number.length < 4) {
        setTicket(null);
        return;
      }
      try {
        const response = await fetch(`/api/read/ticket/${ticket_number}`);
        const data = await response.json();
        if (!data.success) {
          throw new Error(data.message);
        }
        setTicket(data.ticket);
      } catch (error) {
        toast.error(error.message);
        console.error("[TICKET FETCH ERROR]: ", error);
        setTicket(null);
      }
    };
    fetchTicket(ticketNumber || initialTicketNumber);
  }, [ticketNumber, editing, initialTicketNumber]);

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!confirm(`Add transaction to ticket#${ticket.ticket_number}?`)) {
      return;
    }

    if (formData.line_items.length < 1) {
      toast.error("You must add at leat 1 line item");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`/api/create/transaction/${ticket.id}`, {
        method: "POST",
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
      setTicket(data.ticket);
      setFormData({
        posted_date: "",
        user_id: user.id,
        location_id: user.location_id,
        line_items: [
          {
            category: "",
            payment_type: "",
            amount: "",
            date: "",
            is_return: false,
          },
        ],
      });
      setAdding(false);
      toast.success(data.message);
    } catch (error) {
      toast.error(error.message);
      console.error("[NEW LINE ITEM ERROR]: ", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTicket = async () => {
    if (!confirm(`Delete Ticket# ${ticket.ticket_number}?`)) return;

    try {
      const response = await fetch(`/api/delete/ticket/${ticket.id}`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success(data.message);
      setTicket(null);
      setTicketNumber("");
    } catch (error) {
      console.error("[TICKET DELETION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  const handleDeleteTransaction = async (txID) => {
    if (!confirm("Delete transaction?")) return;

    try {
      const response = await fetch(`/api/delete/transaction/${txID}`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success(data.message);
      setTicket((prev) => ({
        ...prev,
        transactions: prev.transactions.filter((tx) => tx.id !== txID),
      }));
      setEditing(false);
    } catch (error) {
      console.error("[TRANSACTION DELETION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  const handleDeleteLineItem = async (liID) => {
    if (!confirm("Delete line item?")) return;

    try {
      const response = await fetch(`/api/delete/line_item/${liID}`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success(data.message);
      setTicket((prev) => ({
        ...prev,
        transactions: prev.transactions.map((tx) => ({
          ...tx,
          line_items: tx.line_items.filter((li) => li.id !== liID),
        })),
      }));
      setEditing(false);
    } catch (error) {
      console.error("[LINE ITEM DELETION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  // console.log(ticket);

  return (
    <div className={styles.searchPage}>
      <div className={styles.ticketSearch}>
        <label htmlFor="ticket_number">Ticket Number:</label>
        <input
          type="text"
          name="ticket_number"
          value={ticketNumber}
          onChange={(e) => setTicketNumber(e.target.value)}
        />
      </div>
      {ticket && (
        <div className={styles.ticketData}>
          <div className={styles.ticketHeader}>
            <div>
              <h2>
                Ticket #{ticket.ticket_number}{" "}
                <div className={styles.ticketControls}>
                  <button
                    className={styles.addTransaction}
                    onClick={() => setAdding(!adding)}
                  >
                    <FontAwesomeIcon
                      icon={adding ? faSquareMinus : faSquarePlus}
                    />
                  </button>
                  <button
                    className={styles.editTicket}
                    onClick={() => setEditing(!editing)}
                  >
                    <FontAwesomeIcon
                      icon={editing ? faRotateLeft : faPenToSquare}
                    />
                  </button>
                  <button
                    className={styles.deleteTicket}
                    onClick={handleDeleteTicket}
                  >
                    <FontAwesomeIcon icon={faTrash} />
                  </button>
                </div>
              </h2>

              <p>
                {ticket.user.first_name} {ticket.user.last_name}
              </p>
              <p>{formatDate(ticket.ticket_date)}</p>
              <p>Store: {ticket.location.name}</p>
            </div>
            {adding && (
              <form className={styles.transactionForm} onSubmit={handleSubmit}>
                {user.is_admin && (
                  <div>
                    <label htmlFor="user_id">User</label>
                    <select
                      name="user_id"
                      value={formData.user_id}
                      onChange={(e) =>
                        setFormData({ ...formData, user_id: e.target.value })
                      }
                    >
                      <option value="">--select a user--</option>
                      {users.map((u, index) => (
                        <option value={u.id} key={index}>
                          {u.first_name} {u.last_name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                <div>
                  <label htmlFor="posted_date">Date</label>
                  <input
                    type="date"
                    name="posted_date"
                    value={formData.posted_date}
                    onChange={(e) =>
                      setFormData({ ...formData, posted_date: e.target.value })
                    }
                  />
                </div>

                <div>
                  <label htmlFor="line_items">
                    Line Items{" "}
                    <button
                      className={styles.addLineItem}
                      type="button"
                      onClick={addLineItem}
                    >
                      add
                    </button>
                  </label>
                  {formData.line_items.map((li, index) => (
                    <div className={styles.formLineItem} key={index}>
                      <button
                        type="button"
                        className={styles.removeLineItem}
                        onClick={() => removeLineItem(index)}
                      >
                        remove
                      </button>
                      <select
                        name="category"
                        value={li.category}
                        onChange={(e) =>
                          updateLineItem(index, "category", e.target.value)
                        }
                      >
                        <option value="">--select a category--</option>
                        {renderOptions(SALES_CATEGORY)}
                      </select>
                      <select
                        name="payment_type"
                        value={li.payment_type}
                        onChange={(e) =>
                          updateLineItem(index, "payment_type", e.target.value)
                        }
                      >
                        <option value="">--select a payment type--</option>
                        {renderOptions(PAYMENT_TYPE)}
                      </select>
                      <MoneyField
                        name={"unit_price"}
                        value={li.unit_price || 0}
                        onChange={(e) =>
                          updateLineItem(index, "unit_price", e.target.value)
                        }
                        placeholder={"$0.00"}
                        className={styles.unitPriceInput}
                      />
                      <label htmlFor="is_return" className={styles.returnCheck}>
                        <input
                          type="checkbox"
                          name="is_return"
                          id="is_return"
                          checked={li.is_return}
                          onChange={(e) =>
                            updateLineItem(index, "is_return", e.target.checked)
                          }
                        />
                        Return?
                      </label>
                    </div>
                  ))}
                </div>
                <button className={styles.submitTransaction} type="submit">
                  Submit
                </button>
              </form>
            )}
            <div className={styles.ticketTotals}>
              <p>
                Subtotal: <span>{formatCurrency(ticket.subtotal)}</span>
              </p>
              <p>
                Taxes Applied: <span>{formatCurrency(ticket.tax_total)}</span>
              </p>
              <p>
                Total: <span>{formatCurrency(ticket.total)}</span>
              </p>
            </div>
          </div>
          <div className={styles.transactionData}>
            <h3>Transactions</h3>
            <p>Total Transactions: {ticket.transactions.length}</p>
            {ticket.transactions.map((tx, index) => (
              <div key={index} className={styles.lineItemData}>
                {editing && (
                  <button
                    className={styles.deleteTransaction}
                    onClick={() => handleDeleteTransaction(tx.id)}
                  >
                    <FontAwesomeIcon icon={faDeleteLeft} />
                  </button>
                )}
                <h4>
                  {formatDate(tx.posted_date)}{" "}
                  <span> - {tx.line_items.length} Items</span>
                </h4>
                <ul>
                  {tx.line_items.map((item, liIndex) => (
                    <li key={liIndex}>
                      {editing && (
                        <button
                          className={styles.deleteLineItem}
                          onClick={() => handleDeleteLineItem(item.id)}
                        >
                          <FontAwesomeIcon icon={faXmark} />
                        </button>
                      )}
                      <div>
                        <p>Category: {SALES_CATEGORY[item.category]}</p>
                        <p>Paid With: {PAYMENT_TYPE[item.payment_type]}</p>
                      </div>
                      <div className={styles.lineItemTotal}>
                        <p>Subtotal: {formatCurrency(item.unit_price)}</p>
                        <p>Total: {formatCurrency(item.total)}</p>
                      </div>
                    </li>
                  ))}
                </ul>
                <p className={styles.transactionTotal}>
                  Transaction Total: {formatCurrency(tx.total)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;
