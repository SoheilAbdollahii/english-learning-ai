"use client";

import Link from "next/link";
import { useState } from "react";
import type { FormEvent } from "react";
import { useLocale } from "../../components/locale-provider";

async function csrf(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("The secure service is unavailable.");
  return data.csrfToken;
}

export default function ResendVerificationPage() {
  const { t } = useLocale();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const token = await csrf();
      const response = await fetch("/api/v1/auth/verify-email/resend/", {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify({ email }),
      });
      const data = await response.json().catch(() => ({})) as { detail?: string };
      if (!response.ok) throw new Error(data.detail ?? "Please try again later.");
      setMessage(data.detail ?? "If an account matches that email address and needs verification, instructions will be sent.");
    } catch (cause) {
      setMessage(cause instanceof Error ? cause.message : "The request could not be completed.");
    } finally { setBusy(false); }
  }

  return (
    <main className="login-shell">
      <Link className="login-back" href="/login">{t("Back to sign in")}</Link>
      <section className="login-card" aria-labelledby="resend-title">
        <p className="eyebrow login-eyebrow">EMAIL VERIFICATION</p>
        <h1 id="resend-title">Resend verification email</h1>
        <p className="login-description">Enter the email address used to create your account.</p>
        <form className="login-form" onSubmit={submit}>
          <label htmlFor="resend-email">Email address</label>
          <input id="resend-email" type="email" dir="ltr" autoComplete="email" value={email} onChange={event => setEmail(event.target.value)} required maxLength={254} />
          {message && <p role="status" className="login-description">{message}</p>}
          <button className="login-submit" type="submit" disabled={busy}>{busy ? "Sending…" : "Resend verification email"}</button>
        </form>
      </section>
    </main>
  );
}
