"""
Convert Walkthrough Markdown to PDF
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def convert_markdown_to_pdf(md_file: str, output_pdf: str):
    """Convert markdown file to PDF with styling"""
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'nl2br'
        ]
    )
    
    # Add CSS styling
    css_style = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 8px;
            margin-top: 25px;
        }
        h3 {
            color: #7f8c8d;
            margin-top: 20px;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }
        pre {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.85em;
        }
        pre code {
            background-color: transparent;
            color: #ecf0f1;
            padding: 0;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }
        .emoji {
            font-size: 1.2em;
        }
        ul, ol {
            margin-left: 20px;
        }
        li {
            margin: 8px 0;
        }
    </style>
    """
    
    # Create full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>8-Phase Signal Engine - Implementation Walkthrough</title>
        {css_style}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert to PDF
    print(f"Converting {md_file} to PDF...")
    HTML(string=full_html).write_pdf(output_pdf)
    print(f"✅ PDF created: {output_pdf}")

if __name__ == '__main__':
    # Convert walkthrough
    artifact_dir = Path(r'C:\Users\BALASARAVANAN\.gemini\antigravity\brain\35b59cfd-9bbb-44e2-bee7-4ceaa8eb2cdf')
    backend_dir = Path(__file__).parent
    
    # Convert walkthrough from artifacts
    walkthrough_md = artifact_dir / 'walkthrough.md'
    walkthrough_pdf = backend_dir / '8Phase_Walkthrough.pdf'
    
    if walkthrough_md.exists():
        convert_markdown_to_pdf(str(walkthrough_md), str(walkthrough_pdf))
    else:
        print(f"❌ Walkthrough not found at {walkthrough_md}")
    
    # Also convert the README
    readme_md = backend_dir / '8PHASE_README.md'
    readme_pdf = backend_dir / '8Phase_QuickReference.pdf'
    
    if readme_md.exists():
        convert_markdown_to_pdf(str(readme_md), str(readme_pdf))
    else:
        print(f"❌ README not found at {readme_md}")
    
    print("\n✅ PDF generation complete!")
    print(f"  - {walkthrough_pdf}")
    print(f"  - {readme_pdf}")
