import os
import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Use MPS backend
device = "mps" if torch.backends.mps.is_available() else "cpu"

# Setup: local model loading
os.environ["TRANSFORMERS_OFFLINE"] = "1"  # Prevents downloading from Hugging Face
local_model_path = "./DeepSeek-R1-Distill-Qwen-1.5B" 

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    local_model_path,
    use_safetensors=True
).to(device)

tokenizer = AutoTokenizer.from_pretrained(local_model_path)

model = torch.compile(model)

# Function to Format the Input Messages
def format_messages(messages):
    return "\n\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages)

# Function to Simplify the Legal Document Text
def simplify_document(user_input, max_new_tokens=1024):
    system_message = (
        "You are an expert in summarization and legal document simplification. Your task is to summarize the following agreement "
        "in a way that is easy for a layperson to understand. The summary should include all key details while using simple, clear language "
        "and relevant real-life examples where needed. Ensure that no critical information is lost.\n\n"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input}
    ]

    prompt = format_messages(messages)

    # Tokenize and move to device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Generate output
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=max_new_tokens)

    return tokenizer.decode(output[0], skip_special_tokens=True)

# Streamlit UI
st.set_page_config(page_title="Legal Document Simplifier", layout="wide")
st.title("Legal Document Simplification System")
st.markdown("##### Enter legal text for simplification")

# User input
user_input = st.text_area("Enter legal document text:", height=300)

if st.button("Simplify"):
    if user_input.strip():
        with st.spinner("Simplifying..."):
            result = simplify_document(user_input)
        st.markdown("### Simplified Text:")
        st.write(result)
    else:
        st.error("Please enter some text.")
