export const formatLocationName = (location) => {
  const formatted = {
    lake_charles: "Lake Charles",
    jennings: "Jennings",
    lafayette: "Lafayette",
  };

  return formatted[location];
};

export const getTodayLocalDate = () => {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
};

export const formatDate = (date_str) => {
  if (!date_str) return "";
  if (date_str instanceof Date) {
    return formatDateObj(date_str);
  }

  const [year, month, day] = date_str.split("-");
  if (!year || !month || !day) {
    return "";
  }

  return `${month}/${day}/${year}`;
};

export const formatDateObj = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

export const formatCurrency = (amount) => {
  const decimalAmount = amount / 100;
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  });
  return formatter.format(decimalAmount);
};

export const renderOptions = (obj) => {
  return Object.entries(obj).map(([value, label], index) => (
    <option value={value} key={index}>
      {label}
    </option>
  ));
};
