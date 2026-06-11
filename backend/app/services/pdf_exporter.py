"""PDF Export service using Puppeteer (pyppeteer) for A4 PDF generation.

Converts Markdown to HTML, renders with Chinese fonts, and exports as A4 PDF.
"""

import base64
import os
from markdown import markdown

# Path to Chinese font for embedding
FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "fonts")
FONT_PATH = os.path.join(FONT_DIR, "NotoSansSC-Regular.ttf")

# CSS template for A4 PDF with Chinese font support
PDF_CSS = """
@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        color: #999;
    }
}

body {
    font-family: 'Times New Roman', serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #333;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}

h1 { font-size: 16pt; margin-top: 0; border-bottom: 2px solid #d97706; padding-bottom: 6px; }
h2 { font-size: 13pt; margin-top: 18pt; color: #d97706; }
h3 { font-size: 11pt; margin-top: 14pt; }
h4 { font-size: 10.5pt; margin-top: 10pt; }

p { margin: 6pt 0; }

ul, ol { margin: 6pt 0; padding-left: 24pt; }
li { margin: 3pt 0; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 10pt;
}
table th, table td {
    border: 1px solid #ddd;
    padding: 6pt 8pt;
    text-align: left;
}
table th {
    background-color: #f0f4ff;
    font-weight: bold;
}
table tr:nth-child(even) {
    background-color: #fafafa;
}

code {
    font-family: 'Courier New', monospace;
    background-color: #f5f5f5;
    padding: 1pt 4pt;
    border-radius: 2pt;
    font-size: 10pt;
}

pre {
    background-color: #f5f5f5;
    padding: 10pt;
    border-radius: 4pt;
    overflow-x: auto;
    font-size: 10pt;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #1a73e8;
    margin: 12pt 0;
    padding: 6pt 12pt;
    background-color: #f8f9ff;
    color: #555;
}

strong { color: #222; }
em { color: #555; }

.katex { font-size: 1.1em; }

.watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 72pt;
    color: #d97706;
    opacity: 0.06;
    pointer-events: none;
    z-index: 9999;
    white-space: nowrap;
    font-family: 'Times New Roman', serif;
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {font_face}
        {css}
    </style>
</head>
<body>
    <div class="watermark">Cheese Roll</div>
    {body}
</body>
</html>"""


def _get_font_base64() -> str:
    """Read Chinese font and encode as base64 for CSS embedding.

    Returns empty string if font file not found.
    """
    if os.path.exists(FONT_PATH):
        with open(FONT_PATH, "rb") as f:
            font_data = base64.b64encode(f.read()).decode("ascii")
        return f"""
@font-face {{
    font-family: 'Noto Sans SC';
    src: url(data:font/ttf;base64,{font_data}) format('truetype');
    font-weight: normal;
    font-style: normal;
}}
"""
    # Fallback: no font embedding, rely on system fonts
    return ""


async def markdown_to_pdf(
    markdown_text: str,
    title: str = "复习笔记",
) -> bytes:
    """Convert Markdown text to A4 PDF bytes using Puppeteer.

    Args:
        markdown_text: The Markdown content to render.
        title: Document title for the HTML <title> and displayed at top.

    Returns:
        PDF file as bytes.
    """
    # Convert Markdown to HTML
    html_body = markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "codehilite", "toc", "nl2br"],
    )

    # Build complete HTML document
    font_face = _get_font_base64()
    html = HTML_TEMPLATE.format(
        title=title,
        font_face=font_face,
        css=PDF_CSS,
        body=html_body,
    )

    # Render PDF with Puppeteer
    try:
        import asyncio
        from pyppeteer import launch

        browser = await launch(
            headless=True,
            executablePath="/usr/bin/chromium",
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        page = await browser.newPage()
        await page.setContent(html)
        await page.waitFor(1000)  # wait for rendering

        pdf_bytes = await page.pdf({
            "format": "A4",
            "printBackground": True,
            "margin": {
                "top": "20mm",
                "bottom": "20mm",
                "left": "15mm",
                "right": "15mm",
            },
            "displayHeaderFooter": False,
        })

        await browser.close()
        return pdf_bytes

    except ImportError:
        # Fallback: return the HTML wrapped for browser-based PDF printing
        # In production, pyppeteer should always be available
        html_with_note = html.replace(
            "</body>",
            '<p style="color:red;text-align:center;">[PDF 引擎未安装 - 请在浏览器中打印此页面]</p></body>',
        )
        return html_with_note.encode("utf-8")
