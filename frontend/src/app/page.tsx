export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">YOUR ENGLISH LEARNING SPACE</p>
        <h1 id="page-title">Build your English, one step at a time.</h1>
        <p className="intro">
          Practice writing, explore reading, and grow your vocabulary.
          Your personal learning dashboard is being built.
        </p>
        <div className="feature-grid" aria-label="Learning areas">
          <article className="feature-card">
            <span className="feature-number">01</span>
            <h2>Writing</h2>
            <p>Get clear, educational feedback on your English.</p>
            <span className="status">Planned</span>
          </article>
          <article className="feature-card">
            <span className="feature-number">02</span>
            <h2>Reading</h2>
            <p>Read levelled passages and check your understanding.</p>
            <span className="status">Planned</span>
          </article>
          <article className="feature-card">
            <span className="feature-number">03</span>
            <h2>Vocabulary</h2>
            <p>Review words and track learning over time.</p>
            <span className="status">Planned</span>
          </article>
        </div>
        <p className="footnote">
          This is an early project scaffold. Learning features are not yet implemented.
        </p>
      </section>
    </main>
  );
}
