import { createContext, useContext, useState } from "react";

const TicketContext = createContext();

export const TicketProvider = ({ children }) => {
  const [selectedTicketNumber, setSelectedTicketNumber] = useState(null);

  return (
    <TicketContext.Provider
      value={{ selectedTicketNumber, setSelectedTicketNumber }}
    >
      {children}
    </TicketContext.Provider>
  );
};

export const useTicket = () => useContext(TicketContext);
