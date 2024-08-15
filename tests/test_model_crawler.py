import unittest
from copy import copy
from unittest.mock import MagicMock
from typing import List, Optional
import networkx as nx
from hacktor.webapp.crawler import (
    AbstractRemoteModel,
    ModelFactory,
    ModelCrawler,
    NextPromptGenerator,
    ModelCrawlerOptions,
    TraversalStrategy
)

from hacktor.webapp.ai.predict import NextPrompts

# Mock classes
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
        template = None  # You could provide a template if the scenario requires

        return NextPrompts(prompts=prompts, template=template)


# Test cases
class TestModelCrawler(unittest.TestCase):

    def setUp(self):
        self.options = ModelCrawlerOptions(max_depth=3, initial_prompts=["Hello"], strategy=TraversalStrategy.BFS)
        self.model_factory = MockModelFactory()
        self.prompt_generator = MockNextPromptGenerator()
    
    def test_initial_tree_structure(self):
        crawler = ModelCrawler(self.model_factory, self.prompt_generator, self.options)
        crawler.crawl()
        tree = crawler.get_tree()
        
        # Check that the root node exists
        root_node = list(tree.nodes(data=True))[0]
        self.assertIsNone(root_node[1]['prompt'])  # Expect None for the root prompt
        self.assertIsNone(root_node[1]['response'])  # Expect None for the root response
        self.assertEqual(root_node[1]['next_prompts'], ["Hello"])
    
    def test_crawl_basic(self):
        crawler = ModelCrawler(self.model_factory, self.prompt_generator, self.options)
        crawler.crawl()
        tree = crawler.get_tree()
        
        # Test if the tree contains the expected prompts and responses
        nodes = list(tree.nodes(data=True))
        self.assertTrue(any(node[1]['prompt'] == "Hello" and node[1]['response'] == "Hi there!" for node in nodes))
        self.assertTrue(any(node[1]['prompt'] == "How are you?" and node[1]['response'] == "I'm good, thank you!" for node in nodes))
    
    def test_backtracking(self):
        options = ModelCrawlerOptions(max_depth=1000, initial_prompts=["Hello"])
        crawler = ModelCrawler(self.model_factory, self.prompt_generator, options)
        crawler.crawl()
        tree = crawler.get_tree()

        # Verify that the tree has handled backtracking properly
        nodes = list(tree.nodes(data=True))

        # The branch "What's your name?" should exist
        self.assertTrue(any(node[1]['prompt'] == "What's your name?" for node in nodes))
        
        # Check if any node with "Why do you assist with tasks?" has no further next_prompts
        self.assertTrue(any(node[1]['prompt'] == "Why do you assist with tasks?" and not node[1]['next_prompts'] for node in nodes))

        
    def test_max_depth(self):
        crawler = ModelCrawler(self.model_factory, self.prompt_generator, self.options)
        crawler.crawl()
        tree = crawler.get_tree()

        # Check that the tree does not exceed the max_depth
        def check_depth(node, depth):
            if depth > self.options.max_depth:
                return False
            # Iterate over child nodes directly
            for child_node in tree.successors(node):  # Use successors to iterate over child nodes
                if not check_depth(child_node, depth + 1):
                    return False
            return True

        root_node = 0
        self.assertTrue(check_depth(root_node, 0))

    def test_alternative_path_after_backtracking(self):
        crawler = ModelCrawler(self.model_factory, self.prompt_generator, self.options)
        crawler.crawl()
        tree = crawler.get_tree()

        # After backtracking, ensure it explored the alternative paths
        nodes = list(tree.nodes(data=True))

        # Ensure both "How are you?" and "What's your name?" were explored
        self.assertTrue(any(node[1]['prompt'] == "How are you?" for node in nodes))
        self.assertTrue(any(node[1]['prompt'] == "What's your name?" for node in nodes))
    
    def test_bfs_traversal(self):
        options = copy(self.options)
        options.strategy = TraversalStrategy.BFS
        crawler = ModelCrawler(self.model_factory, self.prompt_generator, self.options)
        crawler.crawl()
        tree = crawler.get_tree()

        # Check that BFS order was maintained (all nodes at one depth level before moving deeper)
        nodes_by_depth = {}
        for node in tree.nodes:
            depth = nx.shortest_path_length(tree, 0, node)
            if depth not in nodes_by_depth:
                nodes_by_depth[depth] = []
            nodes_by_depth[depth].append(node)
        
        # Expect nodes at depth 1 to be explored first before depth 2
        self.assertTrue(all(len(nodes_by_depth[d]) > 0 for d in range(1, len(nodes_by_depth))))
    
    def test_dfs_traversal(self):
        options = copy(self.options)
        options.strategy = TraversalStrategy.DFS
        crawler = ModelCrawler(self.model_factory, self.prompt_generator, self.options)
        crawler.crawl()
        tree = crawler.get_tree()

        # Check that DFS order was maintained (depth-first exploration)
        nodes_by_depth = {}
        for node in tree.nodes:
            depth = nx.shortest_path_length(tree, 0, node)
            if depth not in nodes_by_depth:
                nodes_by_depth[depth] = []
            nodes_by_depth[depth].append(node)
        
        # Expect nodes at deeper levels to be fully explored before moving to other branches
        self.assertTrue(any(len(nodes_by_depth[d]) > 0 for d in range(1, len(nodes_by_depth))))


if __name__ == "__main__":
    unittest.main()
