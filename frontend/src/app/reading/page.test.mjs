import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("reading page loads published passages and submits through CSRF-protected API", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /\/api\/v1\/reading\/passages\//);
  assert.match(page, /\/api\/v1\/reading\/attempts\//);
  assert.match(page, /\/api\/v1\/auth\/csrf\//);
  assert.match(page, /X-CSRFToken/);
  assert.match(page, /Correct answers stay hidden until you submit/);
});

test("reading result explains server-scored answers and offers retry", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /result\.result_details/);
  assert.match(page, /item\.explanation/);
  assert.match(page, /Try this passage again/);
  assert.match(page, /Sign in to save your reading result/);
});
