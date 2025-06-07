# File: orchids-challenge/backend/hello.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import uvicorn

# ─── Load CodeGen-350M locally ───────────────────────────────────────────────────
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

MODEL_NAME = "Salesforce/codegen-350M-multi"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32)
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=1500,
    do_sample=False,
    return_full_text=False,   # only return the generated HTML
    device_map="cpu",
)

# ─── FastAPI setup ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Orchids Challenge (CodeGen-350M)",
    description="Scrape & clone websites using CodeGen-350M locally",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CloneRequest(BaseModel):
    url: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchids-codegen"}

@app.get("/test-codegen")
async def test_codegen():
    """
    Generates only the raw HTML for a minimal page with <h1>Hello from CodeGen-350M</h1>.
    """
    prompt = (
        "### Instructions:\n"
        "- Generate ONLY the raw HTML for a minimal static page.\n"
        "- The page must contain exactly <h1>Hello from CodeGen-350M</h1> as its heading.\n"
        "- Do NOT include any comments, docstrings, or JavaScript.\n\n"
        "### HTML:\n"
    )
    try:
        out = generator(prompt, max_new_tokens=200)
        # extract only the HTML string
        return {"sample_html": out[0]["generated_text"]}
    except Exception as e:
        return {"error": str(e)}

def fetch_rendered_html(url: str) -> str:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.text

@app.post("/clone")
async def clone_website(data: CloneRequest):
    url = data.url

    # a) Fetch raw HTML
    try:
        raw_html = fetch_rendered_html(url)
    except Exception as e:
        return {"detail": f"Error fetching URL: {e}"}

    # b) Strip out <script> and <iframe>
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup.find_all(["script", "iframe"]):
        tag.decompose()
    cleaned = soup.prettify()

    # c) Build prompt for HTML/CSS only
    prompt = (
        "### Instructions:\n"
        "- You are a front-end engineer. Below is the stripped HTML of a web page.\n"
        "- Generate ONLY the final static HTML and CSS (using TailwindCSS classes is OK).\n"
        "- Do NOT include any JavaScript or function wrappers.\n\n"
        "### HTML:\n"
        f"{cleaned}\n"
    )

    # d) Generate clone
    try:
        out = generator(prompt, max_new_tokens=1500)
        return {"cloned_html": out[0]["generated_text"]}
    except Exception as gen_err:
        # fallback to cleaned HTML if generation fails
        return {"detail": f"Generation failed: {gen_err}", "cloned_html": cleaned}

if __name__ == "__main__":
    uvicorn.run("hello:app", host="127.0.0.1", port=8000, reload=True)
