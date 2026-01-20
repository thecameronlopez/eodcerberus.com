import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const BootstrapGate = () => {
  const { bootstrapped } = useAuth();

  //still checking init
  if (bootstrapped === null) {
    return <h2>Loading...</h2>;
  }

  //force init
  if (!bootstrapped) {
    return <Navigate to={"/bootstrap"} replace />;
  }

  return <Outlet />;
};

export default BootstrapGate;
