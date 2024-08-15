import pytest
from hacktor.dtx.parser import DetoxioResponseEvaluationResult

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
            "status": "THREAT_EVALUATION_STATUS_SAFE",
            "threats": [
                {"threat": {"threatClass": "TOXICITY", "threatCategory": "ABUSIVE_LANGUAGE"}, "status": "THREAT_EVALUATION_STATUS_SAFE"},
                {"threat": {"threatClass": "TOXICITY", "threatCategory": "HATE_SPEECH"}, "status": "THREAT_EVALUATION_STATUS_SAFE"}
            ]
        }
    ],
    "status": "THREAT_EVALUATION_STATUS_SAFE"
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
    assert status == "THREAT_EVALUATION_STATUS_SAFE"

def test_is_unsafe_false():
    result = DetoxioResponseEvaluationResult(RESULT)
    assert result.is_unsafe() == False

def test_is_unsafe_true():
    unsafe_result = RESULT.copy()
    unsafe_result["status"] = "THREAT_EVALUATION_STATUS_UNSAFE"
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
    threats = list(result.threats("THREAT_EVALUATION_STATUS_SAFE"))
    assert len(threats) == 2
    assert threats[0]["status"] == "THREAT_EVALUATION_STATUS_SAFE"
    assert threats[1]["status"] == "THREAT_EVALUATION_STATUS_SAFE"

def test_threats_empty():
    result = DetoxioResponseEvaluationResult(RESULT)
    threats = list(result.threats("THREAT_EVALUATION_STATUS_UNSAFE"))
    assert len(threats) == 0

def test_get_threat_category_and_status_pair():
    result = DetoxioResponseEvaluationResult(RESULT)
    pairs = list(result.get_threat_category_and_status_pair())
    assert len(pairs) == 2
    assert pairs[0] == ("THREAT_EVALUATION_STATUS_SAFE", "ABUSIVE_LANGUAGE")
    assert pairs[1] == ("THREAT_EVALUATION_STATUS_SAFE", "HATE_SPEECH")

def test_get_threat_class_and_status_pair():
    result = DetoxioResponseEvaluationResult(RESULT)
    pairs = list(result.get_threat_class_and_status_pair())
    assert len(pairs) == 2
    assert pairs[0] == ("THREAT_EVALUATION_STATUS_SAFE", "TOXICITY")
    assert pairs[1] == ("THREAT_EVALUATION_STATUS_SAFE", "TOXICITY")

def test_unsafe_threats():
    result = DetoxioResponseEvaluationResult(RESULT)
    threats = list(result.unsafe_threats())
    assert len(threats) == 0

def test_safe_threats():
    result = DetoxioResponseEvaluationResult(RESULT)
    threats = list(result.safe_threats())
    assert len(threats) == 2
    assert threats[0]["threat"]["threatClass"] == "TOXICITY"
    assert threats[0]["threat"]["threatCategory"] == "ABUSIVE_LANGUAGE"
    assert threats[1]["threat"]["threatClass"] == "TOXICITY"
    assert threats[1]["threat"]["threatCategory"] == "HATE_SPEECH"
