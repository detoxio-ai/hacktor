import logging
from .exceptions import InvalidInputException

class BaseModel:
    """
    Base model class with common functionalities for listing models.
    """
    _logger = logging.getLogger(__name__)

    _MODELS = {}

    def __init__(self):
        """
        Initialize the BaseModel.
        """
        if not self._MODELS:
            raise NotImplementedError("Subclasses should define a _MODELS dictionary.")

    def list_models(self):
        """
        List all available models.
        
        Returns:
            list: A list of model names.
        """
        return list(self._MODELS.keys())

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
