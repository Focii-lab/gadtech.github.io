import os
import re
import sys
import urllib.parse
from google import genai
from google.genai import types

# ==========================================
# 1. INITIALIZATION & SECURITY CHECK
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: 'GEMINI_API_KEY' secret is missing.")
    sys.exit(1)

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize GenAI Client: {e}")
    sys.exit(1)

# ==========================================
# 2. FILE PATH DATA LAYERS
# ==========================================
HISTORY_FILE = "past_topics.txt"
INDEX_FILE = "index.html"

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        past_topics = f.read().strip()
else:
    past_topics = "None (This is the brand-new first post)."

AFFILIATE_LINKS = {
    "AI_TOOL": "https://www.example-affiliate.com/tracking-id-1",
    "BOOK_REC": "https://www.example-affiliate.com/tracking-id-2"
}

def generate_slug(title_string):
    slug = title_string.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    return re.sub(r'[\s-]+', '-', slug).strip('-') + ".html"

# ==========================================
# 3. GENERATE ARTICLE CONTENT (TEXT CORE ONLY)
# ==========================================
prompt = f"""
Context: You are an expert B2B SaaS optimization blogger writing technical articles for digital creators. 
To avoid duplication, here are the topics you have ALREADY covered:
---
{past_topics}
---

Your Task:
1. Identify a highly specific, narrow troubleshooting problem, error message, or system limitation that professional digital creators face online (e.g., issues inside tools like DaVinci Resolve, Canva, Premiere Pro). Pick a topic NOT listed in the history above.
2. Write a comprehensive, 1,200-word highly actionable troubleshooting guide about it.

Formatting Guidelines (Strict Text Core):
- Do NOT output any <html>, <head>, <meta>, or <style> blocks. Output raw article content body directly.
- Use a single <h1> tag for your main headline at the absolute top of your response.
- Place a 50-word bolded summary paragraph (<p><b>...</b></p>) immediately under that <h1>.
- Use structured <h2> and <h3> tags for subheaders.
- For lists, use standard <ul> and <li> tags. Do NOT use markdown notation like ** or ## anywhere.
- Naturally weave the anchor text [LINK:AI_TOOL] as the premium recommended solution.
"""

print("Querying Gemini 2.5 Engine...")
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    article_body = response.text
except Exception as e:
    print(f"CRITICAL ERROR: Gemini API call failed: {e}")
    sys.exit(1)

# Strip out any unwanted markdown formatting wrappers
article_body = re.sub(r'(^```html\s*|^```xml\s*|^```\s*)|(\s*```$)', '', article_body.strip(), flags=re.IGNORECASE)

# Extract dynamic title name for file generation and keyword filtering
title_search = re.search(r'<h1>(.*?)</h1>', article_body)
extracted_title = title_search.group(1).strip() if title_search else "Latest Automation Update"
filename = generate_slug(extracted_title)

# Create a clean searchable topic keyword for custom Unsplash matches
words = extracted_title.lower().split()
topic_keyword = "workspace"
for core_app in ['premiere', 'davinci', 'canva', 'illustrator', 'photoshop', 'figma', 'email', 'marketing']:
    if core_app in words:
        topic_keyword = core_app
        break

# Clean up raw markdown string anomalies if any remain
for placeholder, real_link in AFFILIATE_LINKS.items():
    link_html = f'<a href="{real_link}" target="_blank" style="color: #0066cc; font-weight: bold; text-decoration: underline;">Check out our recommended optimization tool here</a>'
    article_body = article_body.replace(f"[LINK:{placeholder}]", link_html)

# Strip the raw H1 tag from the generated body text so we can control its layout structure manually
article_body_clean = re.sub(r'<h1>.*?</h1>', '', article_body, count=1).strip()

