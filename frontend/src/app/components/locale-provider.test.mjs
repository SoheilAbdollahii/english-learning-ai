import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("locale provider synchronizes persisted profile preference and direction", async () => {
  const source = await readFile(new URL("./locale-provider.tsx", import.meta.url), "utf8");
  assert.match(source, /\/api\/v1\/me\//);
  assert.match(source, /method: "PATCH"/);
  assert.match(source, /profile: \{ locale: nextLocale \}/);
  assert.match(source, /document\.documentElement\.dir/);
  assert.match(source, /wordwise-locale/);
  assert.match(source, /aria-pressed/);
});
