"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type AssessmentSummary = {
  id: number;
  title: string;
  version: number;
  question_count: number;
};

type PlacementQuestion = {
  id: number;
  prompt: string;
  options: Record<string, string>;
  points: number;
  order: number;
};

type AssessmentDetail = AssessmentSummary & {
  questions: PlacementQuestion[];
};

type AttemptResult = {
  id: number;
  assessment_id: number;
  score: number;
  max_score: number;
  estimated_level: string;
  scoring_version: number;
  completed_at: string;
};

async function readError(response: Response): Promise<string> {
  const data = await response.json().catch(() => ({}));
  if (typeof data.detail === "string") return data.detail;
  if (typeof data.answers === "string") return data.answers;
  if (typeof data.assessment_id === "string") return data.assessment_id;
  return "Something went wrong. Please try again.";
}

export default function PlacementPage() {
  const [assessment, setAssessment] = useState<AssessmentDetail | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<AttemptResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [needsSignIn, setNeedsSignIn] = useState(false);

  useEffect(() => {
    let active = true;
    async function loadAssessment() {
      try {
        const listResponse = await fetch("/api/v1/placement/assessments/", {
          credentials: "same-origin",
          cache: "no-store",
        });
        if (!listResponse.ok) throw new Error("We couldn't load the placement assessment.");
        const assessments = (await listResponse.json()) as AssessmentSummary[];
        if (!assessments.length) {
          if (active) setError("No published placement assessment is available yet.");
          return;
        }
        const detailResponse = await fetch(
          `/api/v1/placement/assessments/${assessments[0].id}/`,
          { credentials: "same-origin", cache: "no-store" },
        );
        if (!detailResponse.ok) throw new Error("We couldn't load the assessment questions.");
        const detail = (await detailResponse.json()) as AssessmentDetail;
        if (active) setAssessment(detail);
      } catch (cause) {
        if (active) setError(cause instanceof Error ? cause.message : "We couldn't load the assessment.");
      } finally {
        if (active) setLoading(false);
      }
    }
    void loadAssessment();
    return () => {
      active = false;
    };
  }, []);

  const answeredCount = useMemo(
    () => assessment?.questions.filter((question) => Boolean(answers[String(question.id)] )).length ?? 0,
    [assessment, answers],
  );
  const questionCount = assessment?.questions.length ?? 0;
  const progress = questionCount ? (answeredCount / questionCount) * 100 : 0;

  function chooseAnswer(questionId: number, option: string) {
    setAnswers((current) => ({ ...current, [String(questionId)]: option }));
    setError("");
  }

  async function submitAssessment() {
    if (!assessment || answeredCount !== questionCount) {
      setError("Please answer every question before submitting.");
      return;
    }
    setSubmitting(true);
    setError("");
    setNeedsSignIn(false);
    try {
      const csrfResponse = await fetch("/api/v1/auth/csrf/", {
        credentials: "same-origin",
        cache: "no-store",
      });
      if (!csrfResponse.ok) throw new Error("We couldn't start a secure session. Please sign in again.");
      const csrfData = (await csrfResponse.json()) as { csrfToken?: string };
      if (!csrfData.csrfToken) throw new Error("We couldn't start a secure session. Please sign in again.");

      const response = await fetch("/api/v1/placement/attempts/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfData.csrfToken,
        },
        body: JSON.stringify({ assessment_id: assessment.id, answers }),
      });
      if (response.status === 401 || response.status === 403) {
        setNeedsSignIn(true);
        throw new Error("Please sign in to save your placement result.");
      }
      if (!response.ok) throw new Error(await readError(response));
      const submittedResult = (await response.json()) as AttemptResult;
      setResult(submittedResult);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't submit your answers.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <main className="placement-shell"><p className="placement-loading" role="status">Loading your placement assessment…</p></main>;
  }

  if (result) {
    const percentage = result.max_score ? Math.round((result.score / result.max_score) * 100) : 0;
    return (
      <main className="placement-shell">
        <div className="placement-topline">
          <Link href="/" className="placement-back">← Dashboard</Link>
          <span className="placement-kicker">YOUR STARTING POINT</span>
        </div>
        <section className="placement-result" aria-labelledby="result-title">
          <span className="placement-result-mark" aria-hidden="true">✦</span>
          <p className="placement-eyebrow">ASSESSMENT COMPLETE</p>
          <h1 id="result-title">A place to <em>begin.</em></h1>
          <p className="placement-result-copy">Your answers have been scored and saved to your account.</p>
          <div className="placement-result-grid">
            <div className="placement-result-stat"><span>Estimated level</span><strong>{result.estimated_level}</strong></div>
            <div className="placement-result-stat"><span>Your score</span><strong>{result.score}<small> / {result.max_score}</small></strong></div>
            <div className="placement-result-stat"><span>Correct percentage</span><strong>{percentage}%</strong></div>
          </div>
          <p className="placement-caveat">This is a provisional estimate based on a short starter quiz, not a certified or adaptive CEFR assessment.</p>
          <div className="placement-result-actions">
            <Link href="/" className="placement-primary-link">Back to dashboard</Link>
            <button className="placement-secondary-button" type="button" onClick={() => { setAnswers({}); setResult(null); setError(""); }}>
              Try again
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="placement-shell">
      <div className="placement-topline">
        <Link href="/" className="placement-back">← Dashboard</Link>
        <span className="placement-kicker">WORDWISE · LEVEL CHECK</span>
      </div>
      <section className="placement-intro" aria-labelledby="placement-title">
        <p className="placement-eyebrow">YOUR LEARNING JOURNEY STARTS HERE</p>
        <h1 id="placement-title">Find your <em>starting point.</em></h1>
        <p>Answer a few short questions to get a first estimate of your English level. Take your time; this is a guide, not a test to fear.</p>
        {assessment && <div className="placement-meta"><span>{assessment.title}</span><span>{questionCount} questions</span><span>About 3 minutes</span></div>}
      </section>

      {assessment && (
        <section className="placement-quiz" aria-label="Placement questions">
          <div className="placement-progress-heading">
            <span>YOUR PROGRESS</span>
            <strong>{answeredCount} of {questionCount} answered</strong>
          </div>
          <div className="placement-progress-track" role="progressbar" aria-label="Questions answered" aria-valuemin={0} aria-valuemax={questionCount} aria-valuenow={answeredCount}>
            <div className="placement-progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <div className="placement-question-list">
            {assessment.questions.map((question, index) => (
              <fieldset className="placement-question" key={question.id}>
                <legend>
                  <span className="placement-question-number">{String(index + 1).padStart(2, "0")}</span>
                  <span>{question.prompt}</span>
                </legend>
                <div className="placement-options">
                  {Object.entries(question.options).map(([key, label]) => {
                    const inputId = `question-${question.id}-option-${key}`;
                    return (
                      <label className={answers[String(question.id)] === key ? "placement-option placement-option-selected" : "placement-option"} htmlFor={inputId} key={key}>
                        <input
                          id={inputId}
                          type="radio"
                          name={`question-${question.id}`}
                          value={key}
                          checked={answers[String(question.id)] === key}
                          onChange={() => chooseAnswer(question.id, key)}
                        />
                        <span className="placement-option-key">{key.toUpperCase()}</span>
                        <span>{label}</span>
                      </label>
                    );
                  })}
                </div>
              </fieldset>
            ))}
          </div>
          {error && <p className="placement-error" role="alert">{error} {needsSignIn && <Link href="/login">Sign in</Link>}</p>}
          <div className="placement-submit-row">
            <p>Your score is calculated and stored securely by the server.</p>
            <button className="placement-submit" type="button" onClick={submitAssessment} disabled={submitting || answeredCount !== questionCount}>
              {submitting ? "Saving your result…" : "Submit answers"} <span aria-hidden="true">↗</span>
            </button>
          </div>
        </section>
      )}
      {!assessment && error && <p className="placement-error" role="alert">{error}</p>}
    </main>
  );
}
