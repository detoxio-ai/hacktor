import logging
from retry import retry
from .exceptions import InvalidInputException
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from .exceptions import NoneResultException
from .utils import escape_special_characters
from .base import BaseModel

class OpenAIModel(BaseModel):
    """
    Model that talks to the OpenAI service to interact with models.
    """
    _logger = logging.getLogger(__name__)
    _MODELS = {
        "gpt-4o": "gpt-4o"
    }

    DEFAULT_MODEL_PARAMS = {
        "temperature": 0.7,
    }
    
    def __init__(self, model_name="gpt-4o"):
        """
        Initialize the OpenAIModel with the given model.
        
        Args:
            model_name (str): The name of the model to use.
        """
        super().__init__()
        model_id = self._name2model_id(model_name)
        self.model = ChatOpenAI(model=model_id, **self.DEFAULT_MODEL_PARAMS)
        self.parser = StrOutputParser()

    def _name2model_id(self, model_name):
        """
        Convert a model name to its corresponding model ID.
        
        Args:
            model_name (str): The name of the model.
        
        Returns:
            str: The corresponding model ID.
        
        Raises:
            InvalidInputException: If the model name is not supported.
        """
        model_id = self._MODELS.get(model_name)
        if model_id is None:
            self._logger.debug("Model %s not found. Options: %s", model_name, self._MODELS.keys())
            raise InvalidInputException(f"Model {model_name} is not supported")
        return model_id

    @retry((NoneResultException), tries=3, delay=2, backoff=2, logger=logging)
    def run(self, prompt: str, system: str=None):
        """
        Run the prompt analysis with retry logic.
        
        Args:
            prompt (str): The prompt to analyze.
        
        Returns:
            Any: The result of the prompt analysis.
        
        Raises:
            NoneResultException: If the result is None after all retry attempts.
        """
        message = []
        if system:
            message.append(("system", system))
        
        escaped_prompt = escape_special_characters(prompt)
        message.append(("human", escaped_prompt))
        prompt = ChatPromptTemplate.from_messages(message)

        chain = prompt | self.model | self.parser
        result = chain.invoke({})
        if result is None:
            raise NoneResultException()
        return result
