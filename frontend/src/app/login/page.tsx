"use client";

import { useState } from "react";
import type { FormEvent } from "react";

async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", {
    credentials: "same-origin",
    cache: "no-store",
  });
  if (!response.ok) throw new Error("The secure sign-in service is unavailable.");
  const data: { csrfToken?: string } = await response.json();
  if (!data.csrfToken) throw new Error("The secure sign-in service is unavailable.");
  return data.csrfToken;
}

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch("/api/v1/auth/login/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ username: username.trim(), password }),
      });
      const data: { detail?: string } = await response.json().catch(() => ({}));
      if (!response.ok) {
        setError(data.detail ?? "Sign-in failed. Please try again.");
        return;
      }
      window.location.assign("/");
    } catch {
      setError("We couldn't reach the sign-in service. Check that the backend is running.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-shell">
      <a className="login-back" href="/" aria-label="Back to dashboard">← Back to dashboard</a>
      <section className="login-card" aria-labelledby="login-title">
        <a className="brand login-brand" href="/">
          <span className="brand-mark" aria-hidden="true">e.</span>
          <span className="brand-name">wordwise<span>LEARNING STUDIO</span></span>
        </a>
        <p className="eyebrow login-eyebrow">WELCOME BACK</p>
        <h1 id="login-title">Make today<br /><em>count.</em></h1>
        <p className="login-description">Sign in to continue your English learning journey.</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
            maxLength={150}
          />
          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          {error && <p className="login-error" role="alert">{error}</p>}
          <button className="login-submit" type="submit" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="login-footnote">Use an account created in the Django admin. Public registration is not available yet.</p>
      </section>
    </main>
  );
}
