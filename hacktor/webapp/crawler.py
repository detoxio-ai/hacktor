from enum import Enum
import networkx as nx
from collections import deque
from typing import Deque, Tuple, List
from hacktor.utils.printer import BasePrinter
from hacktor.webapp.ai.predict import NextPrompts


class TraversalStrategy(Enum):
    BFS = "BFS"
    DFS = "DFS"

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
    
    def next_prompts(self, prompt_text: str, response_text: str) -> NextPrompts:
        """Generate next prompts 

        Args:
            prompt_text (str): _description_
            response_text (str): _description_

        Raises:
            Exception: _description_

        Returns:
            NextPrompts: _description_
        """
        raise Exception("Not Implemented")

class ModelCrawlerOptions:
    def __init__(self, max_depth: int, 
                 initial_prompts: List[str],
                 max_steps:int=None,
                 strategy: TraversalStrategy = TraversalStrategy.DFS):
        """
        Initialize CrawlerOptions with max depth and initial prompts.

        Parameters:
        - max_depth (int): The maximum depth of the conversation tree to explore.
        - initial_prompts (List[str]): List of initial prompts to start the conversation.
        """
        self.max_depth = max_depth
        self.initial_prompts = initial_prompts
        self.max_steps = max_steps or 100000000 # Some large number
        self.strategy = strategy


class ModelCrawler:
    
    def __init__(self, model_factory: ModelFactory, 
                 prompt_generator: NextPromptGenerator,
                 options: ModelCrawlerOptions,
                 printer: BasePrinter = None):
        """
        Initialize ModelCrawler with a model factory, prompt generator, and options.

        Parameters:
        - model_factory (ModelFactory): The factory to create or get model instances.
        - prompt_generator (NextPromptGenerator): The generator for the next prompts.
        - options (ModelCrawlerOptions): Options for crawling, including max depth and initial prompts.
        - strategy (TraversalStrategy): Strategy for traversal, either BFS or DFS.
        - printer (BasePrinter): Optional printer object for logging information.
        """
        self.model_factory = model_factory
        self.prompt_generator = prompt_generator
        self.options = options
        self.printer = printer or BasePrinter()
        
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
        
        # Use a deque to implement the queue (FIFO for BFS, LIFO for DFS)
        queue: Deque[Tuple[int, str, int]] = deque()
        
        # Enqueue all initial prompts
        for prompt in self.options.initial_prompts:
            queue.append((root_id, prompt, self.options.max_depth))
        
        bar = self.printer.progress_bar("Crawling", len(queue) or 4)
        # Process the queue
        while queue and self.node_counter < self.options.max_steps:
            # self.printer.info(f"Queue length: {len(queue)}, Processed: {self.node_counter}")
            if self.options.strategy == TraversalStrategy.BFS:
                parent_id, current_prompt, depth = queue.popleft()
            else:  # DFS
                parent_id, current_prompt, depth = queue.pop()
            self.printer.trace(f"Processing Node: {current_prompt} at depth {self.options.max_depth - depth}")
            
            processed = self._process_node(queue, parent_id, current_prompt, depth)
            if processed:
                bar.next(max=self.node_counter+len(queue))
    
    def _process_node(self, queue: Deque[Tuple[int, str, int]], 
                      parent_id: int, 
                      current_prompt: str, 
                      depth: int) -> bool:
        """
        Process a single node in the tree.

        Parameters:
        - queue (Deque): The queue used for BFS or DFS traversal.
        - parent_id (int): The ID of the parent node in the tree.
        - current_prompt (str): The current prompt to use.
        - depth (int): Remaining depth to traverse.
        Returns:
         - Status whether any node is processed
        """
        if depth == 0:
            self.printer.trace(f"Reached max depth with prompt: {current_prompt}")
            return False
        
        # Get the current model instance and generate a response
        model = self.model_factory.get()
        _, response = model.generate(current_prompt)
        
        # Create a new node ID for this prompt-response pair
        node_id = self.node_counter
        self.tree.add_node(node_id, prompt=current_prompt, response=response, next_prompts=[])
        self.node_counter += 1
        
        self.printer.trace(f"Generated Response: {response} for Prompt: {current_prompt}")

        # Add an edge from the parent to the current node
        self.tree.add_edge(parent_id, node_id)
        
        # Generate the next set of prompts based on the current prompt and response
        next_prompts = self.prompt_generator.next_prompts(current_prompt, response)
        
        if not next_prompts.prompts:
            self.printer.trace(f"No further prompts for: {current_prompt}, stopping here.")
            return  # No next prompts, stop further processing
        
        # As next prompts are left prioritized, reverse the priority in case of DFS, before inserting
        if self.options.strategy == TraversalStrategy.DFS:
            next_prompts.prompts.reverse()
                   
        # Update the next prompts for the current node
        self.tree.nodes[node_id]["next_prompts"] = next_prompts.prompts
        self.tree.nodes[node_id]['template'] = next_prompts.template
        
        # Enqueue the next prompts
        for next_prompt in next_prompts.prompts:
            queue.append((node_id, next_prompt, depth - 1))
            self.printer.trace(f"Enqueued next prompt: {next_prompt} at depth {self.options.max_depth - (depth - 1)}")
        return True
    
    def print_tree(self):
        """
        Print the conversation tree in a human-friendly format with nodes and indentation.
        """
        def print_subtree(node_id, indent=""):
            node_data = self.tree.nodes[node_id]
            prompt = node_data.get('prompt')
            response = node_data.get('response')
            template = node_data.get('template')
            
            if prompt is None:
                print(f"{indent}Root")
            else:
                # print(f"{indent}Node ID: {node_id}")
                print(f"{indent}  Prompt: {prompt} Template: {template}")
                # print(f"{indent}  Response: {response}")
                
            # Recursively print each child node, with increased indentation
            for child_node in self.tree.successors(node_id):
                print_subtree(child_node, indent + "    ")

        root_node = 0  # Assuming the root node has ID 0
        print_subtree(root_node)

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

    
    