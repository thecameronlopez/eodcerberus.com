import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ProtectedLayout = () => {
  const { user, loading } = useAuth();

  // Still checking auth or init
  if (loading) {
    return <h2>Loading...</h2>;
  }

  // No user after init -> login
  if (!user) {
    return <Navigate to={"/login"} replace />;
  }

  return <Outlet />;
};

export default ProtectedLayout;
