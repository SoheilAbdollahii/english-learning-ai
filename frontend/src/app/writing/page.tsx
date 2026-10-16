"use client";

import Link from "next/link";
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
  const [text, setText] = useState("");
  const [history, setHistory] = useState<WritingSubmission[]>([]);
  const [current, setCurrent] = useState<WritingSubmission | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [needsSignIn, setNeedsSignIn] = useState(false);

  useEffect(() => {
    let active = true;
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
      setSubmitting(false);
    }
  }

  return (
    <main className="writing-shell">
      <div className="writing-topline">
        <Link href="/" className="placement-back">← Dashboard</Link>
        <span className="placement-kicker">WORDWISE · WRITING STUDIO</span>
      </div>

      <section className="writing-intro" aria-labelledby="writing-title">
        <p className="placement-eyebrow">PRACTICE MAKES PROGRESS</p>
        <h1 id="writing-title">Put your thoughts <em>into words.</em></h1>
        <p>Write a few sentences in English and save them to your personal practice history. The current demo mode checks the integration only; it does not yet evaluate grammar.</p>
      </section>

      <section className="writing-composer" aria-labelledby="composer-title">
        <div className="writing-composer-heading">
          <div>
            <p className="placement-eyebrow">YOUR DRAFT</p>
            <h2 id="composer-title">What would you like to say?</h2>
          </div>
          <span className="writing-character-count">{text.length} / 5,000</span>
        </div>
        <label className="writing-sr-only" htmlFor="writing-text">Your English writing</label>
        <textarea
          id="writing-text"
          value={text}
          onChange={(event) => { setText(event.target.value); setError(""); }}
          placeholder="Today I learned something new about…"
          maxLength={5000}
          minLength={3}
          rows={8}
        />
        <div className="writing-composer-footer">
          <p>Your writing is saved to your account when you submit it.</p>
          <button className="placement-submit" type="button" onClick={submitWriting} disabled={submitting || text.trim().length < 3 || text.length > 5000}>
            {submitting ? "Saving draft…" : "Save and review"} <span aria-hidden="true">↗</span>
          </button>
        </div>
        {error && <p className="placement-error" role="alert">{error} {needsSignIn && <Link href="/login">Sign in</Link>}</p>}
      </section>

      {current?.result && (
        <section className="writing-result" aria-labelledby="writing-result-title" aria-live="polite">
          <div className="writing-result-header">
            <div>
              <p className="placement-eyebrow">SAVED SUBMISSION #{current.id}</p>
              <h2 id="writing-result-title">Your writing is saved.</h2>
            </div>
            <span className="writing-status">{current.status}</span>
          </div>
          <blockquote className="writing-original">{current.original_text}</blockquote>
          <p className="writing-feedback">{current.result.general_feedback}</p>
          <div className="writing-limitations">
            <strong>Demo mode limitations</strong>
            <ul>{current.result.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul>
          </div>
        </section>
      )}

      <section className="writing-history" aria-labelledby="writing-history-title">
        <div className="writing-history-heading">
          <div>
            <p className="placement-eyebrow">YOUR PRACTICE</p>
            <h2 id="writing-history-title">Recent writing</h2>
          </div>
          <span>{history.length} shown</span>
        </div>
        {loadingHistory ? <p className="writing-empty" role="status">Loading your saved writing…</p> : history.length === 0 ? (
          <p className="writing-empty">Your saved writing will appear here after your first submission.</p>
        ) : (
          <div className="writing-history-list">
            {history.map((item) => (
              <article className="writing-history-item" key={item.id}>
                <div className="writing-history-item-copy">
                  <p>{item.original_text}</p>
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
