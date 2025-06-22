#!/usr/bin/env python3
"""
ASCII Art to HTML Converter
Converts ASCII art diagrams from text or markdown files to academic-style HTML pages.

Usage:
    python convert_ascii_to_html.py <input_folder> <output_folder>
"""

import os
import sys
import re
from pathlib import Path


def extract_title_from_content(content):
    """Extract title from ASCII art content."""
    lines = content.strip().split('\n')
    
    # Look for patterns like "FIGURE X:" or titles in first few lines
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        if re.match(r'^FIGURE\s+\d+:', line, re.IGNORECASE):
            title = line
            # Check if next line has description
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not any(char in next_line for char in '┌┐└┘│─┬┴├┤┼'):
                    title += f" - {next_line}"
            return title
        elif re.match(r'^[A-Z][A-Z\s]+[A-Z]$', line) and len(line) > 10:
            return line
    
    return "ASCII Diagram"


def clean_ascii_content(content):
    """Clean and prepare ASCII content for HTML display."""
    # Remove any markdown code block markers
    content = re.sub(r'^```[\w]*\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n```$', '', content, flags=re.MULTILINE)
    
    # Ensure proper line endings
    lines = content.split('\n')
    
    # Remove excessive empty lines at start and end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    return '\n'.join(lines)


def create_html_from_ascii(ascii_content, title, filename):
    """Create HTML content from ASCII art."""
    
    # Clean the ASCII content
    clean_content = clean_ascii_content(ascii_content)
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Academic paper styling */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            line-height: 1.6;
            color: #000;
            background: #fff;
            padding: 40px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .paper-container {{
            background: white;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            border: 1px solid #ddd;
            margin: 0 auto;
            padding: 60px;
            min-height: calc(100vh - 80px);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
        }}
        
        .header h1 {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            font-style: italic;
            color: #555;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            font-size: 0.9em;
            color: #666;
            margin-top: 15px;
        }}
        
        .figure-container {{
            margin: 40px 0;
            page-break-inside: avoid;
        }}
        
        .figure-title {{
            font-weight: bold;
            font-size: 1.1em;
            text-align: center;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .ascii-diagram {{
            font-family: 'Courier New', 'Lucida Console', monospace;
            font-size: 12px;
            line-height: 1.2;
            background: #fafafa;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 30px;
            margin: 20px 0;
            overflow-x: auto;
            white-space: pre;
            color: #000;
            text-align: left;
        }}
        
        .figure-caption {{
            font-size: 0.95em;
            text-align: center;
            margin-top: 15px;
            font-style: italic;
            color: #555;
            padding: 0 40px;
        }}
        
        .navigation {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
        }}
        
        .nav-link {{
            display: inline-block;
            margin: 0 10px;
            padding: 8px 16px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            text-decoration: none;
            color: #495057;
            font-size: 0.9em;
        }}
        
        .nav-link:hover {{
            background: #e9ecef;
            text-decoration: none;
        }}
        
        /* Print styles */
        @media print {{
            body {{
                font-size: 11pt;
                padding: 0;
            }}
            
            .paper-container {{
                box-shadow: none;
                border: none;
                padding: 40px;
            }}
            
            .navigation {{
                display: none;
            }}
        }}
        
        /* High contrast for better readability */
        @media (prefers-contrast: high) {{
            .ascii-diagram {{
                background: #fff;
                border: 2px solid #000;
            }}
        }}
    </style>
</head>
<body>
    <div class="paper-container">
        <div class="header">
            <h1>Technical Diagram</h1>
            <div class="subtitle">Agentic Infrastructure Intelligence System</div>
            <div class="meta">
                Source: {filename} | Generated: Academic Format
            </div>
        </div>
        
        <div class="figure-container">
            <div class="figure-title">{title}</div>
            <div class="ascii-diagram">{clean_content}</div>
            <div class="figure-caption">
                Technical architecture diagram showing system components and their relationships.
                This figure illustrates the structural organization and data flow patterns
                within the agentic infrastructure intelligence framework.
            </div>
        </div>
        
        <div class="navigation">
            <a href="index.html" class="nav-link">← Back to Index</a>
            <a href="#" onclick="window.print()" class="nav-link">🖨 Print</a>
        </div>
    </div>
</body>
</html>"""
    
    return html_template


def create_index_html(diagrams_info, output_dir):
    """Create an index HTML file for all diagrams."""
    
    index_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASCII Diagrams Index - Academic Collection</title>
    <style>
        /* Academic index styling */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            line-height: 1.6;
            color: #000;
            background: #f5f5f5;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
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
        
        .diagrams-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .diagram-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .diagram-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .diagram-card a {{
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
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 5px;
            color: #2c3e50;
        }}
        
        .card-meta {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .card-preview {{
            padding: 15px;
            background: #fafafa;
            font-family: 'Courier New', monospace;
            font-size: 0.7em;
            line-height: 1.1;
            max-height: 120px;
            overflow: hidden;
            white-space: pre;
            position: relative;
        }}
        
        .card-preview::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30px;
            background: linear-gradient(transparent, #fafafa);
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
        
        @media (max-width: 768px) {{
            .diagrams-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ASCII Diagrams Collection</h1>
            <div class="subtitle">Academic Technical Documentation</div>
        </div>
        
        <div class="content">
            <div class="description">
                Technical diagrams rendered in ASCII format for academic and patent documentation.
                Each diagram provides detailed architectural insights into the Agentic Infrastructure Intelligence System,
                following academic publishing standards for technical illustrations.
            </div>
            
            <div class="diagrams-grid">"""

    # Add each diagram card
    for info in diagrams_info:
        preview_lines = info['content'].split('\n')[:8]  # First 8 lines for preview
        preview = '\n'.join(preview_lines)
        
        index_template += f"""
                <div class="diagram-card">
                    <a href="{info['filename']}">
                        <div class="card-header">
                            <div class="card-title">{info['title']}</div>
                            <div class="card-meta">Source: {info['source_file']}</div>
                        </div>
                        <div class="card-preview">{preview}</div>
                    </a>
                </div>"""

    index_template += f"""
            </div>
            
            <div class="stats">
                <h3>Collection Statistics</h3>
                <div class="stat-item">
                    <span class="stat-number">{len(diagrams_info)}</span>
                    <span class="stat-label">Diagrams</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">ASCII</span>
                    <span class="stat-label">Format</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">Academic</span>
                    <span class="stat-label">Style</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return index_template


def convert_ascii_to_html(input_folder, output_folder):
    """Convert all ASCII art files in input_folder to HTML in output_folder."""
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    if not input_path.exists():
        print(f"❌ Input folder not found: {input_folder}")
        return
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("📚 ASCII Art to HTML Converter - Academic Style")
    print(f"📂 Input:  {input_folder}")
    print(f"📂 Output: {output_folder}")
    print()
    
    # Find all text and markdown files
    ascii_files = []
    for pattern in ['*.txt', '*.md']:
        ascii_files.extend(input_path.glob(pattern))
    
    if not ascii_files:
        print("❌ No ASCII art files found (.txt or .md)")
        return
    
    print(f"🔍 Found {len(ascii_files)} ASCII art files")
    
    diagrams_info = []
    converted_count = 0
    
    for ascii_file in sorted(ascii_files):
        print(f"📖 Processing: {ascii_file.name}")
        
        try:
            # Read the ASCII content
            with open(ascii_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(f"⚠️  Skipping empty file: {ascii_file.name}")
                continue
            
            # Extract title
            title = extract_title_from_content(content)
            print(f"✨ Extracted title: {title}")
            
            # Create HTML filename
            html_filename = ascii_file.stem + '.html'
            html_path = output_path / html_filename
            
            # Generate HTML
            html_content = create_html_from_ascii(content, title, ascii_file.name)
            
            # Write HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Created: {html_filename}")
            
            # Store info for index
            diagrams_info.append({
                'title': title,
                'filename': html_filename,
                'source_file': ascii_file.name,
                'content': content[:1000]  # First 1000 chars for preview
            })
            
            converted_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {ascii_file.name}: {str(e)}")
    
    # Create index.html
    if diagrams_info:
        print("📋 Creating index...")
        index_content = create_index_html(diagrams_info, output_folder)
        index_path = output_path / 'index.html'
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print("✅ Created: index.html")
    
    print()
    print("🎉 Conversion complete!")
    print(f"📊 Summary:")
    print(f"   • {converted_count} files converted")
    print(f"   • {len(diagrams_info)} diagrams processed")
    print(f"   • Output folder: {output_folder}")
    print(f"   • Open {output_folder}/index.html in your browser")


def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_ascii_to_html.py <input_folder> <output_folder>")
        print("Example: python convert_ascii_to_html.py docs/ascii-art docs/ascii-html")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    convert_ascii_to_html(input_folder, output_folder)


if __name__ == "__main__":
    main()
