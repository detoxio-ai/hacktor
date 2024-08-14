
import unittest


import proto.dtx.messages.common.threat_pb2 as dtx_threat_pb2
import proto.dtx.messages.common.industry_pb2 as dtx_industry_pb2
import proto.dtx.services.prompts.v1.prompts_pb2 as dtx_prompts_pb2
from hector.scanner import DetoxioGeneratorFilterBuilder


class TestBuildFilter(unittest.TestCase):
    def setUp(self):
        self.filter_builder = DetoxioGeneratorFilterBuilder()

    def test_build_empty_filter(self):
        # Test building filter with no attributes set
        built_filter = self.filter_builder.build_filter()
        self.assertIsInstance(built_filter, dtx_prompts_pb2.PromptGenerationFilterOption)
        self.assertEqual(built_filter, dtx_prompts_pb2.PromptGenerationFilterOption())

    def test_build_filter_with_threat_class(self):
        # Test building filter with threat class set
        self.filter_builder.threat_class('toxic')
        built_filter = self.filter_builder.build_filter()
        self.assertIsInstance(built_filter, dtx_prompts_pb2.PromptGenerationFilterOption)
        self.assertEqual(built_filter.threat_class, dtx_threat_pb2.THREAT_CLASS_TOXICITY)

    def test_build_filter_with_threat_category(self):
        # Test building filter with threat category set
        self.filter_builder.threat_category('malware')
        built_filter = self.filter_builder.build_filter()
        self.assertIsInstance(built_filter, dtx_prompts_pb2.PromptGenerationFilterOption)
        self.assertEqual(built_filter.threat_category, dtx_threat_pb2.THREAT_CATEGORY_MALWARE_GENERATION)

    def test_build_filter_with_industry(self):
        # Test building filter with industry set
        self.filter_builder.industry('Finance')
        built_filter = self.filter_builder.build_filter()
        self.assertIsInstance(built_filter, dtx_prompts_pb2.PromptGenerationFilterOption)
        self.assertEqual(built_filter.industry, dtx_industry_pb2.INDUSTRY_DOMAIN_FINANCE)

    def test_build_filter_with_label(self):
        # Test building filter with label set
        self.filter_builder.label('severity', 'High')
        built_filter = self.filter_builder.build_filter()
        self.assertIsInstance(built_filter, dtx_prompts_pb2.PromptGenerationFilterOption)
        self.assertEqual(built_filter.labels['severity'], 'High')

    def test_build_filter_with_deceptiveness(self):
        # Test building filter with deceptiveness set
        self.filter_builder.deceptiveness('low')
        built_filter = self.filter_builder.build_filter()
        self.assertIsInstance(built_filter, dtx_prompts_pb2.PromptGenerationFilterOption)
        self.assertEqual(built_filter.labels['deceptiveness'], 'low')

    def tearDown(self):
        del self.filter_builder

if __name__ == '__main__':
    unittest.main()
