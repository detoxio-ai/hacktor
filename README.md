# Hacktor

![Hacktor Demo Short 21 Aug](https://github.com/user-attachments/assets/0cbcf9a5-aaa7-4c77-8851-368ee6c8221b)

## Why does it exist?

Hacktor is a versatile tool designed for:

- **Web App Pentesters & Security Engineers**: Security test GenAI Chatbots, Assistants, and Agents.
- **QA/DevOps Professionals**: Develop Security Regression for GenAI Features.

GenAI Apps Security Testing should cover various Vulnerability Categories (OWASP LLM Top 10), including:

- **Data Leakage**: Assess if your app inadvertently leaks private or sensitive data.
- **Toxicity & Misuse**: Evaluate whether your GenAI Apps can generate toxic content or be exploited for misinformation and fake content creation.
- **Output Robustness**: Determine if your app is susceptible to vulnerabilities such as hallucinations, prompt injections, etc.

Refer to the Features and Use Case Section for more details.

## Quick Start 

**Pull the latest image**
```
docker pull docker.io/detoxio/hacktor:latest
```
**Run it**
Change API key as appripriate
```
docker run --rm -e DETOXIO_API_KEY=xxxxxxx  docker.io/detoxio/hacktor:latest webapps https://medusa.detoxio.dev/ --use_ai --max_crawling_steps 10 --no_of_tests 10 --attack_module OWASP-LLM-APP --json report.json --markdown report.md -v
```

>> Get the API Key here - https://detoxio.ai/contact_us


## Install without Docker

### Clone and Install Hacktor

To get started with Hacktor, first clone the repository and install dependencies:

```bash
git clone https://github.com/detoxio/hacktor.git
cd hacktor
poetry install
```

### Install using pip

Alternatively, you can install Hacktor and its dependencies using pip:

```bash
pip install hacktor \
  detoxio-ai-api-protocolbuffers-python detoxio-ai-api-grpc-python \
  --upgrade --extra-index-url https://buf.build/gen/python
```

or the latest code

```bash
pip install hacktor@git+https://github.com/detoxio/hacktor@main \
  detoxio-ai-api-protocolbuffers-python detoxio-ai-api-grpc-python \
  --upgrade --extra-index-url https://buf.build/gen/python
```

### Setup Environment Variables

Set up the Detoxio API Key, which is required for using Hacktor:

```bash
export DETOXIO_API_KEY=xxxx
```

### Run the tool on Demo Web App

```
poetry run hacktor webapps https://medusa.detoxio.dev/ --use_ai --max_crawling_steps 10 --no_of_tests 10 --attack_module OWASP-LLM-APP --json report.json --markdown report.md -v
```

### Optionally, Install Playwright for Web App Feature Testing

To assist in crawling GenAI web app features, install Playwright:

```bash
playwright install
```

*Various browsers, including Chromium, should be installed. Ignore the error at the end.*


## Usage

[Watch Detailed Demo](https://youtu.be/HGHMR8UNA0k)

### As a GenAI App Scanner

Hacktor works as follows:

1. Run `poetry run hacktor webapps <URL>` to start crawling web applications.
2. Open a browser window and insert `[FUZZ]` or `[HACKTOR]` in relevant text areas.
3. Close the browser after recording interactions.
4. The tool automatically fuzzes requests using recorded prompts.
5. Generate a report summarizing the fuzzing results.
6. Reports can be printed to the console or saved for further analysis.

#### Quick Start

To run Hacktor:

```bash
poetry run hacktor webapps <URL>
```

#### Record a Crawling Session

To record a crawling session:

```bash
hacktor webapps <URL> -s session.har --skip_testing
cat session.har | grep [FUZZ] | wc -l
```

The above command will open the browser. Specify the Fuzzing Marker `[FUZZ]` in a chat box. Close the browser window to save the session.

#### Test Using Recorded Session

To run tests using a recorded session:

```bash
hacktor webapps <URL> -s session.har --skip_crawling --markdown report.md --json report.json
```

No browser will open. The recorded crawling session will be used to perform security testing, and the report will be saved to markdown and JSON files.

#### Use Attack Module

You can specify a particular attack module for more targeted testing:

```bash
poetry run hacktor webapps <URL> --use_ai --max_crawling_steps 10 --no_of_tests 10 --attack_module OWASP-LLM-APP --json report.json --markdown report.md -v
```

### Augment your Burp Scanner

Test any burp recorded http request testing:

1. Use Burpsuite to intercept requests made to the GenAI application.
2. Save this request to a file.
3. Run `poetry run hacktor burp <URL> -r <Request file path>` to start testing.
4. The tool automatically fuzzes requests using the recorded prompt.
5. Generate a report summarizing the fuzzing results.
6. Reports can be printed to the console or saved for further analysis.

#### Example Command

```bash
poetry run hacktor burp <URL> -r <Request file path>
```

## Use Cases

### Red Teaming GenAI Chatbots

Craft toxic prompts to test the resilience of your GenAI chatbots against adversarial attacks. Hacktor aids in evaluating your chatbot's ability to handle unexpected or malicious inputs.

### Mobile GenAI App Security Testing

Fortify the security of your GenAI mobile apps. By combining Hacktor with Burpsuite:

- Decompile the mobile app to understand its inner workings.
- Record requests and responses using Burp to capture the app's interactions.
- Test the captured APIs using Hacktor to identify potential vulnerabilities.

### CI/CD Integration for GenAI Testing

Streamline GenAI security testing into your CI/CD pipeline, ensuring continuous security throughout the development lifecycle. Hacktor integrates with Playwright to:

- Record user sessions within the GenAI application.
- Automatically execute Hacktor tests based on recorded sessions during the CI/CD process.

## Features 

### AI Assisted Chat Crawler 

The AI Assisted Chat Crawler in Hacktor leverages advanced AI capabilities to enhance the security testing of GenAI chat applications. By using the --use_ai option, Hacktor intelligently analyzes and interacts with chat interfaces to identify potential vulnerabilities that may not be easily detectable through traditional methods. The AI-driven approach allows for more sophisticated crawling and testing, making it ideal for evaluating the robustness and security of chatbots and other conversational AI systems.

### Human-Assisted Fuzz Location Detection

Hacktor involves detecting fuzzing locaiton in web applications with human assistance, which is essential for modern web frameworks. This approach involves using a browser to record crawled data and inserting markers like `[FUZZ]` for fuzzing or testing purposes.

### Testing GenAI Chatbot for OWASP TOP 10 Categories

Hacktor generates various prompts, sends them to a GenAI chatbot, collects responses, and evaluates them, focusing on testing the chatbot's responses against OWASP TOP 10 categories.

### MLOps / DevOps Integration - Regression Security Testing of GenAI ChatBots

Hacktor enables saving crawled sessions and running tests as part of the DevOps regression testing process, focusing on the regression security testing of GenAI chatbots.

## Powered by 

### Detoxio APIs for LLM Testing

Hacktor leverages Detoxio SDK and APIs for features like:

- **Prompt Generation**: Generate toxic prompts using the Testing Platform.
- **Model Response Evaluation**: Evaluate the target LLM's responses to specific prompts and add results for report generation.
- **Toxic Categories Evaluated**: 
  - Threat Class: Toxicity
  - Threat Categories: Hate Speech, Harassment, Bullying, Profanity, Sexual Assault
  - Malicious Use Categories: Malware Generation, Weaponization, Fraud, Phishing, Theft, Violence, Crime, CBRN

### Playwright Framework

Hacktor uses [Playwright](https://playwright.dev/) to record crawled data.

## How to Start Development

### Clone the Repository

```bash
git clone https://github.com/detoxio/hacktor
```

### Install Dependencies

```bash
pip install poetry
cd hacktor
poetry install
```

### Develop and Run the Code

Start developing and running Hacktor:

```bash
poetry run hacktor
```

*Ensure that you set the Detoxio AI API key before running.*

## License

This project is distributed under

 the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

© [Detoxio](https://detoxio.ai)
