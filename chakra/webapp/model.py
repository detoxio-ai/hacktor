import logging
import requests
import requests
import string
import random
from gradio_client import Client

class RemoteModel:
    """A class representing a remote model for generating responses."""

    def __init__(self, request, mutator, output_field="", prompt_prefix=""):
        """
        Initialize the RemoteModel object.

        Parameters:
        - request: The request object representing the remote model.
        - mutator (RequestMutator): The mutator object to modify requests.
        - output_field (str): The field in the response to extract information from.
        - prompt_prefix (str): Prefix to add to prompts sent to the model.
        """
        self._request = request
        self._mutator = mutator
        self._output_field = output_field
        self._prompt_prefix = prompt_prefix
        self._marker = self._random_string(12)
        self._response_parser = ModelResponseParser()

    def generate(self, input_text):
        """
        Generate a response from the remote model.

        Parameters:
        - input_text (str): The input text for generating the response.

        Returns:
        - tuple: A tuple containing the response content and possible model output, is parsing is successful otherwise empty.
        """
        prompt = self._create_prompt(input_text)
        res = self._generate_raw(prompt)
        return self._response_parser.parse(res)

    def _generate_raw(self, input_text):
        """
        Generate a raw response from the remote model.

        Parameters:
        - input_text (str): The input text for generating the response.

        Returns:
        - response: The raw response from the remote model.
        """
        if self._request.method in ["POST", "PUT"]:
            res = self._method(requests.post, input_text)
            return res
        elif self._method in ["GET"]:
            res = self._method(requests.get, input_text)
            return res
        else:
            logging.debug("Method not supported %s", self._method)
        return None

    def _method(self, method, input_text):
        """
        Perform the HTTP request to the remote model.

        Parameters:
        - method: The HTTP method to use for the request.
        - input_text (str): The input text for generating the response.

        Returns:
        - response: The response from the remote model.
        """
        _headers = dict(
            (d['name'], d['value']) for d in self._request.headers if not d['name'].startswith(':'))

        _cookies = dict(
            (d['name'], d['value']) for d in self._request.cookies if not d['name'].startswith(':'))


        data = self._mutator.replace_body(self._request, input_text)
        url = self._mutator.replace_url(self._request, input_text)
        res = method(url=url, headers=_headers, cookies=_cookies, data=data)
        return res
    
    def _random_string(self, length):
        # Define the characters to choose from
        characters = string.ascii_letters + string.digits

        # Generate a random string of specified length
        random_string = ''.join(random.choice(characters) for _ in range(length))

        return random_string

    def _create_prompt(self, text):
        """
        Create a prompt by adding prefix to the given text.

        Parameters:
        - text (str): The input text to create the prompt.

        Returns:
        - str: The generated prompt.
        """
        return self._prompt_prefix + text

    def prechecks(self):
        """
        Perform prechecks to determine the location of the marker in the response.
        """
        # Send some prompts to check if response has marker
        texts = [f"Do you know about {self._marker}? Can you tell something it?", 
                f"Hello, {self._marker}? How are you?"]
        for text in texts:
            prompt = self._create_prompt(text)
            res = self._generate_raw(prompt)
            res_json = self._attempt_json(res)
            if res_json:
                loc = self._locate_marker_in_json(res_json, prompt, self._marker)
                if loc:
                    self._response_parser = ModelResponseParser("json", loc)
                    break
    
    def _attempt_json(self, res):
        """
        Attempt to parse the response as JSON.

        Parameters:
        - res: The response object to parse.

        Returns:
        - dict or None: The parsed JSON response, or None if parsing fails.
        """
        try:
            return res.json()  
        except:
            pass
        return None

    def _locate_marker_in_json(self, res_json, prompt, marker):
        """
        Locate the marker within the JSON response.

        Parameters:
        - res_json (dict): The parsed JSON response.
        - prompt (str): The prompt used to generate the response.
        - marker (str): The marker to locate within the response.

        Returns:
        - str or None: The location of the marker within the response, or None if not found.
        """
        for k, v in res_json.items():
            if v != prompt and marker in v:
                return k
        return None 

class GradioAppModel:
    def __init__(self, url, signature, fuzz_markers):
        self._url = url
        self._client = Client(url)
        self._signature = signature
        self._fuzz_markers = fuzz_markers

    @classmethod
    def is_gradio_endpoint(self, url):
        try:
            logging.debug("Checking if url is a gradio endpint")
            _client = Client(url)
            return True
        except Exception as ex:
            logging.debug("Received while connecting to client", ex)
            return False
    
    def generate(self, prompt):
        args = self._create_predict_arguements(prompt)
        logging.debug("Arguements to Gradio App %s", args)
        out = self._client.predict(*args)
        return out, ""
    
    def _create_predict_arguements(self, prompt):
        signature = self._signature
        if not signature:
            signature = [self._fuzz_markers[0], "Chat"]  # Set default signature, a best guess
        arguements = []
        for param in signature:
            value = param
            for marker in self._fuzz_markers:
                if isinstance(param, str) and marker in param:
                    value = param.replace(marker, prompt)
                    break
            arguements.append(value)
        return arguements

class ModelResponseParser:
    """A class to parse model responses and extract relevant information."""

    def __init__(self, content_type="text", location=None):
        """
        Initialize the ModelResponseParser object.

        Parameters:
        - content_type (str): The type of content expected in the response ("text" or "json").
        - location (str): The location within the JSON response to extract information from.
        """
        self._content_type = content_type
        self._location = location
    
    def parse(self, response):
        """
        Parse the response and extract relevant information.

        Parameters:
        - response: The response object to parse.

        Returns:
        - tuple: A tuple containing the parsed content and the extracted information.
        """
        if self._content_type == "text":
            return response.content, ""
        elif self._content_type == "json":
            try:
                res_json = response.json()
                return response.content, res_json[self._location]
            except Exception as ex:
                logging.exception("Error while parsing json", ex)
                return response.content, ""
