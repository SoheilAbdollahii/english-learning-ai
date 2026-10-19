import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("vocabulary page connects add and review actions to authenticated API", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /\/api\/v1\/vocabulary\/cards\//);
  assert.match(page, /\/api\/v1\/auth\/csrf\//);
  assert.match(page, /X-CSRFToken/);
  assert.match(page, /How well did you remember/);
  assert.match(page, /Show due only/);
  assert.match(page, /Sign in/);
});

test("vocabulary UI records review outcomes instead of marking words mastered on display", async () => {
  const page = await readFile(new URL("./page.tsx", import.meta.url), "utf8");
  assert.match(page, /reviewCard\(card, 1\)/);
  assert.match(page, /reviewCard\(card, 3\)/);
  assert.match(page, /reviewCard\(card, 4\)/);
  assert.match(page, /reviewCard\(card, 5\)/);
  assert.match(page, /card\.repetitions/);
  assert.match(page, /setCards/);
});
