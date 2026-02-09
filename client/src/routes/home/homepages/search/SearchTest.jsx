import styles from "./SearchTest.module.css";
import React, { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDeleteLeft, faPlus, faRotateLeft, faTrash } from "@fortawesome/free-solid-svg-icons";
import { useAuth } from "../../../../context/AuthContext";
import { CategoriesList, PaymentTypeList, UserList, list } from "../../../../utils/api";
import { formatCurrency, formatDate, getTodayLocalDate } from "../../../../utils/tools";
import MoneyField from "../../../../components/MoneyField";

const SearchTest = ({ ticketNumber: initialTicketNumber }) => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [paymentTypes, setPaymentTypes] = useState([]);
  const [ticketNumber, setTicketNumber] = useState(initialTicketNumber || "");
  const [ticket, setTicket] = useState(null);
  const [addingTransaction, setAddingTransaction] = useState(false);
  const [transactionForm, setTransactionForm] = useState({
    user_id: user.id,
    transaction_type: "sale",
    posted_at: getTodayLocalDate(),
    line_items: [
      {
        sales_category_id: "",
        unit_price: "",
        quantity: 1,
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
    if (!initialTicketNumber) return;
    setTicketNumber(initialTicketNumber);
  }, [initialTicketNumber]);

  useEffect(() => {
    const loadLookups = async () => {
      const [usersRes, categoriesRes, paymentTypesRes] = await Promise.all([
        UserList(),
        CategoriesList(),
        PaymentTypeList(),
      ]);
      if (usersRes.success) setUsers(usersRes.users || []);
      if (categoriesRes.success) setCategories(categoriesRes.categories || []);
      if (paymentTypesRes.success) setPaymentTypes(paymentTypesRes.payment_types || []);
    };
    loadLookups();
  }, []);

  const fetchTicketDetail = async (ticketId) => {
    const response = await fetch(`/api/tickets/${ticketId}?expand=true`, {
      credentials: "include",
    });
    const data = await response.json();
    if (!data.success) {
      throw new Error(data.message || "Failed to load ticket");
    }
    setTicket(data.ticket || null);
  };

  const handleSearch = async () => {
    const requestedNumber = Number(ticketNumber);
    if (!requestedNumber) {
      toast.error("Enter a valid ticket number");
      return;
    }

    try {
      const res = await list("tickets");
      if (!res.success) {
        throw new Error(res.message || "Failed to load tickets");
      }

      const found = (res.items || []).find(
        (item) => Number(item.ticket_number) === requestedNumber,
      );
      if (!found) {
        setTicket(null);
        toast.error("Ticket not found");
        return;
      }

      await fetchTicketDetail(found.id);
    } catch (error) {
      setTicket(null);
      toast.error(error.message);
    }
  };

  const addLineItem = () => {
    setTransactionForm((prev) => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        {
          sales_category_id: "",
          unit_price: "",
          quantity: 1,
        },
      ],
    }));
  };

  const updateLineItem = (index, field, value) => {
    setTransactionForm((prev) => {
      const lineItems = [...prev.line_items];
      lineItems[index] = { ...lineItems[index], [field]: value };
      return { ...prev, line_items: lineItems };
    });
  };

  const removeLineItem = (index) => {
    setTransactionForm((prev) => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index),
    }));
  };

  const addTender = () => {
    setTransactionForm((prev) => ({
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
    setTransactionForm((prev) => {
      const tenders = [...prev.tenders];
      tenders[index] = { ...tenders[index], [field]: value };
      return { ...prev, tenders };
    });
  };

  const removeTender = (index) => {
    setTransactionForm((prev) => ({
      ...prev,
      tenders: prev.tenders.filter((_, i) => i !== index),
    }));
  };

  const handleAddTransaction = async (e) => {
    e.preventDefault();
    if (!ticket) return;

    const validLineItems = transactionForm.line_items
      .map((lineItem) => ({
        sales_category_id: Number(lineItem.sales_category_id),
        unit_price: Number(lineItem.unit_price),
        quantity: Number(lineItem.quantity) || 1,
      }))
      .filter((lineItem) => lineItem.sales_category_id && lineItem.unit_price >= 1);

    if (!validLineItems.length) {
      toast.error("At least one valid line item is required");
      return;
    }

    const validTenders = transactionForm.tenders
      .map((tender) => ({
        payment_type_id: Number(tender.payment_type_id),
        amount: Number(tender.amount),
      }))
      .filter((tender) => tender.payment_type_id && tender.amount >= 1);

    if (!validTenders.length) {
      toast.error("At least one valid tender is required");
      return;
    }

    const payload = {
      ticket_id: Number(ticket.id),
      user_id: Number(transactionForm.user_id || user.id),
      location_id: Number(ticket.location_id || ticket.location?.id),
      transaction_type: transactionForm.transaction_type,
      posted_at: transactionForm.posted_at,
      line_items: validLineItems,
      tenders: validTenders,
    };

    try {
      const response = await fetch("/api/transactions", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message || "Failed to add transaction");
      }
      toast.success(data.message || "Transaction added");
      setAddingTransaction(false);
      setTransactionForm({
        user_id: user.id,
        transaction_type: "sale",
        posted_at: getTodayLocalDate(),
        line_items: [
          {
            sales_category_id: "",
            unit_price: "",
            quantity: 1,
          },
        ],
        tenders: [
          {
            payment_type_id: "",
            amount: "",
          },
        ],
      });
      await fetchTicketDetail(ticket.id);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (!confirm("Delete transaction?")) return;
    try {
      const response = await fetch(`/api/transactions/${transactionId}`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message || "Failed to delete transaction");
      }
      toast.success(data.message || "Transaction deleted");
      await fetchTicketDetail(ticket.id);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const transactionCount = useMemo(
    () => (ticket?.transactions ? ticket.transactions.length : 0),
    [ticket],
  );

  const lineItemsByTransaction = useMemo(() => {
    const map = {};
    (ticket?.line_items || []).forEach((item) => {
      const txId = Number(item.transaction_id);
      if (!map[txId]) map[txId] = [];
      map[txId].push(item);
    });
    return map;
  }, [ticket]);

  const tendersByTransaction = useMemo(() => {
    const map = {};
    (ticket?.tenders || []).forEach((tender) => {
      const txId = Number(tender.transaction_id);
      if (!map[txId]) map[txId] = [];
      map[txId].push(tender);
    });
    return map;
  }, [ticket]);

  const taxRate = Number(user?.location?.current_tax_rate || 0);
  const categoriesById = useMemo(() => {
    const map = new Map();
    categories.forEach((category) => map.set(Number(category.id), !!category.taxable));
    return map;
  }, [categories]);

  const lineItemTotals = useMemo(() => {
    return transactionForm.line_items.map((lineItem) => {
      const unitPrice = Number(lineItem.unit_price) || 0;
      const quantity = Number(lineItem.quantity) || 1;
      const salesCategoryId = Number(lineItem.sales_category_id);
      const isTaxable = categoriesById.get(salesCategoryId) ?? true;
      const subtotal = unitPrice * quantity;
      const tax = isTaxable ? Math.round(subtotal * taxRate) : 0;
      return {
        subtotal,
        tax,
        total: subtotal + tax,
      };
    });
  }, [transactionForm.line_items, categoriesById, taxRate]);

  const summarySubtotalCents = useMemo(
    () => lineItemTotals.reduce((sum, lineItem) => sum + lineItem.subtotal, 0),
    [lineItemTotals],
  );
  const summaryTaxCents = useMemo(
    () => lineItemTotals.reduce((sum, lineItem) => sum + lineItem.tax, 0),
    [lineItemTotals],
  );
  const summaryTotalCents = useMemo(
    () => lineItemTotals.reduce((sum, lineItem) => sum + lineItem.total, 0),
    [lineItemTotals],
  );
  const summaryPaidCents = useMemo(
    () => transactionForm.tenders.reduce((sum, tender) => sum + (Number(tender.amount) || 0), 0),
    [transactionForm.tenders],
  );
  const summaryBalanceCents = summaryTotalCents - summaryPaidCents;
  const isUnderpaid = summaryBalanceCents > 0;
  const isOverpaid = summaryBalanceCents < 0;

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
          <button type="button" className={styles.searchBtn} onClick={handleSearch}>
            Search
          </button>
        </div>

        {ticket && (
          <>
            <div className={styles.ticketMetaDetails}>
              <div className={styles.ticketControls}>
                <button
                  className={styles.addTransaction}
                  onClick={() => setAddingTransaction((prev) => !prev)}
                  type="button"
                >
                  <FontAwesomeIcon icon={addingTransaction ? faRotateLeft : faPlus} />
                </button>
              </div>
              <h4>Ticket # {ticket.ticket_number}</h4>
              <p>
                {ticket.user?.first_name} {ticket.user?.last_name}
              </p>
              <p>{formatDate(ticket.ticket_date)}</p>
              <p>Store: {ticket.location?.name}</p>
            </div>
            <div className={styles.ticketTotals}>
              <p>
                Subtotal: <span>{formatCurrency(ticket.subtotal || 0)}</span>
              </p>
              <p>
                Taxes: <span>{formatCurrency(ticket.tax_total || 0)}</span>
              </p>
              <p>
                Total: <span>{formatCurrency(ticket.total || 0)}</span>
              </p>
              <p>
                Paid: <span>{formatCurrency(ticket.total_paid || 0)}</span>
              </p>
              <p>
                Balance: <span>{formatCurrency(ticket.balance_owed || 0)}</span>
              </p>
              <p>Status: {ticket.is_open ? "Open" : "Closed"}</p>
            </div>

            {addingTransaction && (
              <form className={styles.transactionForm} onSubmit={handleAddTransaction}>
                <div className={styles.metaGrid}>
                  {user.is_admin && (
                    <div>
                      <label htmlFor="tx_user_id">User</label>
                      <select
                        id="tx_user_id"
                        value={transactionForm.user_id}
                        onChange={(e) =>
                          setTransactionForm((prev) => ({
                            ...prev,
                            user_id: e.target.value,
                          }))
                        }
                      >
                        {users.map((u) => (
                          <option key={u.id} value={u.id}>
                            {u.first_name} {u.last_name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                  <div>
                    <label htmlFor="transaction_type">Type</label>
                    <select
                      id="transaction_type"
                      value={transactionForm.transaction_type}
                      onChange={(e) =>
                        setTransactionForm((prev) => ({
                          ...prev,
                          transaction_type: e.target.value,
                        }))
                      }
                    >
                      <option value="sale">Sale</option>
                      <option value="return">Return</option>
                      <option value="adjustment">Adjustment</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="posted_at">Posted Date</label>
                    <input
                      id="posted_at"
                      type="date"
                      value={transactionForm.posted_at}
                      onChange={(e) =>
                        setTransactionForm((prev) => ({
                          ...prev,
                          posted_at: e.target.value,
                        }))
                      }
                    />
                  </div>
                </div>
                <div className={styles.sectionsGrid}>
                  <div className={styles.formSection}>
                    <div className={styles.sectionHeader}>
                      <h5>Line Items</h5>
                      <button type="button" onClick={addLineItem}>
                        <FontAwesomeIcon icon={faPlus} /> Add
                      </button>
                    </div>
                    {transactionForm.line_items.map((lineItem, index) => (
                      <div className={styles.formLineItem} key={index}>
                        <button
                          type="button"
                          className={styles.removeRow}
                          onClick={() => removeLineItem(index)}
                          disabled={transactionForm.line_items.length <= 1}
                        >
                          <FontAwesomeIcon icon={faDeleteLeft} />
                        </button>
                        <select
                          value={lineItem.sales_category_id}
                          onChange={(e) =>
                            updateLineItem(index, "sales_category_id", e.target.value)
                          }
                        >
                          <option value="">--category--</option>
                          {categories.map((category) => (
                            <option key={category.id} value={category.id}>
                              {category.name}
                            </option>
                          ))}
                        </select>
                        <MoneyField
                          name={`line_item_amount_${index}`}
                          value={lineItem.unit_price || 0}
                          onChange={(e) => updateLineItem(index, "unit_price", e.target.value)}
                          className={styles.amountInput}
                        />
                        <input
                          type="number"
                          min="1"
                          max="999"
                          value={lineItem.quantity}
                          onChange={(e) => updateLineItem(index, "quantity", e.target.value)}
                          className={styles.qtyInput}
                        />
                      </div>
                    ))}
                  </div>
                  <div className={styles.formSection}>
                    <div className={styles.sectionHeader}>
                      <h5>Tenders</h5>
                      <button type="button" onClick={addTender}>
                        <FontAwesomeIcon icon={faPlus} /> Add
                      </button>
                    </div>
                    {transactionForm.tenders.map((tender, index) => (
                      <div className={styles.formTender} key={index}>
                        <button
                          type="button"
                          className={styles.removeRow}
                          onClick={() => removeTender(index)}
                          disabled={transactionForm.tenders.length <= 1}
                        >
                          <FontAwesomeIcon icon={faDeleteLeft} />
                        </button>
                        <select
                          value={tender.payment_type_id}
                          onChange={(e) =>
                            updateTender(index, "payment_type_id", e.target.value)
                          }
                        >
                          <option value="">--payment type--</option>
                          {paymentTypes.map((paymentType) => (
                            <option key={paymentType.id} value={paymentType.id}>
                              {paymentType.name}
                            </option>
                          ))}
                        </select>
                        <MoneyField
                          name={`tender_amount_${index}`}
                          value={tender.amount || 0}
                          onChange={(e) => updateTender(index, "amount", e.target.value)}
                          className={styles.amountInput}
                        />
                      </div>
                    ))}
                  </div>
                </div>
                <div className={styles.formSummary}>
                  <h5>Summary</h5>
                  <p>
                    Subtotal: <span>{formatCurrency(summarySubtotalCents)}</span>
                  </p>
                  <p>
                    Taxes: <span>{formatCurrency(summaryTaxCents)}</span>
                  </p>
                  <p>
                    Total: <span>{formatCurrency(summaryTotalCents)}</span>
                  </p>
                  <p>
                    Paid: <span>{formatCurrency(summaryPaidCents)}</span>
                  </p>
                  {isOverpaid ? (
                    <p className={styles.summaryChange}>
                      Change Due: <span>{formatCurrency(Math.abs(summaryBalanceCents))}</span>
                    </p>
                  ) : (
                    <p className={styles.summaryBalance}>
                      Balance: <span>{formatCurrency(summaryBalanceCents)}</span>
                    </p>
                  )}
                  {isUnderpaid && (
                    <p className={styles.openTicketHint}>
                      Partial payment detected. Ticket will remain open.
                    </p>
                  )}
                </div>
                <button className={styles.submitTransaction} type="submit">
                  Add Transaction
                </button>
              </form>
            )}
          </>
        )}
      </div>

      <div className={styles.ticketResults}>
        {ticket && (
          <>
            <h4>Transactions ({transactionCount})</h4>

            {(ticket.transactions || []).map((transaction) => (
              <div className={styles.transaction} key={transaction.id}>
                {(() => {
                  const txId = Number(transaction.id);
                  const txLineItems = lineItemsByTransaction[txId] || [];
                  const txTenders = tendersByTransaction[txId] || [];
                  return (
                    <>
                      <div className={styles.transactionHeader}>
                        <div>
                          <p>Transaction #{transaction.id}</p>
                          <p>{formatDate(transaction.posted_at)}</p>
                          <p>Type: {transaction.transaction_type}</p>
                          <p>Line Items: {txLineItems.length || (transaction.line_item_ids || []).length}</p>
                        </div>
                        <button
                          className={styles.deleteTransaction}
                          type="button"
                          onClick={() => handleDeleteTransaction(transaction.id)}
                        >
                          <FontAwesomeIcon icon={faTrash} />
                        </button>
                      </div>
                      <div className={styles.transactionTotals}>
                        <p>
                          Subtotal: <span>{formatCurrency(transaction.subtotal || 0)}</span>
                        </p>
                        <p>
                          Taxes: <span>{formatCurrency(transaction.tax_total || 0)}</span>
                        </p>
                        <p>
                          Total: <span>{formatCurrency(transaction.total || 0)}</span>
                        </p>
                        <p>
                          Paid: <span>{formatCurrency(transaction.total_paid || 0)}</span>
                        </p>
                      </div>

                      {!!txLineItems.length && (
                        <div className={`${styles.transactionDetailBlock} ${styles.lineItemsBlock}`}>
                          <h5>Line Items</h5>
                          {txLineItems.map((item) => (
                            <div className={styles.detailRow} key={item.id}>
                              <p>{item.sales_category_name || `Category #${item.sales_category_id}`}</p>
                              <p>Qty: {item.quantity}</p>
                              <p>{formatCurrency(item.total || 0)}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {!!txTenders.length && (
                        <div className={`${styles.transactionDetailBlock} ${styles.tendersBlock}`}>
                          <h5>Tenders</h5>
                          {txTenders.map((tender) => (
                            <div className={styles.detailRow} key={tender.id}>
                              <p>{tender.payment_type || `Payment #${tender.payment_type_id || "?"}`}</p>
                              <p>{formatCurrency(tender.amount || 0)}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default SearchTest;
