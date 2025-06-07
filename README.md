# Website Cloner – Orchids Challenge Submission

This is a local web app that clones any public website using a combination of:

- **Playwright** (for fully rendered HTML & CSS scraping)
- **BeautifulSoup** (to clean & parse the DOM)
- **CodeGen-350M** (for HTML regeneration using LLM)
- **FastAPI** (to expose the backend API)
- **Next.js or React (frontend)** for user interaction

---

## Project Summary

This app lets users input any URL, fetches the fully rendered HTML and CSS, and uses a local LLM (CodeGen-350M) to generate a cleaned, aesthetic HTML-only clone of the website.

---

## Setup Instructions

### 1. Clone or extract this repo

If you're using the `.zip`, just extract the contents.

```bash
cd orchids-challenge/backend

# (Optional) Create virtual environment
python -m venv .venv
# Activate it
# On Windows:
. .venv/Scripts/activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python hello.py

### 2. Setup the Frontend (Next.js UI)

cd orchids-challenge/frontend

# Install dependencies
npm install

# Run frontend
npm run dev

### How It Works
Type a website URL in the input box (e.g. https://example.com)

Click Clone Now

Wait for the HTML preview to load

Toggle View Code to see the generated HTML

###LLM Model

Model: Salesforce/codegen-350M-multi

Runs locally (no API key needed)

HTML is passed to the LLM with a structured prompt

Output is clean, readable HTML
