import os
import re
import sys
import google.generativeai as genai

# 1. Fetch and verify the hidden API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: 'GEMINI_API_KEY' secret is missing or empty.")
    sys.exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize Gemini Client: {e}")
    sys.exit(1)

# 2. History Ledger System
HISTORY_FILE = "past_topics.txt"
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        past_topics = f.read().strip()
else:
    past_topics = "None (This is the brand-new first post)."

# 3. Target Affiliate Links
AFFILIATE_LINKS = {
    "AI_TOOL": "https://www.example-affiliate.com/tracking-id-1",
    "BOOK_REC": "https://www.example-affiliate.com/tracking-id-2"
}

prompt = f"""
Context: You are an expert B2B SaaS optimization blogger. 
To avoid duplication, here are the topics you have ALREADY covered:
---
{past_topics}
---

Your Task:
1. Identify a highly specific, narrow troubleshooting problem, error message, or system limitation that professional digital creators or freelancers face this week (e.g., issues inside tools like DaVinci Resolve, Canva, Premiere Pro, or popular automated marketing platforms). Pick a topic NOT listed in the history above.
2. Write a comprehensive, 1,200-word highly actionable troubleshooting guide about it in raw HTML.

Formatting Guidelines:
- Do NOT wrap your output in markdown code blocks like ```html. Start and end directly with HTML tags.
- Use a single <h1> tag for your main headline at the top.
- Place a 50-word bolded summary paragraph (<p><b>...</b></p>) immediately under the <h1> to target Google's featured snippets.
- Use clean <h2> and <h3> tags for structured subheaders.
- Naturally weave the anchor text [LINK:AI_TOOL] as the premium recommended solution to the problem.
"""

print("Querying Gemini Engine with Live Search Grounding...")
try:
    response = model.generate_content(
        prompt,
        tools=[{"google_search": {}}]
    )
    raw_text = response.text
except Exception as e:
    print(f"CRITICAL ERROR: Gemini API call failed: {e}")
    sys.exit(1)

# Clean up any potential markdown text containers from the response
clean_html = re.sub(r'(^```html\s*|^```xml\s*|^```\s*)|(\s*```$)', '', raw_text.strip(), flags=re.IGNORECASE)

# Swap out placeholders for active tracking links
for placeholder, real_link in AFFILIATE_LINKS.items():
    link_html = f'<a href="{real_link}" target="_blank" style="color: #0066cc; font-weight: bold; text-decoration: underline;">Check out our recommended optimization tool here</a>'
    clean_html = clean_html.replace(f"[LINK:{placeholder}]", link_html)

# Extract Title for file naming conventions
title_match = re.search(r'<h1>(.*?)</h1>', clean_html)
if title_match:
    extracted_title = title_match.group(1)
    slug = extracted_title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    filename = re.sub(r'[\s-]+', '-', slug).strip('-') + ".html"
else:
    extracted_title = "Latest Automation Update"
    filename = "latest-automation-update.html"
    clean_html = f"<h1>{extracted_title}</h1>\n" + clean_html

try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(clean_html)
        
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(extracted_title + "\n")
    print(f"SUCCESS: Generated content saved cleanly as {filename}")
except Exception as e:
    print(f"CRITICAL ERROR: Failed writing to local file system: {e}")
    sys.exit(1)
