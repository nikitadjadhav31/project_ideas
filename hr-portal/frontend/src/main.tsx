import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import { App } from "./App";
import { Dashboard } from "./pages/Dashboard";
import { Approvals } from "./pages/Approvals";
import { AuditLog } from "./pages/AuditLog";
import { Intake } from "./pages/Intake";
import "./styles.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "intake", element: <Intake /> },
      { path: "approvals", element: <Approvals /> },
      { path: "audit", element: <AuditLog /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
