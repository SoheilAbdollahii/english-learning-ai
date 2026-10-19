"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type RecentActivity = { type: string; label: string; created_at: string };
type ProgressSummaryData = {
  sessions_completed: number;
  words_reviewed: number;
  reading_attempts: number;
  writing_submissions: number;
  placement_attempts: number;
  due_words: number;
  mastered_words: number;
  current_streak_days: number;
  recent_activity: RecentActivity[];
};

export default function ProgressOverview() {
  const [summary, setSummary] = useState<ProgressSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [needsSignIn, setNeedsSignIn] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let active = true;
    async function loadSummary() {
      try {
        const response = await fetch("/api/v1/progress/summary/", {
          credentials: "same-origin",
          cache: "no-store",
        });
        if (response.status === 401 || response.status === 403) {
          if (active) setNeedsSignIn(true);
          return;
        }
        if (!response.ok) throw new Error("Progress unavailable");
        const data = await response.json() as ProgressSummaryData;
        if (active) setSummary(data);
      } catch {
        if (active) setFailed(true);
      } finally {
        if (active) setLoading(false);
      }
    }
    void loadSummary();
    return () => { active = false; };
  }, []);

  const value = (number: number | undefined) => loading ? "—" : String(number ?? 0);

  return (
    <div className="progress-overview" aria-busy={loading}>
      <section className="stats-grid" aria-label="Learning overview">
        <article className="stat-card">
          <span className="stat-icon stat-icon-green" aria-hidden="true">◷</span>
          <p className="stat-label">Learning sessions</p>
          <p className="stat-value">{value(summary?.sessions_completed)} <span>sessions</span></p>
          <p className="stat-hint">Completed activities saved to your account</p>
        </article>
        <article className="stat-card">
          <span className="stat-icon stat-icon-yellow" aria-hidden="true">✦</span>
          <p className="stat-label">Day streak</p>
          <p className="stat-value">{value(summary?.current_streak_days)} <span>days</span></p>
          <p className="stat-hint">Consecutive days with recorded learning</p>
        </article>
        <article className="stat-card">
          <span className="stat-icon stat-icon-lilac" aria-hidden="true">Aa</span>
          <p className="stat-label">Words reviewed</p>
          <p className="stat-value">{value(summary?.words_reviewed)} <span>reviews</span></p>
          <p className="stat-hint">Saved vocabulary review outcomes</p>
        </article>
      </section>

      {needsSignIn ? (
        <p className="progress-note">Sign in to see your personal progress. <Link href="/login">Sign in</Link></p>
      ) : failed ? (
        <p className="progress-note">Progress is temporarily unavailable. Your learning pages are still available.</p>
      ) : summary ? (
        <>
          <section className="progress-details" aria-label="Learning activity totals">
            <article><span>Reading attempts</span><strong>{summary.reading_attempts}</strong></article>
            <article><span>Writing submissions</span><strong>{summary.writing_submissions}</strong></article>
            <article><span>Level checks</span><strong>{summary.placement_attempts}</strong></article>
            <article><span>Words due</span><strong>{summary.due_words}</strong></article>
            <article><span>Mastered words</span><strong>{summary.mastered_words}</strong></article>
          </section>
          <section className="progress-recent" aria-labelledby="recent-activity-title">
            <div className="section-heading">
              <div><p className="eyebrow">YOUR LEARNING TRAIL</p><h2 id="recent-activity-title">Recent activity</h2></div>
              <span className="section-caption">Latest saved sessions</span>
            </div>
            {summary.recent_activity.length === 0 ? (
              <p className="writing-empty">Your activity will appear after your first saved learning session.</p>
            ) : (
              <ul className="progress-activity-list">
                {summary.recent_activity.map((item, index) => (
                  <li key={`${item.type}-${item.created_at}-${index}`}>
                    <span className={`progress-activity-dot progress-activity-${item.type}`} aria-hidden="true" />
                    <strong>{item.label}</strong>
                    <time dateTime={item.created_at}>{new Date(item.created_at).toLocaleString()}</time>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      ) : !loading && !needsSignIn && !failed ? (
        <p className="progress-note">No progress has been recorded yet.</p>
      ) : null}
    </div>
  );
}
