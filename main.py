from transformers import AutoTokenizer, AutoModelForSequenceClassification
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()


MODEL_PATH = "./InLegalBERT"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model or tokenizer: {e}")


class LegalText(BaseModel):
    text: str


@app.post("/")
async def index(legal_text: LegalText):
    try:
        # Tokenize the input text
        inputs = tokenizer(
            legal_text.text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        # Model inference
        outputs = model(**inputs)

        # Get probabilities (softmax)
        probabilities = outputs.logits.softmax(dim=-1).detach().numpy()

        # Extract predicted class
        predicted_class = probabilities.argmax(axis=-1).tolist()[0]

        return {
            "input_text": legal_text.text,
            "predicted_class": predicted_class,
            "probabilities": probabilities.tolist()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
