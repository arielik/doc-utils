#!/usr/bin/env python3
"""
Script to generate a single HTML file from all implementation guideline markdown files.
Can then be converted to PDF using browser print functionality.
"""

import os
import re
from pathlib import Path
from datetime import datetime

def read_markdown_files():
    """Read all implementation guideline markdown files in order"""
    guidelines_dir = Path("docs/implementation-guidelines")
    
    # Define the order of files
    file_order = [
        "stage-1-intent-processing-implementation.md",
        "stage-2-rag-enhanced-retrieval-implementation.md", 
        "stage-3-promql-generation-implementation.md",
        "stage-4-execution-self-healing-implementation.md",
        "stage-5-semantic-analysis-implementation.md",
        "stage-6-counterfactual-visualization-implementation.md"
    ]
    
    combined_content = []
    
    for filename in file_order:
        filepath = guidelines_dir / filename
        if filepath.exists():
            print(f"Reading {filename}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()
                
            # Add a page break before each new stage (except the first)
            if combined_content:
                combined_content.append('<div style="page-break-before: always;"></div>')
            
            combined_content.append(f'<!-- {filename} -->')
            combined_content.append(file_content)
        else:
            print(f"Warning: {filename} not found")
    
    return "\n\n".join(combined_content)

def simple_markdown_to_html(markdown_content):
    """Simple markdown to HTML conversion using regex"""
    html = markdown_content
    
    # Convert headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Convert code blocks
    html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # Convert inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Convert bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Convert lists
    html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # Convert paragraphs
    paragraphs = html.split('\n\n')
    html_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<') and not para.startswith('<!--'):
            para = f'<p>{para}</p>'
        html_paragraphs.append(para)
    
    return '\n\n'.join(html_paragraphs)

def create_html_document(content):
    """Create complete HTML document with styling"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adaptive Infrastructure Intelligence System - Implementation Guidelines</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 100%;
            margin: 0;
            padding: 0;
            color: #333;
            background: white;
        }}
        
        .title-page {{
            text-align: center;
            margin: 100px 0;
            page-break-after: always;
        }}
        
        .title-page h1 {{
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 20px;
            border-bottom: none;
        }}
        
        .title-page h2 {{
            font-size: 1.5em;
            color: #7f8c8d;
            font-weight: normal;
            margin-bottom: 50px;
            border-bottom: none;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-before: always;
            margin-top: 40px;
            font-size: 1.8em;
        }}
        
        h1:first-of-type {{
            page-break-before: auto;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 1.4em;
        }}
        
        h3 {{
            color: #2980b9;
            margin-top: 25px;
            font-size: 1.2em;
        }}
        
        h4 {{
            color: #8e44ad;
            margin-top: 20px;
            font-size: 1.1em;
        }}
        
        p {{
            margin: 12px 0;
            text-align: justify;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-size: 0.9em;
            color: #d63384;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            margin: 16px 0;
            white-space: pre-wrap;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: #333;
        }}
        
        ul {{
            margin: 12px 0;
            padding-left: 20px;
        }}
        
        li {{
            margin: 6px 0;
            list-style-type: disc;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        em {{
            color: #7f8c8d;
            font-style: italic;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 20px;
            margin: 20px 0;
            page-break-after: always;
        }}
        
        .toc h2 {{
            margin-top: 0;
            border-bottom: none;
            color: #2c3e50;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 8px 0;
            padding: 5px;
            background: white;
            border-radius: 3px;
        }}
        
        .section-break {{
            page-break-before: always;
            height: 0;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 0;
            }}
            
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>Adaptive Infrastructure Intelligence System</h1>
        <h2>Implementation Guidelines</h2>
        <p style="font-size: 1.1em; margin-top: 50px;">
            Comprehensive Technical Specifications for Development Teams
        </p>
        <p style="margin-top: 30px; color: #666;">
            Generated on: {current_date}
        </p>
    </div>
    
    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
            <li><strong>Stage 1:</strong> Intent Processing and Hierarchical Decomposition</li>
            <li><strong>Stage 2:</strong> RAG-Enhanced Context Retrieval and Reranking</li>
            <li><strong>Stage 3:</strong> PromQL Generation, Validation, and Expert Feedback</li>
            <li><strong>Stage 4:</strong> Execution and Self-Healing Feedback Collection</li>
            <li><strong>Stage 5:</strong> Semantic Data Analysis and Evidence Synthesis</li>
            <li><strong>Stage 6:</strong> Counterfactual Analysis and Visualization</li>
        </ul>
    </div>
    
    {content}
    
    <div style="margin-top: 50px; text-align: center; color: #666; font-size: 0.9em;">
        <p>End of Implementation Guidelines</p>
        <p>Generated on {current_date}</p>
    </div>
</body>
</html>"""
    
    return html_template

def main():
    """Main function to generate HTML file"""
    print("🚀 Generating Implementation Guidelines HTML...")
    
    # Read all markdown files
    print("\n📖 Reading markdown files...")
    markdown_content = read_markdown_files()
    
    if not markdown_content.strip():
        print("❌ No markdown content found!")
        return
    
    # Convert to HTML (simple conversion)
    print("\n🔄 Converting markdown to HTML...")
    html_content = simple_markdown_to_html(markdown_content)
    
    # Create complete HTML document
    complete_html = create_html_document(html_content)
    
    # Save HTML file
    output_file = "implementation_guidelines.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(complete_html)
    
    file_size = os.path.getsize(output_file) / 1024
    
    print(f"\n✅ HTML file generated successfully: {output_file}")
    print(f"📄 File size: {file_size:.1f} KB")
    
    print("\n🖨️  To convert to PDF:")
    print("1. Open the HTML file in your browser (Chrome, Safari, Firefox)")
    print("2. Press Cmd+P (Mac) or Ctrl+P (Windows/Linux)")
    print("3. Choose 'Save as PDF' or 'Microsoft Print to PDF'")
    print("4. Adjust settings:")
    print("   - Paper size: A4")
    print("   - Margins: Default or Minimum")
    print("   - Include background graphics: Yes")
    print("5. Save as 'implementation_guidelines.pdf'")
    
    print(f"\n📂 HTML file location: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
