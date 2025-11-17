import { useState, useContext, useEffect, createContext } from "react";

const AuthProvider = createContext();

export const AuthContext = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

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

  return (
    <AuthProvider.Provider value={{ user, loading, setLoading, setUser }}>
      {children}
    </AuthProvider.Provider>
  );
};

export const useAuth = () => useContext(AuthProvider);
