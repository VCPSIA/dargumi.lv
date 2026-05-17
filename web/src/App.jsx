import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Section from "./pages/Section";
import Recognize from "./pages/Recognize";
import Collection from "./pages/Collection";
import Catalog from "./pages/Catalog";
import Admin from "./pages/Admin";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import "./index.css";

const qc = new QueryClient();

function RequireAuth({ children }) {
  return localStorage.getItem("token") ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Navbar />
        <div style={{ display: "flex" }}>
          <Sidebar />
          <main style={{ flex: 1, minWidth: 0, padding: "0 24px 40px" }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/section/:type" element={<RequireAuth><Section /></RequireAuth>} />
              <Route path="/recognize/:type" element={<RequireAuth><Recognize /></RequireAuth>} />
              <Route path="/collection" element={<RequireAuth><Collection /></RequireAuth>} />
              <Route path="/catalog" element={<RequireAuth><Catalog /></RequireAuth>} />
              <Route path="/admin" element={<RequireAuth><Admin /></RequireAuth>} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
