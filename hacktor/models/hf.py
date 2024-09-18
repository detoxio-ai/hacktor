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
    def __init__(self, model_id:str):
        self.model_id = model_id 
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )
    
    def generate(self, prompt_txt, max_tokens=2048, temperature=0.7, top_k=50, top_p=0.95):
        messages = [{"role": "user", "content": prompt_txt}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = self.pipeline(prompt, max_new_tokens=max_tokens, do_sample=True, temperature=temperature, top_k=top_k, top_p=top_p)
        output = outputs[0]["generated_text"]
        return output, output

class GPT2(HFModel):
    def __init__(self):
        super().__init__(model_id=HF_MODEL_IDS.GPT2.value)
    
    def generate(self, prompt_txt, max_tokens=256, temperature=0.7, top_k=50, top_p=0.95):
        super().generate(prompt_txt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p)



class HFModelFactory:
    
    MODEL_MAP = {
        HF_MODEL_IDS.GPT2: GPT2()
    }
    
    def __init__(self):
        pass
    
    def get_instance(self, model_id:str):
        if model_id in HF_MODEL_IDS.list_options():
            _model_id = HF_MODEL_IDS(model_id)
            return self.MODEL_MAP.get(_model_id) 
        else:
            return HFModel(model_id) 