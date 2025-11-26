export const formatLocationName = (location) => {
  const formatted = { lake_charles: "Lake Charles", jennings: "Jennings" };

  return formatted[location];
};

export const getToday = () => {
  const d = new Date();
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, "0"),
    String(d.getDate()).padStart(2, "0"),
  ].join("-");
};

export function formatDate(dateString) {
  if (!dateString) return "";

  const [year, month, day] = dateString.split("-").map(Number);

  const date = new Date(year, month - 1, day);

  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  const dayName = days[date.getDay()];
  const monthName = months[month - 1];

  // Determine ordinal suffix (st, nd, rd, th)
  const suffix = (n) => {
    if (n > 3 && n < 21) return "th"; // covers 11th–13th
    switch (n % 10) {
      case 1:
        return "st";
      case 2:
        return "nd";
      case 3:
        return "rd";
      default:
        return "th";
    }
  };

  return `${dayName}, ${monthName} ${day}${suffix(day)} ${year}`;
}

export const formatCurrency = (amount) => {
  const decimalAmount = amount / 100;
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  });
  return formatter.format(decimalAmount);
};

export const shiftDate = (dateStr, amount) => {
  const [year, month, day] = dateStr.split("-").map(Number);
  const d = new Date(year, month - 1, day);
  d.setDate(d.getDate() + amount);

  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");

  return `${yyyy}-${mm}-${dd}`;
};
