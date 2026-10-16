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
