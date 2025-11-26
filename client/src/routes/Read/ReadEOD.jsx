import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faPenToSquare,
  faRotateLeft,
  faTrash,
} from "@fortawesome/free-solid-svg-icons";
import toast from "react-hot-toast";
import styles from "./ReadEOD.module.css";
import React, { useEffect, useState } from "react";
import { formatCurrency, formatDate } from "../../utils/Helpers";
import MoneyField from "../../components/MoneyField";

const ReadEOD = ({ ticket }) => {
  const [ticketNumber, setTicketNumber] = useState(ticket || "");
  const [eodData, setEodData] = useState(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    units: "",
    new: "",
    used: "",
    extended_warranty: "",
    diagnostic_fees: "",
    in_shop_repairs: "",
    ebay_sales: "",
    service: "",
    parts: "",
    delivery: "",
    refunds: "",
    ebay_returns: "",
    card: "",
    cash: "",
    checks: "",
  });

  useEffect(() => {
    const fetchEOD = async () => {
      setEditing(false);
      try {
        const response = await fetch(
          `/api/read/get_eod_by_ticket/${Number(ticketNumber)}`
        );
        const data = await response.json();
        if (!data.success) {
          throw new Error(data.message);
        }
        setEodData(data.eod);
        setFormData({
          units: data.eod.units || "",
          new: data.eod.new || "",
          used: data.eod.used || "",
          extended_warranty: data.eod.extended_warranty || "",
          diagnostic_fees: data.eod.diagnostic_fees || "",
          in_shop_repairs: data.eod.in_shop_repairs || "",
          ebay_sales: data.eod.ebay_sales || "",
          service: data.eod.service || "",
          parts: data.eod.parts || "",
          delivery: data.eod.delivery || "",
          refunds: data.eod.refunds || "",
          ebay_returns: data.eod.ebay_returns || "",
          card: data.eod.card || "",
          cash: data.eod.cash || "",
          checks: data.eod.checks || "",
        });
      } catch (error) {
        console.error("[ERROR]:", error);
        setEodData(null);
      }
    };
    if (ticketNumber.length >= 4) fetchEOD();
    else if (ticketNumber.length < 4) setEodData(null);
  }, [ticketNumber]);

  useEffect(() => {
    if (ticket) {
      setTicketNumber(ticket.toString());
    } else {
      setTicketNumber("");
      setEodData(null);
    }
  }, [ticket]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleActions = async (action) => {
    if (editing && action.toLowerCase() === "update") {
      setFormData({
        units: eodData.units || "",
        new: eodData.new || "",
        used: eodData.used || "",
        extended_warranty: eodData.extended_warranty || "",
        diagnostic_fees: eodData.diagnostic_fees || "",
        in_shop_repairs: eodData.in_shop_repairs || "",
        ebay_sales: eodData.ebay_sales || "",
        service: eodData.service || "",
        parts: eodData.parts || "",
        delivery: eodData.delivery || "",
        refunds: eodData.refunds || "",
        ebay_returns: eodData.ebay_returns || "",
        card: eodData.card || "",
        cash: eodData.cash || "",
        checks: eodData.checks || "",
      });
      setEditing(false);
      return;
    }
    if (action.toLowerCase() === "delete") {
      if (!confirm(`Are you sure you want to ${action} this EOD?`)) return;
      const response = await fetch(`/api/delete/delete_eod/${eodData.id}`, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await response.json();
      if (!data.success) {
        toast.error(`Error deleting EOD: ${data.message}`);
        return;
      }
      toast.success("EOD deleted successfully.");
      setEodData(null);
      setTicketNumber("");
    } else if (action.toLowerCase() === "update") {
      setEditing(true);
    }
  };

  const handleSubmit = async () => {
    if (!confirm("Submit EOD Edits?")) return;
    try {
      const response = await fetch(`/api/update/update_eod/${eodData.id}`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(`Error updating EOD: ${data.message}`);
      }
      toast.success("EOD updated successfully.");
      setEodData(data.eod);
      setEditing(false);
    } catch (error) {
      console.error("[ERROR]:", error);
      toast.error(error.message);
    }
  };

  return (
    <section>
      <div className={styles.searchBar}>
        <div className={styles.ticketNumberSearch}>
          <label htmlFor="ticket_number">Enter Ticket Number</label>
          <input
            type="text"
            name="ticket_number"
            id="ticket_number"
            value={ticketNumber}
            onChange={(e) => setTicketNumber(e.target.value)}
          />
        </div>
      </div>
      {eodData && (
        <div className={styles.eodDetails}>
          <div className={styles.ticketHeader}>
            <div>
              <h2>{eodData.ticket_number}</h2>
              <p className={styles.eodDate}>{formatDate(eodData.date)}</p>
              <h3>
                {eodData.salesman.first_name} {eodData.salesman.last_name[0]}.
              </h3>
            </div>
            <div className={styles.eodDataButtonBlock}>
              {editing && (
                <button
                  className={styles.submitEditsButton}
                  onClick={handleSubmit}
                >
                  Submit Edits
                </button>
              )}
              <button onClick={() => handleActions("update")}>
                {editing ? (
                  <FontAwesomeIcon icon={faRotateLeft} />
                ) : (
                  <FontAwesomeIcon icon={faPenToSquare} />
                )}
              </button>
              <button onClick={() => handleActions("delete")}>
                <FontAwesomeIcon icon={faTrash} />
              </button>
            </div>
          </div>
          <div className={styles.ticketData}>
            <ul>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="units">Units:</label>
                    <small>
                      <input
                        type="text"
                        name="units"
                        value={formData.units}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Units: <small>{eodData.units}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="new">New:</label>
                    <small>
                      <MoneyField
                        name={"new"}
                        value={eodData.new}
                        placeholder={eodData.new}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    New Appliances: <small>{formatCurrency(eodData.new)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="used">Used:</label>
                    <small>
                      <MoneyField
                        name={"used"}
                        value={eodData.used}
                        placeholder={eodData.new}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Used Appliances:{" "}
                    <small>{formatCurrency(eodData.used)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="extended_warranty">
                      Extended Warranty:
                    </label>
                    <small>
                      <MoneyField
                        name={"extended_warranty"}
                        value={eodData.extended_warranty}
                        placeholder={eodData.extended_warranty}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Extended Warranty:{" "}
                    <small>{formatCurrency(eodData.extended_warranty)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="diagnostic_fees">Diagnostic Fees:</label>
                    <small>
                      <MoneyField
                        name={"diagnostic_fees"}
                        value={eodData.diagnostic_fees}
                        placeholder={eodData.diagnostic_fees}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Diagnostic Fees:{" "}
                    <small>{formatCurrency(eodData.diagnostic_fees)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="in_shop_repairs">In-Shop Repairs:</label>
                    <small>
                      <MoneyField
                        name={"in_shop_repairs"}
                        value={eodData.in_shop_repairs}
                        placeholder={eodData.in_shop_repairs}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    In-Shop Repairs:{" "}
                    <small>{formatCurrency(eodData.in_shop_repairs)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="service">Service:</label>
                    <small>
                      <MoneyField
                        name={"service"}
                        value={eodData.service}
                        placeholder={eodData.service}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Service: <small>{formatCurrency(eodData.service)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="parts">Parts:</label>
                    <small>
                      <MoneyField
                        name={"parts"}
                        value={eodData.parts}
                        placeholder={eodData.parts}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Parts: <small>{formatCurrency(eodData.parts)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="delivery">Delivery:</label>
                    <small>
                      <MoneyField
                        name={"delivery"}
                        value={eodData.delivery}
                        placeholder={eodData.delivery}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Delivery: <small>{formatCurrency(eodData.delivery)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="ebay_sales">Ebay Sales:</label>
                    <small>
                      <MoneyField
                        name={"ebay_sales"}
                        value={eodData.ebay_sales}
                        placeholder={eodData.ebay_sales}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Ebay Sales:{" "}
                    <small>{formatCurrency(eodData.ebay_sales)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="card">Card:</label>
                    <small>
                      <MoneyField
                        name={"card"}
                        value={eodData.card}
                        placeholder={eodData.card}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Card: <small>{formatCurrency(eodData.card)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="cash">Cash:</label>
                    <small>
                      <MoneyField
                        name={"cash"}
                        value={eodData.cash}
                        placeholder={eodData.cash}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Cash: <small>{formatCurrency(eodData.cash)}</small>{" "}
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="checks">Check:</label>
                    <small>
                      <MoneyField
                        name={"checks"}
                        value={eodData.checks}
                        placeholder={eodData.checks}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Checks: <small>{formatCurrency(eodData.checks)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="acima">Acima:</label>
                    <small>
                      <MoneyField
                        name={"acima"}
                        value={eodData.acima}
                        placeholder={eodData.acima}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Acima: <small>{formatCurrency(eodData.acima)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="tower_loan">Tower Loan:</label>
                    <small>
                      <MoneyField
                        name={"tower_loan"}
                        value={eodData.tower_loan}
                        placeholder={eodData.tower_loan}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Tower Loan:{" "}
                    <small>{formatCurrency(eodData.tower_loan)}</small>
                  </>
                )}
              </li>
              <li>
                {editing ? (
                  <>
                    <label htmlFor="refunds">Refunds:</label>
                    <small>
                      <MoneyField
                        name={"refunds"}
                        value={eodData.refunds}
                        placeholder={eodData.refunds}
                        onChange={handleChange}
                      />
                    </small>
                  </>
                ) : (
                  <>
                    Refunds: <small>{formatCurrency(eodData.refunds)}</small>
                  </>
                )}
              </li>
            </ul>
            <hr />
            <h4 className={styles.eodSubTotal}>
              Sub-Total: <strong>{formatCurrency(eodData.sub_total)}</strong>
            </h4>
          </div>
        </div>
      )}
    </section>
  );
};

export default ReadEOD;
