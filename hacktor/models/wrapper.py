

from enum import Enum
from .groq import GroqModel
from .openai import OpenAIModel

class Registry(Enum):
    GROQ = "GROQ"
    OPENAI = "OPENAI"
    HF = "HF"  # Hugging Face

    @classmethod
    def list_options(cls):
        return [option.value for option in cls]

class LLMModel:

    def __init__(self, registry, model_id):
        
        # Placeholder for future registry-specific setup
        if registry == Registry.GROQ:
            self.model = GroqModel(model_id)
        elif registry == Registry.OPENAI:
            self.model = OpenAIModel(model_id)
        elif registry == Registry.HF:
            # Initialize Hugging Face-specific components or configurations here
            raise Exception("Undefined Hugging Face")
        else:
            raise Exception("Undefined registry" + registry)

    def generate(self, input_text):
        """
        Generate a response from the remote model.

        Parameters:
        - input_text (str): The input text for generating the response.

        Returns:
        - tuple: A tuple containing the response content and possible model output, is parsing is successful otherwise empty.
        """
        # Placeholder for the actual generation logic based on the registry
        # You'll need to implement the _response_parser and 'res' variable based on your setup
        response_text = self.model.run(input_text, "") 
        return response_text, response_text