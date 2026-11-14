#!/usr/bin/env python3
"""
Converts all markdown files in submissions/ directories into high-quality PDFs
using Markdown + MathJax 3 + Headless Chromium for vector formula rendering.
"""
import os
import subprocess
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBMISSIONS = os.path.join(ROOT, "submissions")

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<script>
window.MathJax = {{
  tex: {{
    inlineMath: [["$", "$"], ["\\\\(", "\\\\)"]],
    displayMath: [["$$", "$$"], ["\\\\[", "\\\\]"]],
    processEscapes: true
  }},
  options: {{
    renderActions: {{
      addMenu: []
    }}
  }}
}};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
@page {{
  size: A4;
  margin: 18mm 16mm 18mm 16mm;
}}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #1f2328;
  max-width: 900px;
  margin: 0 auto;
}}
h1 {{
  font-size: 19pt;
  font-weight: 700;
  border-bottom: 2px solid #0969da;
  padding-bottom: 0.3em;
  margin-top: 0;
  color: #0969da;
}}
h2 {{
  font-size: 14pt;
  font-weight: 600;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 0.25em;
  margin-top: 1.4em;
  color: #1f2328;
}}
h3 {{
  font-size: 12pt;
  font-weight: 600;
  margin-top: 1.1em;
  color: #1f2328;
}}
h4 {{
  font-size: 10.5pt;
  font-weight: 600;
  margin-top: 0.9em;
}}
code {{
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  font-size: 88%;
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 4px;
}}
pre {{
  background-color: #f6f8fa;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
  font-size: 8.5pt;
  line-height: 1.45;
}}
pre code {{
  background-color: transparent;
  padding: 0;
}}
table {{
  border-collapse: collapse;
  width: 100%;
  margin: 14px 0;
  font-size: 9.5pt;
}}
th, td {{
  border: 1px solid #d0d7de;
  padding: 7px 11px;
  text-align: left;
}}
th {{
  background-color: #f6f8fa;
  font-weight: 600;
  color: #24292f;
}}
tr:nth-child(2n) {{
  background-color: #fcfcfc;
}}
blockquote {{
  margin: 12px 0;
  padding: 6px 14px;
  color: #57606a;
  background-color: #f6f8fa;
  border-left: 0.25em solid #0969da;
  border-radius: 0 4px 4px 0;
}}
hr {{
  border: 0;
  height: 1px;
  background-color: #d0d7de;
  margin: 20px 0;
}}
ul, ol {{
  padding-left: 24px;
}}
li {{
  margin: 4px 0;
}}
img {{
  max-width: 100%;
  height: auto;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  margin: 10px 0;
}}
</style>
</head>
<body>
{body}
</body>
</html>"""

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert markdown to html with extensions
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "nl2br"])
    title = os.path.basename(md_path).replace(".md", "")
    full_html = HTML_TEMPLATE.format(title=title, body=body)

    tmp_html = md_path.replace(".md", "_tmp.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    cmd = [
        "chromium",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=6000",
        f"--print-to-pdf={pdf_path}",
        tmp_html
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(tmp_html):
        os.remove(tmp_html)

    if res.returncode != 0 or not os.path.exists(pdf_path):
        raise RuntimeError(f"Failed to convert {md_path} to {pdf_path}: {res.stderr}")

    size_kb = os.path.getsize(pdf_path) // 1024
    print(f"Generated {os.path.basename(pdf_path)} ({size_kb} KB)")

def main():
    target_docs = [
        "userguide.md",
        "performance_report.md",
        "technical_report.md",
        "ai_usage.md",
        "team_info.md",
        "DOCUMENTATION_AND_ANALYSIS.md",
        "README.md"
    ]

    for sub in ["QC-C1-01", "QC-C2-03", "QC-C3-03"]:
        sub_dir = os.path.join(SUBMISSIONS, sub)
        print(f"\n=== Converting Markdown to PDF for {sub} ===")
        for doc in target_docs:
            md_path = os.path.join(sub_dir, doc)
            if os.path.exists(md_path):
                pdf_path = md_path.replace(".md", ".pdf")
                convert_md_to_pdf(md_path, pdf_path)

if __name__ == "__main__":
    main()
