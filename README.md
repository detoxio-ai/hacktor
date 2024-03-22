# Conocer

## Why does it exist?

Conocer offers the perfect solution for:

- **Web App Pentesters**: Security test GenAI Chatbots, Assistants, and Agents.
- **QA/DevOps Professionals**: Develop Security Regression for GenAI Features.

Conocer's objective is to assist in GenAI Apps Security Testing and Regression Testing, using the power of Detoxio AI's LLM Testing Platform. 

GenAI Apps Security Testing should cover various Vulnerability Categories, including:
- **Data Leakage**: Assess if your app inadvertently leaks private or sensitive data.
- **Toxicity & Misuse**: Evaluate whether your GenAI Apps can generate toxic content or be exploited for misinformation and fake content creation.
- **Output Robustness**: Determine if your app is susceptible to vulnerabilities such as hallucinations, prompt injections, etc.

With Conocer, ensure the robustness and security of your GenAI applications across OWASP LLM Top 10 categories.

## Getting Started

**Clone and install Conocer**

```bash
git clone https://github.com/safedep/conocer.git
cd conocer 
poetry install
```

**Install using pip**
```bash
pip install conocer@git+https://github.com/safedep/conocer@main \
    detoxio-api-protocolbuffers-python detoxio_api_grpc_python  \
    --upgrade --extra-index-url https://buf.build/gen/python
```

In order to assist in crawling GenAI web app features testing, setup playwright

```bash
playwright install
```
**Various browsers should be installed including Chromium. Ignore the error at the end**


Install it as a dependency using pip
```bash
pip install conocer@git+https://github.com/safedep/conocer detoxio-api-protocolbuffers-python detoxio_api_grpc_python   --upgrade --extra-index-url https://buf.build/gen/python
```

## Usage

### As GenAI App Scanner

It works as follows: 
1. Run `python conocer/main.py webapps <>` to start crawling web applications.
2. Open a browser window and insert `[FUZZ]` or `[CONOCER]` in relevant text areas.
3. Close the browser after recording interactions.
4. Tool automatically fuzzes requests using recorded prompts.
5. Generate report summarizing fuzzing results.
6. Report can be printed to console or saved for further analysis.

**Quick Start**

Specify the Detoxio API Key. More information here on [API Docs](https://docs.detoxio.ai/api/authentication)

```bash
export DETOXIO_API_KEY=xxxx
```

Run it
```bash
poetry run conocer webapps <URL>
```

**Record a Crawling Session**
```bash
conocer webapps <URL> -s session.har --skip_testing
cat session.har | grep [FUZZ] | wc -l  
```
The above command will open the browser. Specify the Fuzzing Marker [FUZZ] in a chat box. Close the browser window to save the session 

**Just Test using Recorded Session**
```bash
conocer webapps <URL> -s session.har --skip_crawling --markdown report.md --json report.json
```
No Browser will open. Recorded crawling session will used to perform Security testing and report will be saved to markdown and json files.

**Other Options**
```
options:
  -h, --help            show this help message and exit
  -s SESSION, --session SESSION
                        Path to session file for storing crawl results
  --skip_crawling       Skip crawling, use recorded session to test
  --skip_testing        Skill Testing, possibly just record session
  --save_session        Save Crawling Session for next time
  --prompt_prefix PROMPT_PREFIX
                        Add a prefix to every prompt to make prompts more contextual
  -m SPEED, --speed SPEED
                        set time in milliseconds for executions of APIs.
  -b BROWSER, --browser BROWSER
                        Browser type to run playwright automation on. Allowed values are Webkit, Firefox and Chromium.
  --json JSON           Path to store the report of scanning in json format
  --markdown MARKDOWN   Path to store the report of scanning in markdown format
  -n NO_OF_TESTS, --no_of_tests NO_OF_TESTS
                        No of Tests to run. Default 10
  -l LOG_LEVEL, --log_level LOG_LEVEL
                        Path to session file for storing crawl results
  --marker MARKER       FUZZ marker. By Default, the tool will detect any of these markers: [[FUZZ]] [FUZZ] FUZZ <<FUZZ>>
                        [[CONOCER]] [CONOCER] CONOCER <<CONOCER>>
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

## Features 

### Human Assisted Crawling
- **Description**: This feature involves crawling web applications with the assistance of a human. Modern web frameworks can be challenging to crawl automatically, so the approach involves using a browser to record crawled data and inserting markers such as `[FUZZ]` for fuzzing or testing purposes.
- **Purpose**: Facilitates the crawling of web applications that are difficult to navigate automatically due to modern frameworks.
- **Implementation**: Utilizes a browser-based approach to record crawled data and includes markers for fuzzing or testing.

### Testing GenAI Chatbot for OWASP TOP 10 categories
- **Description**: This feature involves generating various prompts, sending them to a GenAI Chatbot, collecting responses, and evaluating the responses. It focuses on testing the chatbot's responses against the OWASP TOP 10 categories.
- **Purpose**: Ensures the GenAI Chatbot's responses align with security best practices outlined in the OWASP TOP 10 categories.
- **Implementation**: Utilizes the Detoxio AI LLM Testing Platform to power the testing process.

### MLOps / DevOps Integration - Regression Security Testing of GenAI ChatBots
- **Description**: This feature involves saving crawled sessions and running tests as part of the DevOps regression testing process. It focuses on regression security testing of GenAI Chatbots.
- **Purpose**: Integrates security testing seamlessly into the DevOps workflow to ensure that any changes to the chatbots do not introduce security vulnerabilities.
- **Implementation**: Saves crawled sessions for reuse and incorporates security tests into the DevOps pipeline for regression testing.


## Powered by 

### Detoxio APIs for LLM Testing

Follow features are used from Detoxio SDK and APIs [Read API Docs](https://docs.detoxio.ai/) for more details

- **Prompt Generation:** Generate toxic prompts using the Testing Platform.

- **Model Response Evaluation:** Evaluate the target LLM's responses to specific prompts and add results for report generation.

- **Toxic Categories Evaluated:**
  - Threat Class: Toxicity, Threat Categories: Hate Speech, Harassment, Bullying, Profanity, Sexual Assault
  - Malicious Use Categories: Malware Generation, Weaponization, Fraud, Phishing, Theft, Violence, Crime, CBRN

### Playwrite Framework
We are using [Playwrite](https://playwright.dev/) to record Crawled data 

## License

This project is distributed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

© [Detoxio](https://detoxio.ai)
```
