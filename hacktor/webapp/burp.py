import json
import logging
import requests
from .model import ModelResponseParserBuilder, ModelResponseParser

class RequestModel:
    def __init__(self, method, url, headers, data, ctype):
        self._method = method
        self._url = url
        self._headers = headers
        self._data = data
        self._ctype = ctype

class MobileAppRemoteModel:
    """A class representing a remote model for generating responses."""

    def __init__(self, request, mutator, output_field="", prompt_prefix=""):
        """
        Initialize the MobileAppRemoteModel object.

        Parameters:
        - request (MobileAppRemoteModel): The RequestModel object representing the remote model.
        - mutator (RequestMutator): The mutator object to modify requests.
        - output_field (str): The field in the response to extract information from.
        - prompt_prefix (str): Prefix to add to prompts sent to the model.
        """
        self._request = request
        self._mutator = mutator
        self._output_field = output_field
        self._prompt_prefix = prompt_prefix
        self._response_parser = ModelResponseParser()

    def generate(self, input_text):
        """
        Generate a response from the remote model.

        Parameters:
        - input_text (str): The input text for generating the response.

        Returns:
        - tuple: A tuple containing the response content and possible model output, is parsing is successful otherwise empty.
        """
        res = self._generate_raw(input_text)
        return self._response_parser.parse(input_text, res)

    def _generate_raw(self, input_text):
        """
        Generate a raw response from the remote model.

        Parameters:
        - input_text (str): The input text for generating the response.

        Returns:
        - response: The raw response from the remote model.
        """
        prompt = self._create_prompt(input_text)
        if self._request._method in ["POST", "PUT"]:
            res = self._method(requests.post, prompt)
            return res
        elif self._method in ["GET"]:
            res = self._method(requests.get, prompt)
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
        data = self._mutator.replace_body(self._request, input_text)
        url = self._mutator.replace_url(self._request, input_text)
        if self._request._ctype == 0:
            res = method(url=url, headers=self._request._headers, json=data)
        elif self._request._ctype == 1:
            res = method(url=url, headers=self._request._headers, data=data)
        else:
            raise ValueError("UnImplemented Content type")
        return res

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
        mrpb = ModelResponseParserBuilder()
        self._response_parser = mrpb.generate(self)