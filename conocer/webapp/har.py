import json
import copy
import requests
import random
import string
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from haralyzer import HarParser, HarPage

class URLManipulator:
    """A class to manipulate URLs by replacing query parameters containing a specific marker."""

    def __init__(self, fuzz_marker="[FUZZ]"):
        """
        Initialize the URLManipulator object.

        Parameters:
        - fuzz_marker (str): Marker used to identify parameters to be replaced.
        """
        self._fuzz_marker = fuzz_marker
    
    def replace_fuzz(self, url, new_value):
        """
        Replace parameters containing the fuzz marker with a new value.

        Parameters:
        - url (str): The URL to manipulate.
        - new_value (str): The new value to replace the fuzz marker with.

        Returns:
        - str: The modified URL.
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        for key, value in query_params.items():
            if any(self._fuzz_marker in param for param in value):
                query_params[key] = [new_value if self._fuzz_marker in param else param for param in value]

        modified_query = urlencode(query_params, doseq=True)
        modified_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            modified_query,
            parsed_url.fragment
        ))
        return modified_url

class RequestMutator:
    """A class to modify requests by replacing body content and URLs based on a fuzz marker."""

    def __init__(self, fuzz_marker="[FUZZ]"):
        """
        Initialize the RequestMutator object.

        Parameters:
        - fuzz_marker (str): Marker used to identify content to be replaced.
        """
        self._fuzz_marker = fuzz_marker
        self._url_manipulator = URLManipulator(self._fuzz_marker)
    
    def match(self, request):
        """
        Check if the request matches the fuzz marker.

        Parameters:
        - request: The request object to match.

        Returns:
        - bool: True if the request matches the fuzz marker, False otherwise.
        """
        if request.text and self._fuzz_marker in request.text:
            return True
        elif self._match_query_param(request.queryString):
            return True
    
    def replace_body(self, request, replacement_text):
        """
        Replace the body content of the request.

        Parameters:
        - request: The request object to modify.
        - replacement_text (str): The text to replace the fuzz marker with.

        Returns:
        - str: The modified body content.
        """
        if request.text:
            if self._fuzz_marker in request.text:
                return request.text.replace(self._fuzz_marker, replacement_text)
            else:
                return request.text
        return ""
    
    def replace_url(self, request, replacement_text):
        """
        Replace the URL of the request.

        Parameters:
        - request: The request object to modify.
        - replacement_text (str): The text to replace the fuzz marker with.

        Returns:
        - str: The modified URL.
        """
        return self._url_manipulator.replace_fuzz(request.url, replacement_text)

    def _match_query_param(self, queryStrings):
        for kv in queryStrings:
            for k, v in kv.items():
                if k == "value":
                    if self._fuzz_marker in v:
                        return True
        return False

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

class RemoteModel:
    """A class representing a remote model for generating responses."""

    def __init__(self, request, mutator:RequestMutator, output_field="", prompt_prefix=""):
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
        print(prompt)
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

class Har2RemoteModel:
    """A class to convert HAR files to RemoteModel instances."""

    def __init__(self, har_file_path, fuzz_marker="[FUZZ]", prompt_prefix=""):
        """
        Initialize the Har2RemoteModel object.

        Parameters:
        - har_file_path (str): The path to the HAR file.
        - fuzz_marker (str): Marker used to identify parameters to be replaced.
        """
        with open(har_file_path, 'r') as f:
            self._har_parser = HarParser(json.loads(f.read())) 
        self._fuzz_marker = fuzz_marker
        self._prompt_prefix = prompt_prefix

    def convert(self):
        """
        Convert HAR entries to RemoteModel instances.

        Yields:
        - RemoteModel: The converted RemoteModel instances.
        """
        matcher = RequestMutator(self._fuzz_marker)
        for page in self._har_parser.pages:
            for har_entry in page.entries:
                if matcher.match(har_entry.request):
                    model = RemoteModel(request=har_entry.request, mutator=matcher, prompt_prefix=self._prompt_prefix)
                    yield(model)

if __name__ == "__main__":
    har_file_path = '/tmp/har_file_pathkvrbrn9e.har'
    conv = Har2RemoteModel(har_file_path)
    for model in conv.convert():
        for prompt in ["Hello, How are you?", "Give me tips on onion crops"]:
            model.prechecks()
            res = model.generate(prompt)
            print(res)