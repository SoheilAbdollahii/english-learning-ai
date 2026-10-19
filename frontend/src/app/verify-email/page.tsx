"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useLocale } from "../components/locale-provider";

async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
  const data = await response.json().catch(() => ({})) as { csrfToken?: string };
  if (!response.ok || !data.csrfToken) throw new Error("The verification service is unavailable.");
  return data.csrfToken;
}

export default function VerifyEmailPage() {
  const { t } = useLocale();
  const [message, setMessage] = useState("Verifying your email address…");
  const [busy, setBusy] = useState(true);

  useEffect(() => {
    let active = true;
    async function verify() {
      try {
        const params = new URLSearchParams(window.location.search);
        const uid = params.get("uid");
        const token = params.get("token");
        if (!uid || !token) throw new Error("This verification link is invalid or incomplete.");
        const csrfToken = await getCsrfToken();
        const response = await fetch("/api/v1/auth/verify-email/", {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
          body: JSON.stringify({ uid, token }),
        });
        const data = await response.json().catch(() => ({})) as { detail?: string; status?: string };
        if (!response.ok) throw new Error(data.detail ?? "This verification link is invalid or has expired.");
        if (active) setMessage("Your email is verified. You can now sign in.");
      } catch (cause) {
        if (active) setMessage(cause instanceof Error ? cause.message : "Email verification failed.");
      } finally {
        if (active) setBusy(false);
      }
    }
    void verify();
    return () => { active = false; };
  }, []);

  return (
    <main className="login-shell">
      <Link className="login-back" href="/">{t("Back to dashboard")}</Link>
      <section className="login-card" aria-labelledby="verify-title">
        <p className="eyebrow login-eyebrow">EMAIL VERIFICATION</p>
        <h1 id="verify-title">Verify your email</h1>
        <p className="login-description" role={busy ? "status" : "status"}>{message}</p>
        {!busy && <p className="login-footnote"><Link href="/login">{t("Continue to sign in")}</Link> · <Link href="/verify-email/resend">Resend verification email</Link></p>}
      </section>
    </main>
  );
}
