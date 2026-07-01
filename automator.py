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
Context: You are a Senior Support Engineer writing a troubleshooting column for digital freelancers. Your tone is conversational, authoritative, and direct—no robotic filler phrases.

To avoid duplication, here are the topics you have ALREADY covered:
---
{past_topics}
---

Your Task:
1. Select a highly narrow troubleshooting problem, error code, or system limitation that digital creators face inside popular platforms (e.g., DaVinci Resolve, Canva, Adobe Suite, Premiere, Figma).
2. Write a comprehensive, 1,200-word deep-dive manual to resolve the issue.

Formatting Rules (Strict Markdown Protocol):
- Begin your response with a single '# ' style title block (e.g., # Fixing Premiere Pro GPU Overflows).
- Follow immediately with a 50-word bolded summary paragraph explaining the root issue and quick fix.
- Use '## ' and '### ' headers for structural breakdowns.
- Always structure lists using simple hyphens (e.g., - Step One). Do NOT use asterisks (*) for lists.
- Naturally weave the placeholder link [LINK:AI_TOOL] into your solution steps.
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
    raw_markdown = response.text
except Exception as e:
    print(f"CRITICAL ERROR: Gemini API call failed: {e}")
    sys.exit(1)

# Clean out any structural system markdown blocks if generated
raw_markdown = re.sub(r'(^```html\s*|^```markdown\s*|^```\s*)|(\s*```$)', '', raw_markdown.strip(), flags=re.IGNORECASE)

# Extract Title safely from Markdown header (# Title) or HTML h1 tag
title_match = re.search(r'^#\s+(.*?)$', raw_markdown, re.MULTILINE)
if not title_match:
    title_match = re.search(r'<h1>(.*?)</h1>', raw_markdown, re.IGNORECASE)

extracted_title = title_match.group(1).strip() if title_match else "Advanced Optimization Matrix Guide"
filename = generate_slug(extracted_title)

# Convert Markdown elements to pure HTML tags seamlessly
def convert_markdown_to_html(text):
    # Remove the main title from the body text
    text = re.sub(r'^#\s+.*?$', '', text, flags=re.MULTILINE)
    
    # Process headers
    text = re.sub(r'^##\s+(.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Process lists handling both '-' and '*' variants found in 1000186838.jpg
    processed_lines = []
    in_list = False
    for line in text.split('\n'):
        clean_line = line.strip()
        if clean_line.startswith('- ') or clean_line.startswith('* '):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            processed_lines.append(f'<li>{clean_line[2:]}</li>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            if clean_line:
                if not clean_line.startswith('<h') and not clean_line.startswith('<u') and not clean_line.startswith('<l'):
                    processed_lines.append(f'<p>{clean_line}</p>')
            else:
                processed_lines.append('')
    if in_list:
        processed_lines.append('</ul>')
    return '\n'.join(processed_lines)

html_body_content = convert_markdown_to_html(raw_markdown)

# Inject partner link references
for placeholder, real_link in AFFILIATE_LINKS.items():
    link_html = f'<a href="{real_link}" target="_blank" style="color: #0066cc; font-weight: bold; text-decoration: underline;">Check out our recommended optimization tool here</a>'
    html_body_content = html_body_content.replace(f"[LINK:{placeholder}]", link_html)

# ==========================================
# 4. MASTER FRAMEWORK ASSEMBLY (MOBILE-FIRST UI)
# ==========================================
# Verified CDN asset fallback parameters guarantee live imagery without timeout drops
hero_img_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&h=630&q=80"
inline_img_url = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&h=450&q=80"

full_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{extracted_title} - GadTech Labs</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.7; max-width: 660px; margin: 0 auto; padding: 24px 16px; color: #2d3748; background-color: #ffffff; -webkit-text-size-adjust: 100%; }} 
        h1 {{ color: #1a202c; font-size: 2.1rem; font-weight: 800; line-height: 1.25; margin: 10px 0 20px 0; letter-spacing: -0.5px; }}
        h2 {{ color: #1a202c; font-size: 1.45rem; font-weight: 700; margin: 1.8em 0 12px 0; border-bottom: 2px solid #edf2f7; padding-bottom: 6px; line-height: 1.3; }}
        h3 {{ color: #2d3748; font-size: 1.2rem; margin: 1.5em 0 8px 0; font-weight: 600; }}
        p {{ margin-bottom: 20px; font-size: 1.05rem; color: #4a5568; word-wrap: break-word; }}
        ul, ol {{ margin: 0 0 24px 0; padding-left: 24px; }}
        li {{ margin-bottom: 8px; font-size: 1.05rem; color: #4a5568; line-height: 1.6; }}
        a {{ color: #0066cc; text-decoration: none; word-break: break-all; }}
        a:hover {{ text-decoration: underline; }}
        .img-container {{ width: 100%; margin: 20px 0 25px 0; background: #f7fafc; border-radius: 8px; overflow: hidden; }}
        img.hero, img.inline {{ width: 100%; height: auto; display: block; object-fit: cover; max-height: 360px; }}
        .caption {{ text-align: center; font-size: 0.85rem; color: #718096; font-style: italic; padding: 8px 12px; background: #f7fafc; border-top: 1px solid #edf2f7; }}
        @media (max-width: 480px) {{
            body {{ padding: 16px 12px; }}
            h1 {{ font-size: 1.65rem; margin-bottom: 16px; }}
            h2 {{ font-size: 1.3rem; }}
            p, li {{ font-size: 1rem; line-height: 1.6; }}
            ul, ol {{ padding-left: 20px; }}
        }}
    </style>
</head>
<body>
    <main>
        <h1>{extracted_title}</h1>
        <div class="img-container">
            <img src="{hero_img_url}" class="hero" alt="Technical Workspace Optimization Processing">
        </div>
        
        {html_body_content}
        
        <div class="img-container">
            <img src="{inline_img_url}" class="inline" alt="Diagnostic Console Tracking Layout">
            <p class="caption">System diagnostics data verification architecture log telemetry metrics panel.</p>
        </div>
    </main>
</body>
</html>
"""

try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_page_html)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(extracted_title + "\n")
    print(f"SUCCESS: Generated responsive article layout: {filename}")
except Exception as e:
    print(f"CRITICAL ERROR: Failed saving article: {e}")
    sys.exit(1)

# ==========================================
# 5. HOMEPAGE GENERATOR
# ==========================================
print("Compiling mobile-responsive homepage index...")

with open(HISTORY_FILE, "r", encoding="utf-8") as f:
    all_posts = [line.strip() for line in f.readlines() if line.strip()]

all_posts = [post for post in all_posts if post != "Baseline History Init"]

list_items_html = ""
for post_title in reversed(all_posts):
    post_url = generate_slug(post_title)
    list_items_html += f"""
    <li style="margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid #edf2f7; list-style: none;">
        <h2 style="margin: 0 0 8px 0; font-size: 1.35rem; line-height: 1.3; border: none; padding: 0;">
            <a href="{post_url}" style="color: #1a202c; text-decoration: none; font-weight: 700;">{post_title}</a>
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
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 660px; margin: 0 auto; padding: 40px 16px; color: #2d3748; }}
        header {{ margin-bottom: 35px; border-bottom: 3px solid #1a202c; padding-bottom: 16px; }}
        h1 {{ color: #1a202c; margin: 0; font-size: 1.9rem; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2; }}
        p.subtitle {{ color: #718096; margin: 6px 0 0 0; font-size: 1.05rem; line-height: 1.4; }}
        ul {{ padding: 0; margin: 0; }}
        a:hover {{ text-decoration: underline !important; }}
        @media (max-width: 480px) {{
            body {{ padding: 24px 12px; }}
            h1 {{ font-size: 1.55rem; }}
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
            {list_items_html if list_items_html else '<li style="list-style:none; color:#718096;">No articles published yet. Check back soon!</li>'}
        </ul>
    </main>
</body>
</html>
"""

try:
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_html_content)
    print("SUCCESS: Homepage index updated successfully!")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to write homepage: {e}")
    sys.exit(1)
