"use client";

import Link from "next/link";
import { useLocale } from "../components/locale-provider";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type VocabularyCard = {
  id: number;
  word: string;
  definition: string;
  example_sentence: string;
  translation: string;
  status: "new" | "learning" | "review" | "mastered";
  repetitions: number;
  interval_days: number;
  ease_factor: string;
  due_at: string;
  last_reviewed_at: string | null;
};

type CardDraft = {
  word: string;
  definition: string;
  example_sentence: string;
  translation: string;
};

async function csrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("Your secure session could not be started. Please sign in again.");
  return data.csrfToken;
}

export default function VocabularyPage() {
  const { t } = useLocale();
  const [cards, setCards] = useState<VocabularyCard[]>([]);
  const [draft, setDraft] = useState<CardDraft>({ word: "", definition: "", example_sentence: "", translation: "" });
  const [revealed, setRevealed] = useState<Record<number, boolean>>({});
  const [dueOnly, setDueOnly] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [reviewingId, setReviewingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [needsSignIn, setNeedsSignIn] = useState(false);

  const loadCards = useCallback(async () => {
    setError("");
    try {
      const response = await fetch("/api/v1/vocabulary/cards/", { credentials: "same-origin", cache: "no-store" });
      if (response.status === 401 || response.status === 403) {
        setNeedsSignIn(true);
        setCards([]);
        return;
      }
      if (!response.ok) throw new Error("We couldn't load your vocabulary cards.");
      const data = await response.json() as VocabularyCard[];
      setCards(data);
      setNeedsSignIn(false);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't load your vocabulary cards.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void loadCards(); }, [loadCards]);

  const dueCards = useMemo(() => cards.filter((card) => new Date(card.due_at).getTime() <= Date.now()), [cards]);
  const visibleCards = dueOnly ? dueCards : cards;

  async function addCard(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setNotice("");
    setSaving(true);
    try {
      const token = await csrfToken();
      const response = await fetch("/api/v1/vocabulary/cards/", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify(draft),
      });
      const data = await response.json().catch(() => ({})) as VocabularyCard & { detail?: string; word?: string[] };
      if (response.status === 401 || response.status === 403) {
        setNeedsSignIn(true);
        throw new Error("Sign in to save your vocabulary.");
      }
      if (!response.ok) throw new Error(data.word?.[0] ?? data.detail ?? "We couldn't save this word.");
      setCards((previous) => [data, ...previous]);
      setDraft({ word: "", definition: "", example_sentence: "", translation: "" });
      setDueOnly(false);
      setRevealed((previous) => ({ ...previous, [data.id]: true }));
      setNotice(`“${data.word}” was added to your review list.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't save this word.");
    } finally {
      setSaving(false);
    }
  }

  async function reviewCard(card: VocabularyCard, quality: number) {
    setError("");
    setNotice("");
    setReviewingId(card.id);
    try {
      const token = await csrfToken();
      const response = await fetch(`/api/v1/vocabulary/cards/${card.id}/review/`, {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify({ quality }),
      });
      const data = await response.json().catch(() => ({})) as VocabularyCard & { detail?: string };
      if (response.status === 401 || response.status === 403) {
        setNeedsSignIn(true);
        throw new Error("Sign in to save your review.");
      }
      if (!response.ok) throw new Error(data.detail ?? "We couldn't save your review.");
      setCards((previous) => previous.map((item) => item.id === data.id ? data : item));
      setRevealed((previous) => ({ ...previous, [data.id]: false }));
      setNotice(`Review saved. Next review: ${new Date(data.due_at).toLocaleDateString()}.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't save your review.");
    } finally {
      setReviewingId(null);
    }
  }

  return (
    <main className="writing-shell vocabulary-shell">
      <div className="writing-topline">
        <Link href="/" className="placement-back">← {t("Back to dashboard")}</Link>
        <span className="placement-kicker">{t("WORDWISE · VOCABULARY")}</span>
      </div>

      <section className="writing-intro" aria-labelledby="vocabulary-title">
        <p className="placement-eyebrow">{t("REMEMBER MORE, WITH LESS CRAMMING")}</p>
        <h1 id="vocabulary-title">{t("Words that stay with you.")}</h1>
        <p>{t("Build your own word collection and review each card when it is due. Your next review date changes only after you record how well you remembered the word.")}</p>
      </section>

      <section className="vocabulary-summary" aria-label="Vocabulary overview">
        <article><span>{t("Due now")}</span><strong>{dueCards.length}</strong><small>{t("Ready for a review")}</small></article>
        <article><span>{t("In your collection")}</span><strong>{cards.length}</strong><small>{t("Words saved to your account")}</small></article>
        <article><span>{t("Mastered")}</span><strong>{cards.filter((card) => card.status === "mastered").length}</strong><small>{t("Based on review history")}</small></article>
      </section>

      <section className="writing-composer vocabulary-add" aria-labelledby="vocabulary-add-title">
        <div className="writing-composer-heading">
          <div><p className="placement-eyebrow">{t("GROW YOUR WORD BANK")}</p><h2 id="vocabulary-add-title">{t("Add a word")}</h2></div>
        </div>
        <form onSubmit={addCard} className="vocabulary-form">
          <label>{t("Word")}<input required minLength={1} maxLength={100} value={draft.word} onChange={(event) => setDraft({ ...draft, word: event.target.value })} placeholder="e.g. resilient" /></label>
          <label>{t("Meaning in English")}<input required maxLength={500} value={draft.definition} onChange={(event) => setDraft({ ...draft, definition: event.target.value })} placeholder="Able to recover after difficulty" /></label>
          <label>{t("Example sentence")} <span>(optional)</span><input maxLength={500} value={draft.example_sentence} onChange={(event) => setDraft({ ...draft, example_sentence: event.target.value })} placeholder="She stayed resilient during the challenge." /></label>
          <label>{t("Translation")} <span>(optional)</span><input maxLength={150} value={draft.translation} onChange={(event) => setDraft({ ...draft, translation: event.target.value })} placeholder="ترجمه" /></label>
          <button className="placement-submit" type="submit" disabled={saving || !draft.word.trim() || !draft.definition.trim()}>{saving ? "Saving word…" : t("Add to vocabulary")} <span aria-hidden="true">↗</span></button>
        </form>
      </section>

      {(error || notice) && <p className={error ? "placement-error" : "vocabulary-notice"} role={error ? "alert" : "status"}>{error || notice} {needsSignIn && <Link href="/login">Sign in</Link>}</p>}

      <section className="writing-history vocabulary-review" aria-labelledby="review-title">
        <div className="writing-history-heading">
          <div><p className="placement-eyebrow">{t("YOUR STUDY SESSION")}</p><h2 id="review-title">{t("Review your words")}</h2></div>
          <button type="button" className="writing-view-button" onClick={() => setDueOnly((previous) => !previous)}>{dueOnly ? t("Show all words") : t("Show due only")}</button>
        </div>
        {loading ? <p className="writing-empty" role="status">Loading your vocabulary…</p> : needsSignIn ? (
          <p className="writing-empty">Your personal word collection is private. <Link href="/login">Sign in</Link> to continue.</p>
        ) : visibleCards.length === 0 ? (
          <p className="writing-empty">{dueOnly ? "You're all caught up. Add a word or show your full collection." : "Your word collection is empty. Add your first word above."}</p>
        ) : (
          <div className="vocabulary-card-list">
            {visibleCards.map((card) => (
              <article className="vocabulary-card" key={card.id}>
                <div className="vocabulary-card-head">
                  <div><span className={`vocabulary-status vocabulary-status-${card.status}`}>{card.status}</span><h3>{card.word}</h3></div>
                  <span className="vocabulary-due">{new Date(card.due_at).getTime() <= Date.now() ? "Due now" : `Due ${new Date(card.due_at).toLocaleDateString()}`}</span>
                </div>
                {revealed[card.id] ? (
                  <div className="vocabulary-definition">
                    <p>{card.definition}</p>
                    {card.translation && <p className="vocabulary-translation">{card.translation}</p>}
                    {card.example_sentence && <blockquote>{card.example_sentence}</blockquote>}
                  </div>
                ) : <button type="button" className="vocabulary-reveal" onClick={() => setRevealed((previous) => ({ ...previous, [card.id]: true }))}>Reveal meaning <span aria-hidden="true">↓</span></button>}
                {revealed[card.id] && (
                  <div className="vocabulary-grades" aria-label={`How well did you remember ${card.word}?`}>
                    <button type="button" disabled={reviewingId === card.id} onClick={() => void reviewCard(card, 1)}>Again</button>
                    <button type="button" disabled={reviewingId === card.id} onClick={() => void reviewCard(card, 3)}>Hard</button>
                    <button type="button" disabled={reviewingId === card.id} onClick={() => void reviewCard(card, 4)}>Good</button>
                    <button type="button" disabled={reviewingId === card.id} onClick={() => void reviewCard(card, 5)}>Easy</button>
                  </div>
                )}
                <p className="vocabulary-card-meta">Reviewed {card.repetitions} {card.repetitions === 1 ? "time" : "times"} · next interval {card.interval_days} {card.interval_days === 1 ? "day" : "days"}</p>
              </article>
            ))}
          </div>
        )}
      </section>
      <p className="vocabulary-footnote">Scheduling uses a deterministic SM-2-inspired rule set. It is a learning aid, not a guarantee of long-term retention.</p>
    </main>
  );
}
