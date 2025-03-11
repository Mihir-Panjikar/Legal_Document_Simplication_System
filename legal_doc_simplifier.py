import os
import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# Setup: local model loading
os.environ["TRANSFORMERS_OFFLINE"] = "1"  # Prevents downloading from Hugging Face
local_model_path = "./DeepSeek-R1-Distill-Qwen-1.5B" 

# quantization config for 8-bit model with CPU offload if needed
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_enable_fp32_cpu_offload=True
)

# Loading the quantized model and tokenizer from the local path
model = AutoModelForCausalLM.from_pretrained(
    local_model_path,
    device_map="auto",
    torch_dtype=torch.float16,
    quantization_config=quantization_config
)
tokenizer = AutoTokenizer.from_pretrained(local_model_path)

# Function to Format the Input Messages
def format_messages(messages):
    formatted = ""
    for msg in messages:
        formatted += f"{msg['role'].capitalize()}: {msg['content']}\n\n"
    return formatted

# Function to Simplify the Legal Document Text
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

# Streamlit UI
st.set_page_config(page_title="Legal Document Simplifier", layout="wide")
st.markdown("""
    <style>
        .reportview-container {
            background-color: #1e1e1e;
        }
        .sidebar .sidebar-content {
            background-color: #333333;
        }
        .css-18e3th9 {
            background-color: #2c2c2c;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("Legal Document Simplification System")
st.markdown("##### Please enter the legal text for simplification")

# Layout: left for history and right for input and output
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("History")
    # Simple history buttons; you can enhance this to save previous inputs
    history_items = ["Previous Input 1", "Previous Input 2", "Previous Input 3"]
    for item in history_items:
        if st.button(item, key=item):
            st.session_state.input_text = item

with col2:
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
    user_input = st.text_area("Enter legal document text here:", height=300, value=st.session_state.input_text)
    
    if st.button("Simplify"):
        if user_input.strip() == "":
            st.error("Please enter some text to simplify.")
        else:
            with st.spinner("Simplifying..."):
                simplified_output = simplify_document(user_input)
            st.markdown("### Simplified Text:")
            st.write(simplified_output)
