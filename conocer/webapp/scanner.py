import tempfile
import logging
from conocer.webapp.har import Har2RemoteModel
from conocer.webapp.crawler import HumanAssistedWebCrawler

class CrawlerOptions:
    def __init__(self, speed=350, browser_name="Chromium", headless=False):
        self.headless=headless
        self.browser_name=browser_name
        self.speed = speed

class ScannerOptions:
    def __init__(self, session_file_path, skip_crawling=False, crawler_options=None, save_session=True):
        self.session_file_path = session_file_path
        self.skip_crawling = skip_crawling
        self.crawler_options = crawler_options
        self.save_session = save_session

class GenAIWebScanner:

    def __init__(self, options:ScannerOptions):
        self.options = options
    
    def scan(self, url):
        session_file_path = self.options.session_file_path

        if not self.options.skip_crawling:
            if not session_file_path:
                outtmp = tempfile.NamedTemporaryFile(prefix="har_file_path", 
                                                     suffix=".har", 
                                                     delete=(not self.options.delete_session))
                session_file_path = outtmp.name
                logging.debug("Crawled Results will stored at a location: %s", session_file_path)

            if not self.options.skip_crawling:
                print("Starting Human Assisted Crawler. Close the Browser to start scanning")
                crawler = HumanAssistedWebCrawler(headless=self.options.crawler_options.headless, 
                                                    speed=self.options.crawler_options.speed, 
                                                    browser_name=self.options.crawler_options.browser_name)
                crawler.crawl(url, session_file_path=session_file_path)

        conv = Har2RemoteModel(session_file_path)
        for model in conv.convert():
            for prompt in ["Hello, How are you?", "Give me tips on onion crops"]:
                model.prechecks()
                res = model.generate(prompt)
                print(res)
        

