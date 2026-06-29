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
# 3. GENERATE THE NEW POST (DYNAMIC IMAGE ARCHITECTURE)
# ==========================================
prompt = f"""
Context: You are an expert B2B SaaS optimization blogger writing highly technical articles for digital creators. 
To avoid duplication, here are the topics you have ALREADY covered:
---
{past_topics}
---

Your Task:
1. Identify a highly specific, narrow troubleshooting problem, error message, or system limitation that professional digital creators or freelancers face online (e.g., issues inside tools like DaVinci Resolve, Canva, Premiere Pro, or popular automated marketing platforms). Pick a topic NOT listed in the history above.
2. Write a comprehensive, 1,200-word highly actionable troubleshooting guide about it in raw HTML.

Formatting Guidelines (Strict Semantic HTML & Layout Architecture):
- Do NOT wrap your output in markdown code blocks like ```html. Start and end directly with HTML tags.
- Inject this global style block at the very top: 
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }} 
    h1, h2, h3 {{ color: #111; margin-top: 1.5em; }} 
    a {{ color: #0066cc; }}
    img.blog-hero {{ width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin: 20px 0; display: block; }}
    img.inline-ill {{ width: 100%; max-height: 350px; object-fit: cover; border-radius: 6px; margin: 25px 0; border: 1px solid #eee; display: block; }}
    .img-caption {{ text-align: center; font-size: 0.85rem; color: #666; margin-top: -15px; margin-bottom: 25px; font-style: italic; }}
  </style>
- Use a single <h1> tag for your main headline at the top.
- Place a 50-word bolded summary paragraph (<p><b>...</b></p>) immediately under the <h1>.
- Leave the exact placeholder string [HERO_IMAGE] right after the summary paragraph.
- Use clean <h2> and <h3> tags for structured subheaders.
- Deep within one of your major diagnostic sections, leave the exact placeholder string [INLINE_IMAGE] followed on the next line by a descriptive caption wrapped in <p class="img-caption">...</p> to match the layout context.
- For lists, use standard <ul> and <li> tags.

CRITICAL NEGATIVE CONSTRAINTS:
- You are strictly FORBIDDEN from using any markdown formatting syntax whatsoever. Do NOT use ** or ##.
- Naturally weave the anchor text [LINK:AI_TOOL] as the premium recommended solution.
"""

print("Querying Gemini 2.5 Engine with Search Grounding...")
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    raw_text = response.text
except Exception as e:
    print(f"CRITICAL ERROR: Gemini modern API call failed: {e}")
    sys.exit(1)

clean_html = re.sub(r'(^```html\s*|^```xml\s*|^```\s*)|(\s*```$)', '', raw_text.strip(), flags=re.IGNORECASE)

# Swap out affiliate links
for placeholder, real_link in AFFILIATE_LINKS.items():
    link_html = f'<a href="{real_link}" target="_blank" style="color: #0066cc; font-weight: bold; text-decoration: underline;">Check out our recommended optimization tool here</a>'
    clean_html = clean_html.replace(f"[LINK:{placeholder}]", link_html)

# Extract Title and determine dynamic contextual keyword targets
title_match = re.search(r'<h1>(.*?)</h1>', clean_html)
if title_match:
    extracted_title = title_match.group(1).strip()
    filename = generate_slug(extracted_title)
    
    # Extract the core app name or context for highly targeted images (e.g., premiere, davinci, canva)
    words = re.sub(r'[^a-zA-Z0-9\s]', '', extracted_title).lower().split()
    search_keywords = "workspace"
    for core_app in ['premiere', 'davinci', 'canva', 'illustrator', 'photoshop', 'figma', 'email', 'marketing']:
        if core_app in words:
            search_keywords = core_app if core_app != 'email' else 'marketing'
            break
else:
    extracted_title = "Latest Automation Update"
    filename = "latest-automation-update.html"
    clean_html = f"<h1>{extracted_title}</h1>\n" + clean_html
    search_keywords = "technology"

# Dynamically construct robust URL paths using Unsplash source keywords
hero_query = urllib.parse.quote(f"{search_keywords},tech")
inline_query = urllib.parse.quote(f"analytics,code")

hero_img_tag = f'<img src="[https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&h=500&q=80&sig=1](https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&h=500&q=80&sig=1)" class="blog-hero" alt="{extracted_title}">'
inline_img_tag = f'<img src="[https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&h=450&q=80&sig=2](https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&h=450&q=80&sig=2)" class="inline-ill" alt="Diagnostic Technical Data">'

# Inject the fixed image HTML layout strings directly into placeholders
clean_html = clean_html.replace("[HERO_IMAGE]", hero_img_tag)
clean_html = clean_html.replace("[INLINE_IMAGE]", inline_img_tag)

try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(clean_html)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(extracted_title + "\n")
    print(f"SUCCESS: Article written cleanly with dynamic image engine as: {filename}")
except Exception as e:
    print(f"CRITICAL ERROR: Failed writing article to disk: {e}")
    sys.exit(1)

# ==========================================
# 4. DYNAMIC HOMEPAGE (INDEX.HTML) GENERATOR
# ==========================================
print("Compiling dynamic homepage index roll...")

with open(HISTORY_FILE, "r", encoding="utf-8") as f:
    all_posts = [line.strip() for line in f.readlines() if line.strip()]

all_posts = [post for post in all_posts if post != "Baseline History Init"]

list_items_html = ""
for post_title in reversed(all_posts):
    post_url = generate_slug(post_title)
    list_items_html += f"""
    <li style="margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #eee; list-style: none;">
        <h2 style="margin: 0 0 10px 0; font-size: 1.5rem;">
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
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 60px auto; padding: 0 20px; color: #333; }}
        header {{ margin-bottom: 50px; border-bottom: 3px solid #111; padding-bottom: 20px; }}
        h1 {{ color: #111; margin: 0; font-size: 2.25rem; font-weight: 800; letter-spacing: -0.5px; }}
        p.subtitle {{ color: #666; margin: 5px 0 0 0; font-size: 1.1rem; }}
        ul {{ padding: 0; }}
        a:hover {{ text-decoration: underline !important; color: #004499 !important; }}
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
    print("SUCCESS: Homepage index.html updated successfully!")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to write homepage: {e}")
    sys.exit(1)
