import argparse
from os import close
import validators
import playwright
from playwright.async_api import async_playwright
import asyncio
from urllib.parse import urlparse
import logging
import tempfile

class HumanAssistedWebCrawler:
    def __init__(self, headless=False, speed=300, browser_name="Chromium", fuzz_marker="[FUZZ]"):
        self._headless = headless
        self._speed = speed
        self._browser_name = browser_name
        self._fuzz_marker = fuzz_marker
    
    def crawl(self, url, session_file_path, handle_request_fn=None):
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.async_crawl(url, session_file_path, handle_request_fn))
        loop.run_until_complete(task)

    def _handle_request(self, request):
        logging.debug(f'>> {request.method} {request.url} \n')  
        # if request.method in ["POST", "PUT"]:
        #     post_data = request.post_data
            # if post_data and self._fuzz_marker in post_data:
            #     print("Found request to be fuzzed: ", f'>> {request.method} {request.url} {post_data} \n')

    async def async_crawl(self, url, session_file_path, handle_request_fn=None):
        if not validators.url(url):
            raise Exception(
                "The url provided is malformed. Exiting Crawling procedure.")
        domain_name = urlparse(url).netloc
        # har_file_path = f'{domain_name.replace(".","_")}-report.har'
        async with async_playwright() as p:
            try:
                if self._browser_name == "Webkit":
                    browser_instance = p.webkit
                elif self._browser_name == "Firefox":
                    browser_instance = p.firefox
                else:
                    browser_instance = p.chromium
                if not self._headless:
                    browser = await browser_instance.launch(headless=False,
                                                            slow_mo=self._speed)
                else:
                    browser = await browser_instance.launch(headless=True,
                                                            slow_mo=self._speed)
                context = await browser.new_context(record_har_path=session_file_path)
                context.set_default_timeout(0)
                page = await context.new_page()
                handle_request_fn = handle_request_fn or self._handle_request
                page.on(
                    "request", lambda request: handle_request_fn(request))
                page.on(
                    "response", lambda response: logging.debug(
                        f'<< {response.status} {response.url} \n'))
                page.on("close", lambda: logging.DEBUG("Browser Closed Successfully"))
                await page.goto(url)
                await page.title()
                await page.wait_for_selector('text="None"')
            except playwright._impl._errors.TargetClosedError:
                pass
            except Exception as e:
                logging.exception("Page got closed manually or got crashed %s", e)
            finally:
                await page.close()
                await context.close()
                await browser.close()
                logging.debug(
                    f"The complete networking details can be found in {session_file_path}"
                )
