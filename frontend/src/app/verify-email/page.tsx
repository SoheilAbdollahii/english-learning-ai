"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useLocale } from "../components/locale-provider";

async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("The verification service is unavailable.");
  return data.csrfToken;
}

export default function VerifyEmailPage() {
  const { t } = useLocale();
  const [uid, setUid] = useState("");
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [complete, setComplete] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setUid(params.get("uid") ?? "");
    setToken(params.get("token") ?? "");
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    if (!uid || !token) {
      setMessage("This verification link is invalid or incomplete.");
      return;
    }
    setBusy(true);
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch("/api/v1/auth/verify-email/", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ uid, token }),
      });
      const data = await response.json().catch(() => ({})) as { detail?: string; status?: string };
      if (!response.ok) throw new Error(data.detail ?? "This verification link is invalid or has expired.");
      setComplete(true);
      setMessage("Your email is verified. You can now sign in.");
    } catch (cause) {
      setMessage(cause instanceof Error ? cause.message : "Email verification failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-shell">
      <Link className="login-back" href="/">{t("Back to dashboard")}</Link>
      <section className="login-card" aria-labelledby="verify-title">
        <p className="eyebrow login-eyebrow">EMAIL VERIFICATION</p>
        <h1 id="verify-title">Verify your email</h1>
        {!complete ? (
          <form className="login-form" onSubmit={submit}>
            <p className="login-description">Press the button below to confirm your email address and activate your account.</p>
            {message && <p className="login-error" role="alert">{message}</p>}
            <button className="login-submit" type="submit" disabled={busy || !uid || !token}>{busy ? "Verifying…" : "Verify email address"}</button>
            {!uid || !token ? <p className="login-footnote">The link is missing its verification details. You can request another email.</p> : null}
          </form>
        ) : (
          <p className="login-description" role="status">{message}</p>
        )}
        {!busy && <p className="login-footnote"><Link href="/login">{t("Continue to sign in")}</Link> · <Link href="/verify-email/resend">Resend verification email</Link></p>}
      </section>
    </main>
  );
}
