import React from "react";
import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from "react-router-dom";
import Home from "./routes/home/Home";
import Register from "./routes/auth/register/Register";
import Login from "./routes/auth/login/Login";
import RootLayout from "./layout/RootLayout";
import ProtectedLayout from "./layout/ProtectedRoutes";
import Settings from "./routes/settings/Settings";
import Reports from "./routes/reports/Reports";
import BootstrapGate from "./layout/BootstrapGate";
import Bootstrap from "./routes/initialize/Bootstrap";
import { TicketProvider } from "./context/TicketContext";
import { TabRouterProvider } from "./context/TabRouterContext";

const App = () => {
  const router = createBrowserRouter(
    createRoutesFromElements(
      <Route path="/" element={<RootLayout />}>
        <Route path="bootstrap" element={<Bootstrap />} />
        <Route element={<BootstrapGate />}>
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route element={<ProtectedLayout />}>
            <Route index element={<Home />} />
            <Route path="settings" element={<Settings />} />
            <Route path="reports" element={<Reports />} />
          </Route>
        </Route>
      </Route>,
    ),
  );
  return (
    <TicketProvider>
      <TabRouterProvider>
        <RouterProvider router={router} />
      </TabRouterProvider>
    </TicketProvider>
  );
};

export default App;
