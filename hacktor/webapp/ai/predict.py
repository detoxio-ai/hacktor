
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Any

# Define your desired data structure.
class NextPrompts(BaseModel):
    prompts: List[str] = Field(description="List of next prompts")

class OpenAIPredictNextPrompts:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initializes the OpenAIWebCrawler with the given model.

        Args:
            model_name (str): The name of the model to use. Defaults to "gpt-4o-mini".
        """
        # Initialize the PromptTemplate with the format
        self.prompt_template = PromptTemplate(
            input_variables=["prompt", "response"],
            template="""
            You are an assistant helping a human to crawl the remote AI system by conversing with it. You are tasked to provide follow-up prompts based on options provided by a remote system. Given the following prompt and response, your task is to create multiple next prompts that align with the options outlined in the response.

            Here's the structure you need to follow:

            1. **Analyze the provided response**: Identify the different options or suggestions given in the response.
            2. **Generate Follow-Up Prompts**: Create prompts based on these options, ensuring each prompt aligns with one of the options presented in the response.

            <prompt>
            {prompt}
            </prompt>

            <response>
            {response}
            </response>

            Your task is to provide next prompts that a human can provide to the remote system. Specific prompts should be at the top, open ended should be at the bottom. Please format your output as a JSON array of strings, where each string represents a possible follow-up prompt. Your JSON response should follow this structure:

            ```json
            ["Prompt1", "Prompt2", "Prompt3"]
            """
            )
        
        # Initialize the model
        self.model = ChatOpenAI(model=model_name)

    def next_prompts(self, prompt_text: str, http_response_text: str) -> List[str]:
        """
        Generates a list of follow-up prompts based on the provided prompt and response.

        Args:
            prompt_text (str): The initial prompt given to the remote system.
            http_response_text (str): The response from the remote system containing options.

        Returns:
            List[str]: A list of follow-up prompts formatted as JSON array of strings.
        """
        # Create a JSON output parser using the NextPrompts data structure
        parser = JsonOutputParser(pydantic_object=NextPrompts)

        # Create a chain with the prompt template, model, and JSON parser
        chain = self.prompt_template | self.model | parser

        # Invoke the model with the formatted prompt
        prompts = chain.invoke(
            {
                "prompt": prompt_text,
                "response": http_response_text
            }
        )
                
        # Return the parsed response as a list of prompts
        return prompts


