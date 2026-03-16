import React from "react";
import { Outlet, useNavigate } from "react-router-dom";
import LOGO from "../assets/cerberus-logo-blue.png";
import toast, { Toaster } from "react-hot-toast";
import { useAuth } from "../context/AuthContext";

const RootLayout = () => {
  const { user, setUser, loading, init } = useAuth();
  const navigate = useNavigate();

  const logout = async () => {
    try {
      const response = await fetch("/api/auth/logout");
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
      <header className="appHeader">
        <div className="appHeaderInner">
          <div className="brandLockup">
            <img id="header-logo" src={LOGO} alt="Cerberus Logo" />
            <div className="brandCopy">
              <p className="brandEyebrow">Operations Portal</p>
              <h1>Cerberus</h1>
            </div>
          </div>
        </div>
      </header>
      <main className="appMain">
        <Outlet />
      </main>
      <footer className="appFooter">
        {user && (
          <button onClick={logout} id="logout-link">
            LOGOUT
          </button>
        )}

        <div className="footerCopy">
          <p>Matt&apos;s Appliances</p>
          <p>Cerberus operations system</p>
        </div>
      </footer>
      <Toaster position="bottom-right" reverseOrder={true} />
    </>
  );
};

export default RootLayout;
