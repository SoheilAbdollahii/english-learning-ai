import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("progress overview reads persisted summary instead of placeholder metrics", async () => {
  const component = await readFile(new URL("./progress-overview.tsx", import.meta.url), "utf8");
  assert.match(component, /\/api\/v1\/progress\/summary\//);
  assert.match(component, /sessions_completed/);
  assert.match(component, /current_streak_days/);
  assert.match(component, /words_reviewed/);
  assert.match(component, /recent_activity/);
  assert.match(component, /Sign in to see your personal progress/);
});
