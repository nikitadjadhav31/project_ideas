import { Outlet } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";

export function App() {
  return (
    <div className="app">
      <Sidebar />
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
