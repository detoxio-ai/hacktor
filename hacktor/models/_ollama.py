import os
import ollama
from urllib.parse import urlparse
from ollama import ChatResponse, Client

class OllamaModel:
    def __init__(self, model_id=None, base_url=None):
        self.default_base_url = "http://localhost:11434"
        self.base_url = base_url or self._extract_base_url_from_env() or self.default_base_url
        self.model_name = None
        self._parse_model_from_id(model_id)
        self._client = Client(host=self.base_url)
        self.run("test")

    def _extract_base_url_from_env(self):
        """
        Extracts the base URL from the OLLAMA_BASE_URL environment variable if it exists.
        """
        return os.getenv("OLLAMA_BASE_URL")

    def _parse_model_from_id(self, model_id):
        """
        Parses the model_id to extract the model name and adjusts the base URL if needed.
        """
        if model_id:
            parsed_url = urlparse(model_id)
            if parsed_url.netloc:  # Check if it's a full URL
                self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) > 1 and path_parts[-2] == "model":
                    self.model_name = path_parts[-1]
                else:
                    self.model_name = path_parts[-1]
            else:
                self.model_name = model_id  # Assume model_id is just the model name

        if not self.model_name:
            raise ValueError("Model name must be specified either in model_id or as a standalone.")

    def run(self, prompt, system: str=None):
        """
        Sends a prompt to the specified model and returns the response.

        Args:
            prompt (str): The text prompt to send to the model.

        Returns:
            str: The response text from the model.
        """
        if not self.model_name:
            raise ValueError("Model name is not initialized.")

        try:
            # Interact with the model using the ollama chat API
            response: ChatResponse = self._client.chat(
                model=self.model_name, 
                messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            return response['message']['content']
        except ollama._types.ResponseError as e:
            raise ValueError(f"Error making call to the model {str(e)}")

# Example Usage:
# BASE_URL and model_id provided
# model_id = "https://custom.ollama.api/model/deepseek-r1:1.5b"
# ollama_model = OllamaModel(model_id=model_id)
# response = ollama_model.run("Tell me a story about exploration.")
# print(response)

# BASE_URL not provided, defaults to the default base URL
# model_name = "deepseek-r1:1.5b"
# ollama_model = OllamaModel(model_id=model_name)
# response = ollama_model.run("What is the meaning of life?")
# print(response)

