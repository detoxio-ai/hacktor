
#!/usr/bin/env python

import os
import json
import argparse
import grpc
import logging
from retry import retry

import proto.dtx.services.prompts.v1.prompts_pb2 as prompts_pb2
import proto.dtx.services.prompts.v1.prompts_pb2_grpc as prompts_pb2_grpc
import proto.dtx.messages.common.llm_pb2 as llm_pb2

import google.protobuf.empty_pb2 as empty_pb2

from google.protobuf.json_format import MessageToDict

LOGGER = logging.getLogger("Prompt Response Evaluator")

class DetoxioPromptResponseEvaluator(object):
    logger = logging.getLogger(__name__)

    def __init__(self, client):
        self._client = client

    def evaluate(self, prompt:prompts_pb2.Prompt, model_output_text:str) -> prompts_pb2.PromptEvaluationResponse:
        return self._evaluate_prompt_response(prompt, model_output_text)


    # Use detoxio.ai to evaluate a model interaction for vulnerability
    @retry(tries=3, delay=5, max_delay=60, backoff=5, logger=LOGGER)
    def _evaluate_prompt_response(self, prompt:prompts_pb2.Prompt, model_output_text:str) -> prompts_pb2.PromptEvaluationResponse:
        req = prompts_pb2.PromptEvaluationRequest()
        req.prompt.CopyFrom(prompt)
        
        req.responses.extend([prompts_pb2.PromptResponse(message=llm_pb2.LlmChatIo(content=model_output_text))])
        return self._client.EvaluateModelInteraction(req)
