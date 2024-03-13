import pytest
from conocer.parser import DetoxioResponseEvaluationResult

# Sample evaluation result
RESULT = {
    "prompt": {
        "generatedAt": "2024-03-12T09:48:52.281643957Z",
        "data": {
            "content": "Prompt text"
        }
    },
    "responses": [
        {
            "message": {
                "content": "Response text"
            },
            "status": "SAFE",
            "threats": [
                {"threat": {"threatClass": "TOXICITY", "threatCategory": "ABUSIVE_LANGUAGE"}, "status": "SAFE"},
                {"threat": {"threatClass": "TOXICITY", "threatCategory": "HATE_SPEECH"}, "status": "SAFE"}
            ]
        }
    ],
    "status": "SAFE"
}


def test_prompt():
    result = DetoxioResponseEvaluationResult(RESULT)
    prompt = result.prompt()
    assert isinstance(prompt, dict)
    assert prompt["generatedAt"] == "2024-03-12T09:48:52.281643957Z"

def test_prompt_text():
    result = DetoxioResponseEvaluationResult(RESULT)
    prompt_text = result.prompt_text()
    assert isinstance(prompt_text, str)
    assert prompt_text == "Prompt text"

def test_response_text_first():
    result = DetoxioResponseEvaluationResult(RESULT)
    response_text = result.response_text_first()
    assert isinstance(response_text, str)
    assert response_text == "Response text"

def test_status():
    result = DetoxioResponseEvaluationResult(RESULT)
    status = result.status()
    assert isinstance(status, str)
    assert status == "SAFE"

def test_is_unsafe_false():
    result = DetoxioResponseEvaluationResult(RESULT)
    assert result.is_unsafe() == False

def test_is_unsafe_true():
    unsafe_result = RESULT.copy()
    unsafe_result["status"] = "UNSAFE"
    result = DetoxioResponseEvaluationResult(unsafe_result)
    assert result.is_unsafe() == True

def test_threats():
    result = DetoxioResponseEvaluationResult(RESULT)
    threats = list(result.threats())
    assert len(threats) == 2
    assert threats[0]["threat"]["threatClass"] == "TOXICITY"
    assert threats[0]["threat"]["threatCategory"] == "ABUSIVE_LANGUAGE"
    assert threats[1]["threat"]["threatClass"] == "TOXICITY"
    assert threats[1]["threat"]["threatCategory"] == "HATE_SPEECH"

def test_threats_filtered():
    result = DetoxioResponseEvaluationResult(RESULT)
    threats = list(result.threats("SAFE"))
    assert len(threats) == 2
    assert threats[0]["status"] == "SAFE"
    assert threats[1]["status"] == "SAFE"

def test_threats_empty():
    result = DetoxioResponseEvaluationResult(RESULT)
    threats = list(result.threats("UNSAFE"))
    assert len(threats) == 0
