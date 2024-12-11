

from enum import Enum
from typing import List
from .groq import GroqModel
from .openai import OpenAIModel
from hacktor.webapp.gradio import GradioUtils
from hacktor.webapp.model import GradioAppModel

import importlib
# Check if torch is installed, then import HFModelFactory
torch_spec = importlib.util.find_spec("torch")
if torch_spec is not None:
    from .hf import HFModelFactory

class Registry(Enum):
    GROQ = "GROQ"
    OPENAI = "OPENAI"
    HF = "HF"  # Hugging Face
    HF_SPACE = "HF_SPACE"

    @classmethod
    def list_options(cls):
        return [option.value for option in cls]

class LLMModel:

    def __init__(self, registry, model_id, fuzz_markers:List[str], use_ai:bool=False):
        rutils = GradioUtils()
        # Placeholder for future registry-specific setup
        if registry == Registry.GROQ:
            self.model = GroqModel(model_id)
        elif registry == Registry.OPENAI:
            self.model = OpenAIModel(model_id)
        elif registry == Registry.HF:
            self.model = HFModelFactory.get_instance(model_id)
        elif registry == Registry.HF_SPACE:
            api_name, predict_signature = rutils.parse_api_signature(model_id, fuzz_markers[0])
            # Detect the Gradio API signature
            self.model = GradioAppModel(model_id, api_name, predict_signature, fuzz_markers)
            self.model.prechecks(use_ai=use_ai)
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