import pytest
from unittest.mock import patch
from chakra.webapp.gradio import GradioUtils

@pytest.fixture
def gradio_utils():
    return GradioUtils()

def test_normalize_url_with_huggingface_url(gradio_utils):
    with patch.object(GradioUtils, '_extract_hugging_face_space_name') as mock_extract:
        mock_extract.return_value = "orgname/app"
        assert gradio_utils.normalize_url("http://huggingface.co/orgname/app") == "orgname/app"

def test_normalize_url_with_non_huggingface_url(gradio_utils):
    with patch.object(GradioUtils, '_extract_hugging_face_space_name') as mock_extract:
        mock_extract.return_value = ""
        assert gradio_utils.normalize_url("http://example.com") == "http://example.com"

def test__extract_hugging_face_space_name_with_valid_huggingface_url(gradio_utils):
    url = "http://huggingface.co/orgname/app"
    assert gradio_utils._extract_hugging_face_space_name(url) == "orgname/app"

def test__extract_hugging_face_space_name_with_invalid_huggingface_url(gradio_utils):
    url = "http://example.com"
    assert gradio_utils._extract_hugging_face_space_name(url) == ""

# Add more test cases for other scenarios as needed
