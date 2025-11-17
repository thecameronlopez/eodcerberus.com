import React from "react";
import { Outlet, Link, Navigate, useNavigate } from "react-router-dom";
import LOGO from "../assets/cerberus-logo-borderless.png";
import toast, { Toaster } from "react-hot-toast";
import { useAuth } from "../context/AuthContext";

const RootLayout = () => {
  const { user, loading } = useAuth();
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
      </header>
      <main>
        <Outlet />{" "}
      </main>
      <footer>
        <button onClick={logout}>logout</button>
        <p>Matt's Appliances</p>
        <p>Cerberus</p>
      </footer>
      <Toaster position="bottom-right" reverseOrder={true} />
    </>
  );
};

export default RootLayout;
