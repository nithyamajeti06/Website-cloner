# # backend/app/main.py
# import anthropic
# import os
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# # Import the Anthropic client instead of openai
# from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# # Import your Playwright-based scraper
# from .scraper import scrape_with_playwright

# # Initialize Anthropic with your Sonnet API key
# anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# app = FastAPI()

# # Allow requests from any origin (so localhost:3000 can reach it)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class CloneRequest(BaseModel):
#     url: str

# def call_llm_with_claude(design_context: dict) -> str:
#     """
#     Uses Claude 4 Sonnet to generate a clean HTML+CSS clone based on:
#       - Fully rendered HTML (truncated)
#       - List of CSS link URLs
#       - Asset URLs (images, fonts, etc.)
#       - (optional) Screenshot data if you want to send that separately
#     Returns only the final HTML string.
#     """
#     # 1) Truncate rendered HTML so we stay under token limits
#     html_snippet = design_context["html"][:2000]

#     # 2) Turn CSS link URLs into newline-separated text
#     css_links_text = "\n".join(design_context["styles"])

#     # 3) Summarize asset URLs into a Python-like dict string
#     assets_info = design_context["assets"]

#     # 4) Build a single prompt for Claude
#     prompt_body = f"""
# You are a world-class front-end developer. Your job is to produce a standalone HTML+CSS clone
# of a website, matching pixel-perfect layout and styling.

# Below is all the context you need:

# 1) Fully rendered HTML (truncated for brevity):
# {html_snippet}

# 2) CSS link URLs (each on its own line):
# {css_links_text}

# 3) Asset URLs (images, fonts, etc.) in JSON-like format:
# {assets_info}

# Please output ONLY the final HTML code (including any <style> or <link> tags necessary,
# and embedding small images as data URIs if needed). Do NOT include any explanation,
# reasoning, or commentary—just the raw HTML.
# """.strip()

#     # 5) Send the prompt to Claude 4 Sonnet
#     response = anthropic.completions.create(
#         model="claude-4-sonnet",
#         prompt=HUMAN_PROMPT + prompt_body + AI_PROMPT,
#         max_tokens_to_sample=2000,    # adjust based on how large you expect the clone to be
#         temperature=0.2,              # low temperature for deterministic, consistent output
#     )

#     return response.completion

# @app.post("/clone")
# def clone_website(data: CloneRequest):
#     try:
#         context = scrape_with_playwright(data.url, screenshot=True)
#         cloned_html = call_claude_llm(context)
#         return {"cloned_html": cloned_html}
#     except Exception as e:
#         # Print the full traceback to the console so you can read it in Uvicorn logs
#         traceback.print_exc()
#         # Return the exception message in JSON so the frontend can display it
#         raise HTTPException(status_code=500, detail=f"Server error: {repr(e)}")


# @app.get("/")
# def read_root():
#     return {"message": "Hello World"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# def call_claude_llm(context: dict) -> str:
#     """
#     Calls Claude Sonnet with the scraped design context and returns generated HTML.
#     """
#     client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

#     prompt = f"""
# You are a helpful assistant that generates clean and readable HTML/CSS websites.
# Your goal is to recreate a public webpage based on the following context:

# --- PAGE HTML ---
# {context['html']}

# --- STYLESHEETS ---
# {context['styles']}

# --- IMAGE URLS ---
# {context['assets']['images']}

# Please output valid and simplified HTML + CSS that visually resembles the original page.
# Do not include any JavaScript or tracking code.
# Wrap everything in a single <html> document.
# """

#     response = client.messages.create(
#         model="claude-3-sonnet-20240229",
#         max_tokens=4000,
#         temperature=0.2,
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return response.content[0].text

# backend/app/main.py

import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the Anthropic client (Claude 3 Sonnet)
import anthropic

# Import your Playwright scraper (adjust if your scraper function has a different name)
from .scraper import scrape_with_playwright

