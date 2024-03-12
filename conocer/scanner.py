import os
import logging
import grpc
from .generator import DetoxioPromptGenerator
from .evaluator import DetoxioPromptResponseEvaluator
import proto.dtx.services.prompts.v1.prompts_pb2 as prompts_pb2
import proto.dtx.services.prompts.v1.prompts_pb2_grpc as prompts_pb2_grpc
import proto.dtx.messages.common.llm_pb2 as llm_pb2

import google.protobuf.empty_pb2 as empty_pb2

from google.protobuf.json_format import MessageToDict


class DetoxioModelTester(object):
    def __init__(self, host='api.detoxio.ai', port=443, api_key=None):
        # Verify we have an API key or fail fast
        dtx_api_host = host
        dtx_api_port = port
        detoxio_api_key = api_key or os.getenv('DETOXIO_API_KEY')
        if detoxio_api_key is None:
            raise ValueError('Please set DETOXIO_API_KEY environment variable')

        logging.debug(f"Creating gRPC channel to detoxio.ai backend at {dtx_api_host}:{dtx_api_port}")

        # Initialize connection to detoxio.ai backend
        token = grpc.access_token_call_credentials(detoxio_api_key)
        channel = grpc.secure_channel(f'{dtx_api_host}:{dtx_api_port}',
            grpc.composite_channel_credentials(grpc.ssl_channel_credentials(), token))

        self._client = prompts_pb2_grpc.PromptServiceStub(channel) 
        self._generator = DetoxioPromptGenerator(self._client)
    
    
    