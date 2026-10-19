import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("writing page submits through the CSRF-protected API and shows demo limitations", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /\/api\/v1\/writing\/submissions\//);
  assert.match(page, /\/api\/v1\/auth\/csrf\//);
  assert.match(page, /X-CSRFToken/);
  assert.match(page, /Sign in/);
  assert.match(page, /Demo mode limitations/);
  assert.match(page, /does not evaluate grammar/);
  assert.match(page, /maxLength=\{5000\}/);
  assert.match(page, /\/api\/v1\/usage\//);
  assert.match(page, /Rolling 24-hour allowance/);
});

test("writing page shows persisted history and accessible feedback", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /writing-history-title/);
  assert.match(page, /role="alert"/);
  assert.match(page, /setHistory/);
  assert.match(page, /View/);
});


test("writing result renders corrected text and individual correction explanations", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /current\.result\.corrected_text/);
  assert.match(page, /current\.result\.errors\.map/);
  assert.match(page, /item\.correction/);
  assert.match(page, /item\.explanation/);
  assert.match(page, /current\.provider === "demo"/);
  assert.match(page, /Analysis notes/);
});