# ─── FastAPI Setup ────────────────────────────────────────────────────────────
app = FastAPI()

# Allow CORS from any origin (so that your Next.js dev server on localhost:3000 can reach it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for the POST /clone request body
class CloneRequest(BaseModel):
    url: str

# ─── Claude (Anthropic) Helper ────────────────────────────────────────────────

def call_claude_llm(context: dict) -> str:
    """
    Calls Claude 3 Sonnet (anthropic-3) with the scraped context and returns the generated HTML.

    context: {
        "html": "<full rendered HTML string>",
        "styles": ["https://…/main.css", …],
        "assets": {
            "images": [...],
            "fonts": [...],
            "others": [...],
        },
        "screenshot_png": bytes or None
    }
    """

    # 1) Read the API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise Exception("ANTHROPIC_API_KEY is not set in environment.")

    client = anthropic.Anthropic(api_key=api_key)

    # 2) Build a prompt that sends Claude a truncated version of the rendered HTML + CSS links
    #    (You can adjust the truncation length to stay within token limits)
    rendered_html_snippet = context["html"][:2000]  # grab first 2000 chars of HTML
    css_links_text        = "\n".join(context["styles"])
    image_urls_text       = "\n".join(context["assets"]["images"])

    # 3) Compose the system/user prompt
    prompt = f"""
You are a world-class front-end developer. Your job is to produce a standalone HTML+CSS clone
of a public website based on the following context (rendered HTML, CSS links, and image URLs).
Do NOT include any JavaScript; output only a valid HTML document (with <head> and <body>),
and either inline small CSS within a <style> tag or use <link rel="stylesheet"> tags exactly
as needed. Do NOT output any explanation or commentary—only the final HTML code.

--- FULLY RENDERED HTML (truncated to 2000 chars) ---
{rendered_html_snippet}

--- CSS LINK URLs (one per line) ---
{css_links_text}

--- IMAGE URLs (one per line) ---
{image_urls_text}

(If an image URL is very large, you may embed it as a data URL in the <img> tag; otherwise,
feel free to reference it normally. The goal is to visually match the original page.)
""".strip()

    # 4) Send the prompt to Claude 3 Sonnet
    try:
        response = client.completions.create(
            model="claude-3-sonnet-20240229",  # or whichever Sonnet model Anthropic gave you
            prompt=anthropic.HUMAN_PROMPT + prompt + anthropic.AI_PROMPT,
            max_tokens_to_sample=4000,         # adjust if you expect bigger clones
            temperature=0.2,                   # low temperature = more deterministic HTML
        )
    except Exception as e:
        # If Anthropic’s client throws, raise it so that our /clone endpoint can catch & show it
        raise Exception(f"Anthropic API error: {e}")

    # 5) Return Claude’s generated HTML string
    return response.completion

# ─── /clone Endpoint ────────────────────────────────────────────────────────────

@app.post("/clone")
def clone_website(request: CloneRequest):
    """
    1) Use Playwright (scrape_with_playwright) to fully render the target site (HTML + CSS links + assets).
    2) Send that context to Claude 3 Sonnet (call_claude_llm) to get back clean HTML.
    3) Return {"cloned_html": "<the HTML code>"}
    """

    try:
        # A) Scrape the site with Playwright (this runs headless Chromium and waits for network idle)
        context = scrape_with_playwright(request.url, screenshot=False)

        # B) Call Claude 3 Sonnet to generate the final clone
        cloned_html = call_claude_llm(context)

        return { "cloned_html": cloned_html }

    except Exception as e:
        # Print full traceback in the Uvicorn console for debugging
        traceback.print_exc()

        # Return a 500 error with the exception’s repr() so the frontend sees the real message
        raise HTTPException(status_code=500, detail=f"Server error: {repr(e)}")


@app.get("/")
def read_root():
    return { "message": "Hello World" }


# ─── If you run this file directly, launch Uvicorn (optional) ────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
