#!/usr/bin/env python3
"""
Flexible script to generate HTML from markdown files.
Can handle single files or multiple files from a directory.
Creates output files in a designated output folder.

Usage: 
  # Single file
  python3 generate_html_flexible.py file.md
  python3 generate_html_flexible.py file.md --output custom_output/
  python3 generate_html_flexible.py file.md --output report.html
  
  # Directory - combined into one HTML file (default)
  python3 generate_html_flexible.py --dir docs/implementation-guidelines
  python3 generate_html_flexible.py --dir docs/ --output ./html_reports/
  
  # Directory - separate HTML files with index navigation
  python3 generate_html_flexible.py --dir docs/ --separate --output ./html_reports/
  python3 generate_html_flexible.py --dir docs/ --separate --title "My Documentation"
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

def read_multiple_files_separate(directory):
    """Read multiple markdown files from a directory as separate documents"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Error: Directory {directory} does not exist")
        return None
    
    # Get all markdown files
    md_files = sorted(dir_path.glob("*.md"))
    if not md_files:
        print(f"No markdown files found in {directory}")
        return None
    
    file_contents = []
    
    for filepath in md_files:
        print(f"Reading {filepath.name}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from first heading or use filename
        title = extract_title_from_markdown(content) or filepath.stem.replace('-', ' ').replace('_', ' ').title()
        
        file_contents.append({
            'path': filepath,
            'name': filepath.name,
            'stem': filepath.stem,
            'content': content,
            'title': title
        })
    
    return file_contents

def extract_title_from_markdown(content):
    """Extract the first H1 heading from markdown content"""
    lines = content.strip().split('\n')
    for line in lines[:20]:  # Check first 20 lines
        line = line.strip()
        if line.startswith('# ') and len(line) > 2:
            return line[2:].strip()
    return None

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

def create_index_html(documents_info, output_dir, collection_title="Markdown Documents Collection"):
    """Create an index HTML file for all documents."""
    
    index_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{collection_title} - Index</title>
    <style>
        /* Academic index styling */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #000;
            background: #f5f5f5;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: normal;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            font-style: italic;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .description {{
            font-size: 1.1em;
            margin-bottom: 40px;
            text-align: center;
            color: #555;
            line-height: 1.8;
        }}
        
        .documents-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .document-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            background: white;
        }}
        
        .document-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .document-card a {{
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        
        .card-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .card-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 8px;
            color: #2c3e50;
        }}
        
        .card-meta {{
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        
        .card-stats {{
            font-size: 0.8em;
            color: #868e96;
        }}
        
        .card-preview {{
            padding: 20px;
            background: white;
            max-height: 150px;
            overflow: hidden;
            position: relative;
        }}
        
        .card-preview p {{
            margin: 0 0 10px 0;
            color: #555;
            line-height: 1.4;
        }}
        
        .card-preview::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30px;
            background: linear-gradient(transparent, white);
        }}
        
        .card-footer {{
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            text-align: center;
        }}
        
        .read-more {{
            background: #3498db;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .read-more:hover {{
            background: #2980b9;
            text-decoration: none;
            color: white;
        }}
        
        .stats {{
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stats h3 {{
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        
        .stat-item {{
            display: inline-block;
            margin: 0 20px;
            padding: 10px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        
        .back-link {{
            margin-top: 30px;
            text-align: center;
        }}
        
        .back-link a {{
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }}
        
        @media (max-width: 768px) {{
            .documents-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .container {{
                margin: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{collection_title}</h1>
            <div class="subtitle">Document Collection</div>
        </div>
        
        <div class="content">
            <div class="description">
                Professional HTML documents generated from markdown files.
                Each document is optimized for reading and printing with clean typography
                and structured navigation.
            </div>
            
            <div class="documents-grid">"""

    # Calculate total words for all documents
    total_words = sum(len(doc['content'].split()) for doc in documents_info)
    
    # Add each document card
    for doc in documents_info:
        word_count = len(doc['content'].split())
        
        # Create a preview from the content (first paragraph or two)
        preview_content = doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content']
        # Convert basic markdown to text for preview
        preview_text = re.sub(r'#{1,6}\s+', '', preview_content)
        preview_text = re.sub(r'\*\*(.*?)\*\*', r'\1', preview_text)
        preview_text = re.sub(r'\*(.*?)\*', r'\1', preview_text)
        preview_text = re.sub(r'`([^`]+)`', r'\1', preview_text)
        
        index_template += f"""
                <div class="document-card">
                    <a href="{doc['html_filename']}">
                        <div class="card-header">
                            <div class="card-title">{escape_html(doc['title'])}</div>
                            <div class="card-meta">Source: {doc['source_filename']}</div>
                            <div class="card-stats">{word_count:,} words</div>
                        </div>
                        <div class="card-preview">
                            <p>{escape_html(preview_text)}</p>
                        </div>
                    </a>
                    <div class="card-footer">
                        <a href="{doc['html_filename']}" class="read-more">Read Document →</a>
                    </div>
                </div>"""

    index_template += f"""
            </div>
            
            <div class="stats">
                <h3>Collection Statistics</h3>
                <div class="stat-item">
                    <span class="stat-number">{len(documents_info)}</span>
                    <span class="stat-label">Documents</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{total_words:,}</span>
                    <span class="stat-label">Total Words</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">HTML</span>
                    <span class="stat-label">Format</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return index_template

def main():
    """Main function to generate HTML file"""
    parser = argparse.ArgumentParser(description='Generate HTML from markdown files')
    parser.add_argument('input', nargs='?', help='Input markdown file or directory (with --dir)')
    parser.add_argument('--dir', action='store_true', help='Process all markdown files in the specified directory')
    parser.add_argument('--separate', action='store_true', help='Create separate HTML files for each markdown file (only with --dir)')
    parser.add_argument('--output', '-o', help='Output directory or HTML filename (default: ./html_output/)')
    parser.add_argument('--no-toc', action='store_true', help='Disable table of contents generation')
    parser.add_argument('--title', help='Document title (default: derived from filename)')
    
    args = parser.parse_args()
    
    if not args.input:
        print("Usage: python3 generate_html_flexible.py <file.md> [options]")
        print("       python3 generate_html_flexible.py --dir <directory> [options]")
        print("       python3 generate_html_flexible.py --dir <directory> --separate [options]")
        return
    
    print("🚀 Generating HTML from markdown...")
    
    # Handle output path setup
    if args.output:
        output_path = Path(args.output)
        if not args.dir and output_path.suffix == '.html':
            # Specific filename provided for single file
            output_file = output_path
            output_dir = output_file.parent
        else:
            # Directory provided
            output_dir = output_path
    else:
        # Default: create html_output directory
        output_dir = Path("html_output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.dir and args.separate:
        # Process directory with separate files + index
        print("\n📖 Reading markdown files for separate processing...")
        file_contents = read_multiple_files_separate(args.input)
        
        if not file_contents:
            return
        
        print(f"📁 Output directory: {output_dir.absolute()}")
        print(f"🔄 Creating separate HTML files...")
        
        documents_info = []
        
        for file_info in file_contents:
            print(f"📝 Processing: {file_info['name']}")
            
            # Convert to HTML
            html_content = simple_markdown_to_html(file_info['content'])
            
            # Create HTML filename
            html_filename = f"{file_info['stem']}.html"
            html_path = output_dir / html_filename
            
            # Create complete HTML document
            include_toc = not args.no_toc
            complete_html = create_html_document(html_content, file_info['title'], include_toc)
            
            # Save HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(complete_html)
            
            print(f"✅ Created: {html_filename}")
            
            # Store info for index
            documents_info.append({
                'title': file_info['title'],
                'html_filename': html_filename,
                'source_filename': file_info['name'],
                'content': file_info['content']
            })
        
        # Create index.html
        collection_title = args.title or Path(args.input).name.replace('-', ' ').replace('_', ' ').title()
        print("📋 Creating index...")
        index_content = create_index_html(documents_info, output_dir, collection_title)
        index_path = output_dir / 'index.html'
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print("✅ Created: index.html")
        
        # Summary
        total_size = sum(os.path.getsize(output_dir / doc['html_filename']) for doc in documents_info)
        total_size += os.path.getsize(index_path)
        
        print(f"\n🎉 Separate files with index generated successfully!")
        print(f"📄 Files created: {len(documents_info)} documents + 1 index")
        print(f"📄 Total size: {total_size / 1024:.1f} KB")
        print(f"📂 Output directory: {output_dir.absolute()}")
        print(f"🌐 Open {index_path} in your browser to navigate")
        
    elif args.dir:
        # Process directory with combined file (original behavior)
        print("\n📖 Reading markdown files for combined processing...")
        markdown_content, base_name = read_multiple_files(args.input)
        
        if not markdown_content:
            return
        
        # Convert to HTML
        print("\n🔄 Converting markdown to HTML...")
        html_content = simple_markdown_to_html(markdown_content)
        
        # Determine title and output file path
        title = args.title or base_name.replace('-', ' ').replace('_', ' ').title()
        output_file = output_dir / f"{base_name}.html"
        
        print(f"📁 Output directory: {output_dir.absolute()}")
        print(f"📄 Output file: {output_file.name}")
        
        # Create complete HTML document
        include_toc = not args.no_toc
        complete_html = create_html_document(html_content, title, include_toc)
        
        # Save HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(complete_html)
        
        file_size = os.path.getsize(output_file) / 1024
        
        print(f"\n✅ Combined HTML file generated successfully: {output_file}")
        print(f"📄 File size: {file_size:.1f} KB")
        print(f"📑 Title: {title}")
        print(f"📑 Table of Contents: {'Included' if include_toc else 'Disabled'}")
        
    else:
        # Process single file (original behavior)
        print("\n📖 Reading markdown file...")
        markdown_content, base_name = read_single_file(args.input)
        
        if not markdown_content:
            return
        
        # Convert to HTML
        print("\n🔄 Converting markdown to HTML...")
        html_content = simple_markdown_to_html(markdown_content)
        
        # Determine title and output file path
        title = args.title or base_name.replace('-', ' ').replace('_', ' ').title()
        
        if args.output and Path(args.output).suffix == '.html':
            output_file = Path(args.output)
        else:
            output_file = output_dir / f"{base_name}.html"
        
        print(f"📁 Output directory: {output_dir.absolute()}")
        print(f"📄 Output file: {output_file.name}")
        
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
    print("5. Save as PDF")

if __name__ == "__main__":
    main()
