import logging
import asyncio
import validators
import playwright
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import networkx as nx
from typing import List, Dict, Optional


class HumanAssistedWebCrawler:
    def __init__(self, headless=False, speed=300, browser_name="Chromium", fuzz_marker="[FUZZ]"):
        self._headless = headless
        self._speed = speed
        self._browser_name = browser_name
        self._fuzz_marker = fuzz_marker
    
    def crawl(self, url, session_file_path, handle_request_fn=None):
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.async_crawl(url, session_file_path, handle_request_fn))
        loop.run_until_complete(task)

    def _handle_request(self, request):
        pass
        # logging.debug(f'>> {request.method} {request.url} \n')  
        # if request.method in ["POST", "PUT"]:
        #     post_data = request.post_data
            # if post_data and self._fuzz_marker in post_data:
            #     print("Found request to be fuzzed: ", f'>> {request.method} {request.url} {post_data} \n')

    def on_web_socket(self, ws):
        logging.warn(f"""
                     Unsupported ##############\nApp is using Web Sockets. 
                     Hacktor does not support Web Sockets yet!!!\n
                     WebSocket opened on URL {ws.url}
                     ##############""")
        ws.send
        # print(f"WebSocket opened: {ws.url}")
        # ws.on("framesent", lambda payload: print("Frame sent:", payload))
        # ws.on("framereceived", lambda payload: print("Frame received:", payload))
        # ws.on("close", lambda payload: print("WebSocket closed"))


    async def async_crawl(self, url, session_file_path, handle_request_fn=None):
        if not validators.url(url):
            raise Exception(
                "The url provided is malformed. Exiting Crawling procedure.")
        domain_name = urlparse(url).netloc
        # har_file_path = f'{domain_name.replace(".","_")}-report.har'
        async with async_playwright() as p:
            try:
                if self._browser_name == "Webkit":
                    browser_instance = p.webkit
                elif self._browser_name == "Firefox":
                    browser_instance = p.firefox
                else:
                    browser_instance = p.chromium
                if not self._headless:
                    browser = await browser_instance.launch(headless=False,
                                                            slow_mo=self._speed)
                else:
                    browser = await browser_instance.launch(headless=True,
                                                            slow_mo=self._speed)
                context = await browser.new_context(record_har_path=session_file_path)
                context.set_default_timeout(0)
                page = await context.new_page()
                handle_request_fn = handle_request_fn or self._handle_request
                page.on(
                    "request", lambda request: handle_request_fn(request))
                page.on(
                    "response", lambda response: logging.debug(
                        f'<< {response.status} {response.url} \n'))
                page.on("close", lambda: logging.debug("Browser Closed Successfully"))
                page.on("websocket", self.on_web_socket)
                await page.goto(url)
                await page.title()
                await page.wait_for_selector('text="None"')
            except playwright._impl._errors.TargetClosedError:
                pass
            except Exception as e:
                logging.exception("Page got closed manually or got crashed %s", e)
            finally:
                await page.close()
                await context.close()
                await browser.close()
                logging.debug(
                    f"The complete networking details can be found in {session_file_path}"
                )


class AbstractRemoteModel:
    
    def generate(self, input_text):
        """
        Generate a response from the remote model.

        Parameters:
        - input_text (str): The input text for generating the response.

        Returns:
        - tuple: A tuple containing the response content and possible model output, is parsing is successful otherwise empty.
        """
        raise Exception("Not Implemented")

class ModelFactory:
    
    def new(self) -> AbstractRemoteModel:
        """ 
            Return new instance of the model
        """
        raise Exception("Not Implemented")
        
    def get(self) -> AbstractRemoteModel:
        """
            Get current instance of the model
        """
        raise Exception("Not Implemented") 
    
class NextPromptGenerator:
    
    def next_prompts(self, prompt_text: str, response_text: str) -> List[str]:
        raise Exception("Not Implemented")

class ModelCrawlerOptions:
    def __init__(self, max_depth: int, 
                 initial_prompts: List[str],
                 max_steps:int=None):
        """
        Initialize CrawlerOptions with max depth and initial prompts.

        Parameters:
        - max_depth (int): The maximum depth of the conversation tree to explore.
        - initial_prompts (List[str]): List of initial prompts to start the conversation.
        """
        self.max_depth = max_depth
        self.initial_prompts = initial_prompts
        self.max_steps = max_steps or 100000000 # Some large number


