import Link from "next/link";
import AuthStatus from "./components/auth-status";

const learningAreas = [
  {
    number: "01",
    title: "Writing",
    description: "Build clearer sentences and learn from structured feedback.",
    level: "Guided practice",
    symbol: "✎",
    href: "/writing",
  },
  {
    number: "02",
    title: "Reading",
    description: "Read short passages and check what you understood.",
    level: "Reading practice",
    symbol: "▤",
    href: "/reading",
  },
  {
    number: "03",
    title: "Vocabulary",
    description: "Keep useful words close with focused review sessions.",
    level: "Word review",
    symbol: "Aa",
    href: "/vocabulary",
  },
];

const weeklyPlan = [
  { day: "M", label: "Mon", active: false },
  { day: "T", label: "Tue", active: false },
  { day: "W", label: "Wed", active: true },
  { day: "T", label: "Thu", active: false },
  { day: "F", label: "Fri", active: false },
  { day: "S", label: "Sat", active: false },
  { day: "S", label: "Sun", active: false },
];

export default function HomePage() {
  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Main navigation">
        <a className="brand" href="#home" aria-label="English Learning home">
          <span className="brand-mark" aria-hidden="true">e.</span>
          <span className="brand-name">wordwise<span>LEARNING STUDIO</span></span>
        </a>

        <p className="nav-label">WORKSPACE</p>
        <nav className="main-nav">
          <a className="nav-link nav-link-active" href="#home" aria-current="page">
            <span aria-hidden="true">⌂</span> Overview
          </a>
          <Link className="nav-link" href="/placement"><span aria-hidden="true">✦</span> Level check</Link>
          <Link className="nav-link" href="/writing"><span aria-hidden="true">✎</span> Writing</Link>
          <Link className="nav-link" href="/reading"><span aria-hidden="true">▤</span> Reading</Link>
          <Link className="nav-link" href="/vocabulary"><span aria-hidden="true">Aa</span> Vocabulary</Link>
        </nav>

        <div className="sidebar-note">
          <span className="note-icon" aria-hidden="true">✦</span>
          <p className="note-title">Small steps add up.</p>
          <p className="note-copy">A little practice today makes tomorrow easier.</p>
        </div>
        <p className="sidebar-foot">EARLY ACCESS · PREVIEW</p>
      </aside>

      <section className="main-panel" id="home">
        <header className="topbar">
          <p><span className="topbar-dot" /> YOUR PERSONAL LEARNING SPACE</p>
          <div className="topbar-actions"><span className="preview-pill">UI PREVIEW</span><AuthStatus /></div>
        </header>

        <div className="content-wrap">
          <section className="welcome" aria-labelledby="page-title">
            <div>
              <p className="eyebrow">MAKE ROOM FOR PROGRESS</p>
              <h1 id="page-title">Your English journey,<br /><em>one day at a time.</em></h1>
              <p className="welcome-copy">
                A calmer place to practice, build confidence, and make English part of your routine.
              </p>
            </div>
            <div className="welcome-art" aria-hidden="true">
              <div className="art-sun" />
              <div className="art-book art-book-back" />
              <div className="art-book art-book-front"><span>abc</span><i>✦</i></div>
              <span className="art-spark spark-one">✳</span>
              <span className="art-spark spark-two">✦</span>
            </div>
          </section>

          <section className="stats-grid" aria-label="Learning overview">
            <article className="stat-card">
              <span className="stat-icon stat-icon-green" aria-hidden="true">◷</span>
              <p className="stat-label">Study time</p>
              <p className="stat-value">— <span>min</span></p>
              <p className="stat-hint">Your activity will appear here</p>
            </article>
            <article className="stat-card">
              <span className="stat-icon stat-icon-yellow" aria-hidden="true">✦</span>
              <p className="stat-label">Day streak</p>
              <p className="stat-value">— <span>days</span></p>
              <p className="stat-hint">One session at a time</p>
            </article>
            <article className="stat-card">
              <span className="stat-icon stat-icon-lilac" aria-hidden="true">↗</span>
              <p className="stat-label">Words reviewed</p>
              <p className="stat-value">— <span>words</span></p>
              <p className="stat-hint">Your vocabulary progress</p>
            </article>
          </section>

          <section className="section-block" aria-labelledby="areas-title">
            <div className="section-heading">
              <div>
                <p className="eyebrow">YOUR TOOLKIT</p>
                <h2 id="areas-title">Choose your next step</h2>
              </div>
              <span className="section-caption">3 learning areas</span>
            </div>
            <div className="area-grid">
              {learningAreas.map((area) => (
                <article className="area-card" id={area.title.toLowerCase()} key={area.number}>
                  <div className={`area-symbol area-symbol-${area.number}`} aria-hidden="true">{area.symbol}</div>
                  <p className="area-number">AREA {area.number}</p>
                  <h3>{area.title}</h3>
                  <p className="area-description">{area.description}</p>
                  <div className="area-card-bottom">
                    <span className="area-level">{area.level}</span>
                    <Link href={area.href} aria-label={`Open ${area.title}`} className="area-arrow">↗</Link>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="bottom-grid">
            <article className="week-card">
              <div className="section-heading compact-heading">
                <div>
                  <p className="eyebrow">BUILD A ROUTINE</p>
                  <h2>Your week</h2>
                </div>
                <span className="week-tag">A fresh start</span>
              </div>
              <p className="week-copy">Consistency matters more than a perfect streak. Pick a small goal and keep it kind.</p>
              <div className="week-days" aria-label="Illustrative weekly schedule">
                {weeklyPlan.map((day, index) => (
                  <div className="week-day" key={`${day.label}-${index}`}>
                    <span>{day.label}</span>
                    <span className={day.active ? "day-circle day-circle-active" : "day-circle"}>{day.active ? "•" : ""}</span>
                  </div>
                ))}
              </div>
              <p className="demo-note">Sample layout only — activity tracking is not connected yet.</p>
            </article>
            <article className="focus-card" id="coming-soon">
              <div className="focus-decoration" aria-hidden="true">✦</div>
              <p className="eyebrow">A GENTLE REMINDER</p>
              <h2>Progress, not<br /><em>perfection.</em></h2>
              <p>Ten thoughtful minutes can be more useful than an hour of distracted studying.</p>
              <span className="focus-label">YOUR PACE IS THE RIGHT PACE</span>
              <Link className="placement-cta" href="/placement">Take the level check <span aria-hidden="true">↗</span></Link>
            </article>
          </section>
          <footer className="page-footer">
            <span>WORDWISE · ENGLISH LEARNING STUDIO</span>
            <span>Built for steady progress <span aria-hidden="true">✦</span></span>
          </footer>
        </div>
      </section>
    </main>
  );
}
