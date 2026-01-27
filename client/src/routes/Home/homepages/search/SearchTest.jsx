import styles from "./SearchTest.module.css";
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
  faPlus,
  faRotateLeft,
  faSquareMinus,
  faSquarePlus,
  faTrash,
  faXmark,
} from "@fortawesome/free-solid-svg-icons";
import MoneyField from "../../../../components/MoneyField";
import { useTicket } from "../../../../context/TicketContext";

const SearchTest = ({ ticketNumber: initialTicketNumber }) => {
  const navigate = useNavigate();
  const { user, location, setLoading } = useAuth();
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
        sales_category: "",
        unit_price: "",
        is_return: false,
      },
    ],
    tenders: [
      {
        payment_type: "",
        amount: "",
      },
    ],
  });
  const [editData, setEditData] = useState({
    ticket_number: "",
    ticket_date: "",
    user_id: "",
  });

  /* ------------------ intitial setup ------------------ */
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
        console.log(data.ticket);
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

  /* ------------------ handle line items/tenders ------------------ */
  const addLineItem = () => {
    setFormData((prev) => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        {
          category: "",
          unit_price: "",
          is_return: false,
        },
      ],
    }));
  };
  const addTender = () => {
    setFormData((prev) => ({
      ...prev,
      tenders: [
        ...prev.tenders,
        {
          amount: "",
          payment_type: "",
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
  const updateTender = (index, field, value) => {
    setFormData((prev) => {
      const items = [...prev.tenders];
      items[index] = { ...items[index], [field]: value };
      return { ...prev, tenders: items };
    });
  };

  const removeLineItem = (index) => {
    if (formData.line_items.length === 1) {
      setAdding(false);
      return;
    }
    setFormData((prev) => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index),
    }));
  };
  const removeTender = (index) => {
    if (formData.tenders.length === 1) return;
    setFormData((prev) => ({
      ...prev,
      tenders: prev.tenders.filter((_, i) => i !== index),
    }));
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

  ///-------------UI----------------
  ///--------------------------------
  return (
    <div className={styles.ticketSearchPage}>
      <div className={styles.searchPanel}>
        <div className={styles.ticketNumberInput}>
          <label htmlFor="ticket_number">Ticket Number</label>
          <input
            type="text"
            name="ticket_number"
            id="ticket_number"
            value={ticketNumber}
            onChange={(e) => setTicketNumber(e.target.value)}
          />
        </div>
        {ticket && (
          <>
            <div className={styles.ticketMetaDetails}>
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
              <h4>Ticket# {ticket.ticket_number}</h4>
              <p>
                {ticket.user.first_name} {ticket.user.last_name}
              </p>
              <p>{ticket.ticket_date}</p>
              <p>Store: {ticket.location.name}</p>
            </div>
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
          </>
        )}
      </div>
      {ticket && (
        <div className={styles.ticketResults}>
          <h4>Transactions</h4>
          {adding && (
            <form className={styles.addTrannyForm}>
              <fieldset>
                <legend>
                  <button
                    type="button"
                    onClick={addTender}
                    className={styles.addTender}
                  >
                    <FontAwesomeIcon icon={faPlus} /> Add Payment Type
                  </button>
                </legend>
                {formData.tenders.map((t, index) => (
                  <div key={index} className={styles.formTender}>
                    <button
                      type="button"
                      onClick={() => removeTender(index)}
                      className={styles.removeTender}
                    >
                      <FontAwesomeIcon icon={faDeleteLeft} />
                    </button>
                    <select
                      name="payment_type"
                      value={t.payment_type}
                      onChange={(e) =>
                        updateTender(index, "payment_type", e.target.value)
                      }
                    >
                      <option value="">--select a payment type--</option>
                      {renderOptions(PAYMENT_TYPE)}
                    </select>
                    <MoneyField
                      name={"amount"}
                      value={t.amount || 0}
                      onChange={(e) =>
                        updateTender(index, "amount", e.target.value)
                      }
                      placeholder={"$0.00"}
                      className={styles.amountInput}
                    />
                  </div>
                ))}
              </fieldset>
              <fieldset>
                <legend>
                  <button
                    type="button"
                    onClick={addLineItem}
                    className={styles.addLineItem}
                  >
                    <FontAwesomeIcon icon={faPlus} /> Add Line Item
                  </button>
                </legend>
                <div>
                  <input
                    type="date"
                    name="posted_date"
                    id="posted_date"
                    value={formData.posted_date}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        posted_date: e.target.value,
                      })
                    }
                  />
                </div>
                {formData.line_items.map((li, index) => (
                  <div className={styles.formLineItem} key={index}>
                    <button
                      type="button"
                      className={styles.removeLineItem}
                      onClick={() => removeLineItem(index)}
                    >
                      <FontAwesomeIcon icon={faDeleteLeft} />
                    </button>
                    <select
                      name="sales_category"
                      value={li.category}
                      onChange={(e) =>
                        updateLineItem(index, "sales_category", e.target.value)
                      }
                    >
                      <option value="">--select a category--</option>
                      {renderOptions(SALES_CATEGORY)}
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
              </fieldset>
            </form>
          )}
          {ticket.transactions.map((tx, txIndex) => (
            <div className={styles.transaction} key={txIndex}>
              {tx.line_items.map((li, liIndex) => (
                <div className={styles.lineItem} key={liIndex}>
                  <p>{SALES_CATEGORY[li.sales_category]}</p>
                  <div className={styles.lineItemTotal}>
                    <p>
                      Unit Price: <span>{formatCurrency(li.unit_price)}</span>
                    </p>
                    {li.taxable && (
                      <p>
                        Tax: <span>{formatCurrency(li.tax_amount)}</span>
                      </p>
                    )}
                    <p>
                      Total: <span>{formatCurrency(li.total)}</span>
                    </p>
                  </div>
                </div>
              ))}
              <div className={styles.transactionTender}>
                {tx.tenders.map((t, tIndex) => (
                  <p key={tIndex}>
                    {formatCurrency(t.amount)} paid with{" "}
                    {PAYMENT_TYPE[t.payment_type]}
                  </p>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchTest;
