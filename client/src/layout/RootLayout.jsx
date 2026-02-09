import React from "react";
import { Outlet, useNavigate } from "react-router-dom";
import LOGO from "../assets/cerberus-logo-blue.png";
import toast, { Toaster } from "react-hot-toast";
import { useAuth } from "../context/AuthContext";

const RootLayout = () => {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();

  const logout = async () => {
    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      const data = await response.json();
      if (!data.success) {
        throw new Error("There was an error when logging out");
      }
      toast.success(data.message);
      setUser(null);
      navigate("/login");
    } catch (error) {
      console.error("[ERROR]: ", error);
      toast.error(error.message);
    }
  };

  return (
    <>
      <header>
        <img id="header-logo" src={LOGO} alt="Cerberus Logo" />
      </header>
      <main>
        <Outlet />
      </main>
      <footer>
        {user && (
          <button onClick={logout} id="logout-link">
            LOGOUT
          </button>
        )}

        <p>Matt's Appliances</p>
        <p>Cerberus</p>
      </footer>
      <Toaster position="bottom-right" reverseOrder={true} />
    </>
  );
};

export default RootLayout;
