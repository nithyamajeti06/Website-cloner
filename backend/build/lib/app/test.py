# backend/app/test_claude.py

import os
from main import call_llm_with_claude

# A very small “fake” context just to see if Claude returns something:
dummy_context = {
    "html": "<!DOCTYPE html><html><head><title>Test Page</title></head><body><h1>Hello from Test</h1></body></html>",
    "styles": ["https://example.com/style.css"],
    "assets": {
        "images": ["https://example.com/logo.png"],
        "fonts": [],
        "others": []
    },
    "screenshot_png": None
}

if __name__ == "__main__":
    print("👉  Testing Claude‐4‐Sonnet call…")
    try:
        result_html = call_llm_with_claude(dummy_context)
        print("\n✅ Claude returned HTML (first 300 chars):\n")
        print(result_html[:300])
    except Exception as e:
        print("\n❌ Claude raised an exception:\n")
        print(e)
