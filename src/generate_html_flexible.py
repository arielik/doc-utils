#!/usr/bin/env python3
"""
Flexible script to generate HTML from markdown files.
Can handle single files or multiple files from a directory.
Usage: 
  python3 generate_html_flexible.py file.md
  python3 generate_html_flexible.py --dir docs/implementation-guidelines
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

def simple_markdown_to_html(markdown_content):
    """Enhanced markdown to HTML conversion using regex"""
    html = markdown_content
    
    # Convert headers (with IDs for table of contents)
    html = re.sub(r'^# (.*?)$', lambda m: f'<h1 id="{create_anchor_id(m.group(1))}">{m.group(1)}</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', lambda m: f'<h2 id="{create_anchor_id(m.group(1))}">{m.group(1)}</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', lambda m: f'<h3 id="{create_anchor_id(m.group(1))}">{m.group(1)}</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', lambda m: f'<h4 id="{create_anchor_id(m.group(1))}">{m.group(1)}</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^##### (.*?)$', lambda m: f'<h5 id="{create_anchor_id(m.group(1))}">{m.group(1)}</h5>', html, flags=re.MULTILINE)
    
    # Convert code blocks with language support
    html = re.sub(r'```(\w+)?\n(.*?)\n```', lambda m: f'<pre><code class="language-{m.group(1) or "text"}">{escape_html(m.group(2))}</code></pre>', html, flags=re.DOTALL)
    
    # Convert inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Convert bold and italic
    html = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Convert numbered lists
    html = re.sub(r'^(\d+)\. (.*?)$', r'<li>\2</li>', html, flags=re.MULTILINE)
    
    # Convert bullet lists
    html = re.sub(r'^[-*+] (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Wrap consecutive list items in ul/ol tags
    html = re.sub(r'(<li>.*?</li>(?:\s*<li>.*?</li>)*)', wrap_list_items, html, flags=re.DOTALL)
    
    # Convert blockquotes
    html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # Convert horizontal rules
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)
    
    # Convert tables (basic support)
    html = convert_tables(html)
    
    # Convert paragraphs (preserve existing HTML tags)
    paragraphs = html.split('\n\n')
    html_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<') and not para.startswith('<!--') and not is_html_block(para):
            # Only wrap in <p> if it doesn't contain block elements
            if not contains_block_elements(para):
                para = f'<p>{para}</p>'
        html_paragraphs.append(para)
    
    return '\n\n'.join(html_paragraphs)

def create_anchor_id(text):
    """Create a URL-friendly anchor ID from header text"""
    # Remove HTML tags and convert to lowercase
    text = re.sub(r'<[^>]+>', '', text)
    text = text.lower()
    # Replace spaces with hyphens and remove special characters
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def escape_html(text):
    """Escape HTML special characters"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def wrap_list_items(match):
    """Wrap list items in appropriate ul or ol tags"""
    content = match.group(1)
    # Check if it's a numbered list by looking for patterns like "1. " in the original
    if re.search(r'\d+\.\s', content):
        return f'<ol>{content}</ol>'
    else:
        return f'<ul>{content}</ul>'

def is_html_block(text):
    """Check if text is already an HTML block element"""
    block_tags = ['<div', '<section', '<article', '<header', '<footer', '<nav', '<aside', '<main', '<pre', '<blockquote', '<ul', '<ol', '<li', '<table', '<tr', '<td', '<th']
    return any(text.strip().startswith(tag) for tag in block_tags)

def contains_block_elements(text):
    """Check if text contains HTML block elements"""
    block_tags = ['<h1', '<h2', '<h3', '<h4', '<h5', '<h6', '<div', '<section', '<pre', '<blockquote', '<ul', '<ol', '<table']
    return any(tag in text for tag in block_tags)

def convert_tables(html):
    """Convert markdown tables to HTML tables"""
    lines = html.split('\n')
    result = []
    in_table = False
    
    for i, line in enumerate(lines):
        if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
            if not in_table:
                result.append('<table>')
                in_table = True
                # Check if next line is separator
                if i + 1 < len(lines) and re.match(r'^\|[-:\s|]+\|$', lines[i + 1].strip()):
                    result.append('<thead>')
                    result.append('<tr>')
                    cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                    for cell in cells:
                        result.append(f'<th>{cell}</th>')
                    result.append('</tr>')
                    result.append('</thead>')
                    result.append('<tbody>')
                    continue
                else:
                    result.append('<tbody>')
            
            # Skip separator lines
            if re.match(r'^\|[-:\s|]+\|$', line.strip()):
                continue
                
            # Process table row
            result.append('<tr>')
            cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
            for cell in cells:
                result.append(f'<td>{cell}</td>')
            result.append('</tr>')
        else:
            if in_table:
                result.append('</tbody>')
                result.append('</table>')
                in_table = False
            result.append(line)
    
    if in_table:
        result.append('</tbody>')
        result.append('</table>')
    
    return '\n'.join(result)

def extract_toc_from_html(html_content):
    """Extract table of contents from HTML headers"""
    toc_items = []
    
    # Find all headers with IDs
    header_pattern = r'<h([1-6])[^>]*id="([^"]*)"[^>]*>(.*?)</h[1-6]>'
    matches = re.findall(header_pattern, html_content, re.IGNORECASE)
    
    for level, anchor_id, title in matches:
        level = int(level)
        # Clean title of HTML tags
        clean_title = re.sub(r'<[^>]+>', '', title)
        toc_items.append({
            'level': level,
            'anchor': anchor_id,
            'title': clean_title
        })
    
    return toc_items

