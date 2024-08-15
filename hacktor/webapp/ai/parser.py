from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate

class OpenAIResponseExtractor:
    def __init__(self, model_name="gpt-4o-mini"):
        # Initialize the PromptTemplate with the format
        self.prompt_template = PromptTemplate(
            input_variables=["prompt", "response"],
            template="""
You are an assistant that parse the latest response from a remote model http_response. http_response may contain prompts and historical conversations.
Your task is to extract the response from the http response returned by a remote model, based on the provided prompt within <prompt>. 
The http_response is provided within <http_response>. The http_response may contain prompts and the latest response from the remote AI model.

<prompt>
{prompt}
</prompt>

<http_response>
{response}
</http_response>

Provide only the response without any additional text or details
"""
        )

        # Initialize the model
        self.model = ChatOpenAI(model=model_name)

    def extract_response(self, prompt_text, http_response_text):
        # Prepare the input for the model
        formatted_prompt = self.prompt_template.format(prompt=prompt_text, response=http_response_text)

        # Invoke the model with the formatted prompt
        response = self.model.invoke(
            [HumanMessage(content=formatted_prompt)]
        )

        # Extract and return the response from the model's output
        if response and isinstance(response, AIMessage):
            return response.content.strip()
        else:
            return ""
