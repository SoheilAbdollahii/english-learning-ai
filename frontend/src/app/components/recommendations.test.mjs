import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("recommendations display evidence-backed next steps from the API", async () => {
  const component = await readFile(new URL("./recommendations.tsx", import.meta.url), "utf8");
  assert.match(component, /\/api\/v1\/progress\/recommendations\//);
  assert.match(component, /item\.reason/);
  assert.match(component, /item\.href/);
  assert.match(component, /Based on your saved activity/);
});
