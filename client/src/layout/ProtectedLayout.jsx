import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
const ProtectedLayout = () => {
  const { user, loading } = useAuth();

  if (loading) return <h2>loading...</h2>;
  if (!user) return <Navigate to={"/login"} />;
  return <Outlet />;
};

export default ProtectedLayout;
