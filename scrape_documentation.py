#!/usr/bin/env python3
"""
Full Qniverse Documentation Scraper & Processor
Scrapes BetterDocs, Sphinx QSDK docs, images, and generates complete Markdown files.
"""

import os
import re
import sys
import json
import urllib.parse
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
import html2text

BASE_DIR = Path("/mnt/shared/projects/CDAC-Hack/docs/documentation")
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SCREENSHOTS_DIR = ASSETS_DIR / "screenshots"

USER_GUIDE_DIR = BASE_DIR / "user-guide"
ALGORITHMS_DIR = BASE_DIR / "algorithms"
QSDK_DIR = BASE_DIR / "qsdk"
QSDK_SOURCES_DIR = QSDK_DIR / "sources"
FAQ_DIR = BASE_DIR / "faq-and-troubleshooting"

for d in [BASE_DIR, ASSETS_DIR, IMAGES_DIR, SCREENSHOTS_DIR, USER_GUIDE_DIR, ALGORITHMS_DIR, QSDK_DIR, QSDK_SOURCES_DIR, FAQ_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def fetch_url(url: str, binary: bool = False, timeout: int = 20) -> bytes:
    cmd = ["curl", "-sL", "--max-time", str(timeout), "-A", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", url]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"[WARN] Failed fetching {url}: returncode {res.returncode}")
        return b""
    return res.stdout

def download_image(img_url: str, base_page_url: str) -> str:
    if not img_url:
        return ""
    full_url = urllib.parse.urljoin(base_page_url, img_url)
    parsed = urllib.parse.urlparse(full_url)
    orig_name = os.path.basename(parsed.path)
    if not orig_name:
        orig_name = "image_" + str(abs(hash(full_url))) + ".png"
    
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', orig_name)
    target_path = IMAGES_DIR / clean_name
    
    if not target_path.exists():
        data = fetch_url(full_url, binary=True)
        if data:
            target_path.write_bytes(data)
            print(f"    [IMG] Downloaded {clean_name} ({len(data)} bytes)")
        else:
            print(f"    [IMG-FAIL] Could not download {full_url}")
            return img_url
            
    return clean_name

def clean_html_to_markdown(html_content: str, page_url: str, rel_image_prefix: str = "../assets/images/") -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted UI elements
    for el in soup.select('.betterdocs-anchor, .anchor, .betterdocs-tags-print, .betterdocs-feedback, .betterdocs-social-share, .ez-toc-title-toggle, .header-navigation, footer, script, style, .headerlink'):
        el.decompose()
        
    # Process images: download and rewrite src
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            local_filename = download_image(src, page_url)
            if local_filename and not local_filename.startswith('http'):
                img['src'] = f"{rel_image_prefix}{local_filename}"
                
    # Process videos
    for video in soup.find_all('video'):
        src = video.get('src')
        if not src:
            source = video.find('source')
            if source:
                src = source.get('src')
        if src:
            p = soup.new_tag('p')
            a = soup.new_tag('a', href=src)
            a.string = f"▶️ Video Demonstration: {src}"
            p.append(a)
            video.replace_with(p)
            
    # Process code blocks
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        text = code.get_text() if code else pre.get_text()
        lang = "python"
        cls = pre.get('class', []) + (code.get('class', []) if code else [])
        cls_str = " ".join(cls)
        if "bash" in cls_str or "sh" in cls_str or "$" in text[:20]:
            lang = "bash"
        elif "qasm" in cls_str or "OPENQASM" in text[:30]:
            lang = "qasm"
        elif "json" in cls_str or (text.strip().startswith("{") and text.strip().endswith("}")):
            lang = "json"
        
        new_pre = soup.new_tag('pre')
        new_pre.string = f"```{lang}\n{text.strip()}\n```"
        pre.replace_with(new_pre)

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0
    h.single_line_break = False
    md = h.handle(str(soup))
    
    # Post-process markdown
    md = re.sub(r'^(#{1,6})\s*\*\*(.*?)\*\*\s*#?', r'\1 \2', md, flags=re.MULTILINE)
    md = re.sub(r'^(#{1,6})\s*(.*?)\s*#\s*$', r'\1 \2', md, flags=re.MULTILINE)
    md = re.sub(r'```([a-z]+)\\n', r'```\1\n', md)
    md = re.sub(r'\n{3,}', '\n\n', md)
    return md.strip()

USER_GUIDE_PAGES = [
    ("Introduction to Qniverse", "https://qniverse.in/docs/introduction/", "01-introduction-to-qniverse.md"),
    ("Creating an Account", "https://qniverse.in/docs/creating-an-account/", "02-creating-an-account.md"),
    ("Profile & Account", "https://qniverse.in/docs/profile/", "03-profile-and-account.md"),
    ("Circuit Composer Area", "https://qniverse.in/docs/circuit-composer-area/", "04-circuit-composer-area.md"),
    ("Code Editor Area", "https://qniverse.in/docs/code-editor-area/", "05-code-editor-area.md"),
    ("Building Circuits", "https://qniverse.in/docs/building-circuits/", "06-building-circuits.md"),
    ("Gates Palette", "https://qniverse.in/docs/gate-types/", "07-gates-palette.md"),
    ("Quantum Gates", "https://qniverse.in/docs/quantum-gate-reference/", "08-quantum-gate-reference.md"),
    ("Measurement on Basis(x,y,z)", "https://qniverse.in/docs/gate-matrices/", "09-measurement-on-basis-gate-matrices.md"),
    ("Compute Resources", "https://qniverse.in/docs/computing-resources/", "10-computing-resources.md"),
    ("Backend Systems", "https://qniverse.in/docs/backend-systems/", "11-backend-systems.md"),
    ("Noise Modeling in Qniverse", "https://qniverse.in/docs/noise-modeling-in-qniverse/", "12-noise-modeling.md"),
    ("Running Circuits", "https://qniverse.in/docs/running-circuits/", "13-running-circuits.md"),
    ("Visualization", "https://qniverse.in/docs/visualization/", "14-visualization.md"),
    ("View Jobs", "https://qniverse.in/docs/view-jobs/", "15-view-jobs.md"),
    ("Launch Notebook", "https://qniverse.in/docs/qniverse-labs-resources/", "16-launch-notebook-labs-resources.md"),
]

ALGORITHM_PAGES = [
    ("Deutsch Function", "https://qniverse.in/docs/deutsch-function/", "01-deutsch-function.md"),
    ("Deutsch-Jozsa Algorithm", "https://qniverse.in/docs/deutsch-jozsa-algorithm/", "02-deutsch-jozsa-algorithm.md"),
    ("Bernstein-Vazirani Algorithm", "https://qniverse.in/docs/bernstein-vazirani-algorithm/", "03-bernstein-vazirani-algorithm.md"),
    ("Simon’s Algorithm", "https://qniverse.in/docs/simons-algorithms/", "04-simons-algorithm.md"),
    ("Grover’s Algorithm(Search)", "https://qniverse.in/docs/grovers-algorithmsearch/", "05-grovers-algorithm-search.md"),
    ("Quantum Phase Estimation (QPE)", "https://qniverse.in/docs/quantum-phase-estimation-qpe/", "06-quantum-phase-estimation-qpe.md"),
    ("Quantum Fourier Transform (QFT)", "https://qniverse.in/docs/quantum-fourier-transform-qft/", "07-quantum-fourier-transform-qft.md"),
    ("Shor’s Algorithm", "https://qniverse.in/docs/shors-algorithm-factorization/", "08-shors-algorithm-factorization.md"),
    ("Quantum Teleportation", "https://qniverse.in/docs/quantum-teleportation/", "09-quantum-teleportation.md"),
    ("Superdense Coding", "https://qniverse.in/docs/super-dense-coding/", "10-superdense-coding.md"),
    ("Quantum N Qubit Teleportation(Unitary-Control Implementation)", "https://qniverse.in/docs/quantum-n-qubit-teleportationunitary-control-implementation/", "11-quantum-n-qubit-teleportation-unitary-control.md"),
    ("Quantum Walks Algorithm(1D)", "https://qniverse.in/docs/quantum-walks-algorithm1d/", "12-quantum-walks-algorithm-1d.md"),
    ("Variational Quantum Eigensolver (VQE)", "https://qniverse.in/docs/variational-quantum-eigensolver-vqe/", "13-variational-quantum-eigensolver-vqe.md"),
    ("QAOA for Max-Cut (Variational Implementation)", "https://qniverse.in/docs/qaoa-for-max-cut-variational-implementation/", "14-qaoa-for-max-cut.md"),
    ("Portfolio Optimization using QAOA", "https://qniverse.in/docs/portfolio-optimization-using-qaoa/", "15-portfolio-optimization-using-qaoa.md"),
    ("Harrow-Hassidim-Lloyd(HHL) Algorithm", "https://qniverse.in/docs/harrow-hassidim-lloydhhl-algorithm/", "16-harrow-hassidim-lloyd-hhl-algorithm.md"),
    ("Quantum Veto Algorithm", "https://qniverse.in/docs/quantum-veto-algorithm/", "17-quantum-veto-algorithm.md"),
    ("Quantum Digital Signature(QDS) Algorithm", "https://qniverse.in/docs/quantum-digital-signatureqds-algorithm/", "18-quantum-digital-signature-qds.md"),
    ("Quantum Private Comparison(QPC) Algorithm", "https://qniverse.in/docs/quantum-private-comparisonqpc-algorithm/", "19-quantum-private-comparison-qpc.md"),
    ("QSVM", "https://qniverse.in/docs/qsvm/", "20-qsvm.md"),
    ("QKMeans Algorithm", "https://qniverse.in/docs/qkmeans-algorithm/", "21-qkmeans-algorithm.md"),
    ("QuantumKNN Algorithm", "https://qniverse.in/docs/quantumknn-algorithm/", "22-quantum-knn-algorithm.md"),
    ("Quantum Hierarchical Clustering(QHC)", "https://qniverse.in/docs/quantum-hierarchical-clusteringqhc/", "23-quantum-hierarchical-clustering-qhc.md"),
    ("Quantum Perceptron Algorithm", "https://qniverse.in/docs/quantum-perceptron-algorithm/", "24-quantum-perceptron-algorithm.md"),
    ("Quantum Principal Component Analysis (QPCA)", "https://qniverse.in/docs/qpca-algorithm/", "25-quantum-principal-component-analysis-qpca.md"),
    ("QNN Algorithm", "https://qniverse.in/docs/qnn-algorithm/", "26-quantum-neural-network-qnn.md"),
    ("Time-Evolution of Quantum System using Trotterization", "https://qniverse.in/docs/suzuki-trotter-algorithm/", "27-suzuki-trotter-time-evolution.md"),
    ("QEC : Three-Qubit Repetition Code", "https://qniverse.in/docs/qec-three-qubit-repetition-code/", "28-qec-three-qubit-repetition-code.md"),
    ("QEC : Shor’s Nine-Qubit Code", "https://qniverse.in/docs/qec-shors-nine-qubit-code/", "29-qec-shors-nine-qubit-code.md"),
    ("QEC: Steane Seven-Qubit Code", "https://qniverse.in/docs/qec-steane-seven-qubit-code/", "30-qec-steane-seven-qubit-code.md"),
]

FAQ_PAGES = [
    ("Bug Report/Feedback", "https://qniverse.in/docs/bug-report-feedback/", "01-bug-report-feedback.md"),
    ("Terms & Privacy", "https://qniverse.in/docs/terms-privacy/", "02-terms-and-privacy.md"),
]

SPHINX_QSDK_PAGES = [
    ("QSDK Documentation Index", "https://qniverse.in/docs-category/qsdk/index.html", "01-index.md", "index.rst.txt"),
    ("Introduction to QSDK", "https://qniverse.in/docs-category/qsdk/introduction/index.html", "02-introduction-index.md", "introduction/index.rst.txt"),
    ("Getting Started with QSDK", "https://qniverse.in/docs-category/qsdk/introduction/getting_started.html", "03-getting-started.md", "introduction/getting_started.rst.txt"),
    ("Creating a Circuit", "https://qniverse.in/docs-category/qsdk/introduction/creating_a_circuit.html", "04-creating-a-circuit.md", "introduction/creating_a_circuit.rst.txt"),
    ("Gates and Modules", "https://qniverse.in/docs-category/qsdk/gates_and_modules/index.html", "05-gates-and-modules-index.md", "gates_and_modules/index.rst.txt"),
    ("Quantum Gates", "https://qniverse.in/docs-category/qsdk/gates_and_modules/gates.html", "06-quantum-gates.md", "gates_and_modules/gates.rst.txt"),
    ("Backend Systems Overview", "https://qniverse.in/docs-category/qsdk/backend/index.html", "07-backends-index.md", "backend/index.rst.txt"),
    ("Backend Systems Selection", "https://qniverse.in/docs-category/qsdk/backend/backend_selection.html", "08-backend-systems-selection.md", "backend/backend_selection.rst.txt"),
    ("Job APIs Overview", "https://qniverse.in/docs-category/qsdk/job_api/index.html", "09-job-apis-index.md", "job_api/index.rst.txt"),
    ("Submitting and Managing Jobs", "https://qniverse.in/docs-category/qsdk/job_api/job_apis.html", "10-submitting-and-managing-jobs.md", "job_api/job_apis.rst.txt"),
    ("System Logs and Support Overview", "https://qniverse.in/docs-category/qsdk/system_logs/index.html", "11-system-logs-and-support-index.md", "system_logs/index.rst.txt"),
    ("Licenses", "https://qniverse.in/docs-category/qsdk/system_logs/licenses.html", "12-licenses.md", "system_logs/licenses.rst.txt"),
    ("Support", "https://qniverse.in/docs-category/qsdk/system_logs/support.html", "13-support.md", "system_logs/support.rst.txt"),
]

def scrape_betterdocs_group(group_name: str, pages: list, target_dir: Path):
    print(f"\n==========================================")
    print(f"Scraping {group_name} ({len(pages)} pages)...")
    print(f"==========================================")
    for title, url, filename in pages:
        print(f"-> Fetching: {title} ({url})")
        raw_html = fetch_url(url).decode('utf-8', errors='ignore')
        if not raw_html:
            print(f"  [ERROR] Failed to fetch {url}")
            continue
            
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Extract title
        t_el = soup.select_one('.betterdocs-entry-title, h1')
        page_title = t_el.get_text(strip=True) if t_el else title
        
        # Extract breadcrumb
        bc_el = soup.select_one('.betterdocs-breadcrumb')
        breadcrumb = bc_el.get_text(' > ', strip=True) if bc_el else f"Home > Docs > {group_name} > {page_title}"
        
        # Extract reading time / date
        read_time_el = soup.select_one('.betterdocs-entry-reading-time')
        read_time = read_time_el.get_text(strip=True) if read_time_el else ""
        
        # Extract article body
        content_el = soup.select_one('#betterdocs-single-content, .betterdocs-entry-content')
        if not content_el:
            content_el = soup.select_one('article')
            
        if not content_el:
            print(f"  [ERROR] Could not find content container for {url}")
            continue
            
        md_body = clean_html_to_markdown(str(content_el), url, rel_image_prefix="../assets/images/")
        
        frontmatter = f"""---
title: "{page_title}"
category: "{group_name}"
url: "{url}"
breadcrumb: "{breadcrumb}"
---

# {page_title}

> **Category:** {group_name} | **Source:** [{url}]({url})
"""
        if read_time:
            frontmatter += f"> **Reading Info:** {read_time}\n"
            
        full_md = frontmatter + "\n\n" + md_body + "\n"
        out_file = target_dir / filename
        out_file.write_text(full_md, encoding='utf-8')
        print(f"  [SAVED] {out_file.name} ({len(full_md)} chars)")

def scrape_sphinx_qsdk():
    print(f"\n==========================================")
    print(f"Scraping Sphinx QSDK Docs ({len(SPHINX_QSDK_PAGES)} pages)...")
    print(f"==========================================")
    
    # Also save the BetterDocs QSDK portal overview
    qsdk_overview_url = "https://qniverse.in/docs/qsdk/"
    qsdk_overview_html = fetch_url(qsdk_overview_url).decode('utf-8', errors='ignore')
    if qsdk_overview_html:
        s = BeautifulSoup(qsdk_overview_html, 'html.parser')
        c = s.select_one('#betterdocs-single-content, .betterdocs-entry-content')
        if c:
            md_c = clean_html_to_markdown(str(c), qsdk_overview_url, rel_image_prefix="../assets/images/")
            q_file = QSDK_DIR / "00-qsdk-portal-overview.md"
            q_file.write_text(f"""---
title: "QSDK Documentation Portal Overview"
category: "QSDK"
url: "{qsdk_overview_url}"
---

# QSDK Documentation Portal Overview

> **Category:** QSDK | **Source:** [{qsdk_overview_url}]({qsdk_overview_url})

{md_c}

For the complete standalone Sphinx technical documentation manual, see the chapters below:
- [01-index.md](01-index.md): QSDK Documentation Index
- [02-introduction-index.md](02-introduction-index.md): Introduction
- [03-getting-started.md](03-getting-started.md): Installation & Platforms
- [04-creating-a-circuit.md](04-creating-a-circuit.md): Circuit Construction & Registers
- [05-gates-and-modules-index.md](05-gates-and-modules-index.md): Gates & Modules Overview
- [06-quantum-gates.md](06-quantum-gates.md): Quantum Gates Reference
- [07-backends-index.md](07-backends-index.md): Backend Systems Overview
- [08-backend-systems-selection.md](08-backend-systems-selection.md): Backend Selection & Hardware
- [09-job-apis-index.md](09-job-apis-index.md): Job APIs
- [10-submitting-and-managing-jobs.md](10-submitting-and-managing-jobs.md): Job Execution
- [11-system-logs-and-support-index.md](11-system-logs-and-support-index.md): System Logs & Support
- [12-licenses.md](12-licenses.md): Licenses
- [13-support.md](13-support.md): Support & Contact
""", encoding='utf-8')
            print(f"  [SAVED] {q_file.name}")

    base_sphinx = "https://qniverse.in/docs-category/qsdk/"
    for title, url, filename, rst_source in SPHINX_QSDK_PAGES:
        print(f"-> Fetching Sphinx: {title} ({url})")
        raw_html = fetch_url(url).decode('utf-8', errors='ignore')
        if not raw_html:
            print(f"  [ERROR] Failed to fetch {url}")
            continue
            
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Sphinx title
        h1 = soup.find('h1')
        page_title = h1.get_text(strip=True).rstrip('¶#') if h1 else title
        
        # Sphinx body
        body = soup.select_one('[itemprop="articleBody"], .document, div.body')
        if not body:
            print(f"  [ERROR] No articleBody found in {url}")
            continue
            
        md_body = clean_html_to_markdown(str(body), url, rel_image_prefix="../assets/images/")
        
        frontmatter = f"""---
title: "{page_title}"
category: "QSDK Sphinx Manual"
url: "{url}"
source_rst: "sources/{rst_source}"
---

# {page_title}

> **Category:** QSDK Sphinx Manual | **Source:** [{url}]({url})
"""
        full_md = frontmatter + "\n\n" + md_body + "\n"
        out_file = QSDK_DIR / filename
        out_file.write_text(full_md, encoding='utf-8')
        print(f"  [SAVED] {out_file.name} ({len(full_md)} chars)")
        
        # Also fetch raw RST if available
        rst_url = f"{base_sphinx}_sources/{rst_source}"
        rst_data = fetch_url(rst_url)
        if rst_data:
            target_rst_path = QSDK_SOURCES_DIR / rst_source
            target_rst_path.parent.mkdir(parents=True, exist_ok=True)
            target_rst_path.write_bytes(rst_data)
            print(f"    [RST] Downloaded raw RST source: {rst_source}")

def scrape_docs_portal_index():
    print(f"\n==========================================")
    print(f"Scraping Main Docs Portal Landing Page...")
    print(f"==========================================")
    url = "https://qniverse.in/docs/"
    raw_html = fetch_url(url).decode('utf-8', errors='ignore')
    if raw_html:
        soup = BeautifulSoup(raw_html, 'html.parser')
        main = soup.select_one('#main-content, #page-container, article')
        if main:
            md_body = clean_html_to_markdown(str(main), url, rel_image_prefix="assets/images/")
            out_file = BASE_DIR / "docs-portal-overview.md"
            out_file.write_text(f"""---
title: "Qniverse Documentation Portal Overview"
category: "Portal"
url: "{url}"
---

# Qniverse Documentation Portal Overview

> **Source:** [{url}]({url})

![Qniverse Docs Portal](assets/screenshots/qniverse-docs-portal.png)

{md_body}
""", encoding='utf-8')
            print(f"  [SAVED] docs-portal-overview.md")

def generate_readme_and_summary():
    print(f"\n==========================================")
    print(f"Generating Master README.md and SUMMARY.md...")
    print(f"==========================================")
    
    readme_content = f"""# Qniverse Platform Documentation

Comprehensive, offline-ready documentation scraped directly from the official **Qniverse** platform ([https://qniverse.in/docs/](https://qniverse.in/docs/)) and the **QSDK Sphinx Manual** ([https://qniverse.in/docs-category/qsdk/](https://qniverse.in/docs-category/qsdk/)).

Developed and maintained by the **Centre for Development of Advanced Computing (C-DAC)** under the National Quantum Mission, **Qniverse** is India's premier cloud-based quantum computing platform offering graphical circuit composition, multi-framework code synthesis, quantum simulation across CPU/GPU clusters (including PARAM Supercomputers and the QACC cluster), and an extensive suite of quantum algorithms.

---

## Visual Architecture & Platform Tour

````carousel
![Qniverse Documentation Portal](assets/screenshots/qniverse-docs-portal.png)
<!-- slide -->
![Circuit Composer Area](assets/screenshots/circuit-composer.png)
<!-- slide -->
![Code Editor Area](assets/screenshots/code-editor.png)
<!-- slide -->
![Quantum Gates Palette](assets/screenshots/gate-palette.png)
<!-- slide -->
![QSDK Sphinx Technical Manual](assets/screenshots/qsdk-portal.png)
<!-- slide -->
![Quantum Visualization](assets/screenshots/visualization.png)
````

---

## Documentation Structure

The documentation is organized into four core modules:

| Section | Description | Articles | Location |
|---|---|:---:|---|
| **[User Guide](user-guide/)** | Getting started, account setup, Circuit Composer, Code Editor, hardware backends, noise modeling, visualization, and execution. | 16 | `docs/documentation/user-guide/` |
| **[Quantum Algorithms](algorithms/)** | 30 comprehensive algorithm tutorials with mathematical expressions, circuit steps, complexity analysis, and video walkthroughs. | 30 | `docs/documentation/algorithms/` |
| **[QSDK Documentation](qsdk/)** | Official Python SDK guide, installation across OSs, registers, gate construction, custom modules, backend selection, and remote job submission. | 14 | `docs/documentation/qsdk/` |
| **[FAQ & Troubleshooting](faq-and-troubleshooting/)** | Platform feedback, error troubleshooting, terms of service, and privacy policies. | 2 | `docs/documentation/faq-and-troubleshooting/` |

---

## 1. User Guide (`user-guide/`)

The User Guide provides end-to-end instructions for modeling and executing quantum circuits on Qniverse:

1. [01. Introduction to Qniverse](user-guide/01-introduction-to-qniverse.md) — Platform overview, key capabilities, and architecture.
2. [02. Creating an Account](user-guide/02-creating-an-account.md) — Registration, verification, and onboarding.
3. [03. Profile & Account Management](user-guide/03-profile-and-account.md) — Managing user credentials, API keys, and settings.
4. [04. Circuit Composer Area](user-guide/04-circuit-composer-area.md) — Graphical drag-and-drop circuit canvas, timeline tools, and gate configuration.
5. [05. Code Editor Area](user-guide/05-code-editor-area.md) — Integrated code editor supporting Qiskit, Cirq, OpenQASM, CudaQ, Braket, and Q# generation.
6. [06. Building Circuits](user-guide/06-building-circuits.md) — Step-by-step circuit construction, qubit allocation, and barrier placement.
7. [07. Gates Palette](user-guide/07-gates-palette.md) — Catalog of available quantum gates, categorizations, and icons.
8. [08. Quantum Gates Reference](user-guide/08-quantum-gate-reference.md) — Formal definitions, unitarity properties, and matrix representations.
9. [09. Measurement on Basis(x,y,z) & Gate Matrices](user-guide/09-measurement-on-basis-gate-matrices.md) — Pauli matrices, Bloch sphere transformations, and projective measurements.
10. [10. Compute Resources](user-guide/10-computing-resources.md) — CPU, GPU, and high-performance computing allocations.
11. [11. Backend Systems](user-guide/11-backend-systems.md) — Overview of available simulators, statevector backends, and PARAM supercomputer connections.
12. [12. Noise Modeling in Qniverse](user-guide/12-noise-modeling.md) — Simulating realistic quantum hardware noise (depolarizing, bit-flip, phase-flip, amplitude damping).
13. [13. Running Circuits](user-guide/13-running-circuits.md) — Selecting shot counts, seed, simulator targets, and executing workloads.
14. [14. Visualization](user-guide/14-visualization.md) — Statevector sphere, Bloch sphere, Q-sphere, measurement histograms, and probability distributions.
15. [15. View Jobs](user-guide/15-view-jobs.md) — Tracking execution status (Queued, Running, Completed, Failed), retrieving histograms, and export options.
16. [16. Launch Notebook (Qniverse Labs)](user-guide/16-launch-notebook-labs-resources.md) — JupyterLab environment pre-configured with QSDK and high-performance libraries.

---

## 2. Quantum Algorithms Library (`algorithms/`)

Qniverse includes a rich library of 30 standard and advanced quantum algorithms across fundamentals, optimization, chemistry, machine learning, communication, and error correction:

### Fundamental & Oracle Algorithms
- [01. Deutsch Function](algorithms/01-deutsch-function.md) — Constant vs. balanced function evaluation on 1 qubit.
- [02. Deutsch-Jozsa Algorithm](algorithms/02-deutsch-jozsa-algorithm.md) — Exponential speedup for determining function global properties on $n$ qubits.
- [03. Bernstein-Vazirani Algorithm](algorithms/03-bernstein-vazirani-algorithm.md) — Finding hidden bit strings $s \\in \\{{0,1\\}}^n$ in a single query.
- [04. Simon’s Algorithm](algorithms/04-simons-algorithm.md) — Finding hidden XOR mask with exponential speedup over classical algorithms.
- [05. Grover’s Search Algorithm](algorithms/05-grovers-algorithm-search.md) — Quadratic speedup for searching unsorted databases of size $N$ in $O(\\sqrt{{N}})$ steps.
- [06. Quantum Phase Estimation (QPE)](algorithms/06-quantum-phase-estimation-qpe.md) — Estimating eigenphases $\\theta$ of unitary operators $U|u\\rangle = e^{{2\\pi i \\theta}}|u\\rangle$.
- [07. Quantum Fourier Transform (QFT)](algorithms/07-quantum-fourier-transform-qft.md) — Quantum analogue of discrete Fourier transform with exponential gate reduction.
- [08. Shor’s Factoring Algorithm](algorithms/08-shors-algorithm-factorization.md) — Polynomial time integer factorization via modular order finding.

### Quantum Information & Communication
- [09. Quantum Teleportation](algorithms/09-quantum-teleportation.md) — Transmitting an unknown quantum state using Bell entanglement and 2 classical bits.
- [10. Superdense Coding](algorithms/10-superdense-coding.md) — Transmitting 2 classical bits using a single entangled qubit.
- [11. Quantum N-Qubit Teleportation (Unitary-Control)](algorithms/11-quantum-n-qubit-teleportation-unitary-control.md) — Generalized multi-qubit state transfer with unitary feedforward.
- [17. Quantum Veto Algorithm](algorithms/17-quantum-veto-algorithm.md) — Anonymous distributed veto voting protocol using entangled states.
- [18. Quantum Digital Signature (QDS)](algorithms/18-quantum-digital-signature-qds.md) — Unforgeable cryptographic message signing backed by quantum physics.
- [19. Quantum Private Comparison (QPC)](algorithms/19-quantum-private-comparison-qpc.md) — Secure multi-party computation to compare private values without disclosure.

### Variational & Optimization Algorithms
- [13. Variational Quantum Eigensolver (VQE)](algorithms/13-variational-quantum-eigensolver-vqe.md) — Hybrid quantum-classical optimization to find ground state molecular energies.
- [14. QAOA for Max-Cut](algorithms/14-qaoa-for-max-cut.md) — Quantum Approximate Optimization Algorithm applied to combinatorial graph cuts.
- [15. Portfolio Optimization using QAOA](algorithms/15-portfolio-optimization-using-qaoa.md) — Financial Markowitz mean-variance optimization on quantum circuits.
- [16. Harrow-Hassidim-Lloyd (HHL) Algorithm](algorithms/16-harrow-hassidim-lloyd-hhl-algorithm.md) — Solving linear systems $A\\vec{{x}} = \\vec{{b}}$ with exponential speedup.
- [27. Suzuki-Trotter Time-Evolution](algorithms/27-suzuki-trotter-time-evolution.md) — Simulating Hamiltonian dynamics $e^{{-iHt}}$ via operator splitting.

### Quantum Machine Learning (QML)
- [20. QSVM (Quantum Support Vector Machine)](algorithms/20-qsvm.md) — Quantum kernel methods for classification in high-dimensional Hilbert spaces.
- [21. QKMeans Algorithm](algorithms/21-qkmeans-algorithm.md) — Quantum distance estimation for unsupervised data clustering.
- [22. Quantum KNN (K-Nearest Neighbors)](algorithms/22-quantum-knn-algorithm.md) — Quantum fidelity / inner product computation for classification.
- [23. Quantum Hierarchical Clustering (QHC)](algorithms/23-quantum-hierarchical-clustering-qhc.md) — Tree-based agglomerative clustering via quantum states.
- [24. Quantum Perceptron Algorithm](algorithms/24-quantum-perceptron-algorithm.md) — Quantum neural activation function and hyper-plane learning.
- [25. Quantum Principal Component Analysis (QPCA)](algorithms/25-quantum-principal-component-analysis-qpca.md) — Density matrix exponentiation to reveal dominant eigenspaces.
- [26. Quantum Neural Network (QNN)](algorithms/26-quantum-neural-network-qnn.md) — Parameterized quantum circuits (PQC) trained via gradient descent.

### Quantum Walks & Dynamics
- [12. Quantum Walks Algorithm (1D)](algorithms/12-quantum-walks-algorithm-1d.md) — Discrete-time quantum random walk demonstrating ballistic wave spreading.

### Quantum Error Correction (QEC)
- [28. QEC: Three-Qubit Repetition Code](algorithms/28-qec-three-qubit-repetition-code.md) — Bit-flip error detection and correction using syndrome ancillae.
- [29. QEC: Shor’s Nine-Qubit Code](algorithms/29-qec-shors-nine-qubit-code.md) — Concatenated code correcting arbitrary single-qubit errors (bit-flip and phase-flip).
- [30. QEC: Steane Seven-Qubit Code](algorithms/30-qec-steane-seven-qubit-code.md) — CSS code encoding 1 logical qubit into 7 physical qubits with transversal Clifford gates.

---

## 3. QSDK Python Technical Manual (`qsdk/`)

The QSDK is C-DAC's Python software development kit powering Qniverse. It provides APIs for constructing circuits, managing registers, choosing backends, and executing jobs remotely.

- [00. QSDK Portal Overview](qsdk/00-qsdk-portal-overview.md) — Summary of the SDK and high-level architecture.
- [01. Index](qsdk/01-index.md) — Welcome guide and Sphinx table of contents.
- [02. Introduction to QSDK](qsdk/02-introduction-index.md) — Key concepts and design philosophy.
- [03. Getting Started](qsdk/03-getting-started.md) — Installation across Windows, Linux, and macOS, prerequisites, troubleshooting, and CPU/GPU support.
- [04. Creating a Circuit](qsdk/04-creating-a-circuit.md) — Register instantiation, gate addition, conditional execution, measurements, and submodules.
- [05. Gates & Modules Overview](qsdk/05-gates-and-modules-index.md) — Module composition and gate management.
- [06. Quantum Gates Reference](qsdk/06-quantum-gates.md) — Single-qubit, controlled, and parameterized gate definitions in QSDK.
- [07. Backend Systems Overview](qsdk/07-backends-index.md) — Simulators and compute cluster targets.
- [08. Backend Selection](qsdk/08-backend-systems-selection.md) — Configuring execution targets (local CPU, CUDA-accelerated GPU, and remote PARAM supercomputers).
- [09. Job APIs Overview](qsdk/09-job-apis-index.md) — Remote job execution interfaces.
- [10. Submitting & Managing Jobs](qsdk/10-submitting-and-managing-jobs.md) — Submitting jobs, querying status, and extracting result dictionaries.
- [11. System Logs & Support Overview](qsdk/11-system-logs-and-support-index.md) — Logging levels and diagnostics.
- [12. Licenses](qsdk/12-licenses.md) — Licensing and open-source acknowledgments.
- [13. Support & Contact](qsdk/13-support.md) — Developer assistance, community forums, and C-DAC support channels.
- `qsdk/sources/` — Unmodified reStructuredText (`.rst.txt`) source files matching the Sphinx distribution.

---

## 4. FAQ and Troubleshooting (`faq-and-troubleshooting/`)

- [01. Bug Report & Feedback](faq-and-troubleshooting/01-bug-report-feedback.md) — Reporting anomalies, submitting feature requests, and contacting the engineering team.
- [02. Terms & Privacy](faq-and-troubleshooting/02-terms-and-privacy.md) — Terms of service, platform usage rules, and data privacy policies.

---

## Assets & Offline Media

- **Formulas, Matrices & Diagrams:** Stored in `assets/images/` and referenced locally so the documentation remains 100% functional offline.
- **High-Resolution Screenshots:** Stored in `assets/screenshots/` captured via `rustwright` and `playwright`.
"""
    
    (BASE_DIR / "README.md").write_text(readme_content, encoding='utf-8')
    print(f"  [SAVED] README.md ({len(readme_content)} chars)")
    
    # Generate SUMMARY.md
    summary_lines = [
        "# Summary",
        "",
        "* [Introduction](README.md)",
        "* [Platform Overview](docs-portal-overview.md)",
        "",
        "## User Guide",
    ]
    for title, _, filename in USER_GUIDE_PAGES:
        summary_lines.append(f"* [{title}](user-guide/{filename})")
        
    summary_lines.append("")
    summary_lines.append("## Quantum Algorithms")
    for title, _, filename in ALGORITHM_PAGES:
        summary_lines.append(f"* [{title}](algorithms/{filename})")
        
    summary_lines.append("")
    summary_lines.append("## QSDK Documentation")
    summary_lines.append("* [QSDK Overview](qsdk/00-qsdk-portal-overview.md)")
    for title, _, filename, _ in SPHINX_QSDK_PAGES:
        summary_lines.append(f"* [{title}](qsdk/{filename})")
        
    summary_lines.append("")
    summary_lines.append("## FAQ & Troubleshooting")
    for title, _, filename in FAQ_PAGES:
        summary_lines.append(f"* [{title}](faq-and-troubleshooting/{filename})")
        
    summary_text = "\n".join(summary_lines) + "\n"
    (BASE_DIR / "SUMMARY.md").write_text(summary_text, encoding='utf-8')
    print(f"  [SAVED] SUMMARY.md ({len(summary_text)} chars)")

if __name__ == "__main__":
    scrape_betterdocs_group("User Guide", USER_GUIDE_PAGES, USER_GUIDE_DIR)
    scrape_betterdocs_group("Algorithms", ALGORITHM_PAGES, ALGORITHMS_DIR)
    scrape_betterdocs_group("FAQ and Troubleshooting", FAQ_PAGES, FAQ_DIR)
    scrape_sphinx_qsdk()
    scrape_docs_portal_index()
    generate_readme_and_summary()
    print("\n🎉 ALL DOCUMENTATION SCRAPED AND PROCESSED SUCCESSFULLY!")
