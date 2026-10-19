import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const pageUrl = new URL("../src/app/page.tsx", import.meta.url);
const page = await readFile(pageUrl, "utf8");

test("dashboard exposes the three planned learning areas", () => {
  for (const area of ["Writing", "Reading", "Vocabulary"]) {
    assert.ok(page.includes(`title: "${area}"`), `missing learning area: ${area}`);
  }
});

test("dashboard navigation targets existing sections and the Writing route", () => {
  for (const anchor of ["home", "reading", "vocabulary", "coming-soon"]) {
    assert.ok(page.includes(`id="${anchor}"`) || page.includes(`href="#${anchor}"`),
      `missing dashboard anchor: ${anchor}`);
  }
  assert.ok(page.includes('href: "/writing"'), "Writing area should link to the Writing Studio route");
  assert.ok(page.includes('href="/writing"'), "Writing navigation should open the Writing Studio");
});

test("dashboard does not present sample progress as real learner data", () => {
  assert.match(page, /Your activity will appear here/);
  assert.match(page, /activity tracking is not connected yet/);
  assert.match(page, /UI PREVIEW/);
});
