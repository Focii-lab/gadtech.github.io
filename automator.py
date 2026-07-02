import os
import re
import sys
import urllib.parse
from google import genai
from google.genai import types

# ==========================================
# 0. CONFIGURATION
# ==========================================
TEST_MODE = False
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if not TEST_MODE else None
HISTORY_FILE = "past_topics.txt"
INDEX_FILE = "index.html"

def get_recent_history():
    if not os.path.exists(HISTORY_FILE): return "Baseline Initialization"
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines[-1] if lines else "Baseline Initialization"

def extract_field(field, text):
    match = re.search(f"{field}:\s*(.*)", text)
    return match.group(1).strip() if match else "N/A"

def run_engine():
    try:
        print("PHASE 1: Architecting content waterfall...")
        recent_topic = get_recent_history()
        
        call_1_prompt = f"""
        Role: Lead B2B Technical Editor.
        Task: Create a Pillar-level technical guide.
        Waterfall Foundation: Reference and link to this foundation topic: "{recent_topic}"
        Requirements:
        1. SEARCH_INTENT: Define as Navigational, Commercial, or Transactional.
        2. CTA_STAGE: Define as Awareness, Consideration, or Decision.
        3. PROOF_POINT: Identify one specific metric (e.g., 'reduces latency by 30%').
        4. LINK_STRATEGY: Define how to link to "{recent_topic}".
        5. OUTLINE: Create a 4-part structure that naturally builds upon "{recent_topic}".
        Output ONLY in this format:
        TITLE: [Title]
        SEARCH_INTENT: [Intent]
        CTA_TYPE: [Stage]
        PROOF_POINT: [Metric]
        LINK_STRATEGY: [Strategy]
        OUTLINE: - [Hook] - [Deep Dive] - [Evidence] - [Decision/CTA]
        """
        
        resp1 = client.models.generate_content(model="gemini-2.0-flash", contents=call_1_prompt)
        blueprint = resp1.text
        
        # Extraction
        title = extract_field("TITLE", blueprint)
        link_strat = extract_field("LINK_STRATEGY", blueprint)
        proof = extract_field("PROOF_POINT", blueprint)
        cta = extract_field("CTA_TYPE", blueprint)

        print("PHASE 2: Writing authority content...")
        call_2_prompt = f"""
        Role: Experienced B2B Technical Consultant.
        Task: Write a 1,000-word authority guide. 
        Tone: Human, first-person, opinionated, professional.
        Content Rules:
        1. Introduction: Start with a 2-sentence personal anecdote about the frustration of encountering this problem.
        2. Technical Body: Expert-level guide using "I/We". 
        3. Conclusion: End with a "Human Verdict"—a brief, opinionated summary.
        4. Foundation: Naturally link to: "{recent_topic}" using: {link_strat}.
        5. Visuals: Use [AI_IMAGE: prompt] at 2 logical spots.
        Title: {title}
        Outline: {blueprint}
        """
        resp2 = client.models.generate_content(model="gemini-2.0-flash", contents=call_2_prompt)
        
        # Image Parsing (Elite 1% Constraints)
        def process_match(match):
            prompt = match.group(1).strip()
            style = f"{prompt}, professional technical schematic, vector illustration, white background, #2563eb blue and #1e293b slate color scheme"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(style)}?width=1000&height=560&nologo=true"
            return f'<div class="img-container"><img src="{url}" alt="{prompt}" loading="lazy"><div class="caption">{prompt}</div></div>'
        
        html_content = re.sub(r'\[AI_IMAGE:\s*(.*?)\]', process_match, resp2.text)
        
        # Save History (Simplified for backup representation)
        with open(HISTORY_FILE, "a") as f: f.write(f"\n{title}")
        print("System Success: Content deployed.")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_engine()
