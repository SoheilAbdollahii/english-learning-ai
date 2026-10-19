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
  "Open": "باز کردن",
  "sessions": "جلسه",
  "Completed activities saved to your account": "فعالیت‌های تکمیل‌شده و ذخیره‌شده در حساب شما",
  "Consecutive days with recorded learning": "روزهای پیاپی با فعالیت یادگیری ثبت‌شده",
  "reviews": "مرور",
  "Saved vocabulary review outcomes": "نتایج مرور واژگان ثبت‌شده",
  "Sign in to see your personal progress.": "برای مشاهدهٔ پیشرفت شخصی خود وارد شوید.",
  "Latest saved sessions": "آخرین فعالیت‌های ثبت‌شده",
  "Your activity will appear after your first saved learning session.": "پس از نخستین جلسهٔ یادگیری، فعالیت شما اینجا نمایش داده می‌شود.",
  "Based on your saved activity": "بر اساس فعالیت‌های ذخیره‌شدهٔ شما",
  "We couldn't sign you out. Please check your connection and try again.": "خروج انجام نشد. اتصال خود را بررسی و دوباره تلاش کنید.",
  "WORDWISE · VOCABULARY": "وردوایز · واژگان",
  "Word": "واژه",
  "WORDWISE · READING ROOM": "وردوایز · فضای خواندن",
  "Try again": "تلاش دوباره",
  "WORDWISE · WRITING STUDIO": "وردوایز · استودیوی نوشتن",
  "Welcome": "خوش آمدید",
  "Your account is ready. Sign in to start saving your English practice.": "حساب شما آماده است. برای ذخیرهٔ تمرین‌های انگلیسی وارد شوید.",
  "Email verification and account recovery are not available yet.": "تأیید ایمیل و بازیابی حساب هنوز در دسترس نیست.",
  "Writing submission": "ارسال نوشته",
  "Reading attempt": "تمرین خواندن",
  "Vocabulary review": "مرور واژگان",
  "Placement attempt": "تمرین تعیین سطح",
  "Keep reading regularly": "خواندن را پیوسته ادامه دهید",
  "Keep writing regularly": "نوشتن را پیوسته ادامه دهید",
  "Start with one small session": "با یک جلسهٔ کوتاه شروع کنید",
  "Review vocabulary": "مرور واژگان",
  "Open Reading": "رفتن به خواندن",
  "Open Writing": "رفتن به نوشتن",
  "Choose a practice": "انتخاب یک تمرین",
  "Read a passage": "خواندن یک متن",
  "Your account is ready. Sign in to start saving your English practice.": "حساب شما آماده است. برای ذخیرهٔ تمرین‌های انگلیسی وارد شوید.",
  "Find your words, find your voice.": "واژه‌های خود را پیدا کنید، صدای خود را بیابید.",
  "A clearer path to your next level.": "مسیر روشن‌تری به سوی سطح بعدی.",
  "Start with a short assessment. Your answers are scored on the server and saved to your learner account.": "با یک ارزیابی کوتاه شروع کنید. پاسخ‌ها در سرور نمره‌دهی و در حساب شما ذخیره می‌شوند.",
  "No published placement assessment is available yet.": "هنوز آزمون تعیین سطحی منتشر نشده است.",
  "YOUR PLACEMENT CHECK": "آزمون تعیین سطح شما",
  "FIND YOUR STARTING POINT": "نقطهٔ شروع خود را پیدا کنید",
  "YOUR WRITING STUDIO": "استودیوی نوشتن شما",
  "Writing result": "نتیجهٔ نوشتن",
  "Your saved writing": "نوشته‌های ذخیره‌شدهٔ شما",
  "No saved submissions yet.": "هنوز نوشته‌ای ثبت نشده است.",
  "No vocabulary cards are due right now.": "در حال حاضر واژه‌ای برای مرور موعددار نیست.",
  "No reading passages are available yet.": "هنوز متنی برای خواندن موجود نیست."
  "WORKSPACE": "فضای کار",
  "Overview": "نمای کلی",
  "Level check": "تعیین سطح",
  "Small steps add up.": "قدم‌های کوچک نتیجه می‌دهند.",
  "A little practice today makes tomorrow easier.": "کمی تمرین امروز، فردا را آسان‌تر می‌کند.",
  "YOUR PERSONAL LEARNING SPACE": "فضای شخصی یادگیری شما",
  "MAKE ROOM FOR PROGRESS": "برای پیشرفت جا باز کنید",
  "Your English journey,": "مسیر یادگیری انگلیسی شما،",
  "one day at a time.": "روزبه‌روز.",
  "A calmer place to practice, build confidence, and make English part of your routine.": "جایی آرام برای تمرین، افزایش اعتمادبه‌نفس و تبدیل انگلیسی به بخشی از برنامهٔ روزانه.",
  "YOUR TOOLKIT": "ابزارهای شما",
  "Choose your next step": "قدم بعدی را انتخاب کنید",
  "3 learning areas": "۳ حوزهٔ یادگیری",
  "Build clearer sentences and learn from structured feedback.": "جمله‌های روشن‌تری بسازید و از بازخورد ساختاریافته یاد بگیرید.",
  "Guided practice": "تمرین هدایت‌شده",
  "Read short passages and check what you understood.": "متن‌های کوتاه بخوانید و درک خود را بسنجید.",
  "Reading practice": "تمرین خواندن",
  "Keep useful words close with focused review sessions.": "با مرور هدفمند، واژه‌های کاربردی را به خاطر بسپارید.",
  "Word review": "مرور واژه",
  "BUILD A ROUTINE": "ساختن یک عادت",
  "Your week": "هفتهٔ شما",
  "A fresh start": "شروعی تازه",
  "Consistency matters more than a perfect streak. Pick a small goal and keep it kind.": "تداوم از زنجیرهٔ بی‌نقص مهم‌تر است. هدفی کوچک و واقع‌بینانه انتخاب کنید.",
  "Sample layout only — activity tracking is not connected yet.": "این فقط نمونهٔ چیدمان است؛ ثبت فعالیت هفتگی هنوز متصل نشده است.",
  "A GENTLE REMINDER": "یادآوری دوستانه",
  "Progress, not": "پیشرفت، نه",
  "perfection.": "کمال‌گرایی.",
  "Ten thoughtful minutes can be more useful than an hour of distracted studying.": "ده دقیقه تمرین متمرکز می‌تواند از یک ساعت مطالعهٔ پراکنده مفیدتر باشد.",
  "YOUR PACE IS THE RIGHT PACE": "با سرعت مناسب خودتان پیش بروید",
  "Take the level check": "آزمون تعیین سطح",
  "Built for steady progress": "برای پیشرفت پیوسته ساخته شده",
  "WORDWISE · ENGLISH LEARNING STUDIO": "وردوایز · استودیوی یادگیری انگلیسی",
  "Hi": "سلام",
  "Words that stay with you.": "واژه‌هایی که در ذهن می‌مانند.",
  "REMEMBER MORE, WITH LESS CRAMMING": "با حفظ کردن کمتر، بیشتر به خاطر بسپارید",
  "Build your own word collection and review each card when it is due. Your next review date changes only after you record how well you remembered the word.": "مجموعهٔ واژه‌های خودتان را بسازید و هر کارت را در موعدش مرور کنید. زمان مرور بعدی فقط پس از ثبت میزان یادآوری شما تغییر می‌کند.",
  "Due now": "موعد مرور",
  "Ready for a review": "آمادهٔ مرور",
  "In your collection": "در مجموعهٔ شما",
  "Words saved to your account": "واژه‌های ذخیره‌شده در حساب",
  "Mastered": "مسلط‌شده",
  "Based on review history": "بر اساس سابقهٔ مرور",
  "GROW YOUR WORD BANK": "گسترش واژگان",
  "Meaning in English": "معنی به انگلیسی",
  "Example sentence": "جملهٔ نمونه",
  "Translation": "ترجمه",
  "YOUR STUDY SESSION": "جلسهٔ مطالعهٔ شما",
  "Words stay with you.": "واژه‌ها در ذهن می‌مانند.",
  "No published passages are available yet.": "هنوز متنی برای مطالعه منتشر نشده است.",
  "READ A LITTLE, UNDERSTAND A LOT": "کمی بخوانید، بسیار بیاموزید",
  "Stories for curious minds.": "متن‌هایی برای ذهن‌های کنجکاو.",
  "Read an original short passage, answer a few questions, and get a score with explanations. Correct answers stay hidden until you submit.": "یک متن کوتاه تألیفی بخوانید، به چند پرسش پاسخ دهید و نتیجه را همراه توضیحات ببینید. پاسخ‌های درست تا زمان ارسال پاسخ‌ها پنهان می‌مانند.",
  "YOUR ANSWERS": "پاسخ‌های شما",
  "READING COMPLETE": "پایان تمرین خواندن",
  "correct": "درست",
  "Your secure session could not be started. Please sign in again.": "شروع نشست امن ممکن نشد. لطفاً دوباره وارد شوید.",
  "A FRESH START": "شروعی تازه",
  "Make space to grow.": "برای رشد جا باز کنید.",
  "Create your personal learning space. Use a strong password you do not use elsewhere.": "فضای یادگیری شخصی خود را بسازید. از رمز عبوری قوی و غیرتکراری استفاده کنید.",
  "at least 12 characters": "حداقل ۱۲ نویسه",
  "The passwords do not match.": "رمزهای عبور یکسان نیستند.",
  "Already have an account?": "از قبل حساب دارید؟",
  "New to Wordwise?": "تازه به وردوایز پیوسته‌اید؟",
  "Create an account": "ساخت حساب",
  "Sign in to continue your English learning journey.": "برای ادامهٔ مسیر یادگیری انگلیسی وارد شوید.",
  "WELCOME BACK": "خوش برگشتید",
  "Make today count.": "امروز را پربار کنید.",
  "YOUR DRAFT": "متن شما",
  "What would you like to say?": "دوست دارید چه بنویسید؟",
  "YOUR WRITING STUDIO": "استودیوی نوشتن شما",
  "Writing practice": "تمرین نوشتن",
  "Analyze writing": "تحلیل نوشته",
  "Saved writing": "نوشته‌های ذخیره‌شده",
  "Your personal word collection is private.": "مجموعهٔ واژه‌های شما خصوصی است.",
  "YOUR READING SESSION": "جلسهٔ خواندن شما",
  "No reading attempts are saved yet.": "هنوز تمرین خواندنی ذخیره نشده است."
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
    document.documentElement.lang = locale;
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
      setSaveError("Preference could not be saved. Try again.");
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
      {saveError && <span role="status">{t(saveError)}</span>}
    </div>
  );
}
