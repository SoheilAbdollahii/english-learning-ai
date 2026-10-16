import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("dashboard labels the learning areas and states current scope", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /Writing/);
  assert.match(page, /Reading/);
  assert.match(page, /Vocabulary/);
  assert.match(page, /UI PREVIEW/);
  assert.match(page, /activity tracking is not connected yet/);
});

test("login page uses CSRF-protected session auth and accessible form fields", async () => {
  const login = await readFile(new URL("./login/page.tsx", import.meta.url), "utf8");
  assert.match(login, /\/api\/v1\/auth\/csrf\//);
  assert.match(login, /\/api\/v1\/auth\/login\//);
  assert.match(login, /X-CSRFToken/);
  assert.match(login, /autoComplete="username"/);
  assert.match(login, /autoComplete="current-password"/);
  assert.match(login, /role="alert"/);
  assert.match(login, /Public registration is not available yet/);
});

test("dashboard header exposes session status controls", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  const auth = await readFile(new URL("./components/auth-status.tsx", import.meta.url), "utf8");
  assert.match(page, /AuthStatus/);
  assert.match(auth, /\/api\/v1\/me\//);
  assert.match(auth, /\/api\/v1\/auth\/logout\//);
  assert.match(auth, /X-CSRFToken/);
});
