"use client";

import { useEffect, useState } from "react";

type CurrentUser = { username: string };

async function getCsrfToken(): Promise<string> {
  const response = await fetch("/api/v1/auth/csrf/", {
    credentials: "same-origin",
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Could not start a secure session.");
  const data: { csrfToken?: string } = await response.json();
  if (!data.csrfToken) throw new Error("Could not start a secure session.");
  return data.csrfToken;
}

export default function AuthStatus() {
  const [username, setUsername] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    fetch("/api/v1/me/", { credentials: "same-origin", cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) return null;
        return (await response.json()) as CurrentUser;
      })
      .then((user) => {
        if (active) setUsername(user?.username ?? null);
      })
      .catch(() => {
        if (active) setUsername(null);
      })
      .finally(() => {
        if (active) setReady(true);
      });
    return () => {
      active = false;
    };
  }, []);

  async function signOut() {
    setBusy(true);
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch("/api/v1/auth/logout/", {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": csrfToken },
      });
      if (!response.ok) throw new Error("Sign out failed. Please try again.");
      setUsername(null);
    } catch {
      window.alert("We couldn't sign you out. Please check your connection and try again.");
    } finally {
      setBusy(false);
    }
  }

  if (!ready) return <span className="auth-status-placeholder" aria-label="Checking sign-in status" />;
  if (!username) return <a className="auth-link" href="/login">Sign in</a>;

  return (
    <div className="auth-status">
      <span className="auth-greeting">Hi, {username}</span>
      <button className="auth-button" type="button" onClick={signOut} disabled={busy}>
        {busy ? "Signing out…" : "Sign out"}
      </button>
    </div>
  );
}
