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


test("all literal translation keys used by core screens have Persian entries", async () => {
  const provider = await readFile(new URL("./locale-provider.tsx", import.meta.url), "utf8");
  const files = [
    "../../page.tsx",
    "./progress-overview.tsx",
    "./recommendations.tsx",
    "./auth-status.tsx",
    "../vocabulary/page.tsx",
    "../reading/page.tsx",
    "../placement/page.tsx",
    "../writing/page.tsx",
    "../login/page.tsx",
    "../register/page.tsx",
  ];
  const dictionaryKeys = new Set([...provider.matchAll(/^\s*"([^"]+)":/gm)].map((match) => match[1]));
  const missing = [];
  for (const file of files) {
    const source = await readFile(new URL(file, import.meta.url), "utf8");
    for (const match of source.matchAll(/t\("([^"]+)"\)/g)) {
      if (!dictionaryKeys.has(match[1])) missing.push(`${file}: ${match[1]}`);
    }
  }
  assert.deepEqual(missing, []);
});

test("Persian direction is applied globally while reading exercises keep English direction", async () => {
  const provider = await readFile(new URL("./locale-provider.tsx", import.meta.url), "utf8");
  const reading = await readFile(new URL("../reading/page.tsx", import.meta.url), "utf8");
  const css = await readFile(new URL("../globals.css", import.meta.url), "utf8");
  assert.match(provider, /document\.documentElement\.dir = locale === "fa" \? "rtl" : "ltr"/);
  assert.match(provider, /document\.documentElement\.lang = locale/);
  assert.match(css, /html\[dir="rtl"\] \.main-panel/);
  assert.match(reading, /className="reading-passage-body" lang="en" dir="ltr"/);
});
