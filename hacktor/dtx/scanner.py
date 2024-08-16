import os
import logging
import grpc
import copy
import json

from contextlib import contextmanager

from .generator import DetoxioPromptGenerator
from .evaluator import DetoxioPromptResponseEvaluator
import proto.dtx.services.prompts.v1.prompts_pb2 as prompts_pb2
import proto.dtx.services.prompts.v1.prompts_pb2_grpc as prompts_pb2_grpc
import proto.dtx.messages.common.threat_pb2 as dtx_threat_pb2
import proto.dtx.messages.common.industry_pb2 as dtx_industry_pb2
import proto.dtx.messages.common.llm_pb2 as llm_pb2
import proto.dtx.services.prompts.v1.prompts_pb2 as dtx_prompts_pb2
import google.protobuf.empty_pb2 as empty_pb2
from google.protobuf.json_format import MessageToDict
from markdown_builder.document import MarkdownDocument
from .parser import DetoxioEvaluationResponseParser, DetoxioResponseEvaluationResult


class DetoxioGeneratorFilterBuilder:
    def __init__(self):
        self._filter = dtx_prompts_pb2.PromptGenerationFilterOption()
        self._industries:str = "All"
        self._threat_classes:str = "All"
        self._threat_categories:str = "All"
        self._deceptiveness = ""
        self._lineage = ""
        
    @classmethod
    def get_threat_classes(self):
        return list(filter(lambda x: "UNSPECIFIED" not in x, map(lambda x: x[0].replace("THREAT_CLASS_", ""), dtx_threat_pb2.ThreatClass.items())))
        
    @classmethod
    def get_threat_categories(self):
        return list(filter(lambda x: "UNSPECIFIED" not in x, map(lambda x: x[0].replace("THREAT_CATEGORY_", ""), dtx_threat_pb2.ThreatCategory.items())))
        
    @classmethod
    def get_industries(self):
        return list(filter(lambda x: "UNSPECIFIED" not in x, map(lambda x: x[0].replace("INDUSTRY_DOMAIN_", ""), dtx_industry_pb2.IndustryDomain.items())))
    
    def _get_threat_class(self, cl:str) -> int:
        for tc, v in dtx_threat_pb2.ThreatClass.items():
            if cl.lower() in tc.lower():
                return v
        raise ValueError(f"Unknown threat class {cl}")
    
    def _get_threat_category(self, cat:str) -> int:
        if not cat:
            return self
        for tc, v in dtx_threat_pb2.ThreatCategory.items():
            if cat.lower() in tc.lower():
                return v
        raise ValueError(f"Unknown threat category {cat}")
    
    def _get_industry(self, ind:str) -> int:
        if not ind:
            return 0
        for tc, v in dtx_industry_pb2.IndustryDomain.items():
            if ind.lower() in tc.lower():
                return v
        raise ValueError(f"Unknown industry {ind}")

    def threat_class(self, tc:str):
        if not tc:
            return self
        self._filter.threat_class = self._get_threat_class(tc)
        self._threat_classes=tc
        return self

    def threat_category(self, cat:str):
        if not cat:
            return self
        self._filter.threat_category = self._get_threat_category(cat)
        self._threat_categories=cat
        return self

    def industry(self, ind:str):
        if not ind:
            return self
        self._filter.industry = self._get_industry(ind)
        self._industries = ind
        return self

    def label(self, key:str, value:str):
        self._filter.labels[key] = value
        return self

    def deceptiveness(self, value:str):
        if not value:
            return self
        possible_values = ["low", "medium", "high"]
        if not value or value.lower() not in possible_values:
            raise ValueError(f"Unknown deceptiveness {','.join(possible_values)}")
        self.label("deceptiveness", value.lower())
        self._deceptiveness=value
        return self

    def lineage(self, value:str):
        if not value:
            return self
        possible_values = ["detoxio.attackio", "detoxio"]
        if not value or value.lower() not in possible_values:
            raise ValueError(f"Unknown lineage {value} not in {','.join(possible_values)}")
        self.label("lineage", value.lower())
        self._lineage=value
        return self

    def build_filter(self):
        return self._filter


class DetoxioModelDynamicScanner(object):
    """
    DetoxioModelDynamicScanner class for dynamic scanning using detoxio.ai.

    This class provides a context manager for creating and managing connections to detoxio.ai services.
    It includes methods for generating prompts and evaluating model responses for vulnerability.

    """
    def __init__(self, host='api.detoxio.ai', port=443, api_key=None):
        """
        Initialize DetoxioModelDynamicScanner.

        Args:
            host (str): Hostname of the detoxio.ai API (default is 'api.detoxio.ai').
            port (int): Port number for the detoxio.ai API (default is 443).
            api_key (str): API key for authentication (if not provided, check for DETOXIO_API_KEY environment variable).

        Raises:
            ValueError: If the API key is not provided.
        """
        # Verify we have an API key or fail fast
        dtx_api_host = host
        dtx_api_port = port
        detoxio_api_key = api_key or os.getenv('DETOXIO_API_KEY')
        if detoxio_api_key is None:
            raise ValueError('Please set DETOXIO_API_KEY environment variable')

        logging.debug(f"Creating gRPC channel to detoxio.ai backend at {dtx_api_host}:{dtx_api_port}")

        # Initialize connection to detoxio.ai backend
        token = grpc.access_token_call_credentials(detoxio_api_key)
        self._channel = grpc.secure_channel(f'{dtx_api_host}:{dtx_api_port}',
            grpc.composite_channel_credentials(grpc.ssl_channel_credentials(), token))

        self._client = prompts_pb2_grpc.PromptServiceStub(self._channel) 
        self._generator = DetoxioPromptGenerator(self._client)
        self._evaluator = DetoxioPromptResponseEvaluator(self._client)
    

    def is_alive(self):
        return self._client.Ping(empty_pb2.Empty())


    @contextmanager
    def new_session(self):
        yield DetoxioModelDynamicScannerSession(self._generator, self._evaluator)


