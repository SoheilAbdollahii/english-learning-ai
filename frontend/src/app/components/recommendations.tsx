"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Recommendation = {
  code: string;
  title: string;
  reason: string;
  href: string;
  action_label: string;
  priority: number;
};

export default function Recommendations() {
  const [items, setItems] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const response = await fetch("/api/v1/progress/recommendations/", {
          credentials: "same-origin",
          cache: "no-store",
        });
        if (!response.ok) return;
        const data = await response.json() as { recommendations: Recommendation[] };
        if (active) setItems(data.recommendations);
      } catch {
        // Recommendations are optional; keep the rest of the dashboard available.
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => { active = false; };
  }, []);

  if (loading || items.length === 0) return null;

  return (
    <section className="recommendations-section" aria-labelledby="recommendations-title">
      <div className="section-heading">
        <div><p className="eyebrow">A SMALL NEXT STEP</p><h2 id="recommendations-title">Recommended for you</h2></div>
        <span className="section-caption">Based on your saved activity</span>
      </div>
      <div className="recommendations-grid">
        {items.map((item) => (
          <article className="recommendation-card" key={item.code}>
            <span className="recommendation-priority">NEXT STEP {item.priority}</span>
            <h3>{item.title}</h3>
            <p>{item.reason}</p>
            <Link href={item.href}>{item.action_label} <span aria-hidden="true">↗</span></Link>
          </article>
        ))}
      </div>
    </section>
  );
}
