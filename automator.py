import os
import re
import sys
import google.generativeai as genai

# 1. Error-proof Secret Check
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: 'GEMINI_API_KEY' secret is missing or not found in GitHub Secrets.")
    sys.exit(1)

try:
    genai.configure(api_key=api_key)
    # Using the standardized model name for stability
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"CRITICAL ERROR: Failed to configure Gemini API client: {e}")
    sys.exit(1)

# History ledger configuration
HISTORY_FILE = "past_topics.txt"
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        past_topics = f.read().strip()
else:
    past_topics = "None (This is the first post)."

AFFILIATE_LINKS = {
    "AI_TOOL": "https://www.example-affiliate.com/tracking-id-1",
    "BOOK_REC": "https://www.example-affiliate.com/tracking-id-2"
}

prompt = f"""
Context: You are a B2B SaaS optimization blogger. To avoid duplication, here are the topics you have ALREADY written about:
---
{past_topics}
---

Your Task (Step-by-Step):
1. Identify a highly specific, recent troubleshooting problem, error message, or narrow software alternative that freelancers, video editors, or marketers face online. Pick a niche topic NOT covered in the list above.
2. Write an explicit, deeply technical 1,200-word problem-solving guide about it formatted in raw HTML.

Formatting Guidelines:
- Do NOT wrap the output code in markdown blocks like ```html. Start directly with the HTML tags.
- Use a single <h1> for the main title at the top.
- Follow the <h1> immediately with a 50-word bolded paragraph (<p><b>...</b></p>) that answers the search query directly for featured snippet optimization.
- Use clean <h2> and <h3> tags for headers.
- Naturally insert the anchor text [LINK:AI_TOOL] as the primary software solution to the problem.
"""

print("Requesting grounded content generation from Gemini API...")
try:
    # Call the core model with integrated search capabilities enabled
    response = model.generate_content(
        prompt,
        tools=[{"google_search": {}}]
    )
    raw_text = response.text
except Exception as e:
    print(f"CRITICAL ERROR: Gemini API generation failed: {e}")
    sys.exit(1)

# 2. Advanced Regex Cleanup for Markdown Wrappers
clean_html = re.sub(r'(^```html\s*|^```xml\s*|^```\s*)|(\s*```$)', '', raw_text.strip(), flags=re.IGNORECASE)

# 3. Dynamic Link Replacements
for placeholder, real_link in AFFILIATE_LINKS.items():
    link_html = f'<a href="{real_link}" target="_blank" style="color: #0066cc; font-weight: bold;">Check out our recommended resource here</a>'
    clean_html = clean_html.replace(f"[LINK:{placeholder}]", link_html)

# 4. Fallback File Target Management
title_match = re.search(r'<h1>(.*?)</h1>', clean_html)
if title_match:
    extracted_title = title_match.group(1)
    slug = extracted_title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    filename = re.sub(r'[\s-]+', '-', slug).strip('-') + ".html"
else:
    extracted_title = "Latest Software Fix Update"
    filename = "latest-software-fix.html"
    # Inject fallback header structure if missing completely to keep the static index rendering valid
    clean_html = f"<h1>{extracted_title}</h1>\n" + clean_html

try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(clean_html)

    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(extracted_title + "\n")
    print(f"File process completed successfully. Saved output as: {filename}")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to write output files to workspace: {e}")
    sys.exit(1)
