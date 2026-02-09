import styles from "./Ticket.module.css";
import { useAuth } from "../../../../context/AuthContext";
import React, { useEffect, useMemo, useState } from "react";
import { formatCurrency, getTodayLocalDate } from "../../../../utils/tools";
import { UserList, CategoriesList, PaymentTypeList } from "../../../../utils/api";
import toast from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquarePlus } from "@fortawesome/free-solid-svg-icons";
import MoneyField from "../../../../components/MoneyField";

const Ticket = () => {
  const { user, setLoading } = useAuth();
  const [users, setUsers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [paymentTypes, setPaymentTypes] = useState([]);

  const defaultLocationId = user?.location?.id ?? user?.location_id;
  const [formData, setFormData] = useState({
    ticket_number: "",
    ticket_date: getTodayLocalDate(),
    location_id: defaultLocationId,
    user_id: user.id,
    line_items: [
      {
        sales_category_id: "",
        unit_price: "",
      },
    ],
    tenders: [
      {
        payment_type_id: "",
        amount: "",
      },
    ],
  });

  useEffect(() => {
    const load = async () => {
      const [usersRes, categoriesRes, paymentTypesRes] = await Promise.all([
        UserList(),
        CategoriesList(),
        PaymentTypeList(),
      ]);

      if (!usersRes.success) {
        toast.error(usersRes.message);
        return;
      }
      if (!categoriesRes.success) {
        toast.error(categoriesRes.message);
        return;
      }
      if (!paymentTypesRes.success) {
        toast.error(paymentTypesRes.message);
        return;
      }

      setUsers(usersRes.users);
      setCategories(categoriesRes.categories);
      setPaymentTypes(paymentTypesRes.payment_types);
    };
    load();
  }, []);

  /* ------------------ handle line items ------------------ */
  const addLineItem = () => {
    setFormData((prev) => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        {
          sales_category_id: "",
          unit_price: "",
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

  /* ------------------ handle tenders ------------------ */
  const addTender = () => {
    setFormData((prev) => ({
      ...prev,
      tenders: [
        ...prev.tenders,
        {
          payment_type_id: "",
          amount: "",
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

  const fillTenderToBalance = (index) => {
    if (balanceOwedCents <= 0) {
      toast.error("No remaining balance to fill");
      return;
    }

    setFormData((prev) => {
      const tenders = [...prev.tenders];
      const currentAmount = Number(tenders[index]?.amount) || 0;
      tenders[index] = {
        ...tenders[index],
        amount: currentAmount + balanceOwedCents,
      };
      return { ...prev, tenders };
    });
  };

  const taxRate = Number(user?.location?.current_tax_rate || 0);
  const categoriesById = useMemo(() => {
    const map = new Map();
    categories.forEach((category) => map.set(Number(category.id), !!category.taxable));
    return map;
  }, [categories]);

  const lineItemTotals = useMemo(() => {
    return formData.line_items.map((lineItem) => {
      const unitPrice = Number(lineItem.unit_price) || 0;
      const salesCategoryId = Number(lineItem.sales_category_id);
      const isTaxable = categoriesById.get(salesCategoryId) ?? true;
      const tax = isTaxable ? Math.round(unitPrice * taxRate) : 0;
      return {
        subtotal: unitPrice,
        tax,
        total: unitPrice + tax,
      };
    });
  }, [formData.line_items, categoriesById, taxRate]);

  const subtotalCents = useMemo(
    () => lineItemTotals.reduce((sum, lineItem) => sum + lineItem.subtotal, 0),
    [lineItemTotals],
  );
  const taxTotalCents = useMemo(
    () => lineItemTotals.reduce((sum, lineItem) => sum + lineItem.tax, 0),
    [lineItemTotals],
  );
  const totalCents = useMemo(
    () => lineItemTotals.reduce((sum, lineItem) => sum + lineItem.total, 0),
    [lineItemTotals],
  );
  const totalPaidCents = useMemo(
    () => formData.tenders.reduce((sum, tender) => sum + (Number(tender.amount) || 0), 0),
    [formData.tenders],
  );
  const balanceOwedCents = totalCents - totalPaidCents;
  const isUnderpaid = balanceOwedCents > 0;
  const isOverpaid = balanceOwedCents < 0;

  const hasPaymentTypeRow = formData.tenders.some((tender) => Number(tender.payment_type_id) > 0);

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

    const validLineItems = formData.line_items
      .map((lineItem) => ({
        sales_category_id: Number(lineItem.sales_category_id),
        unit_price: Number(lineItem.unit_price),
        quantity: 1,
      }))
      .filter((lineItem) => lineItem.sales_category_id && lineItem.unit_price >= 1);

    if (!validLineItems.length) {
      toast.error("At least one valid line item is required");
      return;
    }

    if (!formData.tenders.length) {
      toast.error("At least one tender is required");
      return;
    }

    const validTenders = formData.tenders
      .map((t) => ({
        payment_type_id: Number(t.payment_type_id),
        amount: Number(t.amount),
      }))
      .filter((t) => t.payment_type_id && t.amount >= 1);

    if (!validTenders.length) {
      toast.error("At least one valid tender is required");
      return;
    }

    const payload = {
      ticket_number: Number(formData.ticket_number),
      ticket_date: formData.ticket_date,
      location_id: Number(formData.location_id),
      user_id: Number(formData.user_id),
      transaction_type: "sale",
      line_items: validLineItems,
      tenders: validTenders,
    };
    setLoading(true);
    try {
      const response = await fetch("/api/tickets", {
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
        location_id: defaultLocationId,
        ticket_date: getTodayLocalDate(),
        line_items: [
          {
            sales_category_id: "",
            unit_price: "",
          },
        ],
        tenders: [
          {
            payment_type_id: "",
            amount: "",
          },
        ],
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
              name="ticket_date"
              id="ticket_date"
              value={formData.ticket_date}
              onChange={(e) =>
                setFormData({ ...formData, ticket_date: e.target.value })
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
                <label htmlFor="sales_category">Sales Category</label>
                <select
                  value={li.sales_category_id}
                  onChange={(e) =>
                    updateLineItem(index, "sales_category_id", e.target.value)
                  }
                  required
                >
                  <option value="">--select a sales category--</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
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
        <div className={styles.tenders}>
          <h3>
            Tenders{" "}
            <button type="button" onClick={addTender}>
              <FontAwesomeIcon icon={faSquarePlus} />
            </button>
          </h3>
          {formData.tenders.map((tender, index) => (
            <div key={index} className={styles.tenderRow}>
              <div>
                <label htmlFor={`payment_type_${index}`}>Payment Type</label>
                <select
                  id={`payment_type_${index}`}
                  value={tender.payment_type_id}
                  onChange={(e) =>
                    updateTender(index, "payment_type_id", e.target.value)
                  }
                  required
                >
                  <option value="">--select payment type--</option>
                  {paymentTypes.map((paymentType) => (
                    <option key={paymentType.id} value={paymentType.id}>
                      {paymentType.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <div className={styles.amountHeader}>
                  <label htmlFor={`amount_${index}`}>Amount</label>
                  <button
                    type="button"
                    className={styles.fillBalanceBtn}
                    onClick={() => fillTenderToBalance(index)}
                    disabled={balanceOwedCents <= 0}
                  >
                    Fill Balance
                  </button>
                </div>
                <MoneyField
                  name={`amount_${index}`}
                  value={tender.amount || 0}
                  onChange={(e) => updateTender(index, "amount", e.target.value)}
                  placeholder={"$0.00"}
                  className={styles.unitPriceInput}
                />
              </div>
              <button
                className={styles.removeLiButton}
                type="button"
                onClick={() => removeTender(index)}
              >
                X
              </button>
            </div>
          ))}
        </div>
        <div className={styles.summary}>
          <h3>Summary</h3>
          <p>
            Subtotal: <span>{formatCurrency(subtotalCents)}</span>
          </p>
          <p>
            Taxes: <span>{formatCurrency(taxTotalCents)}</span>
          </p>
          <p>
            Total: <span>{formatCurrency(totalCents)}</span>
          </p>
          <p>
            Paid: <span>{formatCurrency(totalPaidCents)}</span>
          </p>
          {isOverpaid && (
            <p>
              Change Due: <span>{formatCurrency(Math.abs(balanceOwedCents))}</span>
            </p>
          )}
          {!isUnderpaid && !isOverpaid ? (
            <p className={styles.paidInFull}>Paid in Full</p>
          ) : (
            <p className={styles.balanceOwed}>
              Balance Owed: <span>{formatCurrency(balanceOwedCents)}</span>
            </p>
          )}
          {isUnderpaid && (
            <p className={styles.openTicketHint}>
              Deposit detected: ticket will remain open until paid in full.
            </p>
          )}
        </div>
        <button
          type="submit"
          disabled={formData.line_items.length === 0 || !hasPaymentTypeRow}
        >
          Submit Ticket
        </button>
      </form>
    </div>
  );
};

export default Ticket;