def generate_toc_html(toc_items):
    """Generate HTML table of contents"""
    if not toc_items:
        return ""
    
    html = ['<div class="toc">', '<h2>Table of Contents</h2>', '<ul class="toc-list">']
    
    for item in toc_items:
        indent_class = f"toc-level-{item['level']}"
        html.append(f'<li class="{indent_class}"><a href="#{item['anchor']}">{item['title']}</a></li>')
    
    html.extend(['</ul>', '</div>'])
    return '\n'.join(html)

def read_single_file(filepath):
    """Read a single markdown file"""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File {filepath} does not exist")
        return None, None
    
    print(f"Reading {path.name}...")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content, path.stem

def read_multiple_files(directory):
    """Read multiple markdown files from a directory"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Error: Directory {directory} does not exist")
        return None, None
    
    # Get all markdown files
    md_files = sorted(dir_path.glob("*.md"))
    if not md_files:
        print(f"No markdown files found in {directory}")
        return None, None
    
    combined_content = []
    
    for filepath in md_files:
        print(f"Reading {filepath.name}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Add a page break before each new file (except the first)
        if combined_content:
            combined_content.append('<div style="page-break-before: always;"></div>')
        
        combined_content.append(f'<!-- {filepath.name} -->')
        combined_content.append(file_content)
    
    return "\n\n".join(combined_content), "combined_documents"

def create_html_document(content, title, include_toc=True):
    """Create complete HTML document with styling"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Generate table of contents if requested
    toc_html = ""
    if include_toc:
        toc_items = extract_toc_from_html(content)
        if toc_items:
            toc_html = generate_toc_html(toc_items)
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
            padding: 20px;
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
            margin-top: 40px;
            font-size: 1.8em;
        }}
        
        h1:first-of-type {{
            margin-top: 0;
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
        
        h5 {{
            color: #27ae60;
            margin-top: 18px;
            font-size: 1.05em;
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
            font-size: 0.85em;
        }}
        
        ul, ol {{
            margin: 12px 0;
            padding-left: 25px;
        }}
        
        li {{
            margin: 6px 0;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        em {{
            color: #7f8c8d;
            font-style: italic;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        hr {{
            border: none;
            height: 2px;
            background-color: #ecf0f1;
            margin: 30px 0;
        }}
        
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
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
        
        .toc-list {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc-list li {{
            margin: 8px 0;
            padding: 5px;
            background: white;
            border-radius: 3px;
        }}
        
        .toc-level-1 {{ font-weight: bold; font-size: 1.1em; }}
        .toc-level-2 {{ padding-left: 20px; }}
        .toc-level-3 {{ padding-left: 40px; font-size: 0.95em; }}
        .toc-level-4 {{ padding-left: 60px; font-size: 0.9em; }}
        .toc-level-5 {{ padding-left: 80px; font-size: 0.85em; }}
        
        .section-break {{
            page-break-before: always;
            height: 0;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 15px;
            }}
            
            .no-print {{
                display: none;
            }}
            
            h1, h2, h3, h4, h5 {{
                page-break-after: avoid;
            }}
            
            pre, blockquote {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {toc_html}
    
    {content}
    
    <div style="margin-top: 50px; text-align: center; color: #666; font-size: 0.9em;">
        <hr>
        <p>Generated on {current_date}</p>
    </div>
</body>
</html>"""
    
    return html_template

def main():
    """Main function to generate HTML file"""
    parser = argparse.ArgumentParser(description='Generate HTML from markdown files')
    parser.add_argument('input', nargs='?', help='Input markdown file or directory (with --dir)')
    parser.add_argument('--dir', action='store_true', help='Process all markdown files in the specified directory')
    parser.add_argument('--output', '-o', help='Output HTML filename (default: auto-generated)')
    parser.add_argument('--no-toc', action='store_true', help='Disable table of contents generation')
    parser.add_argument('--title', help='Document title (default: derived from filename)')
    
    args = parser.parse_args()
    
    if not args.input:
        print("Usage: python3 generate_html_flexible.py <file.md> [options]")
        print("       python3 generate_html_flexible.py --dir <directory> [options]")
        return
    
    print("🚀 Generating HTML from markdown...")
    
    # Read markdown content
    print("\n📖 Reading markdown files...")
    if args.dir:
        markdown_content, base_name = read_multiple_files(args.input)
    else:
        markdown_content, base_name = read_single_file(args.input)
    
    if not markdown_content:
        return
    
    # Convert to HTML
    print("\n🔄 Converting markdown to HTML...")
    html_content = simple_markdown_to_html(markdown_content)
    
    # Determine title and output filename
    title = args.title or base_name.replace('-', ' ').replace('_', ' ').title()
    output_file = args.output or f"{base_name}.html"
    
    # Create complete HTML document
    include_toc = not args.no_toc
    complete_html = create_html_document(html_content, title, include_toc)
    
    # Save HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(complete_html)
    
    file_size = os.path.getsize(output_file) / 1024
    
    print(f"\n✅ HTML file generated successfully: {output_file}")
    print(f"📄 File size: {file_size:.1f} KB")
    print(f"📑 Title: {title}")
    print(f"📑 Table of Contents: {'Included' if include_toc else 'Disabled'}")
    
    print("\n🖨️  To convert to PDF:")
    print("1. Open the HTML file in your browser (Chrome, Safari, Firefox)")
    print("2. Press Cmd+P (Mac) or Ctrl+P (Windows/Linux)")
    print("3. Choose 'Save as PDF' or 'Microsoft Print to PDF'")
    print("4. Adjust settings:")
    print("   - Paper size: A4")
    print("   - Margins: Default or Minimum")
    print("   - Include background graphics: Yes")
    print(f"5. Save as '{base_name}.pdf'")
    
    print(f"\n📂 HTML file location: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
