import React, { useState, useRef } from "react";

const MoneyField = ({
  name,
  value,
  onChange,
  placeholder,
  className,
  title,
}) => {
  const [localValue, setLocalValue] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef(null);

  const parseCents = (str) => {
    if (!str || !str.trim()) return 0;
    const cleaned = str.replace(/[^0-9.]+/g, "");
    const num = parseFloat(cleaned);
    return Number.isNaN(num) ? 0 : Math.round(num * 100);
  };

  const formatDollars = (cents) =>
    (cents / 100).toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
    });

  const toEditableDollars = (cents) => {
    const dollars = Number(cents || 0) / 100;
    if (!Number.isFinite(dollars)) return "";
    return dollars.toFixed(2).replace(/\.00$/, "");
  };

  const handleChange = (e) => {
    const nextValue = e.target.value;
    setLocalValue(nextValue); // allow free typing
    onChange({ target: { name, value: parseCents(nextValue) } });
  };

  const handleBlur = () => {
    setIsFocused(false);
    const cents = parseCents(localValue);
    onChange({ target: { name, value: cents } });
  };

  const handleFocus = (e) => {
    setIsFocused(true);
    setLocalValue(toEditableDollars(value));
    // select all on focus so typing overwrites
    setTimeout(() => e.target.select(), 0);
  };

  const displayValue = isFocused ? localValue : formatDollars(value || 0);

  return (
    <input
      type="text"
      name={name}
      value={displayValue}
      ref={inputRef}
      placeholder={placeholder || "$0.00"}
      className={className}
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={handleFocus}
      title={title}
    />
  );
};

export default MoneyField;
