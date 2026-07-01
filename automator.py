import os
import re
import sys
import urllib.parse
from google import genai
from google.genai import types

# ==========================================
# 0. SAFETY CONTROLS & INITIALIZATION
# ==========================================
# Set to True to test GitHub Actions and CSS without burning Gemini API quota!
# Set to False to run the real AI API calls.
TEST_MODE = False  

api_key = os.environ.get("GEMINI_API_KEY")
if not TEST_MODE and not api_key:
    print("CRITICAL ERROR: 'GEMINI_API_KEY' secret is missing.")
    sys.exit(1)

client = genai.Client(api_key=api_key) if not TEST_MODE else None

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
# PHASE 1: THE STRATEGIST (Call 1)
# ==========================================
print("LAUNCHING PHASE 1: The Strategist (Intent & Outline)...")

call_1_prompt = f"""
Role: Principal SEO Strategist for a B2B SaaS Optimization Blog.
Task: Define the architecture for a highly technical troubleshooting guide aimed at digital creators.
Past Topics to AVOID: {past_topics}

Create a strict outline for a new article. The topic must be at the intersection of complex software (e.g., Premiere, Canva, Figma, Stripe, Zapier) and an exact error code or automation bottleneck.

Output EXACTLY in this format, with no extra text:
TITLE: [Article Title]
INTENT: [1-sentence Search Intent]
ENTITIES: [3 highly specific software versions, hardware specs, or technical terms to include]
OUTLINE:
- [Heading 1]
- [Heading 2]
- [Heading 3]
"""

if not TEST_MODE:
    try:
        response_1 = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=call_1_prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        strategic_blueprint = response_1.text
    except Exception as e:
        print(f"CRITICAL ERROR in Phase 1: {e}")
        sys.exit(1)
else:
    strategic_blueprint = "TITLE: Fixing Premiere Pro Error Code 160\nINTENT: Help video editors clear cache bugs.\nENTITIES: Adobe Premiere 2024, Media Cache, Scratch Disk.\nOUTLINE:\n- The Root Cause\n- Step 1: Clearing Database\n- Step 2: Rerouting Scratch"

print("Blueprint Generated:\n", strategic_blueprint)

# Extract Title
title_match = re.search(r'TITLE:\s*(.*)', strategic_blueprint)
extracted_title = title_match.group(1).strip() if title_match else "Advanced Systems Optimization Guide"
filename = generate_slug(extracted_title)

# ==========================================
# PHASE 2: THE WRITER (Call 2)
# ==========================================
print("LAUNCHING PHASE 2: The Writer (Execution)...")

call_2_prompt = f"""
Role: Elite B2B Technical Support Engineer.
Task: Write a 1,000-word troubleshooting guide using the following approved blueprint.

Blueprint:
{strategic_blueprint}

Formatting Rules (Strict Markdown):
1. Do NOT write a main `# Title` at the top (it is handled by the system).
2. The very first line MUST be a blockquote starting with "> **AEO Snapshot:**" followed by a 3-sentence definitive fix.
3. Use `## ` and `### ` for the outline headers.
4. DO NOT use horizontal rules (`---`). Use hyphens (`- `) for lists, NEVER asterisks (`* `).
5. At 2 logical points where a visual is needed, insert: `[AI_IMAGE: visual description of a minimal UI or tech interface]`
6. Naturally weave `[LINK:AI_TOOL]` into a solution step.
"""

if not TEST_MODE:
    try:
        response_2 = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=call_2_prompt,
            config=types.GenerateContentConfig(temperature=0.4)
        )
        raw_markdown = response_2.text
    except Exception as e:
        print(f"CRITICAL ERROR in Phase 2: {e}")
        sys.exit(1)
else:
    raw_markdown = "> **AEO Snapshot:** This is a test snapshot. Premiere Pro Error 160 is caused by a corrupted media cache database. To fix it, hold shift while launching to wipe the cache, then reassign your scratch disk to an NVMe drive.\n\n## The Root Cause\nThis happens often.\n\n[AI_IMAGE: Sleek 3D render of a broken hard drive]\n\n## The Fix\n- Click here.\n- Check out [LINK:AI_TOOL] to automate this."

