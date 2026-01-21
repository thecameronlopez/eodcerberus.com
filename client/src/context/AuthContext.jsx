import { useState, useContext, useEffect, createContext } from "react";

const AuthProvider = createContext();

export const AuthContext = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bootstrapped, setBootstrapped] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch("/api/auth/hydrate_user", {
          credentials: "include",
        });

        if (!response.ok) throw new Error("Not authenticated");

        const data = await response.json();
        setUser(data.user);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  useEffect(() => {
    const checkBootstrap = async () => {
      try {
        const res = await fetch("/api/bootstrap/status");
        const data = await res.json();
        setBootstrapped(data.bootstrapped);
      } catch {
        setBootstrapped(false);
      }
    };
    checkBootstrap();
  }, []);

  return (
    <AuthProvider.Provider
      value={{
        user,
        setUser,
        loading,
        setLoading,
        bootstrapped,
        setBootstrapped,
      }}
    >
      {children}
    </AuthProvider.Provider>
  );
};

export const useAuth = () => useContext(AuthProvider);
