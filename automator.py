import os
import re
import sys
import time
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
    "AI_TOOL": "https://www.example-affiliate.com/tracking-id-1"
}

def generate_slug(title_string):
    slug = title_string.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    return re.sub(r'[\s-]+', '-', slug).strip('-') + ".html"

# ==========================================
# 3. GENERATE HUMANIZED CORE CONTENT
# ==========================================
prompt = f"""
Context: You are a Senior B2B SaaS Technical Support Engineer writing highly practical troubleshooting columns for digital freelancers and creative professionals. Your tone is conversational, authoritative, clear, and direct—devoid of robotic AI fluff, generic introductory filler sentences, or corporate jargon. Write as if you are diagnosing a problem for a peer.

To avoid duplication, here are the topics you have ALREADY covered:
---
{past_topics}
---

Your Task:
1. Select a highly narrow troubleshooting problem, cryptic error code, or system limitation that digital creators face inside popular creative platforms (e.g., DaVinci Resolve, Canva, Adobe Suite, Premiere, Figma).
2. Write a comprehensive, 1,200-word deep-dive manual to resolve the issue.

Formatting Rules (Markdown Protocol):
- Output your content in clean, structured Markdown format.
- Begin your response with a single '# ' style title block (e.g., # Fixing the Graphic Glitch).
- Follow immediately with a 50-word bolded summary paragraph explaining the root issue and quick fix.
- Use '## ' and '### ' headers for clear structural breakdown. 
- Use standard markdown bolding (**text**) and bullet configurations (- item) naturally.
- Weave the tracking placeholder [LINK:AI_TOOL] organically into your recommended solution steps.
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
    raw_markdown = response.text
except Exception as e:
    print(f"CRITICAL ERROR: Gemini API call failed: {e}")
    sys.exit(1)

# Helper functions to convert raw markdown to clean responsive HTML structures
def md_to_html(text):
    text = re.sub(r'^#\s+(.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Process bullet list blocks safely
    processed_lines = []
    in_list = False
    for line in text.split('\n'):
        if line.strip().startswith('- '):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            processed_lines.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            if line.strip():
                if not line.strip().startswith('<h') and not line.strip().startswith('<u') and not line.strip().startswith('<l'):
                    processed_lines.append(f'<p>{line.strip()}</p>')
            else:
                processed_lines.append('')
    if in_list:
        processed_lines.append('</ul>')
    return '\n'.join(processed_lines)

html_body = md_to_html(raw_markdown)

# Extract generated title
title_match = re.search(r'<h1>(.*?)</h1>', html_body)
extracted_title = title_match.group(1).strip() if title_match else "Technical Diagnostic Log"
filename = generate_slug(extracted_title)

# Clean out the inline h1 string to control site template positioning
html_body = re.sub(r'<h1>.*?</h1>', '', html_body, count=1).strip()

# Inject active partner monetization routes
for placeholder, real_link in AFFILIATE_LINKS.items():
    link_html = f'<a href="{real_link}" target="_blank" style="color: #0066cc; font-weight: bold; text-decoration: underline;">Check out our recommended optimization tool here</a>'
    html_body = html_body.replace(f"[LINK:{placeholder}]", link_html)

# Generate unique image signatures based on epoch time parameters to prevent repeating assets
timestamp_sig = int(time.time())

# ==========================================
# 4. MASTER FRAMEWORK ASSEMBLY (MOBILE FIRST)
# ==========================================
full_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{extracted_title} - GadTech Labs</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 700px; margin: 0 auto; padding: 25px 20px; color: #333; }}
        h1 {{ color: #111; font-size: 2.25rem; font-weight: 800; line-height: 1.2; margin: 0 0 15px 0; letter-spacing: -0.5px; }}
        h2 {{ color: #111; font-size: 1.5rem; font-weight: 700; margin: 1.6em 0 12px 0; border-bottom: 1px solid #eee; padding-bottom: 6px; }}
        h3 {{ color: #111; font-size: 1.2rem; margin: 1.4em 0 8px 0; }}
        p {{ margin: 0 0 20px 0; font-size: 1.05rem; text-align: justify; }}
        ul {{ margin: 0 0 20px 0; padding-left: 20px; }}
        li {{ margin-bottom: 6px; font-size: 1.05rem; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        img.hero {{ width: 100%; height: auto; aspect-ratio: 16/9; object-fit: cover; border-radius: 8px; margin: 20px 0 25px 0; display: block; background: #fafafa; }}
        img.inline {{ width: 100%; height: auto; aspect-ratio: 16/10; object-fit: cover; border-radius: 6px; margin: 25px 0 8px 0; display: block; border: 1px solid #eee; background: #fafafa; }}
        .caption {{ text-align: center; font-size: 0.85rem; color: #666; font-style: italic; margin-bottom: 25px; }}
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
        <img src="https://images.unsplash.com/featured/?technology,hardware&sig={timestamp_sig}" class="hero" alt="Technical Workspace Setup">
        
        {html_body}
        
        <img src="https://images.unsplash.com/featured/?workspace,code&sig={timestamp_sig + 1}" class="inline" alt="Diagnostic Console Tracking">
        <p class="caption">System diagnostics data layer confirmation matrix configuration.</p>
    </main>
</body>
</html>
"""

try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_page_html)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(extracted_title + "\n")
    print(f"SUCCESS: Assembled humanized post layout: {filename}")
except Exception as e:
    print(f"CRITICAL ERROR: Failed saving article: {e}")
    sys.exit(1)

# ==========================================
# 5. RESPONSE HOMEPAGE GENERATOR
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
    print("SUCCESS: Full dynamic portal rollout complete!")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to write homepage: {e}")
    sys.exit(1)
