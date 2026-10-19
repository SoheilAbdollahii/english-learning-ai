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
  "WORDWISE · VOCABULARY": "وردوایز · واژگان",
  "WORDWISE · READING ROOM": "وردوایز · فضای خواندن",
  "WORDWISE · WRITING STUDIO": "وردوایز · استودیوی نوشتن",
  "WORDWISE · LEVEL CHECK": "وردوایز · تعیین سطح",
  "Open": "باز کردن",
  "days": "روز",
  "Your account is ready. Sign in to start saving your English practice.": "حساب شما آماده است. برای ذخیرهٔ تمرین‌های انگلیسی وارد شوید.",
  "Email verification and account recovery are not available yet.": "تأیید ایمیل و بازیابی حساب هنوز در دسترس نیست.",
  "Your secure session could not be started. Please sign in again.": "شروع نشست امن ممکن نشد. لطفاً دوباره وارد شوید.",
  "A place to begin.": "جایی برای شروع.",
  "Your answers have been scored and saved to your account.": "پاسخ‌های شما نمره‌دهی و در حساب ذخیره شده‌اند.",
  "Estimated level": "سطح تخمینی",
  "Your score": "امتیاز شما",
  "Correct percentage": "درصد پاسخ‌های درست",
  "This is a provisional estimate based on a short starter quiz, not a certified or adaptive CEFR assessment.": "این تخمینی اولیه بر اساس آزمونی کوتاه است و ارزیابی رسمی یا تطبیقی CEFR نیست.",
  "ASSESSMENT COMPLETE": "ارزیابی کامل شد",
  "PRACTICE MAKES PROGRESS": "تمرین باعث پیشرفت می‌شود",
  "Put your thoughts into writing.": "فکرهایتان را بنویسید.",
  "Find your words, find your voice.": "واژه‌های خود را پیدا کنید، صدای خود را بیابید.",
  "Practice makes progress.": "تمرین باعث پیشرفت می‌شود.",
  "Writing analysis": "تحلیل نوشتار",
  "Your writing is ready to review.": "نوشتهٔ شما آمادهٔ بررسی است.",
  "Corrected text": "متن اصلاح‌شده",
  "General feedback": "بازخورد کلی",
  "Limitations": "محدودیت‌ها",
  "Submission history": "سابقهٔ نوشته‌ها",
  "No saved submissions yet.": "هنوز نوشته‌ای ثبت نشده است.",
  "Sign in to save and review your writing.": "برای ذخیره و مرور نوشته‌ها وارد شوید.",
  "Sign in to save your reading result.": "برای ذخیرهٔ نتیجهٔ خواندن وارد شوید.",
  "Please answer every question before submitting.": "لطفاً پیش از ارسال به همهٔ پرسش‌ها پاسخ دهید.",
  "Saving result…": "در حال ذخیرهٔ نتیجه…",
  "Loading your reading passage…": "در حال بارگذاری متن…",
  "No published passages are available yet.": "هنوز متنی برای مطالعه منتشر نشده است.",
  "A few quick questions help estimate your starting point.": "چند پرسش کوتاه به تخمین نقطهٔ شروع شما کمک می‌کند.",
  "Placement assessment": "آزمون تعیین سطح",
  "Start assessment": "شروع آزمون",
  "Your personal progress is temporarily unavailable.": "پیشرفت شخصی شما موقتاً در دسترس نیست.",
  "Progress is temporarily unavailable. Your learning pages are still available.": "پیشرفت موقتاً در دسترس نیست، اما صفحه‌های تمرین همچنان قابل استفاده‌اند.",
  "sessions": "جلسه",
  "reviews": "مرور",
  "Due now": "موعد مرور",
  "Your draft": "پیش‌نویس شما",
  "What would you like to say?": "دوست دارید چه بنویسید؟",
  "Analyzing…": "در حال تحلیل…",
  "Analyze my writing": "تحلیل نوشتهٔ من",
  "Saved writing": "نوشته‌های ذخیره‌شده",
  "No vocabulary cards are due right now.": "در حال حاضر واژه‌ای برای مرور موعددار نیست.",
  "No reading attempts are saved yet.": "هنوز تمرین خواندنی ذخیره نشده است.",
  "Review saved.": "مرور ذخیره شد.",
  "Completed activities saved to your account": "فعالیت‌های تکمیل‌شده و ذخیره‌شده در حساب شما",
  "Consecutive days with recorded learning": "روزهای پیاپی با فعالیت یادگیری ثبت‌شده",
  "Saved vocabulary review outcomes": "نتایج مرور واژگان ثبت‌شده",
  "Sign in to see your personal progress.": "برای مشاهدهٔ پیشرفت شخصی خود وارد شوید.",
  "Latest saved sessions": "آخرین فعالیت‌های ثبت‌شده",
  "Your activity will appear after your first saved learning session.": "پس از نخستین جلسهٔ یادگیری، فعالیت شما اینجا نمایش داده می‌شود.",
  "Based on your saved activity": "بر اساس فعالیت‌های ذخیره‌شدهٔ شما",
  "We couldn't sign you out. Please check your connection and try again.": "خروج انجام نشد. اتصال خود را بررسی و دوباره تلاش کنید.",
  "Word": "واژه",
  "Try again": "تلاش دوباره",
  "Welcome": "خوش آمدید",
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
  "LEARNING STUDIO": "استودیوی یادگیری",
  "EARLY ACCESS · PREVIEW": "دسترسی زودهنگام · پیش‌نمایش",
  "UI PREVIEW": "پیش‌نمایش رابط کاربری",
  "YOUR LEARNING TRAIL": "مسیر یادگیری شما",
  "Signing out…": "در حال خروج…",
  "YOUR STARTING POINT": "نقطهٔ شروع شما",
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
  "Your secure registration service is unavailable.": "سامانهٔ ثبت‌نام امن در دسترس نیست.",
  "ACCOUNT CREATED": "حساب ساخته شد",
  "Vocabulary overview": "نمای کلی واژگان",
  "to continue.": "برای ادامه.",
  "Scheduling uses a deterministic SM-2-inspired rule set. It is a learning aid, not a guarantee of long-term retention.": "زمان‌بندی مرور از الگوریتم قطعی الهام‌گرفته از SM-2 استفاده می‌کند؛ این ابزار آموزشی است و ماندگاری بلندمدت را تضمین نمی‌کند.",
  "Available reading passages": "متن‌های موجود برای خواندن",
  "available": "موجود",
  "questions": "پرسش",
  "VERSION": "نسخه",
  "Reading comprehension questions": "پرسش‌های درک مطلب",
  "of": "از",
  "answered": "پاسخ داده‌شده",
  "Your answers are scored on the server.": "پاسخ‌های شما در سرور نمره‌دهی می‌شوند.",
  "Correct": "درست",
  "Review": "مرور",
  "YOUR LEARNING JOURNEY STARTS HERE": "مسیر یادگیری شما از اینجا شروع می‌شود",
  "Find your starting point.": "نقطهٔ شروع خود را پیدا کنید.",
  "Answer a few short questions to get a first estimate of your English level. Take your time; this is a guide, not a test to fear.": "به چند پرسش کوتاه پاسخ دهید تا تخمینی اولیه از سطح انگلیسی شما به دست آید. با آرامش پیش بروید؛ این راهنماست، نه آزمونی برای نگرانی.",
  "About 3 minutes": "حدود ۳ دقیقه",
  "Placement questions": "پرسش‌های تعیین سطح",
  "YOUR PROGRESS": "پیشرفت شما",
  "Your score is calculated and stored securely by the server.": "امتیاز شما به‌صورت امن در سرور محاسبه و ذخیره می‌شود.",
  "Submit answers": "ارسال پاسخ‌ها",
  "Put your thoughts into words.": "افکارتان را به واژه تبدیل کنید.",
  "Write a few sentences in English and save them to your personal practice history. The current demo mode checks the integration only; it does not yet evaluate grammar.": "چند جمله به انگلیسی بنویسید و در سابقهٔ تمرین خود ذخیره کنید. حالت نمایشی فعلی فقط اتصال سامانه را بررسی می‌کند و هنوز دستور زبان را ارزیابی نمی‌کند.",
  "Your English writing": "نوشتهٔ انگلیسی شما",
  "Your writing is saved to your account when you submit it.": "با ارسال نوشته، آن را در حساب خود ذخیره می‌کنید.",
  "Saving draft…": "در حال ذخیرهٔ پیش‌نویس…",
  "Save and review": "ذخیره و مرور",
  "SAVED SUBMISSION": "ارسال ذخیره‌شده",
  "Your writing is saved.": "نوشتهٔ شما ذخیره شد.",
  "Demo mode limitations": "محدودیت‌های حالت نمایشی",
  "YOUR PRACTICE": "تمرین‌های شما",
  "Recent writing": "نوشته‌های اخیر",
  "shown": "نمایش داده‌شده",
  "Your saved writing will appear here after your first submission.": "پس از نخستین ارسال، نوشته‌های ذخیره‌شده در اینجا نمایش داده می‌شوند.",
  "Due": "موعد",
  "new": "جدید",
  "learning": "در حال یادگیری",
  "review": "نیازمند مرور",
  "mastered": "مسلط‌شده",
  "Saving word…": "در حال ذخیرهٔ واژه…",
  "You are all caught up. Add a word or show your full collection.": "همهٔ واژه‌های موعددار مرور شده‌اند. واژه‌ای اضافه کنید یا کل مجموعه را ببینید.",
  "Your word collection is empty. Add your first word above.": "مجموعهٔ واژگان شما خالی است. نخستین واژه را در بالا اضافه کنید.",
  "Saving your result…": "در حال ذخیرهٔ نتیجه…",
  "Your writing will be saved when you submit it.": "نوشتهٔ شما پس از ارسال ذخیره می‌شود.",
  "No published placement assessment is available yet.": "هنوز آزمون تعیین سطحی منتشر نشده است.",
  "Loading your vocabulary…": "در حال بارگذاری واژگان…",
  "Your personal word collection is private.": "مجموعهٔ واژگان شما خصوصی است.",
  "View": "مشاهده",
  "A SMALL NEXT STEP": "یک قدم کوچک بعدی",
  "NEXT STEP": "قدم بعدی"

  "Hi": "سلام",
  "REMEMBER MORE, WITH LESS CRAMMING": "با حفظ کردن کمتر، بیشتر به خاطر بسپارید",
  "Words that stay with you.": "واژه‌هایی که در ذهن می‌مانند.",
  "Build your own word collection and review each card when it is due. Your next review date changes only after you record how well you remembered the word.": "مجموعهٔ واژه‌های خودتان را بسازید و هر کارت را در موعدش مرور کنید. زمان مرور بعدی فقط پس از ثبت میزان یادآوری شما تغییر می‌کند.",
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
  "READ A LITTLE, UNDERSTAND A LOT": "کمی بخوانید، بسیار بیاموزید",
  "Stories for curious minds.": "متن‌هایی برای ذهن‌های کنجکاو.",
  "Read an original short passage, answer a few questions, and get a score with explanations. Correct answers stay hidden until you submit.": "یک متن کوتاه تألیفی بخوانید، به چند پرسش پاسخ دهید و نتیجه را همراه توضیحات ببینید. پاسخ‌های درست تا زمان ارسال پاسخ‌ها پنهان می‌مانند.",
  "YOUR ANSWERS": "پاسخ‌های شما",
  "READING COMPLETE": "پایان تمرین خواندن",
  "correct": "درست",
  "YOUR DRAFT": "پیش‌نویس شما",
  "Loading your saved writing…": "در حال بارگذاری نوشته‌های ذخیره‌شده…",
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
        // Keep the local preference usable while the profile API is unavailable.
      } finally {
        if (active) setReady(true);
      }
    }
    void loadProfile();
    return () => { active = false; };
  }, []);

  useEffect(() => {
    document.documentElement.dir = locale === "fa" ? "rtl" : "ltr";
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
