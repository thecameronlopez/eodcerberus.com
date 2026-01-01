import styles from "./AddEOD.module.css";
import React, { useState, useMemo, useEffect } from "react";
import toast from "react-hot-toast";
import MoneyField from "../../components/MoneyField";
import {
  formatCurrency,
  formatLocationName,
  getToday,
  UserList,
} from "../../utils/Helpers";
import { useAuth } from "../../context/AuthContext";
import kaChing from "../../assets/audio/ka-ching.mp3";

const AddEOD = () => {
  const { location, user } = useAuth();
  const [date, setDate] = useState(getToday());
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(user.id);
  const [formData, setFormData] = useState({
    ticket_number: "",
    units: "",
    new: "",
    used: "",
    extended_warranty: "",
    diagnostic_fees: "",
    in_shop_repairs: "",
    ebay_sales: "",
    labor: "",
    parts: "",
    delivery: "",
    refunds: "",
    ebay_returns: "",
    acima: "",
    tower_loan: "",
    stripe: "",
    card: "",
    ebay_card: "",
    cash: "",
    checks: "",
  });

  useEffect(() => {
    const get = async () => {
      const got = await UserList();
      if (!got.success) {
        toast.error(got.message);
      }
      setUsers(got.users);
    };

    get();
  }, []);

  const subTotal = useMemo(() => {
    const fields = [
      "new",
      "used",
      "extended_warranty",
      "diagnostic_fees",
      "in_shop_repairs",
      "ebay_sales",
      "labor",
      "parts",
      "delivery",
    ];
    const subtractredFields = ["refunds"];
    let total = 0;
    fields.forEach((field) => {
      const value = parseFloat(formData[field]);
      if (!isNaN(value)) {
        total += value;
      }
    });
    subtractredFields.forEach((field) => {
      const value = parseFloat(formData[field]);
      if (!isNaN(value)) {
        total -= value;
      }
    });
    return total.toFixed(2);
  }, [formData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!confirm("Submit Values?")) return;
    if (formData.ticket_number.length < 4) {
      alert("Ticket Number must be at least 4 digits long");
      return;
    }
    const submitData = {
      ...formData,
      date: date,
      location: location,
      submitted_as: user.id === selectedUser ? null : selectedUser,
    };

    try {
      const response = await fetch("/api/create/submit_eod", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(submitData),
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success(data.message);
      new Audio(kaChing).play();
      setFormData({
        ticket_number: "",
        units: "",
        new: "",
        used: "",
        extended_warranty: "",
        diagnostic_fees: "",
        in_shop_repairs: "",
        ebay_sales: "",
        labor: "",
        parts: "",
        delivery: "",
        refunds: "",
        ebay_returns: "",
        acima: "",
        tower_loan: "",
        stripe: "",
        card: "",
        ebay_card: "",
        cash: "",
        checks: "",
      });
      setDate(getToday());
      return;
    } catch (error) {
      console.error("[ERROR]: ", error);
      toast.error(error.message);
    }
  };

  return (
    <div className={styles.formMasterContainer}>
      <div>
        <input
          type="date"
          name="date"
          id="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className={styles.datePicker}
        />
      </div>
      <form className={styles.eodForm} onSubmit={handleSubmit}>
        <div className={styles.topRow}>
          {user.is_admin && (
            <div>
              <label htmlFor="submitted_as">Submit as</label>
              <select
                name="submitted_as"
                value={selectedUser}
                onChange={(e) => setSelectedUser(Number(e.target.value))}
              >
                {users?.map(({ id, first_name, last_name }) => (
                  <option value={id} key={id}>
                    {first_name} {last_name}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div>
            <label htmlFor="ticket_number">Ticket #</label>
            <input
              type="text"
              name="ticket_number"
              id="ticket_number"
              value={formData.ticket_number}
              onChange={handleChange}
              placeholder="XXXX"
              required
            />
          </div>
          <div>
            <label htmlFor="units">Units</label>
            <input
              type="text"
              name="units"
              id="units"
              value={formData.units}
              onChange={handleChange}
              required
            />
          </div>
          <hr />
          <small style={{ fontWeight: "600", color: "var(--buttonPrimary)" }}>
            Submitting Ticket for {formatLocationName(location)}
          </small>
          <br />
        </div>
        <fieldset>
          <legend>Sale Type</legend>
          <div>
            <label htmlFor="new">New</label>
            <MoneyField
              name={"new"}
              value={formData.new}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="used">Used</label>
            <MoneyField
              name={"used"}
              value={formData.used}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="extended_warranty">Extended Warranty</label>
            <MoneyField
              name={"extended_warranty"}
              value={formData.extended_warranty}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="delivery">Delivery</label>
            <MoneyField
              name={"delivery"}
              value={formData.delivery}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="parts">Parts</label>
            <MoneyField
              name={"parts"}
              value={formData.parts}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="labor">Labor</label>
            <MoneyField
              name={"labor"}
              value={formData.labor}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="diagnostic_fees">Service Call Diagnostic</label>
            <MoneyField
              name={"diagnostic_fees"}
              value={formData.diagnostic_fees}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="in_shop_repairs">In-Shop Diagnostic</label>
            <MoneyField
              name={"in_shop_repairs"}
              value={formData.in_shop_repairs}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="ebay_sales">Ebay Sales</label>
            <MoneyField
              name={"ebay_sales"}
              value={formData.ebay_sales}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="refunds">Refunds</label>
            <MoneyField
              name={"refunds"}
              value={formData.refunds}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
        </fieldset>
        <fieldset>
          <legend>Payment Method</legend>
          <div>
            <label htmlFor="card">Card</label>
            <MoneyField
              name={"card"}
              value={formData.card}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="cash">Cash</label>
            <MoneyField
              name={"cash"}
              value={formData.cash}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="checks">Check</label>
            <MoneyField
              name={"checks"}
              value={formData.checks}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="acima">Acima</label>
            <MoneyField
              name={"acima"}
              value={formData.acima}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="tower_loan">Tower Loan</label>
            <MoneyField
              name={"tower_loan"}
              value={formData.tower_loan}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="stripe">Stripe</label>
            <MoneyField
              name={"stripe"}
              value={formData.stripe}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>

          <div>
            <label htmlFor="ebay_card">Ebay Card</label>
            <MoneyField
              name={"ebay_card"}
              value={formData.ebay_card}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
          <div>
            <label htmlFor="ebay_returns">Ebay Returns</label>
            <MoneyField
              name={"ebay_returns"}
              value={formData.ebay_returns}
              onChange={handleChange}
              placeholder={"0.00"}
            />
          </div>
        </fieldset>
        <div className={styles.buttonRow}>
          <button type="submit">Submit</button>
        </div>
      </form>
      <p className={styles.subTotalDisplay}>
        Sub-Total: {formatCurrency(subTotal)}
      </p>
    </div>
  );
};

export default AddEOD;
