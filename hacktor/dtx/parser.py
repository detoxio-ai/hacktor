import json
import copy
from typing import Dict

class DetoxioResponseEvaluationResult:
    def __init__(self, result: dict):
        """
        Initialize DetoxioResponseEvaluationResult object.

        Args:
            result (dict): Dictionary containing evaluation results.
                Example:
                {
                    'prompt': {
                        'generated_at': '2024-03-12T09:48:52.281643957Z',
                        'data': {
                            'content': '...'
                        }
                    },
                    'status': 'THREAT_EVALUATION_STATUS_SAFE',
                    'responses': [
                        {
                            'message': {'content': '...'},
                            'status': 'THREAT_EVALUATION_STATUS_SAFE',
                            'threats': [
                                {'threat': {'threat_class': 'TOXICITY', 'threat_category': 'ABUSIVE_LANGUAGE'}, 'status': 'THREAT_EVALUATION_STATUS_SAFE'},
                                ...
                            ]
                        },
                        ...
                    ]
                }
        """
        self.__result = result
    
    def prompt(self):
        """
        Get the prompt from the evaluation result.

        Returns:
            dict: The prompt.
        """
        return self.__result["prompt"]

    def prompt_text(self):
        """
        Get the prompt from the evaluation result.

        Returns:
            dict: The prompt.
        """
        return self.__result["prompt"]["data"]["content"]
    
    def response_text_first(self):
        """
        Get the prompt from the evaluation result.

        Returns:
            dict: The prompt.
        """
        return self.__result["responses"][0]["message"]["content"]

    def status(self):
        """
        Get the overall status from the evaluation result.

        Returns:
            str: The overall status.
        """
        return self.__result["status"]
    
    def is_unsafe(self):
        return "THREAT_EVALUATION_STATUS_UNSAFE" in self.status().upper()
    
    def threats(self, filter_by_status: str = None) -> Dict:
        """
        Get threats from the evaluation result.

        Args:
            filter_by_status (str, optional): Filter threats by status. Defaults to None.

        Returns:
            dict: A generator yielding threat dictionaries.
                Example:
                {
                    'threat': {'threat_class': 'TOXICITY', 'threat_category': 'ABUSIVE_LANGUAGE'},
                    'status': 'THREAT_EVALUATION_STATUS_SAFE'
                }
        """
        if not filter_by_status:
            filter_by_status = ['THREAT_EVALUATION_STATUS_UNSAFE', 'THREAT_EVALUATION_STATUS_SAFE']
        else:
            filter_by_status = [filter_by_status]
        for response in self.__result["responses"]:
            for threat in response.get("threats", []):
                if threat["status"] in filter_by_status:
                    yield(copy.copy(threat))
    
    def unsafe_threats(self):
        """
        Get the unsafe threats from the evaluation result.

        Returns:
            Iterator[dict]: An iterator yielding dictionaries representing unsafe threats.
                Example:
                [
                    {
                        'threat': {'threat_class': 'TOXICITY', 'threat_category': 'ABUSIVE_LANGUAGE'},
                        'status': 'THREAT_EVALUATION_STATUS_SAFE'
                    }
                ]
        """
        return self.threats(filter_by_status="THREAT_EVALUATION_STATUS_UNSAFE")

    def safe_threats(self):
        """
        Get the safe threats from the evaluation result.

        Returns:
            Iterator[dict]: An iterator yielding dictionaries representing safe threats.
                Example:
                [
                    {
                        'threat': {'threat_class': 'TOXICITY', 'threat_category': 'ABUSIVE_LANGUAGE'},
                        'status': 'THREAT_EVALUATION_STATUS_SAFE'
                    }
                ]
        """
        return self.threats(filter_by_status="THREAT_EVALUATION_STATUS_SAFE")


    def get_threat_category_and_status_pair(self):
        """
        Get pairs of threat category and status from the evaluation result.

        Yields:
            tuple: A tuple containing the threat status and threat category.
                Example:
                ('THREAT_EVALUATION_STATUS_SAFE', 'ABUSIVE_LANGUAGE')
        """
        for threat in self.threats():
            yield((threat['status'], threat['threat']['threat_category']))
            
    def get_threat_class_and_status_pair(self):
        """
        Get pairs of threat class and status from the evaluation result.

        Yields:
            tuple: A tuple containing the threat status and threat class.
                Example:
                ('THREAT_EVALUATION_STATUS_SAFE', 'TOXICITY')
        """
        for threat in self.threats():
            yield((threat['status'], threat['threat']['threat_class']))


    def get_unsafe_threat_categories(self):
        """
        Get pairs of threat category and status from the evaluation result.

        Yields:
            tuple: A tuple containing the threat status and threat category.
                Example:
                ('THREAT_EVALUATION_STATUS_SAFE', 'ABUSIVE_LANGUAGE')
        """
        for threat in self.threats(filter_by_status="THREAT_EVALUATION_STATUS_UNSAFE"):
            yield(threat['threat']['threat_category'])


    def as_dict(self):
        """
        Return the evaluation result as a dictionary.

        Returns:
            dict: A copy of the evaluation result dictionary.
        """
        return copy.copy(self.__result)


    


class DetoxioEvaluationResponseParser:

    def __init__(self):
        pass

    def parse(self, eval_result: dict) -> DetoxioResponseEvaluationResult:
        """
        Parse evaluation results.

        Args:
            eval_result (dict): Evaluation results dictionary.

        Returns:
            DetoxioResponseEvaluationResult: An instance of DetoxioResponseEvaluationResult.
        """
        prompt = eval_result["prompt"]
        r = {
            "prompt": prompt,
            "status": "THREAT_EVALUATION_STATUS_SAFE",
            "responses": []
        }
        for response in eval_result["responses"]:
            eval_response = {
                "message": response['response']["message"],
                "status": "THREAT_EVALUATION_STATUS_SAFE",
                "threats": []
            }
            for threat in response.get("results", {}):
                if threat["status"] == 'THREAT_EVALUATION_STATUS_UNSAFE':
                    # Set the overall threats result as unsafe
                    eval_response["status"] = "THREAT_EVALUATION_STATUS_UNSAFE"
                eval_response["threats"].append(threat)
            if eval_response["status"] == "THREAT_EVALUATION_STATUS_UNSAFE":
                # Set the overall result as unsafe
                r["status"] = "THREAT_EVALUATION_STATUS_UNSAFE"
            r["responses"].append(eval_response)

        return DetoxioResponseEvaluationResult(r)