# Parser
def convert_markdown_to_html(text):
    text = re.sub(r'(^```html\s*|^```markdown\s*|^```\s*)|(\s*```$)', '', text.strip(), flags=re.IGNORECASE)
    text = re.sub(r'^#\s+.*?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^>\s*\*\*AEO Snapshot:\*\*(.*?)$', r'<div class="aeo-snippet"><strong>Quick Fix Summary:</strong>\1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    
    processed_lines = []
    in_list = False
    for line in text.split('\n'):
        clean_line = line.strip()
        if clean_line.startswith('- '):
            if not in_list:
                processed_lines.append('<ul class="content-list">')
                in_list = True
            processed_lines.append(f'<li>{clean_line[2:]}</li>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            if clean_line:
                if not any(clean_line.startswith(tag) for tag in ['<h', '<u', '<l', '<div class="aeo', '[AI_IMAGE:']):
                    processed_lines.append(f'<p>{clean_line}</p>')
                else:
                    processed_lines.append(clean_line)
    if in_list:
        processed_lines.append('</ul>')
    return '\n'.join(processed_lines)

html_body_content = convert_markdown_to_html(raw_markdown)

# ==========================================
# PHASE 3: THE ART DIRECTOR (Call 3)
# ==========================================
print("LAUNCHING PHASE 3: The Art Director (Metadata & Images)...")

call_3_prompt = f"""
Role: SEO and Art Director.
Task: Read this article title: "{extracted_title}"
Provide exactly two lines of output:
META_DESC: [Write a 150-character highly clickable SEO meta description]
HERO_PROMPT: [Write a highly detailed, 3D minimalist dark-mode tech aesthetic image prompt for Pollinations.ai]
"""

if not TEST_MODE:
    try:
        response_3 = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=call_3_prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        metadata_raw = response_3.text
    except Exception as e:
        print(f"CRITICAL ERROR in Phase 3: {e}")
        sys.exit(1)
else:
    metadata_raw = "META_DESC: Learn how to fix Premiere Pro Error 160 fast.\nHERO_PROMPT: Minimalist 3D render of a Premiere Pro timeline timeline, blue neon accents, dark mode."

meta_match = re.search(r'META_DESC:\s*(.*)', metadata_raw)
hero_match = re.search(r'HERO_PROMPT:\s*(.*)', metadata_raw)

meta_desc = meta_match.group(1).strip() if meta_match else f"Troubleshooting guide for {extracted_title}."
hero_ai_prompt = hero_match.group(1).strip() if hero_match else f"3D tech minimal render of {extracted_title}"

# Build Hero Image URL
encoded_hero_prompt = urllib.parse.quote(hero_ai_prompt)
hero_img_url = f"https://image.pollinations.ai/prompt/{encoded_hero_prompt}?width=1200&height=630&nologo=true"

# Parse Inline Images
def parse_and_inject_ai_images(content):
    image_pattern = r'\[AI_IMAGE:\s*(.*?)\]'
    def process_match(match):
        prompt = match.group(1).strip()
        clean_style = f"{prompt}, minimal UI dashboard, dark mode, 3d render, 8k"
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_style)}?width=1000&height=560&nologo=true"
        return f'<div class="img-container"><img src="{url}" class="inline-img" loading="lazy"><div class="caption">{prompt}</div></div>'
    return re.sub(image_pattern, process_match, content)

html_body_content = parse_and_inject_ai_images(html_body_content)

# Inject Affiliates
for placeholder, real_link in AFFILIATE_LINKS.items():
    link_html = f'<a href="{real_link}" target="_blank" class="affiliate-button">Access the Automated Diagnostics Tool Here &rarr;</a>'
    html_body_content = html_body_content.replace(f"[LINK:{placeholder}]", link_html)

# ==========================================
# PHASE 4: DOM ASSEMBLY & DEPLOYMENT
# ==========================================
print("LAUNCHING PHASE 4: DOM Assembly...")

