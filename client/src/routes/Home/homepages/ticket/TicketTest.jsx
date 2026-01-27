import styles from "./TicketTest.module.css";
import { useAuth } from "../../../../context/AuthContext";
import React, { useMemo, useState } from "react";
import { SALES_CATEGORY, PAYMENT_TYPE } from "../../../../utils/enums";
import {
  renderOptions,
  getTodayLocalDate,
  formatDate,
  formatCurrency,
} from "../../../../utils/tools";
import MoneyField from "../../../../components/MoneyField";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faDeleteLeft,
  faEraser,
  faPlus,
  faTrash,
} from "@fortawesome/free-solid-svg-icons";
import toast from "react-hot-toast";

const TicketTest = () => {
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    ticket_number: "",
    date: getTodayLocalDate(),
    line_items: [
      {
        category: "",
        unit_price_cents: 0,
        is_return: false,
      },
    ],
    tenders: [
      {
        payment_type: "",
        amount: 0,
      },
    ],
    split_tender: false,
  });

  /* ------------------ Line Items ------------------ */
  const addLineItem = () => {
    setFormData((prev) => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        {
          category: "",
          unit_price_cents: 0,
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

  /* ------------------ Tenders ------------------ */
  const addTender = () => {
    setFormData((prev) => ({
      ...prev,
      tenders: [
        ...prev.tenders,
        {
          payment_type: "",
          amount: 0,
        },
      ],
    }));
  };

  const updateTender = (index, field, value) => {
    setFormData((prev) => {
      const tenders = [...prev.tenders];
      tenders[index] = { ...tenders[index], [field]: value };
      return { ...prev, tenders };
    });
  };

  const removeTender = (index) => {
    setFormData((prev) => ({
      ...prev,
      tenders: prev.tenders.filter((_, i) => i !== index),
    }));
  };

  /* ------------------ Math (cents only) ------------------ */
  const subtotalCents = useMemo(() => {
    return formData.line_items.reduce((sum, li) => {
      const price = Number(li.unit_price) || 0;
      return li.is_return ? sum - price : sum + price;
    }, 0);
  }, [formData.line_items]);

  const totalPaidCents = useMemo(() => {
    return formData.tenders.reduce(
      (sum, t) => sum + (Number(t.amount) || 0),
      0,
    );
  }, [formData.tenders]);

  const balanceOwedCents = subtotalCents - totalPaidCents;

  const isUnderpaid = balanceOwedCents > 0;
  const isOverpaid = balanceOwedCents < 0;

  /* ------------------ Submit Ticket ------------------ */
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!confirm("Submit Ticket?")) return;
    if (isUnderpaid) {
      if (!confirm("Submit ticket with remaining balance?")) return;
    }
    const URL = "/api/create/ticket";
    const options = {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };
    options.body = JSON.stringify({
      ticket_number: formData.ticket_number,
      date: formData.date,
      location_id: user.location_id,
      user_id: user.id,
      line_items: [...formData.line_items],
      tenders: [...formData.tenders],
    });

    try {
      const response = await fetch(URL, options);
      const data = await response.json();
      if (!data.success) {
        throw new Error();
      }
      toast.success(data.message);
      setFormData({
        ticket_number: "",
        date: getTodayLocalDate(),
        line_items: [
          {
            category: "",
            unit_price_cents: 0,
            is_return: false,
          },
        ],
        tenders: [
          {
            payment_type: "",
            amount_cents: 0,
          },
        ],
        split_tender: false,
      });
    } catch (error) {
      console.error("[FORM SUBMISSION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  /* ------------------ UI ------------------ */
  return (
    <div className={styles.ticketBox}>
      <form className={styles.ticketForm} onSubmit={handleSubmit}>
        <fieldset className={styles.ticketMeta}>
          <legend>Ticket Info</legend>
          <input
            type="date"
            name="ticket_date"
            id="ticket_date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
          />
          <div className={styles.ticketNumberInput}>
            <label htmlFor="ticket_number">Ticket Number</label>
            <input
              type="text"
              name="ticket_number"
              id="ticket_number"
              value={formData.ticket_number}
              onChange={(e) =>
                setFormData({ ...formData, ticket_number: e.target.value })
              }
            />
          </div>
          <p>Location: {user.location.name}</p>
          <p>Date: {formatDate(formData.date)}</p>
        </fieldset>

        {/* ---------------- Line Items ---------------- */}
        <fieldset className={styles.lineItems}>
          <legend>
            <button
              className={styles.addLi}
              type="button"
              onClick={addLineItem}
            >
              <FontAwesomeIcon icon={faPlus} /> Add Line Item
            </button>
          </legend>
          {formData.line_items.map((li, index) => (
            <div key={index} className={styles.lineItem}>
              <button
                type="button"
                onClick={
                  formData.line_items.length > 1
                    ? () => removeLineItem(index)
                    : () => toast.error("At least one line item required")
                }
                className={styles.removeLi}
              >
                <FontAwesomeIcon icon={faDeleteLeft} />
              </button>

              <select
                value={li.category}
                onChange={(e) =>
                  updateLineItem(index, "category", e.target.value)
                }
                className={styles.catSelect}
              >
                <option value="">--category--</option>
                {renderOptions(SALES_CATEGORY)}
              </select>

              <MoneyField
                value={li.unit_price}
                onChange={(e) =>
                  updateLineItem(index, "unit_price", e.target.value)
                }
                className={styles.unitPrice}
              />

              <label className={styles.returnBox}>
                Return
                <input
                  type="checkbox"
                  checked={li.is_return}
                  onChange={(e) =>
                    updateLineItem(index, "is_return", e.target.checked)
                  }
                />
              </label>
            </div>
          ))}
        </fieldset>

        {/* ---------------- Payment ---------------- */}
        <fieldset className={styles.payments}>
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
            <div key={index} className={styles.tender}>
              <button
                type="button"
                onClick={
                  formData.tenders.length > 1
                    ? () => removeTender(index)
                    : () => toast.error("At least on payment type is required")
                }
                className={styles.removeTender}
              >
                <FontAwesomeIcon icon={faDeleteLeft} />
              </button>

              <select
                value={t.payment_type}
                onChange={(e) =>
                  updateTender(index, "payment_type", e.target.value)
                }
                className={styles.typeSelect}
              >
                <option value="">--payment type--</option>
                {renderOptions(PAYMENT_TYPE)}
              </select>

              <MoneyField
                value={t.amount}
                onChange={(e) => updateTender(index, "amount", e.target.value)}
                className={styles.paymentAmount}
              />
            </div>
          ))}
        </fieldset>

        {/* ---------------- Totals ---------------- */}
        <fieldset className={styles.summary}>
          <legend>Summary</legend>
          <p>Subtotal: ${(subtotalCents / 100).toFixed(2)}</p>
          <p>Total Paid: ${(totalPaidCents / 100).toFixed(2)}</p>

          {isOverpaid && (
            <p>Change Due: ${Math.abs(balanceOwedCents / 100).toFixed(2)}</p>
          )}

          {!isUnderpaid && !isOverpaid ? (
            <p className={styles.paidInFull}>Paid in Full</p>
          ) : (
            <p className={styles.balanceOwed}>
              Balance Owed: {formatCurrency(balanceOwedCents)}
            </p>
          )}
          <button className={styles.submitTicket} type="submit">
            Submit
          </button>
        </fieldset>
      </form>
    </div>
  );
};

export default TicketTest;
