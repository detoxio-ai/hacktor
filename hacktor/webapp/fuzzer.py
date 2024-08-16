import logging
from collections import deque
import networkx as nx
from typing import Deque, List
from hacktor.utils.printer import BasePrinter
from .crawler import ModelCrawler, TraversalStrategy
from hacktor.dtx.scanner import DetoxioModelDynamicScanner
from .crawler import ModelCrawlerOptions


class ModelCrawledState:
    def __init__(self, crawler: ModelCrawler):
        """
        Initialize ModelCrawledState with a ModelCrawler instance.

        Parameters:
        - crawler (ModelCrawler): The model crawler instance from which the fuzzer will derive its tree, model factory, and other settings.
        - strategy (TraversalStrategy): The traversal strategy, either BFS or DFS.
        """
        self.crawler = crawler
        self.crawler_options = crawler.options
        self.tree = crawler.get_tree()
        self.strategy = self.crawler_options.strategy
        self.model_factory = crawler.model_factory
        self.current_model = None  # This will hold the current model instance
        self.current_node_id = 0   # Start at the root node
        self.current_prompt_template = ""

        # Initialize traversal structures based on tree and traversal strategy
        self.nodes_to_visit = self._initialize_nodes_to_visit()
        self._no_of_states = len(self.nodes_to_visit) + 1

    def no_of_states(self) -> int:
        return self._no_of_states

    def _initialize_nodes_to_visit(self):
        """
        Initialize the traversal structure (BFS or DFS) based on the current tree structure and strategy.

        Returns:
        - A deque or list containing the node IDs in the order they should be visited.
        """
        if self.strategy == TraversalStrategy.BFS:
            # Use networkx.bfs_tree to generate nodes in BFS order
            nodes = list(nx.bfs_tree(self.tree, source=0).nodes)
        else:  # DFS
            # Use networkx.dfs_preorder_nodes to generate nodes in DFS pre-order
            nodes = list(nx.dfs_preorder_nodes(self.tree, source=0))
        return deque(nodes[1:])  # Use deque for BFS

    def start(self):
        """
        Reset the fuzzer to the initial state, starting at the root node and creating the initial model.
        This includes resetting the traversal structure (BFS or DFS) and other state variables.
        """
        # Reset current node and model
        self.current_node_id = 0  # Reset to root node
        self.current_model = self.model_factory.new()  # Create a new model for the root

        # Reset the traversal structure
        self.nodes_to_visit = self._initialize_nodes_to_visit()
    
    def invoke(self, prompt: str) -> str:
        """
        Invoke the current model with a specific prompt and return the response.

        Parameters:
        - prompt (str): The prompt to send to the model.

        Returns:
        - str: The response generated by the model.
        """
        if self.current_model is None:
            raise Exception("Fuzzer has not been started. Please call start() before invoking.")
        
        self.current_prompt_template = self.current_prompt_template or "{message}"
        _prompt = self.current_prompt_template.format(message=prompt)
            
        # print("Template", self.current_prompt_template, "Prompt", _prompt)
        _, response = self.current_model.generate(_prompt)
        return response
    
    def next(self):
        """
        Traverse to the next node in the conversation tree based on the selected traversal strategy.
        Update the current_model as per the traversal path, ensuring it reflects the correct state.

        Raises:
        - StopIteration: When there are no more nodes to traverse in the conversation tree.
        """
        if not self.nodes_to_visit:
            raise StopIteration("No further nodes to traverse in the conversation tree.")

        # Get the next node ID based on the traversal strategy
        self.current_node_id = self.nodes_to_visit.popleft()

        # Create a new model instance for the current node's state
        self.current_model = self.model_factory.new()

        # Traverse from root to this node to ensure current model reflects the traversal path
        traversal_path = nx.shortest_path(self.tree, source=0, target=self.current_node_id)
        for node_id in traversal_path[1:]:  # Start from the first child node to follow the path
            node_prompt = self.tree.nodes[node_id]["prompt"]
            self.current_prompt_template = self.tree.nodes[node_id]["template"]
            self.current_model.generate(node_prompt)


class ModelCrawledStateBuilder:
    def __init__(self, crawler: ModelCrawler):
        """
        Initialize ModelCrawledStateBuilder with a ModelCrawler instance.

        Parameters:
        - crawler (ModelCrawler): The model crawler instance that will be used to build the fuzzer.
        """
        self.crawler = crawler
    
    def build(self) -> ModelCrawledState:
        """
        Build and return an instance of ModelCrawledState.

        Returns:
        - ModelCrawledState: A ModelCrawledState instance.
        """
        return ModelCrawledState(self.crawler)


class StatefulModelFuzzerConfig:
    
    def __init__(self, max_tests:int=100, 
                 detoxio_api_key:str=None):
        self.max_tests = max_tests
        self.detoxio_api_key = detoxio_api_key