full_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{extracted_title} - GadTech Labs</title>
    <meta name="description" content="{meta_desc}">
    <meta property="og:title" content="{extracted_title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:image" content="{hero_img_url}">
    <style>
        :root {{ --bg: #f4f7f6; --card: #ffffff; --text: #334155; --head: #0f172a; --accent: #2563eb; --border: #e2e8f0; --aeo: #f8fafc; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.8; background: var(--bg); color: var(--text); padding: 40px 20px; }}
        .container {{ max-width: 720px; margin: 0 auto; background: var(--card); border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; border: 1px solid var(--border); }}
        .hero-banner {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; background: var(--border); border-bottom: 1px solid var(--border); }}
        .content-wrapper {{ padding: 48px; }}
        h1 {{ color: var(--head); font-size: 2.2rem; font-weight: 800; line-height: 1.25; margin-bottom: 24px; letter-spacing: -0.02em; }}
        h2 {{ color: var(--head); font-size: 1.5rem; font-weight: 700; margin: 2em 0 16px 0; border-bottom: 2px solid var(--border); padding-bottom: 8px; }}
        h3 {{ color: var(--head); font-size: 1.25rem; font-weight: 600; margin: 1.5em 0 12px 0; }}
        
        .aeo-snippet {{ background: var(--aeo); border: 1px solid #cbd5e1; border-left: 6px solid var(--accent); padding: 24px; border-radius: 8px; margin-bottom: 32px; font-size: 1.1rem; }}
        .aeo-snippet strong {{ display: block; color: var(--head); margin-bottom: 8px; font-size: 1.2rem; }}
        
        p {{ margin-bottom: 24px; font-size: 1.1rem; }}
        p strong {{ color: var(--head); font-weight: 600; }}
        .content-list {{ margin: 0 0 24px 0; padding-left: 24px; }}
        .content-list li {{ margin-bottom: 10px; font-size: 1.1rem; }}
        
        a {{ color: var(--accent); text-decoration: none; font-weight: 500; transition: color 0.2s; }}
        a:hover {{ text-decoration: underline; color: #1d4ed8; }}
        .affiliate-button {{ display: inline-block; margin: 16px 0; padding: 14px 24px; background: #eff6ff; color: #1d4ed8; border-radius: 8px; font-weight: 600; text-align: center; border: 1px solid #bfdbfe; width: 100%; }}
        .affiliate-button:hover {{ background: #dbeafe; text-decoration: none; }}
        
        .img-container {{ width: 100%; margin: 32px 0; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); background: #f1f5f9; }}
        img.inline-img {{ width: 100%; height: auto; display: block; object-fit: cover; max-height: 380px; }}
        .caption {{ font-size: 0.85rem; color: #64748b; font-style: italic; padding: 12px 16px; text-align: center; border-top: 1px solid var(--border); }}
        
        @media (max-width: 768px) {{
            body {{ padding: 16px 12px; }}
            .content-wrapper {{ padding: 24px 20px; }}
            h1 {{ font-size: 1.75rem; }}
            h2 {{ font-size: 1.35rem; }}
            p, .content-list li {{ font-size: 1.05rem; }}
        }}
    </style>
</head>
<body>
    <article class="container">
        <img src="{hero_img_url}" class="hero-banner" alt="{extracted_title}" loading="lazy">
        <div class="content-wrapper">
            <h1>{extracted_title}</h1>
            {html_body_content}
        </div>
    </article>
</body>
</html>
"""

try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_page_html)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(extracted_title + "\n")
    print(f"SUCCESS: System UI rebuilt successfully: {filename}")
except Exception as e:
    print(f"CRITICAL ERROR: Failed saving article: {e}")
    sys.exit(1)

# ==========================================
# 5. HOMEPAGE GENERATOR
# ==========================================
print("Compiling responsive homepage index...")

with open(HISTORY_FILE, "r", encoding="utf-8") as f:
    all_posts = [line.strip() for line in f.readlines() if line.strip()]

all_posts = [post for post in all_posts if post != "Baseline History Init"]

list_items_html = ""
for post_title in reversed(all_posts):
    post_url = generate_slug(post_title)
    list_items_html += f"""
    <li class="index-item">
        <h2><a href="{post_url}">{post_title}</a></h2>
        <a href="{post_url}" class="read-more">Read Troubleshooting Guide &rarr;</a>
    </li>
    """

index_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GadTech Optimization Labs</title>
    <style>
        :root {{ --bg: #f4f7f6; --card: #ffffff; --text: #334155; --head: #0f172a; --accent: #2563eb; --border: #e2e8f0; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; background: var(--bg); padding: 60px 20px; color: var(--text); }}
        .hub-container {{ max-width: 720px; margin: 0 auto; background: var(--card); padding: 48px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid var(--border); }}
        header {{ margin-bottom: 40px; border-bottom: 3px solid var(--head); padding-bottom: 24px; }}
        h1 {{ color: var(--head); margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.2; }}
        p.subtitle {{ color: #64748b; margin: 12px 0 0 0; font-size: 1.15rem; line-height: 1.5; }}
        ul {{ list-style: none; }}
        .index-item {{ margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }}
        .index-item:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
        .index-item h2 {{ margin: 0 0 12px 0; font-size: 1.4rem; line-height: 1.3; }}
        .index-item h2 a {{ color: var(--head); text-decoration: none; font-weight: 700; transition: color 0.2s; }}
        .index-item h2 a:hover {{ color: var(--accent); }}
        .read-more {{ color: var(--accent); font-size: 1rem; font-weight: 600; text-decoration: none; }}
        .read-more:hover {{ text-decoration: underline; }}
        @media (max-width: 768px) {{
            body {{ padding: 16px 12px; }}
            .hub-container {{ padding: 24px 20px; }}
            h1 {{ font-size: 1.75rem; }}
            .index-item h2 {{ font-size: 1.25rem; }}
        }}
    </style>
</head>
<body>
    <div class="hub-container">
        <header>
            <h1>GadTech Optimization Labs</h1>
            <p class="subtitle">Autonomous diagnostic solutions & troubleshooting playbooks for digital creators.</p>
        </header>
        <main>
            <ul>
                {list_items_html if list_items_html else '<li style="color:#64748b;">No articles published yet. Check back soon!</li>'}
            </ul>
        </main>
    </div>
</body>
</html>
"""

try:
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_html_content)
    print("SUCCESS: Homepage updated successfully!")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to write homepage: {e}")
    sys.exit(1)
