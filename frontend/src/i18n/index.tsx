import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { en } from "./en";
import { zhCN } from "./zh-CN";
import type { Locale, Translate, TranslationValues } from "./types";

const STORAGE_KEY = "nightingale-language";
const locales: Locale[] = ["en", "zh-CN"];

function isLocale(value: string | null): value is Locale {
  return value !== null && locales.includes(value as Locale);
}

function initialLocale(): Locale {
  const queryLocale = new URLSearchParams(window.location.search).get("lang");
  if (isLocale(queryLocale)) return queryLocale;
  const storedLocale = window.localStorage.getItem(STORAGE_KEY);
  return isLocale(storedLocale) ? storedLocale : "en";
}

function interpolate(value: string, values?: TranslationValues) {
  if (!values) return value;
  return Object.entries(values).reduce(
    (result, [key, replacement]) =>
      result.replaceAll(`{{${key}}}`, String(replacement)),
    value,
  );
}

type I18nContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: Translate;
};

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(initialLocale);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, locale);
    document.documentElement.lang = locale === "zh-CN" ? "zh-CN" : "en-SG";
  }, [locale]);

  const setLocale = (nextLocale: Locale) => {
    setLocaleState(nextLocale);
    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.set("lang", nextLocale);
    window.history.replaceState(
      {},
      "",
      `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`,
    );
  };

  const value = useMemo<I18nContextValue>(() => {
    const active = locale === "zh-CN" ? zhCN : en;
    const t: Translate = (key, values) => {
      const translated = active[key];
      if (translated === undefined) {
        if (import.meta.env.DEV) {
          console.warn(`[i18n] Missing translation key: ${key}`);
        }
        return interpolate(en[key] ?? key, values);
      }
      return interpolate(translated, values);
    };
    return { locale, setLocale, t };
  }, [locale]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const value = useContext(I18nContext);
  if (!value) throw new Error("useI18n must be used inside I18nProvider");
  return value;
}

export function LanguageToggle() {
  const { locale, setLocale, t } = useI18n();
  return (
    <div
      className="inline-flex rounded-lg border border-slate-200 bg-white p-1 shadow-sm"
      role="group"
      aria-label={t("language.label")}
      data-testid="language-toggle"
    >
      {locales.map((option) => (
        <button
          key={option}
          type="button"
          className={`rounded-md px-2.5 py-1.5 text-xs font-semibold transition focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-200 ${locale === option ? "bg-blue-700 text-white" : "text-slate-600 hover:bg-slate-100"}`}
          aria-pressed={locale === option}
          onClick={() => setLocale(option)}
        >
          {option === "en" ? t("language.english") : t("language.chinese")}
        </button>
      ))}
    </div>
  );
}

export { en, zhCN };
