import json
import copy
import requests
import random
import string
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from haralyzer import HarParser, HarPage
from .model import RemoteModel

class URLManipulator:
    """A class to manipulate URLs by replacing query parameters containing a specific marker."""

    def __init__(self, fuzz_markers):
        """
        Initialize the URLManipulator object.

        Parameters:
        - fuzz_markers (list):String Markers used to identify parameters to be replaced.
        """
        self._fuzz_markers = fuzz_markers
    
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

class Har2RemoteModel:
    """A class to convert HAR files to RemoteModel instances."""

    def __init__(self, har_file_path, fuzz_markers, prompt_prefix=""):
        """
        Initialize the Har2RemoteModel object.

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
        Convert HAR entries to RemoteModel instances.

        Yields:
        - RemoteModel: The converted RemoteModel instances.
        """
        matcher = RequestMutator(self._fuzz_markers)
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