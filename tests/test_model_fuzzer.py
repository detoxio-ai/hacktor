import unittest
from unittest.mock import MagicMock
from collections import deque
from copy import copy
from typing import List
import networkx as nx
from hacktor.webapp.crawler import (
    AbstractRemoteModel,
    ModelFactory,
    ModelCrawler,
    NextPromptGenerator,
    ModelCrawlerOptions,
    TraversalStrategy
)
from hacktor.webapp.fuzzer import ModelFuzzer, ModelFuzzerBuilder
from hacktor.webapp.ai.predict import NextPrompts

# Mock classes for testing
class MockRemoteModel(AbstractRemoteModel):
    def generate(self, input_text: str) -> str:
        responses = {
            "Hello": ("", "Hi there!"),
            "How are you?": ("", "I'm good, thank you!"),
            "What's your name?": ("", "I'm a bot."),
            "Tell me a joke": ("", "Why did the scarecrow win an award? Because he was outstanding in his field!"),
            "What's your favorite color?": ("", "I like blue."),
            "Why do you like blue?": ("", "It reminds me of the sky."),
            "Do you like the sky?": ("", "Yes, it's vast and beautiful."),
            "What do you do?": ("", "I assist with tasks."),
            "Why do you assist with tasks?": ("", "To make life easier for you.")
        }
        return responses.get(input_text, ("", ""))


class MockModelFactory(ModelFactory):
    def __init__(self):
        self.model = MockRemoteModel()
    
    def new(self) -> AbstractRemoteModel:
        self.model = MockRemoteModel()
        return self.model
        
    def get(self) -> AbstractRemoteModel:
        return self.model


class MockNextPromptGenerator(NextPromptGenerator):
    def next_prompts(self, prompt_text: str, response_text: str) -> NextPrompts:
        prompts_map = {
            "Hi there!": ["How are you?", "What's your name?", "What's your favorite color?"],
            "I'm good, thank you!": ["Tell me a joke", "What do you do?"],
            "I'm a bot.": ["What do you do?"],
            "Why did the scarecrow win an award? Because he was outstanding in his field!": ["Why do you like blue?"],
            "I like blue.": ["Why do you like blue?", "Do you like the sky?"],
            "It reminds me of the sky.": ["Do you like the sky?"],
            "Yes, it's vast and beautiful.": ["What do you do?"],
            "I assist with tasks.": ["Why do you assist with tasks?"],
            "To make life easier for you.": []
        }

        prompts = prompts_map.get(response_text, [])
        return NextPrompts(prompts=prompts, template=None)


