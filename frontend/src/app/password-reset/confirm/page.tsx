"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useLocale } from "../../components/locale-provider";

async function csrf(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("The secure service is unavailable.");
  return data.csrfToken;
}

export default function PasswordResetConfirmPage() {
  const { t } = useLocale();
  const [uid, setUid] = useState("");
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [complete, setComplete] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setUid(params.get("uid") ?? "");
    setToken(params.get("token") ?? "");
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    if (!uid || !token) { setMessage("This password reset link is invalid or incomplete."); return; }
    if (password !== confirmPassword) { setMessage("The passwords do not match."); return; }
    setBusy(true);
    try {
      const csrfToken = await csrf();
      const response = await fetch("/api/v1/auth/password-reset/confirm/", {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ uid, token, password }),
      });
      const data = await response.json().catch(() => ({})) as { detail?: string; password?: string[]; status?: string };
      if (!response.ok) throw new Error(data.password?.[0] ?? data.detail ?? "The password could not be changed.");
      setComplete(true);
      setPassword("");
      setConfirmPassword("");
    } catch (cause) {
      setMessage(cause instanceof Error ? cause.message : "The password could not be changed.");
    } finally { setBusy(false); }
  }

  return (
    <main className="login-shell">
      <Link className="login-back" href="/login">{t("Back to sign in")}</Link>
      <section className="login-card" aria-labelledby="reset-confirm-title">
        <p className="eyebrow login-eyebrow">ACCOUNT RECOVERY</p>
        <h1 id="reset-confirm-title">Choose a new password</h1>
        {complete ? <><p className="login-description" role="status">Your password has been changed. Sign in with your new password.</p><Link className="login-submit register-login-link" href="/login">{t("Continue to sign in")}</Link></> : (
          <form className="login-form" onSubmit={submit}>
            <label htmlFor="new-password">New password <span>(at least 12 characters)</span></label>
            <input id="new-password" type="password" dir="ltr" autoComplete="new-password" value={password} onChange={event => setPassword(event.target.value)} required minLength={12} />
            <label htmlFor="confirm-new-password">Confirm new password</label>
            <input id="confirm-new-password" type="password" dir="ltr" autoComplete="new-password" value={confirmPassword} onChange={event => setConfirmPassword(event.target.value)} required minLength={12} />
            {message && <p className="login-error" role="alert">{message}</p>}
            <button className="login-submit" type="submit" disabled={busy || !uid || !token}>{busy ? "Saving…" : "Set new password"}</button>
          </form>
        )}
      </section>
    </main>
  );
}
