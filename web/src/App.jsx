import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { GoogleOAuthProvider } from "@react-oauth/google";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Section from "./pages/Section";
import Recognize from "./pages/Recognize";
import Collection from "./pages/Collection";
import CollectionItemPage from "./pages/CollectionItemPage";
import Catalog from "./pages/Catalog";
import CatalogItemPage from "./pages/CatalogItemPage";
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
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
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
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/section/:type" element={<RequireAuth><Section /></RequireAuth>} />
              <Route path="/recognize/:type" element={<RequireAuth><Recognize /></RequireAuth>} />
              <Route path="/collection" element={<RequireAuth><Collection /></RequireAuth>} />
              <Route path="/collection/item/:id" element={<RequireAuth><CollectionItemPage /></RequireAuth>} />
              <Route path="/catalog" element={<Catalog />} />
              <Route path="/catalog/:id" element={<CatalogItemPage />} />
              <Route path="/admin" element={<RequireAuth><Admin /></RequireAuth>} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
    </GoogleOAuthProvider>
  );
}
