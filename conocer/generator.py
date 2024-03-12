
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

LOGGER = logging.getLogger("Prompt Generator")

class DetoxioPromptGenerator(object):
    logger = logging.getLogger(__name__)

    def __init__(self, client):
        self._client = client

    def generate(self, count=10) -> iter<prompts_pb2.Promp>t:
        for i in range(0, count):
            yield(self._get_a_prompt())


    # Use detoxio.ai to get a prompt for testing
    @retry(tries=3, delay=5, max_delay=60, backoff=5, logger=LOGGER)
    def _get_a_prompt(self, count=1) -> prompts_pb2.Prompt:
        req = prompts_pb2.PromptGenerationRequest(count=count)
        return self._client.GeneratePrompts(req)
