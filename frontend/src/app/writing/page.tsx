"use client";

import Link from "next/link";
import { useLocale } from "../components/locale-provider";
import { useEffect, useState } from "react";

type WritingError = {
  category: string;
  start: number;
  end: number;
  original: string;
  correction: string;
  explanation: string;
};

type WritingResult = {
  schema_version: number;
  corrected_text: string;
  errors: WritingError[];
  general_feedback: string;
  limitations: string[];
};

type WritingSubmission = {
  id: number;
  original_text: string;
  status: "pending" | "succeeded" | "failed";
  provider: string;
  result: WritingResult | null;
  failure_category: string;
  created_at: string;
};

type WritingHistoryResponse = {
  count: number;
  results: WritingSubmission[];
};

type UsageSummary = {
  limit: number;
  used: number;
  remaining: number;
  window: string;
  cost_tracking: string;
};

async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", {
    credentials: "same-origin",
    cache: "no-store",
  });
  const data = (await response.json().catch(() => ({}))) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("We couldn't start a secure session. Please sign in again.");
  return data.csrfToken;
}

export default function WritingPage() {
  const { t, locale } = useLocale();
  const [text, setText] = useState("");
  const [history, setHistory] = useState<WritingSubmission[]>([]);
  const [current, setCurrent] = useState<WritingSubmission | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [needsSignIn, setNeedsSignIn] = useState(false);
  const [usage, setUsage] = useState<UsageSummary | null>(null);

  useEffect(() => {
    let active = true;
    async function loadUsage() {
      try {
        const response = await fetch("/api/v1/usage/", { credentials: "same-origin", cache: "no-store" });
        if (response.ok && active) setUsage(await response.json() as UsageSummary);
      } catch {
        // Usage visibility is supplementary; the server still enforces the quota.
      }
    }
    void loadUsage();
    async function loadHistory() {
      try {
        const response = await fetch("/api/v1/writing/submissions/?limit=10", {
          credentials: "same-origin",
          cache: "no-store",
        });
        if (response.status === 401 || response.status === 403) {
          if (active) setNeedsSignIn(true);
          return;
        }
        if (!response.ok) throw new Error("We couldn't load your writing history.");
        const data = (await response.json()) as WritingHistoryResponse;
        if (active) setHistory(data.results);
      } catch (cause) {
        if (active) setError(cause instanceof Error ? cause.message : "We couldn't load your writing history.");
      } finally {
        if (active) setLoadingHistory(false);
      }
    }
    void loadHistory();
    return () => { active = false; };
  }, []);

  async function submitWriting() {
    setError("");
    setNeedsSignIn(false);
    setSubmitting(true);
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch("/api/v1/writing/submissions/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ text }),
      });
      const data = await response.json().catch(() => ({})) as WritingSubmission & { detail?: string; code?: string };
      if (response.status === 401 || response.status === 403) {
        setNeedsSignIn(true);
        throw new Error("Sign in to save and review your writing.");
      }
      if (!response.ok) throw new Error(data.detail ?? "We couldn't analyze this submission. Please try again.");
      setCurrent(data);
      setHistory((previous) => [data, ...previous.filter((item) => item.id !== data.id)].slice(0, 10));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't reach the writing service.");
    } finally {
      try {
        const usageResponse = await fetch("/api/v1/usage/", { credentials: "same-origin", cache: "no-store" });
        if (usageResponse.ok) setUsage(await usageResponse.json() as UsageSummary);
      } catch {
        // The usage display is supplementary; quota enforcement remains server-side.
      }
      setSubmitting(false);
    }
  }

  return (
    <main className="writing-shell">
      <div className="writing-topline">
        <Link href="/" className="placement-back">← {t("Back to dashboard")}</Link>
        <span className="placement-kicker">{t("WORDWISE · WRITING STUDIO")}</span>
      </div>

      <section className="writing-intro" aria-labelledby="writing-title">
        <p className="placement-eyebrow">{t("PRACTICE MAKES PROGRESS")}</p>
        <h1 id="writing-title">{t("Put your thoughts into words.")}</h1>
        <p>{t("Write a few sentences in English and save them to your personal practice history. When no AI provider is configured, demo mode only checks the integration and does not evaluate grammar.")}</p>
      </section>

      <section className="writing-composer" aria-labelledby="composer-title">
        <div className="writing-composer-heading">
          <div>
            <p className="placement-eyebrow">{t("YOUR DRAFT")}</p>
            <h2 id="composer-title">{t("What would you like to say?")}</h2>
          </div>
          <span className="writing-character-count">{text.length} / 5,000</span>
        </div>
        {usage && <p className="writing-usage-note">{locale === "fa" ? `سهمیهٔ ۲۴ ساعته: ${usage.remaining} از ${usage.limit} ارسال باقی مانده است. تلاش‌های ناموفق نیز در سهمیه حساب می‌شوند.` : `Rolling 24-hour allowance: ${usage.remaining} of ${usage.limit} submissions remaining. Failed provider attempts count toward the limit; provider costs are not yet available.`}</p>}
        <label className="writing-sr-only" htmlFor="writing-text">{t("Your English writing")}</label>
        <textarea
          id="writing-text"
          lang="en"
          dir="ltr"
          value={text}
          onChange={(event) => { setText(event.target.value); setError(""); }}
          placeholder="Today I learned something new about…"
          maxLength={5000}
          minLength={3}
          rows={8}
        />
        <div className="writing-composer-footer">
          <p>{t("Your writing is saved to your account when you submit it.")}</p>
          <button className="placement-submit" type="button" onClick={submitWriting} disabled={submitting || text.trim().length < 3 || text.length > 5000}>
            {submitting ? t("Saving draft…") : t("Save and review")} <span aria-hidden="true">↗</span>
          </button>
        </div>
        {error && <p className="placement-error" role="alert">{t(error)} {needsSignIn && <Link href="/login">{t("Sign in")}</Link>}</p>}
      </section>

      {current?.result && (
        <section className="writing-result" aria-labelledby="writing-result-title" aria-live="polite">
          <div className="writing-result-header">
            <div>
              <p className="placement-eyebrow">{t("SAVED SUBMISSION")} #{current.id}</p>
              <h2 id="writing-result-title">{t("Your writing is saved.")}</h2>
            </div>
            <span className="writing-status">{current.status}</span>
          </div>
          <p className="writing-provider-note">{current.provider === "demo" ? t("Demo provider — no grammar evaluation") : t("AI provider analysis")} · {current.result.errors.length} {t("suggestions")}</p>
          <blockquote className="writing-original" lang="en" dir="ltr">{current.original_text}</blockquote>
          <p className="writing-feedback" lang="en" dir="ltr">{current.result.general_feedback}</p>
          <section className="writing-corrections" aria-labelledby="writing-corrected-title">
            <h3 id="writing-corrected-title">{t("Suggested revision")}</h3>
            <blockquote lang="en" dir="ltr">{current.result.corrected_text}</blockquote>
            {current.result.errors.length === 0 ? (
              <p>{current.provider === "demo" ? t("No grammar corrections are generated in demo mode.") : t("No specific corrections were returned.")}</p>
            ) : (
              <ol>
                {current.result.errors.map((item, index) => (
                  <li key={`${item.start}-${item.end}-${index}`}>
                    <strong>{t(item.category)}</strong>: <span lang="en" dir="ltr">{item.original}</span> → <span lang="en" dir="ltr">{item.correction}</span>
                    <p>{item.explanation}</p>
                  </li>
                ))}
              </ol>
            )}
          </section>
          {current.result.limitations.length > 0 && (
            <div className="writing-limitations">
              <strong>{current.provider === "demo" ? t("Demo mode limitations") : t("Analysis notes")}</strong>
              <ul>{current.result.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul>
            </div>
          )}
        </section>
      )}

      <section className="writing-history" aria-labelledby="writing-history-title">
        <div className="writing-history-heading">
          <div>
            <p className="placement-eyebrow">{t("YOUR PRACTICE")}</p>
            <h2 id="writing-history-title">{t("Recent writing")}</h2>
          </div>
          <span>{history.length} {t("shown")}</span>
        </div>
        {loadingHistory ? <p className="writing-empty" role="status">{t("Loading your saved writing…")}</p> : history.length === 0 ? (
          <p className="writing-empty">{t("Your saved writing will appear here after your first submission.")}</p>
        ) : (
          <div className="writing-history-list">
            {history.map((item) => (
              <article className="writing-history-item" key={item.id}>
                <div className="writing-history-item-copy">
                  <p lang="en" dir="ltr">{item.original_text}</p>
                  <span>{new Date(item.created_at).toLocaleString()} · {item.status}</span>
                </div>
                <button type="button" className="writing-view-button" onClick={() => setCurrent(item)} disabled={!item.result}>
                  View <span aria-hidden="true">↗</span>
                </button>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
