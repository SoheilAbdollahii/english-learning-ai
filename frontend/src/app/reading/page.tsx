"use client";

import Link from "next/link";
import { useLocale } from "../components/locale-provider";
import { useCallback, useEffect, useMemo, useState } from "react";

type PassageSummary = { id: number; slug: string; title: string; level: string; content_version: number; question_count: number };
type ReadingQuestion = { id: number; prompt: string; options: Record<string, string>; points: number; order: number };
type PassageDetail = PassageSummary & { body: string; source_note: string; questions: ReadingQuestion[] };
type AnswerDetail = { question_id: number; prompt: string; selected_option: string; correct_option: string; correct: boolean; explanation: string };
type ReadingResult = { id: number; passage: number; passage_title: string; passage_version: number; submitted_answers: Record<string, string>; result_details: AnswerDetail[]; score: number; max_score: number; percentage: number; completed_at: string };
type ReadingAttemptSummary = { id: number; passage_title: string; passage_version: number; score: number; max_score: number; percentage: number; completed_at: string };

async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("We couldn't start a secure session. Please sign in again.");
  return data.csrfToken;
}

export default function ReadingPage() {
  const { t, locale } = useLocale();
  const [passages, setPassages] = useState<PassageSummary[]>([]);
  const [passage, setPassage] = useState<PassageDetail | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<ReadingResult | null>(null);
  const [history, setHistory] = useState<ReadingAttemptSummary[]>([]);
  const [historyNeedsSignIn, setHistoryNeedsSignIn] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingPassage, setLoadingPassage] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [needsSignIn, setNeedsSignIn] = useState(false);

  const loadPassage = useCallback(async (id: number) => {
    setLoadingPassage(true);
    setError("");
    setResult(null);
    setAnswers({});
    try {
      const response = await fetch(`/api/v1/reading/passages/${id}/`, { credentials: "same-origin", cache: "no-store" });
      if (!response.ok) throw new Error("We couldn't load this reading passage.");
      setPassage(await response.json() as PassageDetail);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't load this passage.");
    } finally {
      setLoadingPassage(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    async function loadHistory() {
      try {
        const response = await fetch("/api/v1/reading/attempts/?limit=8", { credentials: "same-origin", cache: "no-store" });
        if (response.status === 401 || response.status === 403) {
          if (active) setHistoryNeedsSignIn(true);
          return;
        }
        if (!response.ok) return;
        const data = await response.json() as { results?: ReadingAttemptSummary[] };
        if (active) setHistory(data.results ?? []);
      } catch {
        // History is supplementary; keep passage practice available if it fails.
      }
    }
    void loadHistory();
    async function loadPassages() {
      try {
        const response = await fetch("/api/v1/reading/passages/", { credentials: "same-origin", cache: "no-store" });
        if (!response.ok) throw new Error("We couldn't load reading practice.");
        const data = await response.json() as PassageSummary[];
        if (!active) return;
        setPassages(data);
        if (data.length) await loadPassage(data[0].id);
      } catch (cause) {
        if (active) setError(cause instanceof Error ? cause.message : "We couldn't load reading practice.");
      } finally {
        if (active) setLoading(false);
      }
    }
    void loadPassages();
    return () => { active = false; };
  }, [loadPassage]);

  const answeredCount = useMemo(() => passage?.questions.filter((question) => Boolean(answers[String(question.id)])).length ?? 0, [passage, answers]);

  async function submitAttempt() {
    if (!passage || answeredCount !== passage.questions.length) {
      setError("Please answer every question before submitting.");
      return;
    }
    setSubmitting(true);
    setError("");
    setNeedsSignIn(false);
    try {
      const token = await getCsrfToken();
      const response = await fetch("/api/v1/reading/attempts/", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify({ passage_id: passage.id, answers }),
      });
      const data = await response.json().catch(() => ({})) as ReadingResult & { detail?: string };
      if (response.status === 401 || response.status === 403) {
        setNeedsSignIn(true);
        throw new Error("Sign in to save your reading result.");
      }
      if (!response.ok) throw new Error(data.detail ?? "We couldn't save your reading result.");
      setResult(data);
      setHistoryNeedsSignIn(false);
      setHistory((previous) => [data, ...previous.filter((item) => item.id !== data.id)].slice(0, 8));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't submit your answers.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="placement-shell reading-shell">
      <div className="placement-topline">
        <Link href="/" className="placement-back">← {t("Back to dashboard")}</Link>
        <span className="placement-kicker">{t("WORDWISE · READING ROOM")}</span>
      </div>
      <section className="placement-intro" aria-labelledby="reading-title">
        <p className="placement-eyebrow">{t("READ A LITTLE, UNDERSTAND A LOT")}</p>
        <h1 id="reading-title">{t("Stories for curious minds.")}</h1>
        <p>{t("Read an original short passage, answer a few questions, and get a score with explanations. Correct answers stay hidden until you submit.")}</p>
      </section>

      <section className="reading-library" aria-label={t("Available reading passages")}>
        <div className="placement-progress-heading"><span>{t("Choose a passage")}</span><strong>{passages.length} {t("available")}</strong></div>
        <div className="reading-passage-tabs">
          {passages.map((item) => (
            <button key={item.id} type="button" className={passage?.id === item.id ? "reading-passage-tab reading-passage-tab-active" : "reading-passage-tab"} onClick={() => void loadPassage(item.id)}>
              <span>{item.level}</span><strong>{item.title}</strong><small>{item.question_count} {t("questions")}</small>
            </button>
          ))}
        </div>
      </section>

      {loading || loadingPassage ? <p className="placement-loading" role="status">{t("Loading your reading passage…")}</p> : !passage ? (
        <p className="writing-empty">{t("No published passages are available yet.")}</p>
      ) : (
        <>
          <article className="reading-passage" aria-labelledby="passage-title">
            <div className="reading-passage-meta"><span>{passage.level} · {t("VERSION")} {passage.content_version}</span><span>{passage.questions.length} {t("questions")}</span></div>
            <h2 id="passage-title" lang="en" dir="ltr">{passage.title}</h2>
            <p className="reading-passage-body" lang="en" dir="ltr">{passage.body}</p>
            <p className="reading-source" lang="en" dir="ltr">{passage.source_note}</p>
          </article>

          {!result ? (
            <section className="placement-quiz reading-quiz" aria-label={t("Reading comprehension questions")}>
              <div className="placement-progress-heading"><span>{t("YOUR ANSWERS")}</span><strong>{answeredCount} {t("of")} {passage.questions.length} {t("answered")}</strong></div>
              <div className="placement-progress-track" role="progressbar" aria-label="Questions answered" aria-valuemin={0} aria-valuemax={passage.questions.length} aria-valuenow={answeredCount}>
                <div className="placement-progress-fill" style={{ width: `${passage.questions.length ? answeredCount / passage.questions.length * 100 : 0}%` }} />
              </div>
              <div className="placement-question-list">
                {passage.questions.map((question, index) => (
                  <fieldset className="placement-question" key={question.id} lang="en" dir="ltr">
                    <legend><span className="placement-question-number">{String(index + 1).padStart(2, "0")}</span><span>{question.prompt}</span></legend>
                    <div className="placement-options">
                      {Object.entries(question.options).map(([key, label]) => {
                        const inputId = `reading-${question.id}-${key}`;
                        return <label className={answers[String(question.id)] === key ? "placement-option placement-option-selected" : "placement-option"} htmlFor={inputId} key={key}>
                          <input id={inputId} type="radio" name={`reading-${question.id}`} value={key} checked={answers[String(question.id)] === key} onChange={() => setAnswers((previous) => ({ ...previous, [String(question.id)]: key }))} />
                          <span className="placement-option-key">{key.toUpperCase()}</span><span>{label}</span>
                        </label>;
                      })}
                    </div>
                  </fieldset>
                ))}
              </div>
              {error && <p className="placement-error" role="alert">{t(error)} {needsSignIn && <Link href="/login">{t("Sign in")}</Link>}</p>}
              <div className="placement-submit-row"><p>{t("Your answers are scored on the server.")}</p><button className="placement-submit" type="button" onClick={submitAttempt} disabled={submitting || answeredCount !== passage.questions.length}>{submitting ? t("Saving result…") : t("Check my answers")} <span aria-hidden="true">↗</span></button></div>
            </section>
          ) : (
            <section className="reading-result" aria-labelledby="reading-result-title" aria-live="polite">
              <p className="placement-eyebrow">{t("READING COMPLETE")}</p>
              <h2 id="reading-result-title">{locale === "fa" ? `امتیاز شما ${result.score} از ${result.max_score} است.` : `You got ${result.score} of ${result.max_score} points.`}</h2>
              <p className="reading-result-score">{result.percentage}% <span>{t("correct")}</span></p>
              <div className="reading-feedback-list">
                {result.result_details.map((item, index) => (
                  <article key={item.question_id} className="reading-feedback-item">
                    <span className={item.correct ? "reading-answer-mark reading-answer-correct" : "reading-answer-mark reading-answer-wrong"}>{item.correct ? `✓ ${t("Correct")}` : `↻ ${t("Review")}`}</span>
                    <h3 lang="en" dir="ltr">{index + 1}. {item.prompt}</h3>
                    <p lang="en" dir="ltr">{item.explanation || `Correct answer: ${item.correct_option.toUpperCase()}.`}</p>
                  </article>
                ))}
              </div>
              <div className="placement-result-actions"><button className="placement-secondary-button" type="button" onClick={() => { setAnswers({}); setResult(null); setError(""); }}>{t("Try this passage again")}</button><Link href="/" className="placement-primary-link">{t("Back to dashboard")}</Link></div>
            </section>
          )}
        </>
      )}
      <section className="reading-history" aria-labelledby="reading-history-title">
        <div className="section-heading">
          <div><p className="placement-eyebrow">{t("YOUR PRACTICE")}</p><h2 id="reading-history-title">{t("Your reading history")}</h2></div>
          <span className="section-caption">{history.length} {t("recent attempts")}</span>
        </div>
        {historyNeedsSignIn && history.length === 0 ? (
          <p className="writing-empty">{t("Sign in to see your saved reading history.")} <Link href="/login">{t("Sign in")}</Link></p>
        ) : history.length === 0 ? (
          <p className="writing-empty">{t("Your reading attempts will appear here after you finish a passage.")}</p>
        ) : (
          <div className="reading-history-list">
            {history.map((attempt) => (
              <article className="reading-history-item" key={attempt.id}>
                <div><strong lang="en" dir="ltr">{attempt.passage_title}</strong><span>{new Date(attempt.completed_at).toLocaleDateString(locale === "fa" ? "fa-IR" : "en-US")} · {t("VERSION")} {attempt.passage_version}</span></div>
                <strong className="reading-history-score">{attempt.percentage}%</strong>
              </article>
            ))}
          </div>
        )}
      </section>
      {error && (!passage || result) && <p className="placement-error" role="alert">{t(error)}</p>}
    </main>
  );
}
