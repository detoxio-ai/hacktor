import json
import copy
import requests
import random
import string
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from haralyzer import HarParser, HarPage
from .model import WebappRemoteModel, RequestModel, MobileAppRemoteModel
#from model import WebappRemoteModel, RequestModel, MobileAppRemoteModel

FUZZING_MARKERS = ["[[FUZZ]]", "[FUZZ]", "FUZZ", "<<FUZZ>>", "[[CHAKRA]]", "[CHAKRA]", "CHAKRA", "<<CHAKRA>>"]

class URLManipulator:
    """A class to manipulate URLs by replacing query parameters containing a specific marker."""

    def __init__(self, fuzz_markers):
        """
        Initialize the URLManipulator object.

        Parameters:
        - fuzz_markers (list):String Markers used to identify parameters to be replaced.
        """
        self._fuzz_markers = fuzz_markers
        if type(fuzz_markers) == str:
            self.replace_function = self.replace_fuzz_str
        else:
            self.replace_function = self.replace_fuzz_array
    
    def replace_fuzz(self, url, new_value):
        return self.replace_function(url, new_value)

    def replace_fuzz_array(self, url, new_value):
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
            if any(marker in param for param in value for marker in self._fuzz_markers):
                query_params[key] = [new_value if any(marker in param for marker in self._fuzz_markers) else param for param in value]


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
    
    def replace_fuzz_str(self, url, new_value):
        """
        Replace value of key prompt_param with a new value.

        Parameters:
        - url (str): The URL to manipulate.
        - new_value (str): The new value to replace the fuzz marker with.

        Returns:
        - str: The modified URL.
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        for key, _ in query_params.items():
            if self._fuzz_markers == key:
                query_params[key] = new_value


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

    def __init__(self, fuzz_markers):
        """
        Initialize the RequestMutator object.

        Parameters:
        - fuzz_markers (list): Marker used to identify content to be replaced.
        """
        self._fuzz_markers = fuzz_markers
        self._url_manipulator = URLManipulator(self._fuzz_markers)
    
    def match(self, request):
        """
        Check if the request matches the fuzz marker.

        Parameters:
        - request: The request object to match.

        Returns:
        - bool: True if the request matches the fuzz marker, False otherwise.
        """
        if request.text and any(marker in request.text for marker in self._fuzz_markers):
            return True
        elif self._match_query_param(request.queryString):
            return True
        else:
            return False
    
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
            for marker in self._fuzz_markers:
                if marker in request.text:
                    return request.text.replace(marker, replacement_text)
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
                    if any(marker in v for marker in self._fuzz_markers):
                        return True
        return False

class RequestMutatorBurp:
    """A class to modify requests by replacing body content and URLs based on a prompt parameter marker."""

    def __init__(self, prompt_param):
        """
        Initialize the RequestMutatorBurp object.

        Parameters:
        - prompt_param (str): Parameter which holds the input prompt.
        """
        if type(prompt_param) != str:
            self._prompt_param = prompt_param or FUZZING_MARKERS
            self._body_manipulator = self.replace_body_arr
        else:
            self._prompt_param = prompt_param
            self._body_manipulator = self.replace_body_str

        self._url_manipulator = URLManipulator(self._prompt_param)
        

    def replace_body(self, request, replacement_text):
        return self._body_manipulator(request, replacement_text)
    
    def replace_body_str(self, request, replacement_text):
        """
        Replace the body content of the request.

        Parameters:
        - request (RequestModel): The RequestModel object to modify.
        - replacement_text (str): The text to replace the prompt marker with.

        Returns:
        - dict: The modified body content.
        """
        if request._data:
            for key, _ in request._data.items():
                if self._prompt_param in key:
                    return {**request._data, key: replacement_text}
            else:
                return request._data
        return ""
    
    def replace_body_arr(self, request, replacement_text):
        """
        Replace the body content of the request.

        Parameters:
        - request (RequestModel): The RequestModel object to modify.
        - replacement_text (str): The text to replace the prompt marker with.

        Returns:
        - dict: The modified body content.
        """
        newbody = request._data.copy()
        if request._data:
            for key, value in request._data.items():
                if any(marker in str(value) for marker in self._prompt_param):
                    newbody[key] = replacement_text if any(marker in value for marker in self._prompt_param) else request._data[key]
            return newbody
        else:        
            return ""

    def replace_url(self, request, replacement_text):
        """
        Replace the URL of the request.

        Parameters:
        - request (RequestModel): The RequestModel object to modify.
        - replacement_text (str): The text to replace the prompt marker with.

        Returns:
        - str: The modified URL.
        """
        return self._url_manipulator.replace_fuzz(request._url, [replacement_text])
    
    def match(self, request):
        """
        Check if the request matches the fuzz marker.

        Parameters:
        - request: The request object to match.

        Returns:
        - bool: True if the request matches the fuzz marker, False otherwise.
        """
        if request._data and any(marker in request._data for marker in self._prompt_param):
            return True
        elif self._match_query_param(request._url):
            return True
        else:
            return False
    
    def _match_query_param(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        for _, value in query_params.items():
            if any(marker in param for param in value for marker in self._prompt_param):
                return True
        return False

class Har2WebappRemoteModel:
    """A class to convert HAR files to WebappRemoteModel instances."""

    def __init__(self, har_file_path, fuzz_markers, prompt_prefix=""):
        """
        Initialize the Har2WebappRemoteModel object.

        Parameters:
        - har_file_path (str): The path to the HAR file.
        - fuzz_markers (list): Marker used to identify parameters to be replaced.
        """
        with open(har_file_path, 'r') as f:
            self._har_parser = HarParser(json.loads(f.read())) 
        self._fuzz_markers = fuzz_markers
        self._prompt_prefix = prompt_prefix

    def convert(self):
        """
        Convert HAR entries to WebappRemoteModel instances.

        Yields:
        - WebappRemoteModel: The converted WebappRemoteModel instances.
        """
        matcher = RequestMutator(self._fuzz_markers)
        for page in self._har_parser.pages:
            for har_entry in page.entries:
                if matcher.match(har_entry.request):
                    model = WebappRemoteModel(request=har_entry.request, mutator=matcher, prompt_prefix=self._prompt_prefix)
                    yield(model)

class BurpRequestParser:
    """A class to parse raw Burp Request."""

    def __init__(self, request_file_path, base_url_path):
        """
        Initialize the BurpRequestParser object.

        Parameters:
        - request_file_path (str): The path to the Burp Request file.
        - base_url_path (str): Base URL of request.
        """
        self._request_file_path = request_file_path
        self._request = self.parse_request(base_url_path)


    def parse_request(self, base_url_path):
        """
        Method to Parse Request file. Check for either JSON Content Type or form-data.

        Parameters:
            - base_url_path (str): Base URL of request.

        Returns:
            - RequestModel: The parsed RequestModel instance.
        """
        # Open File
        with open(self._request_file_path, 'r') as file:
            request_text = file.read().strip()
        # Extract Method and URL
        request_lines = [line.strip() for line in request_text.split('\n') if line.strip()]
        method, url = request_lines[0].split(maxsplit=2)[0:2]

        # Extract headers and data from file
        headers = {}
        data = None
        ctype = -1

        if 'Content-Type: application/json' in request_text:
            ctype = 0
            if method.upper() == 'POST':
                data = {}
                data = json.loads(request_lines[-1])
        elif 'Content-Type: multipart/form-data' in request_text:
            ctype = 1
            if method.upper() == 'POST':
                form_data = request_text.split('\n\n', 1)[1]
                boundary = request_text.split('boundary=')[1].split("\n")[0].strip()
                fields = form_data.split('--' + boundary)[1:-1]
                data = {}
                for field in fields:
                    lines = field.split('\n')
                    name = lines[1].split('name="')[1].split('"')[0]
                    value = '\n'.join(lines[3:-1]).strip()
                    data[name] = value
            else:
                raise ValueError("Unsupported Content-Type")

        request_text = request_text.split("\n\n")[0]
        request_lines = [line.strip() for line in request_text.split('\n') if line.strip()]
        for line in request_lines[1:]:
            if line.split(': ')[0] == 'Host':
                headers[line.split(': ')[0]] = line.split(': ')[1]

        return RequestModel(method, base_url_path+url, headers, data, ctype)

class BurpRequest2MobileAppRemoteModel:
    """A class to convert Burp Request to MobileAppRemoteModel instances."""

    def __init__(self, base_url_path, request_file_path, prompt_param="", prompt_prefix="", output_field=""):
        """
        Initialize the BurpRequest2MobileAppRemoteModel object.

        Parameters:
        - base_url_path (str): Base URL of request.
        - request_file_path (str): The path to the Burp request file.
        - prompt_param (str): Parameter which holds the input prompt.
        - prompt_prefix (str): Prefix to add to prompt.
        - output_field (str): Output field which contains GenAI response
        """
        self._burpRequestParser = BurpRequestParser(request_file_path, base_url_path) 
        self._prompt_prefix = prompt_prefix
        self._prompt_param = prompt_param
        self._output_field = output_field


    def convert(self):
        """
        Convert Burp request to MobileAppRemoteModel instances.

        Returns:
        - MobileAppRemoteModel: The converted MobileAppRemoteModel instance.
        """
        mutator = RequestMutatorBurp(self._prompt_param)
        model = MobileAppRemoteModel(request=self._burpRequestParser._request, mutator=mutator, prompt_prefix=self._prompt_prefix, output_field=self._output_field)
        return model

# if __name__ == "__main__":
#     har_file_path = '/tmp/har_file_pathkvrbrn9e.har'
#     res_file_path = '/tmp/KissanAI_Request.txt'
#     base_url = "https://api1.kissangpt.com"
#     conv = BurpRequest2MobileAppRemoteModel(base_url, res_file_path, prompt_param="question")
#     model = conv.convert()

#     for prompt in ["Hello, How are you?", "Give me tips on onion crops"]:
#         model.prechecks()
#         res = model.generate(prompt)
#         print(res)