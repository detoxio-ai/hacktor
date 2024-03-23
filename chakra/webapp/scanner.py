import tempfile
import json
from tqdm import tqdm
import logging
from chakra.webapp.har import Har2WebappRemoteModel
from chakra.webapp.crawler import HumanAssistedWebCrawler
from chakra.scanner import DetoxioModelDynamicScanner
from .model import GradioAppModel

FUZZING_MARKERS = ["[[FUZZ]]", "[FUZZ]", "FUZZ", "<<FUZZ>>", "[[CHAKRA]]", "[CHAKRA]", "CHAKRA", "<<CHAKRA>>"]

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
        if GradioAppModel.is_gradio_endpoint(url):
            return self._scan_gradio_app(url)
        else:
            return self._scan_webapp(url)
    
    def _scan_gradio_app(self, url):
        predict_signature = self._detect_gradio_predict_api_signature(url)
        model = GradioAppModel(url, predict_signature, self.options.fuzz_markers)
        return self.__scan_model(model)

    def _detect_gradio_predict_api_signature(self, url):
        """
            Predict signature of remote gradio endpoint
        """
        predict_signature = {}
        def _handle_request(request):
            logging.debug(f'>> {request.method} {request.url} \n')  
            if request.method in ["POST", "PUT"]:
                post_data = request.post_data
                if post_data and any(marker in post_data for marker in self.options.fuzz_markers):
                    try:
                        logging.debug("Found request to be fuzzed: %s", 
                                      f'>> {request.method} {request.url} {post_data} \n')
                        post_data_json = json.loads(post_data)
                        predict_signature['sig'] = post_data_json.get("data")
                    except Exception as ex:
                        logging.exception("Found an error while detecting gradio predict signature", ex)
        self._crawl(url, _handle_request)
        logging.debug("Identified Gradio Signature", predict_signature)
        if len(predict_signature) <= 0:
            logging.warn("[WARNING] Could not detect gradio predict signature. Did you specify [FUZZ] marker?")
        return predict_signature.get('sig')

    def _crawl(self, url, intercept_request_hook=None):
        """
            Crawl and return the session file path
        """
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
            crawler.crawl(url, session_file_path=session_file_path, handle_request_fn=intercept_request_hook)
        return session_file_path

    def _scan_webapp(self, url):
        session_file_path = self._crawl(url)

        if self.options.skip_testing:
            return None

        logging.debug("Tests will start soon. Using Recorded Session to perform testing..")
        conv = Har2WebappRemoteModel(session_file_path, 
                               prompt_prefix=self.options.prompt_prefix, 
                               fuzz_markers=self.options.fuzz_markers)
        i = 0
        for model in conv.convert():
            i += 1
            model.prechecks()
            return self.__scan_model(model)
        if i == 0:
            logging.warn("No requests found in session with Fuzzing Marker %s. Skipping testing..", )


    def __scan_model(self, model):
        # Provide your API key or set it as an environment variable
        api_key = ''

        scanner = DetoxioModelDynamicScanner(api_key=api_key)
        with scanner.new_session() as session:
            # Generate prompts
            logging.info("Initialized Session..")
            prompt_generator = session.generate(count=self.options.no_of_tests)
            try:
                for prompt in tqdm(prompt_generator, desc="Testing..."):
                    logging.debug("Generated Prompt: \n%s", prompt.data.content)
                    # Simulate model output
                    raw_output, parsed_output = model.generate(prompt.data.content)
                    model_output_text = parsed_output if parsed_output else raw_output

                    logging.debug("Model Executed: \n%s", model_output_text)

                    # Evaluate the model interaction
                    if len(model_output_text) > 2: # Make sure the output is not empty
                        evaluation_response = session.evaluate(prompt, model_output_text)
                        logging.debug("Eveluation Reponse \n%s", evaluation_response)
                    logging.debug("Evaluation Executed...")
            except Exception as ex:
                logging.exception(ex)
                raise ex
            return session.get_report()
        
            