# ==========================================
# 4. RIGID MASTER FRAMEWORK ASSEMBLY (MOBILE FIRST)
# ==========================================
full_article_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{extracted_title}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 680px; margin: 0 auto; padding: 20px; color: #333; -webkit-text-size-adjust: 100%; }} 
        h1 {{ color: #111; margin: 0.5em 0 15px 0; font-size: 2.25rem; line-height: 1.2; font-weight: 800; letter-spacing: -0.5px; }}
        h2 {{ color: #111; margin: 1.6em 0 15px 0; font-size: 1.5rem; font-weight: 700; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
        h3 {{ color: #111; margin: 1.4em 0 10px 0; font-size: 1.2rem; }} 
        p {{ margin: 0 0 20px 0; font-size: 1.05rem; }}
        ul, ol {{ margin: 0 0 20px 0; padding-left: 20px; }}
        li {{ margin-bottom: 8px; font-size: 1.05rem; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        img.blog-hero {{ width: 100%; height: auto; aspect-ratio: 16/9; object-fit: cover; border-radius: 8px; margin: 15px 0 25px 0; display: block; background: #eee; }}
        img.inline-ill {{ width: 100%; height: auto; aspect-ratio: 16/10; object-fit: cover; border-radius: 6px; margin: 25px 0 10px 0; border: 1px solid #eee; display: block; background: #eee; }}
        .img-caption {{ text-align: center; font-size: 0.85rem; color: #666; margin-top: 0; margin-bottom: 25px; font-style: italic; }}
        @media (max-width: 600px) {{
            body {{ padding: 15px; }}
            h1 {{ font-size: 1.75rem; }}
            h2 {{ font-size: 1.35rem; }}
            p, li {{ font-size: 1rem; }}
        }}
    </style>
</head>
<body>
    <main>
        <h1>{extracted_title}</h1>
        <img src="https://images.unsplash.com/featured/?{urllib.parse.quote(topic_keyword)},tech&sig=1" class="blog-hero" alt="{extracted_title}">
        
        {article_body_clean}
        
        <img src="https://images.unsplash.com/featured/?analytics,charts&sig=2" class="inline-ill" alt="Technical Metrics Analysis">
        <p class="img-caption">System analytical visualization metrics log snapshot parameters.</p>
    </main>
</body>
</html>
"""

try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_article_html)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(extracted_title + "\n")
    print(f"SUCCESS: Assembled responsive article cleanly: {filename}")
except Exception as e:
    print(f"CRITICAL ERROR: Failed writing article file: {e}")
    sys.exit(1)

# ==========================================
# 5. DYNAMIC HOMEPAGE (INDEX.HTML) GENERATOR
# ==========================================
print("Compiling responsive homepage index roll...")

with open(HISTORY_FILE, "r", encoding="utf-8") as f:
    all_posts = [line.strip() for line in f.readlines() if line.strip()]

all_posts = [post for post in all_posts if post != "Baseline History Init"]

list_items_html = ""
for post_title in reversed(all_posts):
    post_url = generate_slug(post_title)
    list_items_html += f"""
    <li style="margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #eee; list-style: none;">
        <h2 style="margin: 0 0 10px 0; font-size: 1.4rem; line-height: 1.3; border: none; padding: 0;">
            <a href="{post_url}" style="color: #111; text-decoration: none; font-weight: 700;">{post_title}</a>
        </h2>
        <a href="{post_url}" style="color: #0066cc; font-size: 0.95rem; font-weight: 500;">Read Troubleshooting Guide &rarr;</a>
    </li>
    """

index_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GadTech Optimization Labs</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 680px; margin: 0 auto; padding: 40px 20px; color: #333; }}
        header {{ margin-bottom: 40px; border-bottom: 3px solid #111; padding-bottom: 20px; }}
        h1 {{ color: #111; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2; }}
        p.subtitle {{ color: #666; margin: 8px 0 0 0; font-size: 1.05rem; line-height: 1.4; }}
        ul {{ padding: 0; margin: 0; }}
        a:hover {{ text-decoration: underline !important; color: #004499 !important; }}
        @media (max-width: 600px) {{
            body {{ padding: 20px 15px; }}
            h1 {{ font-size: 1.65rem; }}
            p.subtitle {{ font-size: 0.95rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>GadTech Optimization Labs</h1>
        <p class="subtitle">Autonomous diagnostic solutions & troubleshooting playbooks for digital creators.</p>
    </header>
    <main>
        <ul>
            {list_items_html if list_items_html else '<li style="list-style:none; color:#666;">No articles published yet. Check back soon!</li>'}
        </ul>
    </main>
</body>
</html>
"""

try:
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_html_content)
    print("SUCCESS: Master template engine deployment finished!")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to write homepage: {e}")
    sys.exit(1)
