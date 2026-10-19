"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

export type Locale = "en" | "fa";

const fa: Record<string, string> = {
  "Dashboard": "داشبورد",
  "Placement Test": "آزمون تعیین سطح",
  "Writing": "نوشتن",
  "Reading": "خواندن",
  "Vocabulary": "واژگان",
  "Upcoming": "به‌زودی",
  "Sign in": "ورود",
  "Sign out": "خروج",
  "Back to dashboard": "بازگشت به داشبورد",
  "Learning sessions": "جلسه‌های یادگیری",
  "Day streak": "روزهای پیاپی",
  "Words reviewed": "مرور واژگان",
  "Recent activity": "فعالیت‌های اخیر",
  "Recommended for you": "پیشنهاد برای شما",
  "Review your words": "مرور واژه‌ها",
  "Add a word": "افزودن واژه",
  "Add to vocabulary": "افزودن به واژگان",
  "Show all words": "نمایش همهٔ واژه‌ها",
  "Show due only": "فقط واژه‌های موعددار",
  "Reveal meaning": "نمایش معنی",
  "Again": "دوباره",
  "Hard": "سخت",
  "Good": "خوب",
  "Easy": "آسان",
  "Choose a passage": "انتخاب متن",
  "Check my answers": "بررسی پاسخ‌ها",
  "Try this passage again": "تلاش دوباره برای این متن",
  "Create account": "ساخت حساب",
  "Username": "نام کاربری",
  "Password": "رمز عبور",
  "Confirm password": "تکرار رمز عبور",
  "Continue to sign in": "ادامه برای ورود",
  "Review words that are due": "مرور واژه‌های موعددار",
  "Try a short reading": "خواندن یک متن کوتاه",
  "Write a few sentences": "نوشتن چند جمله",
  "Reading attempts": "تمرین‌های خواندن",
  "Writing submissions": "نوشته‌های ثبت‌شده",
  "Level checks": "آزمون‌های تعیین سطح",
  "Words due": "واژه‌های موعددار",
  "Mastered words": "واژه‌های مسلط‌شده",
  "Your learning trail": "مسیر یادگیری شما",
  "English": "انگلیسی",
  "Persian": "فارسی",
  "Language and layout": "زبان و چیدمان",
  "Preference could not be saved. Try again.": "ذخیرهٔ ترجیح انجام نشد. دوباره تلاش کنید.",
};

type LocaleContextValue = {
  locale: Locale;
  ready: boolean;
  saveError: string;
  changeLocale: (locale: Locale) => Promise<void>;
  t: (text: string) => string;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

async function csrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("No CSRF token");
  return data.csrfToken;
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>("en");
  const [ready, setReady] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [saveError, setSaveError] = useState("");

  useEffect(() => {
    let active = true;
    const saved = window.localStorage.getItem("wordwise-locale");
    if (saved === "fa" || saved === "en") setLocale(saved);
    async function loadProfile() {
      try {
        const response = await fetch("/api/v1/me/", { credentials: "same-origin", cache: "no-store" });
        if (!response.ok) return;
        const data = await response.json() as { profile?: { locale?: Locale } };
        if (!active) return;
        setAuthenticated(true);
        if (data.profile?.locale === "fa" || data.profile?.locale === "en") {
          setLocale(data.profile.locale);
          window.localStorage.setItem("wordwise-locale", data.profile.locale);
        }
      } catch {
        // The saved local preference remains usable while the API is unavailable.
      } finally {
        if (active) setReady(true);
      }
    }
    void loadProfile();
    return () => { active = false; };
  }, []);

  useEffect(() => {
    document.documentElement.dir = locale === "fa" ? "rtl" : "ltr";
    // The instructional content remains English; translated UI controls receive Persian language tags.
    document.documentElement.lang = "en";
  }, [locale]);

  const changeLocale = useCallback(async (nextLocale: Locale) => {
    setSaveError("");
    setLocale(nextLocale);
    window.localStorage.setItem("wordwise-locale", nextLocale);
    if (!authenticated) return;
    try {
      const token = await csrfToken();
      const response = await fetch("/api/v1/me/", {
        method: "PATCH",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify({ profile: { locale: nextLocale } }),
      });
      if (!response.ok) throw new Error("Could not save locale");
    } catch {
      setSaveError(fa["Preference could not be saved. Try again."]);
    }
  }, [authenticated]);

  const value = useMemo<LocaleContextValue>(() => ({
    locale,
    ready,
    saveError,
    changeLocale,
    t: (text: string) => locale === "fa" ? (fa[text] ?? text) : text,
  }), [locale, ready, saveError, changeLocale]);

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const value = useContext(LocaleContext);
  if (!value) throw new Error("useLocale must be used inside LocaleProvider");
  return value;
}

export function LocaleSwitcher() {
  const { locale, ready, saveError, changeLocale, t } = useLocale();
  return (
    <div className="locale-switcher" role="group" aria-label={t("Language and layout")}>
      <button type="button" onClick={() => void changeLocale("en")} aria-pressed={locale === "en"} disabled={!ready}>EN · LTR</button>
      <button type="button" onClick={() => void changeLocale("fa")} aria-pressed={locale === "fa"} disabled={!ready}>فارسی · RTL</button>
      {saveError && <span role="status">{saveError}</span>}
    </div>
  );
}
