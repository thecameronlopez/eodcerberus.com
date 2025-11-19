import React, { useState } from "react";
import { Outlet, Link, Navigate, useNavigate } from "react-router-dom";
import LOGO from "../assets/cerberus-logo-blue.png";
import toast, { Toaster } from "react-hot-toast";
import { useAuth } from "../context/AuthContext";

const RootLayout = () => {
  const { user, loading, setLocation, location } = useAuth();
  const navigate = useNavigate();

  const logout = async () => {
    try {
      const response = await fetch("/api/auth/logout");
      const data = await response.json();
      if (!data.success) {
        throw new Error("There was an error when logging out");
      }
      toast.success(data.message);
      navigate("/login");
    } catch (error) {
      console.error("[ERROR]: ", error);
      toast.error(error.message);
    }
  };
  return (
    <>
      <header>
        <Link to="/">
          <img id="header-logo" src={LOGO} alt="Cerberus Logo" />
        </Link>
        <div className="location-switch">
          <span className={location !== "lake_charles" ? "inactive" : ""}>
            Lake Charles
          </span>

          <label className="toggle">
            <input
              type="checkbox"
              checked={location === "jennings"}
              onChange={() => {
                if (!confirm("Update location?")) return;
                setLocation(
                  location === "jennings" ? "lake_charles" : "jennings"
                );
              }}
            />
            <span className="slider"></span>
          </label>

          <span className={location !== "jennings" ? "inactive" : ""}>
            Jennings
          </span>
        </div>
      </header>
      <main>
        <Outlet />{" "}
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
