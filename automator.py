import os
import re
import sys
import urllib.parse
from google import genai
from google.genai import types

# ==========================================
# 0. INITIALIZATION
# ==========================================
TEST_MODE = False
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if not TEST_MODE else None
HISTORY_FILE = "past_topics.txt"
INDEX_FILE = "index.html"

# Ensure history exists
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f: f.write("Baseline Initialization")

def get_recent_history():
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines[-1] if lines else "No previous topics."

# ==========================================
# PHASE 1: THE STRATEGIST (Waterfall & Intent)
# ==========================================
recent_topic = get_recent_history()

call_1_prompt = f"""
Role: Lead B2B Technical Editor.
Task: Create a Pillar-level technical guide.
Waterfall Foundation: Reference and link to this foundation topic: "{recent_topic}"

Requirements:
1. SEARCH_INTENT: Define as Navigational, Commercial, or Transactional.
2. CTA_STAGE: Define as Awareness, Consideration, or Decision (tailor CTA to this).
3. PROOF_POINT: Identify one specific metric/impact the fix provides (e.g., 'reduces latency by 30%').
4. OUTLINE: Create a 4-part structure that naturally builds upon "{recent_topic}".

Output ONLY in this format:
TITLE: [Article Title]
SEARCH_INTENT: [Intent]
CTA_TYPE: [CTA Stage]
PROOF_POINT: [Impact Metric]
LINK_STRATEGY: [How to link to {recent_topic}]
OUTLINE:
- [Hook/Problem]
- [Deep Dive/Technical Fix]
- [Evidence/Proof]
- [Decision/CTA Section]
"""

# ... [API CALL logic here] ...

# ==========================================
# PHASE 2: THE WRITER (E-E-A-T Authority)
# ==========================================
call_2_prompt = f"""
Role: First-Person Technical Expert.
Task: Write a 1,000-word authority guide. 
Tone: You are an expert who has fixed this in production. Use "I/We".

Content Rules:
1. Hook: Start with a "Problem-First" reflection that mirrors the reader's pain.
2. Foundation: Naturally link to: "{recent_topic}" using: {link_strategy}.
3. Proof: Cite the following impact: {proof_point}.
4. CTA: Insert this decision-stage CTA: {cta_type} (offer a specific diagnostic tool or demo).
5. Visuals: Use [AI_IMAGE: prompt] at 2 logical spots.
"""

# ... [API CALL logic here] ...

# ==========================================
# PHASE 3: THE ART DIRECTOR (Elite Visuals)
# ==========================================
def parse_and_inject_ai_images(content):
    image_pattern = r'\[AI_IMAGE:\s*(.*?)\]'
    def process_match(match):
        prompt = match.group(1).strip()
        # Elite 1% Schematic Constraints
        clean_style = (f"{prompt}, professional technical schematic, labeled components, "
                       f"large clear text-callouts, vector illustration, white background, "
                       f"color palette #2563eb and #1e293b, minimalist UI documentation style, "
                       f"high contrast, 8k, extremely professional and clean")
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_style)}?width=1000&height=560&nologo=true"
        return f'<div class="img-container"><img src="{url}" class="inline-img" loading="lazy"><div class="caption">{prompt}</div></div>'
    return re.sub(image_pattern, process_match, content)

# ... [DOM ASSEMBLY & DEPLOYMENT remain as previously established] ...
