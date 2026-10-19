"use client";

import Link from "next/link";
import { useLocale } from "../components/locale-provider";
import { useState } from "react";
import type { FormEvent } from "react";

async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("The secure registration service is unavailable.");
  return data.csrfToken;
}

export default function RegisterPage() {
  const { t } = useLocale();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [createdUsername, setCreatedUsername] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }
    setBusy(true);
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch("/api/v1/auth/register/", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ username: username.trim(), password }),
      });
      const data = await response.json().catch(() => ({})) as {
        username?: string | string[];
        password?: string[];
        detail?: string;
        status?: string;
      };
      if (!response.ok) {
        const fieldError = Array.isArray(data.password) ? data.password[0] : Array.isArray(data.username) ? data.username[0] : undefined;
        throw new Error(fieldError ?? data.detail ?? "We couldn't create your account.");
      }
      setCreatedUsername(typeof data.username === "string" ? data.username : username.trim().toLowerCase());
      setPassword("");
      setConfirmPassword("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "We couldn't reach the registration service.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-shell">
      <Link className="login-back" href="/" aria-label="Back to dashboard">← {t("Back to dashboard")}</Link>
      <section className="login-card" aria-labelledby="register-title">
        <Link className="brand login-brand" href="/">
          <span className="brand-mark" aria-hidden="true">e.</span>
          <span className="brand-name">wordwise<span>LEARNING STUDIO</span></span>
        </Link>
        {createdUsername ? (
          <div className="register-success" role="status">
            <p className="eyebrow login-eyebrow">ACCOUNT CREATED</p>
            <h1 id="register-title">{t("Welcome")}, <em>{createdUsername}.</em></h1>
            <p className="login-description">{t("Your account is ready. Sign in to start saving your English practice.")}</p>
            <Link className="login-submit register-login-link" href="/login">{t("Continue to sign in")}</Link>
          </div>
        ) : (
          <>
            <p className="eyebrow login-eyebrow">{t("A FRESH START")}</p>
            <h1 id="register-title">{t("Make space to grow.")}</h1>
            <p className="login-description">{t("Create your personal learning space. Use a strong password you do not use elsewhere.")}</p>
            <form className="login-form" onSubmit={handleSubmit}>
              <label htmlFor="register-username">{t("Username")}</label>
              <input id="register-username" name="username" autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} required maxLength={150} minLength={1} />
              <label htmlFor="register-password">{t("Password")} <span>({t("at least 12 characters")})</span></label>
              <input id="register-password" name="password" type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} required minLength={12} />
              <label htmlFor="register-confirm-password">{t("Confirm password")}</label>
              <input id="register-confirm-password" name="confirmPassword" type="password" autoComplete="new-password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required minLength={12} />
              {error && <p className="login-error" role="alert">{error}</p>}
              <button className="login-submit" type="submit" disabled={busy}>{busy ? "Creating account…" : t("Create account")}</button>
            </form>
            <p className="login-footnote">Registration is rate-limited. {t("Email verification and account recovery are not available yet.")}</p>
            <p className="register-switch">{t("Already have an account?")} <Link href="/login">Sign in</Link></p>
          </>
        )}
      </section>
    </main>
  );
}
