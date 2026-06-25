import os
import re
import google.generativeai as genai

# 1. Initialize Gemini using the hidden secret key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use the default free workhorse model for text composition
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Your Static Affiliate Links (Update these with your real ones later)
AFFILIATE_LINKS = {
    "AI_TOOL": "https://www.example-affiliate.com/tracking-id-1",
    "BOOK_REC": "https://www.example-affiliate.com/tracking-id-2"
}

# 3. Secure Narrow-Intent Prompting
prompt = """
Act as a world-class technology blogger and SEO specialist. 
Identify a highly specific, low-competition, long-tail problem-solving keyword in the 'AI tools for freelancers' or 'productivity software hacks' niche.

Write a beautifully structured, comprehensive blog post about it in clean, standard HTML.
Follow these exact formatting rules:
- Do NOT wrap the code in ```html blocks. Output raw text starting directly with the HTML tags.
- Use a single <h1> for the main title at the very top.
- Immediately follow the <h1> with a 50-word bolded paragraph (<p><b>...</b></p>) that directly answers the main user query for AI snippet optimization.
- Use clean <h2> and <h3> tags for sections. No markdown styling (* or #) inside the HTML.
- Include at least one step-by-step list (<ol><li>) or a structured comparison list.
- Naturally insert these exact text anchors where appropriate: [LINK:AI_TOOL] or [LINK:BOOK_REC].

Make the content deeply actionable, eliminating generic fluff words. Include an introductory header section using clean CSS inline styling for a premium look.
"""

print("Requesting content from Gemini...")
response = model.generate_content(prompt)
raw_html = response.text

# 4. Clean up any accidental markdown wrapper artifacts from the AI response
clean_html = re.sub(r'^
```html\s*|\s*```$', '', raw_html.strip())

# 5. Automatically find and replace placeholders with your functional affiliate links
for placeholder, real_link in AFFILIATE_LINKS.items():
    link_html = f'<a href="{real_link}" target="_blank" style="color: #0066cc; font-weight: bold;">Check out our recommended resource here</a>'
    clean_html = clean_html.replace(f"[LINK:{placeholder}]", link_html)

# 6. Extract the safe title string to generate a clean filename
title_match = re.search(r'<h1>(.*?)</h1>', clean_html)
if title_match:
    slug = title_match.group(1).lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    filename = re.sub(r'[\s-]+', '-', slug).strip('-') + ".html"
else:
    filename = "latest-update.html"

# 7. Write out the static standalone webpage file
with open(filename, "w", encoding="utf-8") as f:
    f.write(clean_html)

print(f"Success! Generated file saved locally as: {filename}")
