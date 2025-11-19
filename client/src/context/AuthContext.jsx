import { useState, useContext, useEffect, createContext } from "react";

const AuthProvider = createContext();

export const AuthContext = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [location, setLocation] = useState(
    localStorage.getItem("location") || "lake_charles"
  );

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch("/api/auth/hydrate_user", {
          method: "GET",
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          // console.log(data.user);
          setUser(data.user);
        } else {
          setUser(null);
        }
      } catch (error) {
        console.error("Error when fetching user: ", error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  useEffect(() => {
    localStorage.setItem("location", location);
  }, [location]);

  return (
    <AuthProvider.Provider
      value={{ user, loading, setLoading, setUser, location, setLocation }}
    >
      {children}
    </AuthProvider.Provider>
  );
};

export const useAuth = () => useContext(AuthProvider);
