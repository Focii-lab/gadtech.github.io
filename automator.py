import os
import glob

print("🧹 Starting Bulk Deletion & System Reset...")

# 1. Clear out all blog posts, but save index.html and about.html
for file_path in glob.glob("*.html"):
    if file_path not in ["index.html", "about.html"]:
        try:
            os.remove(file_path)
            print(f"🗑️ Deleted blog post file: {file_path}")
        except Exception as e:
            print(f"❌ Could not delete {file_path}: {e}")

# 2. Reset past_topics.txt back to fresh baseline
try:
    with open("past_topics.txt", "w", encoding="utf-8") as f:
        f.write("Baseline Initialization")
    print("📝 Reset past_topics.txt history file.")
except Exception as e:
    print(f"❌ Could not reset history file: {e}")

# 3. Clear the blog list from index.html, leaving just your clean template
clean_index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GadTech Optimization Labs</title>
    <style>
        :root { --bg: #f4f7f6; --card: #ffffff; --text: #334155; --head: #0f172a; --accent: #2563eb; --border: #e2e8f0; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; background: var(--bg); padding: 60px 20px; color: var(--text); }
        .hub-container { max-width: 720px; margin: 0 auto; background: var(--card); padding: 48px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid var(--border); }
        header { margin-bottom: 40px; border-bottom: 3px solid var(--head); padding-bottom: 24px; }
        h1 { color: var(--head); margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.2; }
        p.subtitle { color: #64748b; margin: 12px 0 0 0; font-size: 1.15rem; line-height: 1.5; }
        .main-nav { margin-top: 16px; }
        .main-nav a { color: var(--accent); font-weight: 600; text-decoration: none; font-size: 1.05rem; }
        .main-nav a:hover { text-decoration: underline; }
        ul { list-style: none; }
        @media (max-width: 768px) {
            body { padding: 16px 12px; }
            .hub-container { padding: 24px 20px; }
            h1 { font-size: 1.75rem; }
        }
    </style>
</head>
<body>
    <div class="hub-container">
        <header>
            <h1>GadTech Optimization Labs</h1>
            <p class="subtitle">Autonomous diagnostic solutions & troubleshooting playbooks for digital creators.</p>
            <nav class="main-nav">
                <a href="about.html">About Me &rarr;</a>
            </nav>
        </header>
        <main>
            <ul>
            </ul>
        </main>
    </div>
</body>
</html>"""

try:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(clean_index_content)
    print("✨ Reset index.html homepage template.")
except Exception as e:
    print(f"❌ Could not reset homepage: {e}")

print("✅ System successfully wiped clean.")
