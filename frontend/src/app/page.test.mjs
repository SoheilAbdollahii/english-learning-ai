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
  assert.match(login, /href="\/register"/);
});

test("dashboard header exposes session status controls", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  const auth = await readFile(new URL("./components/auth-status.tsx", import.meta.url), "utf8");
  assert.match(page, /AuthStatus/);
  assert.match(auth, /\/api\/v1\/me\//);
  assert.match(auth, /\/api\/v1\/auth\/logout\//);
  assert.match(auth, /X-CSRFToken/);
});

test("placement flow loads public questions and submits answers with CSRF", async () => {
  const placement = await readFile(new URL("./placement/page.tsx", import.meta.url), "utf8");
  assert.match(placement, /\/api\/v1\/placement\/assessments\//);
  assert.match(placement, /\/api\/v1\/placement\/attempts\//);
  assert.match(placement, /\/api\/v1\/auth\/csrf\//);
  assert.match(placement, /X-CSRFToken/);
  assert.match(placement, /Please answer every question/);
  assert.match(placement, /estimated_level/);
  assert.match(placement, /not a certified or adaptive CEFR assessment/);
  assert.doesNotMatch(placement, /correct_option/);
});

test("dashboard links to the placement assessment", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /href="\/placement"/);
  assert.match(page, /Take the level check/);
});


test("locale switcher exposes accessible language controls and active selection", async () => {
  const locale = await readFile(new URL("./components/locale-provider.tsx", import.meta.url), "utf8");
  assert.match(locale, /role="group" aria-label={t\("Language and layout"\)}/);
  assert.match(locale, /aria-pressed={locale === "en"}/);
  assert.match(locale, /aria-pressed={locale === "fa"}/);
  assert.match(locale, /disabled={!ready}/);
  assert.match(locale, /role="status"/);
});

test("locale changes update document language and text direction", async () => {
  const locale = await readFile(new URL("./components/locale-provider.tsx", import.meta.url), "utf8");
  assert.match(locale, /document\.documentElement\.dir = locale === "fa" \? "rtl" : "ltr"/);
  assert.match(locale, /document\.documentElement\.lang = locale/);
  assert.match(locale, /window\.localStorage\.setItem\("wordwise-locale", nextLocale\)/);
  assert.match(locale, /window\.localStorage\.getItem\("wordwise-locale"\)/);
});

test("authenticated locale preference writes use same-origin CSRF-protected profile API", async () => {
  const locale = await readFile(new URL("./components/locale-provider.tsx", import.meta.url), "utf8");
  assert.match(locale, /fetch\("\/api\/v1\/auth\/csrf\//);
  assert.match(locale, /fetch\("\/api\/v1\/me\/", \{/);
  assert.match(locale, /method: "PATCH"/);
  assert.match(locale, /"X-CSRFToken": token/);
  assert.match(locale, /credentials: "same-origin"/);
  assert.match(locale, /Preference could not be saved\. Try again\./);
});

test("dashboard primary content and navigation have named landmarks", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /<main className="app-shell">/);
  assert.match(page, /<aside className="sidebar" aria-label="Main navigation">/);
  assert.match(page, /<nav className="main-nav">/);
  assert.match(page, /aria-labelledby="page-title"/);
  assert.match(page, /aria-current="page"/);
});
