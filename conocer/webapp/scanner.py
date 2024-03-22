import tempfile
from tqdm import tqdm
import logging
from conocer.webapp.har import Har2RemoteModel
from conocer.webapp.crawler import HumanAssistedWebCrawler
from conocer.scanner import DetoxioModelDynamicScanner

FUZZING_MARKERS = ["[[FUZZ]]", "[FUZZ]", "FUZZ", "<<FUZZ>>", "[[CONOCER]]", "[CONOCER]", "CONOCER", "<<CONOCER>>"]

class CrawlerOptions:
    def __init__(self, speed=350, browser_name="Chromium", headless=False):
        self.headless=headless
        self.browser_name=browser_name
        self.speed = speed

class ScannerOptions:
    def __init__(self, session_file_path, 
                 skip_crawling=False, 
                 crawler_options=None, 
                 save_session=True,
                 no_of_tests=10, 
                 prompt_prefix="", 
                skip_testing=False, 
                 fuzz_markers=None):
        self.session_file_path = session_file_path
        self.skip_crawling = skip_crawling
        self.crawler_options = crawler_options
        self.save_session = save_session
        self.no_of_tests = no_of_tests
        self.prompt_prefix = prompt_prefix
        self.fuzz_markers = fuzz_markers or FUZZING_MARKERS
        self.skip_testing = skip_testing

class GenAIWebScanner:

    def __init__(self, options:ScannerOptions):
        self.options = options
    
    def scan(self, url):
        session_file_path = self.options.session_file_path
        if not self.options.skip_crawling:
            if not session_file_path:
                outtmp = tempfile.NamedTemporaryFile(prefix="har_file_path", 
                                                     suffix=".har", 
                                                     delete=(not self.options.save_session))
                session_file_path = outtmp.name
                logging.debug("Crawled Results will stored at a location: %s", session_file_path)

            logging.debug("Starting Browser to record session from User...")
            logging.warn("Starting Human Assisted Crawler. The system will wait for user to record session. Close the Browser to start scanning")
            crawler = HumanAssistedWebCrawler(headless=self.options.crawler_options.headless, 
                                                speed=self.options.crawler_options.speed, 
                                                browser_name=self.options.crawler_options.browser_name)
            crawler.crawl(url, session_file_path=session_file_path)

        if self.options.skip_testing:
            return None

        logging.warn("Skipped Human Assisted Crawling. Using Recorded Session to perform testing..")
        conv = Har2RemoteModel(session_file_path, 
                               prompt_prefix=self.options.prompt_prefix, 
                               fuzz_markers=self.options.fuzz_markers)
        i = 0
        for model in conv.convert():
            i += 1
            model.prechecks()
            return self.__scan(model)
        if i == 0:
            logging.warn("No requests found in session with Fuzzing Marker %s. Skipping testing..", )


    def __scan(self, model):
        # Provide your API key or set it as an environment variable
        api_key = ''

        scanner = DetoxioModelDynamicScanner(api_key=api_key)
        with scanner.new_session() as session:
            # Generate prompts
            logging.info("Initialized Session..")
            prompt_generator = session.generate(count=self.options.no_of_tests)
            try:
                for prompt in tqdm(prompt_generator, desc="Testing..."):
        #             print(f"Generated Prompt: {prompt}")
                    logging.debug("Generated Prompt: \n%s", prompt.data.content)
                    # Simulate model output
                    raw_output, parsed_output = model.generate(prompt.data.content)
                    model_output_text = parsed_output if parsed_output else raw_output

                    logging.debug("Model Executed: \n%s", model_output_text)

    #                 print("Model Output", model_output_text)
                    # Evaluate the model interaction
                    if len(model_output_text) > 2: # Make sure the output is not empty
                        evaluation_response = session.evaluate(prompt, model_output_text)
                    logging.debug("Evaluation Executed...")
            except Exception as ex:
                logging.exception(ex)
                raise ex
            return session.get_report()
        
            

