import React, { useState, useEffect, useRef } from "react";

const MoneyField = ({ name, value, onChange, placeholder, className }) => {
  const [localValue, setLocalValue] = useState("");
  const inputRef = useRef(null);

  const parseCents = (str) => {
    if (!str) return 0;
    const num = parseFloat(str.replace(/[^0-9.]+/g, ""));
    return isNaN(num) ? 0 : Math.round(num * 100);
  };

  const formatDollars = (cents) =>
    (cents / 100).toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
    });

  const handleChange = (e) => {
    setLocalValue(e.target.value); // allow free typing
  };

  const handleBlur = () => {
    const cents = parseCents(localValue);
    setLocalValue(formatDollars(cents)); // format nicely on blur
    onChange({ target: { name, value: cents } }); // update parent state
  };

  const handleFocus = (e) => {
    // select all on focus so typing overwrites
    setTimeout(() => e.target.select(), 0);
  };

  // update display when parent value changes (e.g., form reset)
  useEffect(() => {
    setLocalValue(formatDollars(value || 0));
  }, [value]);

  return (
    <input
      type="text"
      name={name}
      value={localValue}
      ref={inputRef}
      placeholder={placeholder || "$0.00"}
      className={className}
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={handleFocus}
    />
  );
};

export default MoneyField;