class ModelCrawler:
    
    def __init__(self, model_factory: ModelFactory, 
                 prompt_generator: NextPromptGenerator,
                 options: ModelCrawlerOptions):
        """
        Initialize ModelCrawler with a model factory, prompt generator, and options.

        Parameters:
        - model_factory (ModelFactory): The factory to create or get model instances.
        - prompt_generator (NextPromptGenerator): The generator for the next prompts.
        - options (ModelCrawlerOptions): Options for crawling, including max depth and initial prompts.
        """
        self.model_factory = model_factory
        self.prompt_generator = prompt_generator
        self.options = options
        self.tree = nx.DiGraph()  # Directed graph to represent the conversation tree
        self.node_counter = 0  # To keep track of node ids
    
    def crawl(self):
        """
        Start crawling based on the options provided during initialization.
        """
        # Initialize the root of the conversation tree
        root_id = self.node_counter
        self.tree.add_node(root_id, prompt=None, response=None, next_prompts=self.options.initial_prompts)
        self.node_counter += 1
        
        # Start the conversation from each initial prompt
        for prompt in self.options.initial_prompts:
            if not self._traverse_conversation(root_id, prompt, self.options.max_depth):
                break  # Stop if traversal completes

    def print_tree(self):
        """
        Print the conversation tree in a human-friendly format with nodes and indentation.
        """
        def print_subtree(node_id, indent=""):
            node_data = self.tree.nodes[node_id]
            print(node_data)
            prompt = node_data.get('prompt')
            response = node_data.get('response')
            
            if prompt is None:
                print(f"{indent}Root")
            else:
                print(f"{indent}Node ID: {node_id}")
                print(f"{indent}  Prompt: {prompt}")
                print(f"{indent}  Response: {response}")
                
            # Recursively print each child node, with increased indentation
            for child_node in self.tree.successors(node_id):
                print(child_node)
                print_subtree(child_node, indent + "    ")

        root_node = 0  # Assuming the root node has ID 0
        print_subtree(root_node)

    
    def _traverse_conversation(self, parent_id: int, current_prompt: str, depth: int) -> bool:
        """
        Recursively traverse the conversation tree.

        Parameters:
        - parent_id (int): The ID of the parent node in the tree.
        - current_prompt (str): The current prompt to use.
        - depth (int): Remaining depth to traverse.

        Returns:
        - bool: True if traversal is successful, False if backtracking is required.
        """
        if depth == 0:
            return False
        # Get the current model instance and generate a response
        print("Current Prompt: ", current_prompt, "\n\n")
        model = self.model_factory.get()
        _, response = model.generate(current_prompt)
        
        # Create a new node ID for this prompt-response pair
        node_id = self.node_counter
        self.tree.add_node(node_id, prompt=current_prompt, response=response, next_prompts=[])
        self.node_counter += 1
        
        print("Node Counter: ", self.node_counter)
        
        if self.node_counter >= self.options.max_steps:
            return False
        
        # Add an edge from the parent to the current node
        self.tree.add_edge(parent_id, node_id)
        
        # Generate the next set of prompts based on the current prompt and response
        next_prompts = self.prompt_generator.next_prompts(current_prompt, response)
        
        print("Pair:", current_prompt, response, next_prompts)
        
        if not next_prompts:
            # If no next prompts, backtrack to the parent node
            return False
        
        # Update the next prompts for the current node
        self.tree.nodes[node_id]["next_prompts"] = next_prompts
        
        # Recursively traverse using the chosen next prompt
        for next_prompt in next_prompts:
            if self._traverse_conversation(node_id, next_prompt, depth - 1):
                return True
        
        # If all next prompts fail, backtrack
        return False

    def get_tree(self):
        """
        Return the conversation tree.
        """
        return self.tree


# Example usage:
# options = CrawlerOptions(max_depth=3, initial_prompts=["Hello", "How are you?"])
# model_factory = YourModelFactoryImplementation()
# prompt_generator = YourNextPromptGeneratorImplementation()
# crawler = ModelCrawler(model_factory, prompt_generator, options)
# crawler.crawl()
# conversation_tree = crawler.get_tree()

    
    