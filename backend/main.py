import json

import faiss
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from transformers import pipeline

app = FastAPI()

# Allow requests from your frontend (adjust origins if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to ["http://localhost:3000"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the structured document (support cases)
with open("support_cases.json", "r") as f:
    support_cases = json.load(f)

# Convert case issues into embeddings for retrieval
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
case_texts = [case["issue"] for case in support_cases]
case_embeddings = embed_model.encode(case_texts)

# Index embeddings for fast lookup
index = faiss.IndexFlatL2(case_embeddings.shape[1])
index.add(case_embeddings)

# Load the local LLM (using a small model for now)
qa_pipeline = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.3")

@app.options("/ask")
async def options_handler():
    return {"response": "OK"}

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_llm(request: QuestionRequest):
    question = request.question

    # Encode the user question and find similar cases
    question_embedding = embed_model.encode([question])
    _, closest_indices = index.search(question_embedding, k=1)
    
    # Retrieve the most relevant case
    best_match = support_cases[closest_indices[0][0]]

    # Prepare prompt for LLM
    prompt = f"""User Question: {question}
    Similar Past Issue: {best_match["issue"]}
    Steps Taken: {best_match["steps_taken"]}
    Solution: {best_match["solution"]}
    This question is coming from a developer and/or support person. Give then some idea on what they could test in order to diagnose this issue, outline the next steps thay can take if needed.
    """

    # Get LLM response
    response = qa_pipeline(prompt, max_length=200, do_sample=True)
    print(response[0]["generated_text"])
    formatted_response = response[0]["generated_text"].replace("\\n", "\n").strip()
    return {"response": formatted_response}

