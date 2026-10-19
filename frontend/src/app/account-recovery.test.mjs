import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("login links to password recovery and verification resend", async () => {
  const page = await readFile(new URL("./login/page.tsx", import.meta.url), "utf8");
  assert.match(page, /href="\/password-reset"/);
  assert.match(page, /href="\/verify-email\/resend"/);
});

test("password reset request uses CSRF-protected generic email endpoint", async () => {
  const page = await readFile(new URL("./password-reset/page.tsx", import.meta.url), "utf8");
  assert.match(page, /\/api\/v1\/auth\/password-reset\//);
  assert.match(page, /\/api\/v1\/auth\/csrf\//);
  assert.match(page, /X-CSRFToken/);
  assert.match(page, /type="email"/);
});

test("password reset confirmation validates matching passwords and submits token", async () => {
  const page = await readFile(new URL("./password-reset/confirm/page.tsx", import.meta.url), "utf8");
  assert.match(page, /\/api\/v1\/auth\/password-reset\/confirm\//);
  assert.match(page, /password !== confirmPassword/);
  assert.match(page, /uid, token, password/);
  assert.match(page, /minLength=\{12\}/);
});

test("verification page and resend page use their protected endpoints", async () => {
  const verify = await readFile(new URL("./verify-email/page.tsx", import.meta.url), "utf8");
  const resend = await readFile(new URL("./verify-email/resend/page.tsx", import.meta.url), "utf8");
  assert.match(verify, /\/api\/v1\/auth\/verify-email\//);
  assert.match(verify, /X-CSRFToken/);
  assert.match(verify, /Press the button below to confirm/);
  assert.match(verify, /onSubmit={submit}/);
  assert.match(resend, /\/api\/v1\/auth\/verify-email\/resend\//);
  assert.match(resend, /X-CSRFToken/);
});
