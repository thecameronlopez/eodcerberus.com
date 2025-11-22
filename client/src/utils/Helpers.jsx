export const formatLocationName = (location) => {
  const formatted = { lake_charles: "Lake Charles", jennings: "Jennings" };

  return formatted[location];
};

export function formatDate(dateString) {
  const date = new Date(dateString);

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
  const monthName = months[date.getMonth()];
  const day = date.getDay();
  const year = date.getFullYear();

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
