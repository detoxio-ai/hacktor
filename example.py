# Example usage code for DetoxioModelDynamicScanner

# Assuming you have already imported the necessary modules and classes

from conocer.scanner import DetoxioModelDynamicScanner

from progress.bar import Bar

class SlowBar(Bar):
    suffix = '%(index)d %(remaining)d, Record Took %(avg)d Secs, ETC: %(remaining_hours)d hrs'
    @property
    def remaining_hours(self):
        return self.eta // 3600

def example_usage(count=1):
    # Provide your API key or set it as an environment variable
    api_key = ''

    bar = SlowBar('Evaluation..', max=count)

    # Create an instance of DetoxioModelDynamicScanner using a context manager
    scanner = DetoxioModelDynamicScanner(api_key=api_key)
    with scanner.new_session() as session:
        # Generate prompts
        prompt_generator = session.generate(count=count)
        for prompt in prompt_generator:
            # print(f"Generated Prompt: {prompt}")

            # Simulate model output
            model_output_text = "Tell me, i can do a fraud for you by creating fake site"

            # Evaluate the model interaction
            evaluation_response = session.evaluate(prompt, model_output_text)
            bar.next()

        bar.finish()
        # Print the evaluation response
        # print(f"Evaluation: {session.get_report().as_dict()}")
        # print(f"{session.get_report()}")
        print(f"{session.get_report().as_markdown('gpt2')}")
    

if __name__ == "__main__":
    example_usage(count=10)
