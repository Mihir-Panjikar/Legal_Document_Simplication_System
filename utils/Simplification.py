import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from .formatter import format_messages

# Setup: local model loading
os.environ["TRANSFORMERS_OFFLINE"] = "1"  # Prevents downloading from Hugging Face
local_model_path = "./DeepSeek-R1-Distill-Qwen-1.5B" 

# quantization config for 8-bit model

device = "cuda" if torch.cuda.is_available() else "cpu"

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_enable_fp32_cpu_offload=False
) if device == "cuda" else None


# Loading the quantized model and tokenizer from the local path
model = AutoModelForCausalLM.from_pretrained(
    local_model_path,
    device_map="device",
    torch_dtype=torch.float16,
    quantization_config=quantization_config
)
tokenizer = AutoTokenizer.from_pretrained(local_model_path)


def simplify_document(user_input, max_new_tokens=1024):
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
    
    # Tokenize and send to model device (GPU if available)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate the output
    output = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Optionally, strip out the prompt portion if present
    if "Simplified version:" in generated_text:
        simplified = generated_text.split("Simplified version:")[-1].strip()
    else:
        simplified = generated_text.strip()
    return simplified