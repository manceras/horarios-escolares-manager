import i18next from "i18next";
import { initReactI18next } from "react-i18next";

import es from "@/locales/es.json";

/**
 * All user-facing copy lives in the locale files. Components use keys only --
 * a literal Spanish string in a component is a bug.
 */
void i18next.use(initReactI18next).init({
  resources: { es: { translation: es } },
  lng: "es",
  fallbackLng: "es",
  interpolation: { escapeValue: false },
});

export default i18next;
