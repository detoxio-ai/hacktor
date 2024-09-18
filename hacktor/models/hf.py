from enum import Enum
from transformers import AutoTokenizer
import transformers
import torch


class HF_MODEL_IDS(Enum):
    GPT2 = "gpt2"

    @classmethod
    def list_options(cls):
        return [option.value for option in cls]

class HFModel:
    def __init__(self, model_id: str):
        self.model_id = model_id 
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.generator = transformers.pipeline(
            "text-generation",
            model=self.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )

    def run(self, prompt_txt, system_prompt="", max_tokens=2048, temperature=0.7, top_k=50, top_p=0.95):
        outputs = self._run(prompt_txt, system_prompt=system_prompt,
                  max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p)
        output = outputs[0]["generated_text"]
        # Replace the prompt itself from the output
        if output:
            output = output.replace(prompt_txt, "")
        return output

    def _run(self, prompt_txt, system_prompt="", max_tokens=2048, temperature=0.7, top_k=50, top_p=0.95):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt_txt})

        # Handle tokenizer chat template, if available
        if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template:
            prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            # Fall back to constructing the prompt manually
            prompt = self._construct_fallback_prompt(messages)

        outputs = self.generator(prompt, max_new_tokens=max_tokens, do_sample=True, temperature=temperature, top_k=top_k, top_p=top_p)
        return outputs

    def _construct_fallback_prompt(self, messages):
        """
        Fallback method to manually construct the chat prompt if no chat template is available.
        """
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                prompt += f"{content}\n"
            elif role == "user":
                prompt += f"{content}\n"
        return prompt


class GPT2(HFModel):
    def __init__(self):
        super().__init__(model_id=HF_MODEL_IDS.GPT2.value)
    
    def _run(self, prompt_txt, system_prompt="", max_tokens=256, temperature=0.7, top_k=50, top_p=0.95):
        if system_prompt:
            prompt = f"{system_prompt}\n{prompt_txt}"
        else:
            prompt = prompt_txt
        outputs = self.generator(prompt, max_new_tokens=max_tokens, do_sample=True, temperature=temperature, top_k=top_k, top_p=top_p)
        return outputs

class HFModelFactory:
    
    MODEL_MAP = {
        HF_MODEL_IDS.GPT2.value: GPT2
    }
    
    def __init__(self):
        pass
    
    @classmethod
    def get_instance(self, model_id:str):
        if model_id in HF_MODEL_IDS.list_options():
            return self.MODEL_MAP.get(model_id)()
        else:
            return HFModel(model_id) 