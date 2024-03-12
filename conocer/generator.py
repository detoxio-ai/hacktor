#!/usr/bin/env python

import os
import json
import argparse
import grpc
import logging
from retry import retry
from typing import List

import proto.dtx.services.prompts.v1.prompts_pb2 as prompts_pb2
import proto.dtx.services.prompts.v1.prompts_pb2_grpc as prompts_pb2_grpc
import proto.dtx.messages.common.llm_pb2 as llm_pb2

import google.protobuf.empty_pb2 as empty_pb2
from google.protobuf.json_format import MessageToDict

# Set up a logger for the Prompt Generator
LOGGER = logging.getLogger("Prompt Generator")

class DetoxioPromptGenerator(object):
    """DetoxioPromptGenerator class for generating prompts using detoxio.ai."""

    # Class-level logger for detailed logging within the class
    logger = logging.getLogger(__name__)

    def __init__(self, client):
        """
        Initialize DetoxioPromptGenerator.

        Args:
            client: gRPC client for communication with detoxio.ai services.
        """
        self._client = client

    def generate(self, count=10) -> List[prompts_pb2.Prompt]:
        """
        Generate a specified number of prompts.

        Args:
            count: Number of prompts to generate (default is 10).

        Yields:
            Generator of prompts.
        """
        for i in range(0, count):
            prompt_response = self._get_a_prompt()
            for prompt in prompt_response.prompts:
                yield(prompt)

    @retry(tries=3, delay=1, max_delay=60, backoff=5, logger=LOGGER)
    def _get_a_prompt(self, count=1) -> prompts_pb2.Prompt:
        """
        Retrieve a prompt from detoxio.ai.

        Args:
            count: Number of prompts to retrieve (default is 1).

        Returns:
            A single prompt as a prompts_pb2.Prompt object.
        """
        req = prompts_pb2.PromptGenerationRequest(count=count)
        return self._client.GeneratePrompts(req)