# Test cases for ModelFuzzer
class TestModelFuzzer(unittest.TestCase):

    def setUp(self):
        self.options = ModelCrawlerOptions(max_depth=3, initial_prompts=["Hello"], strategy=TraversalStrategy.DFS)
        self.model_factory = MockModelFactory()
        self.prompt_generator = MockNextPromptGenerator()
        self.crawler = ModelCrawler(self.model_factory, self.prompt_generator, self.options)
        self.crawler.crawl()
        self.fuzzer_builder = ModelFuzzerBuilder(self.crawler)

    def test_fuzzer_initialization(self):
        fuzzer = self.fuzzer_builder.build()
        self.assertIsNotNone(fuzzer)
        self.assertEqual(fuzzer.current_node_id, 0)
        self.assertEqual(len(fuzzer.nodes_to_visit), len(fuzzer.tree.nodes)-1)  # Ensure all nodes are queued for visit
        self.assertEqual(fuzzer.nodes_to_visit[0], 1)  # Ensure traversal starts from the root node
    
    def test_fuzzer_start(self):
        fuzzer = self.fuzzer_builder.build()
        fuzzer.start()
        self.assertIsNotNone(fuzzer.current_model)
        self.assertEqual(fuzzer.current_node_id, 0)
        self.assertEqual(len(fuzzer.nodes_to_visit), len(fuzzer.tree.nodes)-1)  # Ensure all nodes are queued for visit
        self.assertEqual(fuzzer.nodes_to_visit[0], 1)

    def test_fuzzer_invoke(self):
        fuzzer = self.fuzzer_builder.build()
        fuzzer.start()
        response = fuzzer.invoke("Hello")
        self.assertEqual(response, "Hi there!")

    def test_fuzzer_next_bfs(self):
        fuzzer = self.fuzzer_builder.build()
        fuzzer.start()

        # Perform BFS traversal
        fuzzer.next()  # Move to the first node after root
        self.assertEqual(fuzzer.current_node_id, 1)  # Assuming "Hello" is the first child
        response = fuzzer.invoke("How are you?")
        self.assertEqual(response, "I'm good, thank you!")
        
        fuzzer.next()  # Move to the next node in BFS
        self.assertEqual(fuzzer.current_node_id, 2)  # Assuming "How are you?" is explored
        response = fuzzer.invoke("What's your name?")
        self.assertEqual(response, "I'm a bot.")

    def test_fuzzer_next_dfs(self):
        # Reset options for DFS
        options = copy(self.options)
        options.strategy = TraversalStrategy.DFS
        self.crawler = ModelCrawler(self.model_factory, self.prompt_generator, options)
        self.crawler.crawl()
        fuzzer = ModelFuzzer(self.crawler)

        fuzzer.start()

        # Perform DFS traversal
        fuzzer.next()  # Move to the first node after root
        self.assertEqual(fuzzer.current_node_id, 1)  # Assuming "Hello" is the first child
        response = fuzzer.invoke("How are you?")
        self.assertEqual(response, "I'm good, thank you!")
        
        fuzzer.next()  # Move to next node in DFS
        self.assertEqual(fuzzer.current_node_id, 2)  # Assuming "Tell me a joke" is explored next
        response = fuzzer.invoke("Tell me a joke")
        self.assertEqual(response, "Why did the scarecrow win an award? Because he was outstanding in his field!")

    def test_fuzzer_stop_iteration(self):
        fuzzer = self.fuzzer_builder.build()
        fuzzer.start()
        
        try:
            while True:
                fuzzer.next()
        except StopIteration:
            pass  # Expected outcome when traversal completes
        
        self.assertEqual(len(fuzzer.nodes_to_visit), 0)

    def test_fuzzer_resets_correctly(self):
        fuzzer = self.fuzzer_builder.build()
        fuzzer.start()
        fuzzer.next()  # Perform one traversal step
        fuzzer.start()  # Restart fuzzer to check if it resets correctly
        
        # Check if it resets correctly
        self.assertIsNotNone(fuzzer.current_model)
        self.assertEqual(fuzzer.current_node_id, 0)
        self.assertEqual(len(fuzzer.nodes_to_visit), len(fuzzer.tree.nodes)-1)  # Ensure all nodes are queued for visit
        self.assertEqual(fuzzer.nodes_to_visit[0], 1)

    def test_fuzzer_traversal_order_bfs(self):
        # Reset options for DFS
        options = copy(self.options)
        options.strategy = TraversalStrategy.BFS
        self.crawler = ModelCrawler(self.model_factory, self.prompt_generator, options)
        self.crawler.crawl()
        fuzzer = ModelFuzzer(self.crawler)

        fuzzer.start()

        traversal_order = []
        try:
            while True:
                fuzzer.next()
                traversal_order.append(fuzzer.current_node_id)
        except StopIteration:
            pass
        
        # Expected DFS order for a tree of this structure
        expected_dfs_order = list(nx.bfs_tree(fuzzer.tree, source=0).nodes)[1:]
        self.assertEqual(traversal_order, expected_dfs_order)

    def test_fuzzer_traversal_order_dfs(self):
        # Reset options for DFS
        options = copy(self.options)
        options.strategy = TraversalStrategy.DFS
        self.crawler = ModelCrawler(self.model_factory, self.prompt_generator, options)
        self.crawler.crawl()
        fuzzer = ModelFuzzer(self.crawler)

        fuzzer.start()

        traversal_order = []
        try:
            while True:
                fuzzer.next()
                traversal_order.append(fuzzer.current_node_id)
        except StopIteration:
            pass
        
        # Expected DFS order for a tree of this structure
        expected_dfs_order = list(nx.dfs_preorder_nodes(fuzzer.tree, 0))[1:]
        self.assertEqual(traversal_order, expected_dfs_order)

if __name__ == "__main__":
    unittest.main()