class StatefulModelFuzzer:
    def __init__(self, config: StatefulModelFuzzerConfig, 
                 model: ModelCrawledState):
        self.config = config 
        self.detoxio_api_key = self.config.detoxio_api_key
        self.model = model
        self._unsafe_results_found = 0
        self._total_tests = 0
        self._MAX_TESTS = self.config.max_tests
        
        # Calculate number of tests per state
        self._tests_per_state = max(int(self._MAX_TESTS / self.model.no_of_states() ), 1)

    def plan(self):
        if callable(self.on_planning_started):
            self.on_planning_started()
        
        # Implement your planning logic here
        
        if callable(self.on_planning_completed):
            self.on_planning_completed()

    def scan(self):
        self.model.start()

        if callable(self.on_fuzzing_started):
            self.on_fuzzing_started()

        scanner = DetoxioModelDynamicScanner(api_key=self.detoxio_api_key)
        with scanner.new_session() as session:
            self._scan(session)
            report = session.get_report()
            
            if callable(self.on_fuzzing_completed):
                self.on_fuzzing_completed(self._total_tests, self._unsafe_results_found)
            
            return report

    def _scan(self, session):
        self._scan_single_state(session)
        while self._total_tests < self._MAX_TESTS:
            try:
                self.model.next()
                self._scan_single_state(session)
            except StopIteration:
                break
    
    def _scan_single_state(self, session):                
        # Generate prompts
        logging.info("Initialized Session..")
        prompt_generator = self._generate_prompts(session)
        try:
            for i, prompt in enumerate(prompt_generator):
                logging.debug("Generated Prompt: \n%s", prompt.data.content)
                # self._printer.trace(f"[{i+1}] Generated Prompt: {prompt.data.content[0:100]}...")
                
                # Simulate model output
                model_output_text = self.model.invoke(prompt.data.content)
                # self._printer.trace(f"[{i+1}] Response: {model_output_text}...")
                logging.info("Output %s \n", model_output_text)
                logging.debug("Model Executed: \n%s", model_output_text)
                
                evaluation_response = None
                # Evaluate the model interaction
                if len(model_output_text) > 2:  # Make sure the output is not empty
                    evaluation_response = session.evaluate(prompt, model_output_text)
                    logging.debug("Evaluation Response \n%s", evaluation_response)
                
                # Check for unsafe results
                _new_unsafe_results_found = 0
                if session.get_report().count_unsafe_results() > self._unsafe_results_found:
                    _new_unsafe_results_found = session.get_report().count_unsafe_results() - self._unsafe_results_found
                    self._unsafe_results_found = session.get_report().count_unsafe_results()
                    
                    # self._printer.critical(f"Total Unsafe Responses {self._unsafe_results_found}")
                
                logging.debug("Evaluation Executed...")
                self._total_tests += 1

                # Hook for fuzzing progress
                if callable(self.on_fuzzing_progress):
                    self.on_fuzzing_progress(self._total_tests, _new_unsafe_results_found, self._unsafe_results_found)

                # Hook for test completion
                if callable(self.on_test_completed):
                    self.on_test_completed(prompt.data.content, model_output_text, evaluation_response)

        except Exception as ex:
            logging.exception(ex)
            raise ex

    def _generate_prompts(self, scanner_session, prompt_filter=None):
        logging.debug("Using Detoxio AI Prompts Generation..")
        return scanner_session.generate(count=self._tests_per_state, filter=prompt_filter)

    # event hooks

    # def on_init(self, max_tests: int, no_of_tests_per_state: int):
    #     """
    #     Called during initialization of the fuzzer.

    #     Parameters:
    #     - max_tests: int - The maximum number of tests that will be conducted during fuzzing.
    #     - no_of_tests_per_state: int - The number of tests to be conducted per state.
    #     """
    #     pass


    def on_planning_started(self):
        """
        Called when the planning phase starts.
        """
        pass

    def on_planning_completed(self):
        """
        Called when the planning phase is completed.
        """
        pass

    def on_fuzzing_started(self):
        """
        Called when the fuzzing process starts.
        """
        pass

    def on_fuzzing_completed(self, total_tests, unsafe_results_found):
        """
        Called when the fuzzing process completes.
        
        Parameters:
        - total_tests: int - The total number of tests executed.
        - unsafe_results_found: int - The number of unsafe results found during fuzzing.
        """
        pass

    def on_fuzzing_progress(self, total_tests, new_unsafe_results_found, total_unsafe_results_found):
        """
        Called during fuzzing to report progress.
        
        Parameters:
        - total_tests: int - The total number of tests executed so far.
        - new_unsafe_results_found: int - New unsafe results found so far
        - total_unsafe_results_found: int - The number of unsafe results found so far.
        """
        pass

    def on_test_completed(self, prompt: str, model_response: str, evaluation: dict):
        """
        Called after each test is completed.
        
        Parameters:
        - prompt: str - The prompt that was sent to the model.
        - model_response: str - The response generated by the model.
        - evaluation: dict - The result of the evaluation of the model's response.
        """
        pass



# Example usage:
# options = ModelCrawlerOptions(max_depth=3, initial_prompts=["Hello", "How are you?"])
# model_factory = YourModelFactoryImplementation()
# prompt_generator = YourNextPromptGeneratorImplementation()
# crawler = ModelCrawler(model_factory, prompt_generator, options)
# crawler.crawl()

# fuzzer_builder = ModelCrawledStateBuilder(crawler)
# model_fuzzer = fuzzer_builder.build(strategy=TraversalStrategy.BFS)  # or TraversalStrategy.DFS

# model_fuzzer.start()
# response = model_fuzzer.invoke("Hello")
# print("Response:", response)

# try:
#     while True:
#         model_fuzzer.next()  # Traverse to the next node
#         response = model_fuzzer.invoke("Next prompt text")
#         print("Response:", response)
# except StopIteration:
#     print("Traversal complete. No more nodes to traverse.")
