# Hacktor

## Why does it exist?

Hacktor is a versatile tool for:

- **Web App Pentesters & Security Engineers**: Security test GenAI Chatbots, Assistants, and Agents.
- **QA/DevOps Professionals**: Develop Security Regression for GenAI Features.

GenAI Apps Security Testing should cover various Vulnerability Categories (OWASP LLM Top 10), including:
- **Data Leakage**: Assess if your app inadvertently leaks private or sensitive data.
- **Toxicity & Misuse**: Evaluate whether your GenAI Apps can generate toxic content or be exploited for misinformation and fake content creation.
- **Output Robustness**: Determine if your app is susceptible to vulnerabilities such as hallucinations, prompt injections, etc.

Refer to Features and Use Case Section for more details

## Getting Started

**Clone and install Hacktor**

```bash
git clone https://github.com/detoxio/hacktor.git
cd hacktor 
poetry install
```

**Install using pip**
```bash
pip install hacktor@git+https://github.com/detoxio/hacktor@main \
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
pip install hacktor@git+https://github.com/detoxio/hacktor detoxio-api-protocolbuffers-python detoxio_api_grpc_python   --upgrade --extra-index-url https://buf.build/gen/python
```

## Usage

### As GenAI App Scanner

It works as follows: 
1. Run `python hacktor/main.py webapps <>` to start crawling web applications.
2. Open a browser window and insert `[FUZZ]` or `[HACKTOR]` in relevant text areas.
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
poetry run hacktor webapps <URL>
```

**Record a Crawling Session**
```bash
hacktor webapps <URL> -s session.har --skip_testing
cat session.har | grep [FUZZ] | wc -l  
```
The above command will open the browser. Specify the Fuzzing Marker [FUZZ] in a chat box. Close the browser window to save the session 

**Just Test using Recorded Session**
```bash
hacktor webapps <URL> -s session.har --skip_crawling --markdown report.md --json report.json
```
No Browser will open. Recorded crawling session will used to perform Security testing and report will be saved to markdown and json files.

**Specify filters to generate prompts specific to industry or threat class**

```bash
hacktor webapps https://69c207a7e69699ce8e.gradio.live/ -s demo.har --skip_crawling --json report.json --threat-class bypass --markdown report.md
```

```bash
hacktor webapps https://69c207a7e69699ce8e.gradio.live/ -s demo.har --skip_crawling --industry healthcare --json report.json --threat-class bypass

```


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
                        [[HACKTOR]] [HACKTOR] HACKTOR <<HACKTOR>>

  --industry {HEALTHCARE,FINANCE,RETAIL,AGRICULTURE,AUTOMOTIVE,BANKING,BIOTECHNOLOGY,CHEMICALS,CONSTRUCTION ...}
                        Filter Prompts related to the industry.
  --threat-class {TOXICITY,MISINFORMATION,INFORMATION_HAZARD,MALICIOUS_USE,HUMAN_COMPUTER_INTERACTION,AUTOMATION_ACCESS_ENVIRONMENTAL,DEFENSE_BYPASS}
                        Filter Prompts related to the threat classes.
  --threat-category {ABUSIVE_LANGUAGE,HATE_SPEECH,HARASSMENT,BULLYING,SEXUAL_ASSAULT,PROFANITY,....}
                        filter prompts related to the threat categories.
  --deceptiveness {LOW,MEDIUM,HIGH}
                        How desceptive the promopts are?

```

### As GenAI Mobile Application Scanner

It works as follows: 
1. Use Burpsuite in tandum with Andoird emulator to intercept request made to GenAI application
2. Save this request to a file
3. Run `python hacktor/main.py mobileapp <>` to start testing.
4. Tool automatically fuzzes requests using recorded prompt. In order to fuzz either:
    * Replace the input prompt with `[FUZZ]` OR `[HACKTOR]`
    * Provide a prompt paramtere which is the parameter in the request that maps to the input prompt
5. Generate report summarizing fuzzing results.
6. Report can be printed to console or saved for further analysis.

**Quick Start**

Specify the Detoxio API Key as above. More information here on [API Docs](https://docs.detoxio.ai/api/authentication)

```bash
export DETOXIO_API_KEY=xxxx
```

Run it
```bash
poetry run hacktor mobileapp <URL> -r <Request file path>
```

**Other Options**
```
options:
  -h, --help            show this help message and exit
  --prompt_parameter PROMPT_PARAMETER
                        Parameter which holds the input prompt.
  --prompt_prefix PROMPT_PREFIX
                        Add a prefix to every prompt to make prompts more contextual.
  -r REQUEST, --request REQUEST
                        Path to input burp request file.
  --response_param RESPONSE_PARAM
                        Parameter which holds the GenAI response.
  --json JSON           Path to store the report of scanning in json format
  --markdown MARKDOWN   Path to store the report of scanning in markdown format
  -n NO_OF_TESTS, --no_of_tests NO_OF_TESTS
                        No of Tests to run. Default 10
  -l LOG_LEVEL, --log_level LOG_LEVEL
                        Log Levels - DEBUG, INFO, WARN, ERROR. Default: INFO
```

### As Library

```python
# Example usage code for DetoxioModelDynamicScanner

# Assuming you have already imported the necessary modules and classes

from hacktor.dtx.scanner import DetoxioModelDynamicScanner

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

## Use Cases

**Red Teaming GenAI Chatbots**:  Craft toxic prompts to test the resilience of your GenAI chatbots against adversarial attacks. Hacktor aids in evaluating your chatbot's ability to handle unexpected or malicious inputs.

**Mobile GenAI App Security Testing**:  Fortify the security of your GenAI mobile apps.  By combining Hacktor with Burp, a suite of web security testing tools, you can:

Decompile the mobile app to understand its inner workings.
Record requests and responses using Burp to capture the app's interactions.
Test the captured APIs using Hacktor to identify potential vulnerabilities.

**CI/CD Integration for GenAI Testing**:  Streamline GenAI security testing into your CI/CD pipeline, ensuring continuous security throughout the development lifecycle. Hacktor integrates with Playwright, a popular automation framework, to:

Record user sessions within the GenAI application.
Automatically execute Hacktor tests based on the recorded sessions during the CI/CD process.

## Features 

### Human Assisted Crawling

This feature involves crawling web applications with the assistance of a human. Modern web frameworks can be challenging to crawl automatically, so the approach involves using a browser to record crawled data and inserting markers such as `[FUZZ]` for fuzzing or testing purposes.

### Testing GenAI Chatbot for OWASP TOP 10 categories

This feature involves generating various prompts, sending them to a GenAI Chatbot, collecting responses, and evaluating the responses. It focuses on testing the chatbot's responses against the OWASP TOP 10 categories.


### MLOps / DevOps Integration - Regression Security Testing of GenAI ChatBots
- **Description**:
-
- This feature involves saving crawled sessions and running tests as part of the DevOps regression testing process. It focuses on regression security testing of GenAI Chatbots.

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


### How to start development

**Clone**
```bash
git clone https://github.com/detoxio/hacktor
```

**Install Dependencies**
```bash
pip install poetry
cd hacktor
poetry install
```

**Develop the code**

**Run it**

```bash 
poetry run hacktor
```
[DO NOT FORGET TO SET Detoxio AI API key]

## License

This project is distributed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

© [Detoxio](https://detoxio.ai)
```
