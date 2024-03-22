# Conocer

## Objective

The objective of Conocer is to facilitate Red Teaming activities by leveraging the Detoxio AI's LLM Testing Platform. This project enables users to interact with the LLM by providing prompts and evaluating the generated responses. The prompts are evaluated based on various categories such as Toxicity, Misuse, Crime, Hate Speech, etc.

## Features

- **Prompt Generation:** Generate toxic prompts using the Testing Platform.

- **Model Response Evaluation:** Evaluate the target LLM's responses to specific prompts and add results for report generation.

- **Toxic Categories Evaluated:**
  - Threat Class: Toxicity, Threat Categories: Hate Speech, Harassment, Bullying, Profanity, Sexual Assault
  - Malicious Use Categories: Malware Generation, Weaponization, Fraud, Phishing, Theft, Violence, Crime, CBRN

## Installation

To install Project Conocer, follow these steps:

```bash
git clone https://github.com/safedep/conocer.git
cd conocer 
poetry install
```
In order to assist crawling GenAI webapp features testing, setup playright

```bash
playwright install

```
** Various browsers should be installed including chromium. Ignore error at the end **



## Usage

### As GenAI App Scanner

It works as follows: 

[1] python conocer/main.py webapps <<GenAI APP URL>>

[2] Browser window will open, type [FUZZ] or [CONOCER] in a text area to be used for testing

[3] Once recording is done, close the browser

[4] Tool will start fuzzing requests with prompts

[5] Report will be generated or printed on console

** Basic Command**

```bash
poetry run conocer webapps <URL>
```





### As Library

```python
# Example usage code for DetoxioModelDynamicScanner

# Assuming you have already imported the necessary modules and classes

from conocer.scanner import DetoxioModelDynamicScanner

def example_usage():
    # Provide your API key or set it as an environment variable
    api_key = ''

    # Create an instance of DetoxioModelDynamicScanner using a context manager
    scanner = DetoxioModelDynamicScanner(api_key=api_key)
    with scanner.new_session() as session:
        # Generate prompts
        prompt_generator = session.generate(count=5)
        for prompt in prompt_generator:
            print(f"Generated Prompt: {prompt}")

            # Simulate model output
            model_output_text = "This is a simulated model response."

            # Evaluate the model interaction
            evaluation_response = session.evaluate(prompt, model_output_text)

        # Print the evaluation response
        print(f"Evaluation: {session.get_report().as_dict()}")

if __name__ == "__main__":
    example_usage()
```

## License

This project is distributed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

© [Detoxio](https://detoxio.ai)
```
