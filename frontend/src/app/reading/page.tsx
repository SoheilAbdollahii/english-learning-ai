"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

type PassageSummary = { id: number; slug: string; title: string; level: string; content_version: number; question_count: number };
type ReadingQuestion = { id: number; prompt: string; options: Record<string, string>; points: number; order: number };
type PassageDetail = PassageSummary & { body: string; source_note: string; questions: ReadingQuestion[] };
type AnswerDetail = { question_id: number; prompt: string; selected_option: string; correct_option: string; correct: boolean; explanation: string };
type ReadingResult = { id: number; passage: number; passage_title: string; passage_version: number; submitted_answers: Record<string, string>; result_details: AnswerDetail[]; score: number; max_score: number; percentage: number; completed_at: string };

async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("We couldn't start a secure session. Please sign in again.");
  return data.csrfToken;
}

export default function ReadingPage() {
  const [passages, setPassages] = useState<PassageSummary[]>([]);
  const [passage, setPassage] = useState<PassageDetail | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<ReadingResult | null>(null);
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
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't submit your answers.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="placement-shell reading-shell">
      <div className="placement-topline">
        <Link href="/" className="placement-back">← Dashboard</Link>
        <span className="placement-kicker">WORDWISE · READING ROOM</span>
      </div>
      <section className="placement-intro" aria-labelledby="reading-title">
        <p className="placement-eyebrow">READ A LITTLE, UNDERSTAND A LOT</p>
        <h1 id="reading-title">Stories for <em>curious minds.</em></h1>
        <p>Read an original short passage, answer a few questions, and get a score with explanations. Correct answers stay hidden until you submit.</p>
      </section>

      <section className="reading-library" aria-label="Available reading passages">
        <div className="placement-progress-heading"><span>CHOOSE A PASSAGE</span><strong>{passages.length} available</strong></div>
        <div className="reading-passage-tabs">
          {passages.map((item) => (
            <button key={item.id} type="button" className={passage?.id === item.id ? "reading-passage-tab reading-passage-tab-active" : "reading-passage-tab"} onClick={() => void loadPassage(item.id)}>
              <span>{item.level}</span><strong>{item.title}</strong><small>{item.question_count} questions</small>
            </button>
          ))}
        </div>
      </section>

      {loading || loadingPassage ? <p className="placement-loading" role="status">Loading your reading passage…</p> : !passage ? (
        <p className="writing-empty">No published passages are available yet.</p>
      ) : (
        <>
          <article className="reading-passage" aria-labelledby="passage-title">
            <div className="reading-passage-meta"><span>{passage.level} · VERSION {passage.content_version}</span><span>{passage.questions.length} questions</span></div>
            <h2 id="passage-title">{passage.title}</h2>
            <p className="reading-passage-body">{passage.body}</p>
            <p className="reading-source">{passage.source_note}</p>
          </article>

          {!result ? (
            <section className="placement-quiz reading-quiz" aria-label="Reading comprehension questions">
              <div className="placement-progress-heading"><span>YOUR ANSWERS</span><strong>{answeredCount} of {passage.questions.length} answered</strong></div>
              <div className="placement-progress-track" role="progressbar" aria-label="Questions answered" aria-valuemin={0} aria-valuemax={passage.questions.length} aria-valuenow={answeredCount}>
                <div className="placement-progress-fill" style={{ width: `${passage.questions.length ? answeredCount / passage.questions.length * 100 : 0}%` }} />
              </div>
              <div className="placement-question-list">
                {passage.questions.map((question, index) => (
                  <fieldset className="placement-question" key={question.id}>
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
              {error && <p className="placement-error" role="alert">{error} {needsSignIn && <Link href="/login">Sign in</Link>}</p>}
              <div className="placement-submit-row"><p>Your answers are scored on the server.</p><button className="placement-submit" type="button" onClick={submitAttempt} disabled={submitting || answeredCount !== passage.questions.length}>{submitting ? "Saving result…" : "Check my answers"} <span aria-hidden="true">↗</span></button></div>
            </section>
          ) : (
            <section className="reading-result" aria-labelledby="reading-result-title" aria-live="polite">
              <p className="placement-eyebrow">READING COMPLETE</p>
              <h2 id="reading-result-title">You got {result.score} of {result.max_score} points.</h2>
              <p className="reading-result-score">{result.percentage}% <span>correct</span></p>
              <div className="reading-feedback-list">
                {result.result_details.map((item, index) => (
                  <article key={item.question_id} className="reading-feedback-item">
                    <span className={item.correct ? "reading-answer-mark reading-answer-correct" : "reading-answer-mark reading-answer-wrong"}>{item.correct ? "✓ Correct" : "↻ Review"}</span>
                    <h3>{index + 1}. {item.prompt}</h3>
                    <p>{item.explanation || `Correct answer: ${item.correct_option.toUpperCase()}.`}</p>
                  </article>
                ))}
              </div>
              <div className="placement-result-actions"><button className="placement-secondary-button" type="button" onClick={() => { setAnswers({}); setResult(null); setError(""); }}>Try this passage again</button><Link href="/" className="placement-primary-link">Back to dashboard</Link></div>
            </section>
          )}
        </>
      )}
      {error && (!passage || result) && <p className="placement-error" role="alert">{error}</p>}
    </main>
  );
}
