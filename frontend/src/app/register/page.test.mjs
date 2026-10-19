import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("registration form uses CSRF-protected API and confirms password", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /\/api\/v1\/auth\/register\//);
  assert.match(page, /\/api\/v1\/auth\/csrf\//);
  assert.match(page, /X-CSRFToken/);
  assert.match(page, /password !== confirmPassword/);
  assert.match(page, /minLength=\{12\}/);
  assert.match(page, /id="register-email"/);
  assert.match(page, /email: email.trim\(\)/);
  assert.match(page, /verify your email address before signing in/i);
});
