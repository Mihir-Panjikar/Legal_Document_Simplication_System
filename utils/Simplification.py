import os
import torch
from functools import lru_cache
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from .formatter import format_messages

os.environ["TRANSFORMERS_OFFLINE"] = "1"

local_model_path = "./DeepSeek-R1-Distill-Qwen-1.5B"

# Cache Model Loading (Ensures it's loaded only once)
@lru_cache(maxsize=1)
def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,  # More efficient than 8-bit
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        llm_int8_enable_fp32_cpu_offload=True  # Prevents CPU-GPU mismatch issues
    )

    model = AutoModelForCausalLM.from_pretrained(
        local_model_path,
        device_map="auto",  # Optimizes layer placement across CUDA devices
        torch_dtype=torch.float16,
        quantization_config=quantization_config
    )

    tokenizer = AutoTokenizer.from_pretrained(local_model_path)

    return model, tokenizer, device

# Load model & tokenizer once
model, tokenizer, device = load_model()

def simplify_document(user_input, max_new_tokens=1024):
    """Simplifies a legal document using an optimized CUDA-based LLM."""
    
    system_message = (
        "You are an expert in summarization and legal document simplification. Your task is to summarize the following agreement "
        "in a way that is easy for a layperson to understand. The summary should include all key details while using simple, clear language "
        "and relevant real-life examples where needed. Ensure that no critical information is lost.\n\n"
        "Key requirements for the summary:\n\n"
        "Use plain English, avoiding complex legal terms.\n"
        "Provide relevant examples to make the agreement more understandable.\n"
        "Maintain all important details, such as duration, termination clauses, liability, dispute resolution, and governing law.\n"
        "Ensure the summary remains concise but does not miss crucial points."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input}
    ]
    prompt = format_messages(messages)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=max_new_tokens)

    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    return generated_text.split("Simplified version:")[-1].strip() if "Simplified version:" in generated_text else generated_text.strip()