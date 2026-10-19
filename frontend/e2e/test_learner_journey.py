import re

from playwright.sync_api import expect, sync_playwright


BASE_URL = "http://127.0.0.1:3000"


def test_browser_learner_journey_and_persian_direction():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(BASE_URL, wait_until="networkidle")
            expect(page.get_by_role("heading", name=re.compile("Your English journey"))).to_be_visible()

            page.get_by_role("button", name="فارسی · RTL").click()
            expect(page.locator("html")).to_have_attribute("dir", "rtl")
            expect(page.locator("html")).to_have_attribute("lang", "fa")
            page.get_by_role("button", name="EN · LTR").click()
            expect(page.locator("html")).to_have_attribute("dir", "ltr")
            expect(page.locator("html")).to_have_attribute("lang", "en")

            page.goto(f"{BASE_URL}/login", wait_until="networkidle")
            page.get_by_label("Username").fill("e2e-learner")
            page.get_by_label("Password").fill("Strong-test-pass-123")
            page.get_by_role("button", name="Sign in").click()
            page.wait_for_url(f"{BASE_URL}/")

            page.goto(f"{BASE_URL}/reading", wait_until="networkidle")
            expect(page.get_by_role("heading", name="Stories for curious minds.")).to_be_visible()
            expect(page.locator(".placement-question").first).to_be_visible()
            question_count = page.locator(".placement-question").count()
            assert question_count > 0
            for index in range(question_count):
                page.locator(".placement-question").nth(index).locator('input[type="radio"]').first.check()
            page.get_by_role("button", name=re.compile("Check my answers")).click()
            expect(page.locator("#reading-result-title")).to_be_visible()

            page.goto(f"{BASE_URL}/vocabulary", wait_until="networkidle")
            page.get_by_role("textbox", name="Word").fill("e2e-resilient")
            page.get_by_role("textbox", name="Meaning in English").fill("Able to recover after difficulty.")
            page.get_by_role("button", name=re.compile("Add to vocabulary")).click()
            expect(page.get_by_role("heading", name="e2e-resilient")).to_be_visible()
            expect(page.get_by_text("Able to recover after difficulty.")).to_be_visible()
            page.get_by_role("button", name="Good").click()
            expect(page.get_by_role("status")).to_contain_text("Review saved.")

            page.goto(f"{BASE_URL}/writing", wait_until="networkidle")
            page.get_by_label("Your English writing").fill("I practice English every day.")
            page.get_by_role("button", name=re.compile("Save and review")).click()
            expect(page.get_by_role("heading", name="Your writing is saved.")).to_be_visible()
            expect(page.get_by_text("Demo provider — no grammar evaluation")).to_be_visible()
        finally:
            browser.close()
