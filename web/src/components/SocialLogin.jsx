import { useEffect } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../api";

const FB_APP_ID = import.meta.env.VITE_FB_APP_ID || "";

function loadFbSdk() {
  if (window.FB || !FB_APP_ID) return;
  window.fbAsyncInit = () => {
    window.FB.init({ appId: FB_APP_ID, cookie: true, xfbml: false, version: "v19.0" });
  };
  if (!document.getElementById("fb-sdk")) {
    const s = document.createElement("script");
    s.id = "fb-sdk";
    s.src = "https://connect.facebook.net/lv_LV/sdk.js";
    s.async = true;
    s.defer = true;
    document.body.appendChild(s);
  }
}

export default function SocialLogin({ onError }) {
  const nav = useNavigate();
  const { t } = useTranslation();

  useEffect(() => { loadFbSdk(); }, []);

  async function handleGoogle(credential) {
    try {
      const { data } = await api.post("/auth/google", { token: credential });
      localStorage.setItem("token", data.access_token);
      nav("/");
    } catch (e) {
      onError?.(e.response?.data?.detail || t("auth.googleError"));
    }
  }

  async function handleFacebook() {
    if (!window.FB) { onError?.(t("auth.facebookSdkError")); return; }
    window.FB.login(async (resp) => {
      if (!resp.authResponse) return;
      try {
        const { data } = await api.post("/auth/facebook", { token: resp.authResponse.accessToken });
        localStorage.setItem("token", data.access_token);
        nav("/");
      } catch (e) {
        onError?.(e.response?.data?.detail || t("auth.facebookError"));
      }
    }, { scope: "email" });
  }

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, margin: "18px 0 14px" }}>
        <div style={{ flex: 1, height: 1, background: "#e2e8f0" }} />
        <span style={{ fontSize: 12, color: "#94a3b8", whiteSpace: "nowrap" }}>{t("auth.orLoginWith")}</span>
        <div style={{ flex: 1, height: 1, background: "#e2e8f0" }} />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {/* Google */}
        <div style={{ display: "flex", justifyContent: "center" }}>
          <GoogleLogin
            onSuccess={r => handleGoogle(r.credential)}
            onError={() => onError?.(t("auth.googleError"))}
            text="continue_with"
            shape="rectangular"
            width="360"
            locale="lv"
          />
        </div>

        {/* Facebook */}
        {FB_APP_ID && (
          <button
            type="button"
            onClick={handleFacebook}
            style={{
              width: "100%", padding: "10px 0", borderRadius: 6, border: "none",
              background: "#1877f2", color: "#fff",
              fontWeight: 600, fontSize: 14, cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
            }}
            onMouseEnter={e => e.currentTarget.style.background = "#166fe5"}
            onMouseLeave={e => e.currentTarget.style.background = "#1877f2"}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#fff">
              <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.313 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.267h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>
            </svg>
            {t("auth.continueWithFacebook")}
          </button>
        )}
      </div>
    </div>
  );
}
