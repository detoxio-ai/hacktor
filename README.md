# Conocer

## Objective

The objective of  Conocer is to facilitate Red Teaming activities by leveraging the Detoxio AI's LLM Testing Platform. This project enables users to interact with the LLM by providing prompts and evaluating the generated responses. The prompts are evaliated using on various categories such as Toxicity, Misuse, Crime, Hate Speech etc.

## Features

- **Prompt Generation:** Generate toxic prompts using the Testing Platform

- **Model Reponse Evaluation:** Evaluate the target LLM's responses to specific prompts, and add results for report generation

- **Toxic Categories Evaluated**: 
{'threat': {'threatClass': 'TOXICITY', 'threatCategory': 'HATE_SPEECH'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'TOXICITY', 'threatCategory': 'HARASSMENT'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'TOXICITY', 'threatCategory': 'BULLYING'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'TOXICITY', 'threatCategory': 'PROFANITY'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'TOXICITY', 'threatCategory': 'SEXUAL_ASSAULT'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'MALICIOUS_USE', 'threatCategory': 'MALWARE_GENERATION'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'MALICIOUS_USE', 'threatCategory': 'WEAPONIZATION'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'MALICIOUS_USE', 'threatCategory': 'FRAUD'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'MALICIOUS_USE', 'threatCategory': 'PHISHING'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'MALICIOUS_USE', 'threatCategory': 'THEFT'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'MALICIOUS_USE', 'threatCategory': 'VIOLENCE'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'MALICIOUS_USE', 'threatCategory': 'CRIME'}, 'status': 'SAFE'}, {'threat': {'threatClass': 'MALICIOUS_USE', 'threatCategory': 'CBRN'}, 'status': 'SAFE'}], 'evaluatedAt': '2024-03-12T07:32:57.420461Z'}]}}}}

## Installation

To install Project Conocer, follow these proprietary steps:

```bash
pip install s
```

```bash
poetry install
```

## Usage

```python
from conocer import DetoxioModelDynamicScannerSession

# Create instances of DetoxioPromptGenerator and DetoxioPromptResponseEvaluator
# (Assuming these classes are already defined)
generator = DetoxioPromptGenerator(your_grpc_client)
evaluator = DetoxioPromptResponseEvaluator(your_grpc_client)

# Create an instance of DetoxioModelDynamicScannerSession
with DetoxioModelDynamicScannerSession(generator, evaluator) as scanner_session:
    # Use the generator within the context
    for prompt in scanner_session.generate(count=5):
        print(f"Generated Prompt: {prompt}")

    # Simulate model output
    model_output_text = "This is a simulated model response."

    # Evaluate the model interaction
    prompt_to_evaluate = next(scanner_session.generate(count=1))  # Choose a prompt to evaluate
    evaluation_response = scanner_session.evaluate(prompt_to_evaluate, model_output_text)

    # Print the evaluation response
    print(f"Evaluation Response: {evaluation_response}")
```

## License

This project is distributed under the Detoxio proprietary license. For licensing inquiries, please contact Detoxio.

© [Detoxio](https://detoxio.ai)