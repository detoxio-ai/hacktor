from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.tatacapital.com/")
    page.frame_locator("#iFrameResizer0").get_by_test_id("stChatInputTextArea").fill("FUZZ")
    page.frame_locator("#iFrameResizer0").get_by_test_id("stChatInputTextArea").click()
    expect(page.frame_locator("#iFrameResizer0").get_by_test_id("stChatMessage").nth(1)).to_be_visible()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
