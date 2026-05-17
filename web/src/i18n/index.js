import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import lv from "./lv.json";
import en from "./en.json";
import ru from "./ru.json";
import de from "./de.json";

const saved = localStorage.getItem("lang") || "lv";

i18n.use(initReactI18next).init({
  resources: {
    lv: { translation: lv },
    en: { translation: en },
    ru: { translation: ru },
    de: { translation: de },
  },
  lng: saved,
  fallbackLng: "lv",
  interpolation: { escapeValue: false },
});

export default i18n;
