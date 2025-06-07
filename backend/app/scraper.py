# backend/app/scraper.py
import sys
import asyncio
import random
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# List of User-Agent strings for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
]

def scrape_with_playwright(url: str, screenshot: bool = False) -> dict:
    """
    Open the page in headless Chromium, wait for JS to run,
    capture the final HTML and CSS links, and optionally take a screenshot.
    Returns a dict with:
      {
        "html": "<!doctype html>…</html>",
        "styles": ["https://…/main.css", …],
        "assets": {
          "images": ["https://…/logo.png", …],
          "fonts": ["https://…/font.woff2", …],
          "others": ["…other requests…"]
        },
        "screenshot_png": b"<binary PNG data>"  # only if screenshot=True
      }
    """
    result = {"html": "", "styles": [], "assets": {}, "screenshot_png": None}

    with sync_playwright() as pw:
        # 1) Launch headless Chromium
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        # 2) Rotate User-Agent header to reduce blocking
        page.set_extra_http_headers({
            "User-Agent": random.choice(USER_AGENTS)
        })

        # 3) Intercept network requests to collect asset URLs
        assets = {"images": set(), "fonts": set(), "others": set()}

        def handle_request(route, request):
            req_url = request.url
            if any(req_url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"]):
                assets["images"].add(req_url)
            elif any(req_url.lower().endswith(ext) for ext in [".woff", ".woff2", ".ttf", ".otf"]):
                assets["fonts"].add(req_url)
            else:
                assets["others"].add(req_url)
            route.continue_()

        page.route("**/*", handle_request)

        # 4) Navigate to the target URL and wait until network is idle
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Optional: scroll down to trigger lazy-loaded content
        # page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        # time.sleep(1)

        # 5) Get the fully rendered HTML
        rendered_html = page.content()

        # 6) Optionally take a full-page screenshot
        if screenshot:
            result["screenshot_png"] = page.screenshot(type="png", full_page=True)

        browser.close()

    # 7) Parse the rendered HTML with BeautifulSoup to extract CSS links
    soup = BeautifulSoup(rendered_html, "html.parser")
    styles = [
        tag.get("href")
        for tag in soup.find_all("link", rel="stylesheet")
        if tag.get("href")
    ]

    result["html"] = rendered_html
    result["styles"] = styles
    result["assets"] = {
        "images": list(assets["images"]),
        "fonts": list(assets["fonts"]),
        "others": list(assets["others"]),
    }

    return result

if __name__ == "__main__":
    # A minimal test: try rendering httpbin.org/html (a static page) and print the first 200 chars
    test_url = "https://httpbin.org/html"
    print(f"Testing Playwright rendering for {test_url}…")
    result = scrape_with_playwright(test_url, screenshot=False)
    print("Page rendered successfully. First 200 characters of HTML:\n")
    print(result["html"][:200])
    print("\nDetected CSS links:\n", result["styles"])
    print("\nDetected asset URLs (images/fonts/others):\n", result["assets"])