class InMemoryScannerResults:

    def __init__(self):
        self._results:list[DetoxioResponseEvaluationResult] = []
        self.__parser = DetoxioEvaluationResponseParser()
    
    def add_result(self, prompt, model_output, evaluation_response, model_name="default"):
        eval_res_dict = MessageToDict(evaluation_response)
        
        res:DetoxioResponseEvaluationResult = self.__parser.parse(eval_res_dict)
        self._results.append(res)
    
    def total_results(self) -> int:
        return len(self._results)
    
    def count_unsafe_results(self) -> int:
        return len(self.unsafe_results() )

    def unsafe_results(self) -> list:
        return list(filter(lambda x: x.is_unsafe(), self._results) )

    # def __get_threat_cat_stats(self):
    #     report = {}
    #     for result in self._results:
    #         for status, cat in result.get_threat_category_and_status_pair():
    #             report[cat] = report.get(cat, {})
    #             report[cat][status] = report[cat].get(status, 0) + 1


    def as_markdown(self, model_name=""):
        total = self.total_results()
        unsafe_results = self.unsafe_results()
        count_unsafe_results = self.count_unsafe_results()

        md = MarkdownDocument()
        md.append_heading('LLM Safety Analysis Report', level=1)
        md.append_heading('Executive Sumary', level=2)
        md.append_heading(f"Score {int(100-count_unsafe_results*100/total)}/100:", level=3)
        if model_name:
            md.append_text(f"Model: {model_name}")
        md.append_text(f"Total Tests {total}, Failed Tests {count_unsafe_results}")
        th_cat_count = {}
        for result in unsafe_results:
            for cat in result.get_unsafe_threat_categories():
                th_cat_count[cat] = th_cat_count.get(cat, 0) + 1
        
        if len(th_cat_count) > 0: 
            md.append_text(f"Threats Detected:")
            for cat, count in th_cat_count.items():
                md.append_bullet(f"{cat} - {count} times")
        md.append_text("\n")
        if count_unsafe_results > 0:
            md.append_heading('FAILED PROMPTS', level=1)
            i = 1
            for result in unsafe_results:

                md.append_heading(f"[{i}] Prompt", level=4)
                md.append_text(f"```{result.prompt_text()}```\n")
                md.append_heading(f"[{i}] Response", level=4)
                md.append_text(f"```{result.response_text_first()}```\n")
                md.append_text_indented(f"Threats: {','.join(result.get_unsafe_threat_categories())}\n", depth=0)

                # md.append_heading('This is a level2 heading', 2)
                # md.append_text_indented('This is inset', depth=1)
                # md.append_bullet('This is a top-level bullet point')
                # md.append_bullet('This is a lower level bullet point', depth=1)
                i += 1
                if i >= 10:
                    break
        return md.contents()

    def as_dict(self):
        dict_results = list(map(lambda x: x.as_dict(), self._results))
        return dict_results

    def _save_json_report(self, out_path):
        if out_path:
            with open(out_path, "w") as out:
                json.dump(self.as_dict(), out)

    def _save_markdown_report(self, out_path):
        if out_path:
            with open(out_path, "w") as out:
                out.write(self.as_markdown())

    def save_report(self, json_path="", markdown_path=""):
        self._save_json_report(json_path)
        self._save_markdown_report(markdown_path)


class DetoxioModelDynamicScannerSession:

    def __init__(self, generator, evaluator):
        self._generator = generator
        self._evaluator = evaluator
        self._report = InMemoryScannerResults()

    def __enter__(self):
        # Nothing special to do when entering the context
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Clean up resources if needed when exiting the context
        pass

    def generate(self, count=10, filter:dtx_prompts_pb2.PromptGenerationFilterOption=None):
        """
        Generate a specified number of prompts.

        Args:
            count (int): Number of prompts to generate (default is 10).

        Returns:
            Generator of prompts.
        """
        return self._generator.generate(count=count, filter=filter)

    def evaluate(self, prompt: prompts_pb2.Prompt, model_output_text: str) -> prompts_pb2.PromptEvaluationResponse:
        """
        Evaluate a model interaction for vulnerability.

        Args:
            prompt: Prompt object to be evaluated.
            model_output_text: Text generated by the model in response to the prompt.

        Returns:
            Evaluation response as a prompts_pb2.PromptEvaluationResponse object.
        """
        eval_result = self._evaluator.evaluate(prompt, model_output_text)
        self._report.add_result(prompt, model_output_text, eval_result)
        return eval_result
    
    def get_report(self):
        return self._report
    
