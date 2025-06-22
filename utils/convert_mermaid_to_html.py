#!/usr/bin/env python3
"""
Mermaid Diagram to HTML Converter

This script converts Mermaid diagrams from markdown files to standalone HTML files
that can be viewed in web browsers. It uses the Mermaid.js library to render diagrams.

Requirements:
    No external Python dependencies required - uses built-in libraries only.
    Browsers with JavaScript support to render Mermaid diagrams.

Usage:
    python3 convert_mermaid_to_html.py input_folder output_folder
    
    # Example:
    python3 convert_mermaid_to_html.py docs/patents/diagrams/mermaid docs/patents/diagrams/html

Features:
    - Extracts Mermaid diagrams from markdown files
    - Creates responsive HTML pages with embedded Mermaid.js
    - Adds professional styling and navigation
    - Generates an index page for all diagrams
    - Supports all Mermaid diagram types (flowchart, sequence, etc.)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

def extract_mermaid_from_markdown(markdown_content):
    """Extract mermaid diagram content from markdown"""
    patterns = [
        r'```mermaid\n(.*?)\n```',  # Standard mermaid code block
        r'```mermaid\r?\n(.*?)\r?\n```'  # Handle different line endings
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, markdown_content, re.DOTALL)
        if matches:
            return matches
    
    return []

def extract_title_from_markdown(markdown_content):
    """Extract title from markdown file"""
    lines = markdown_content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Mermaid Diagram"

def create_html_template(title, mermaid_diagrams, source_file):
    """Create HTML template with Mermaid.js integration"""
    
    # Generate diagram sections
    diagram_sections = []
    for i, diagram in enumerate(mermaid_diagrams):
        diagram_id = f"diagram-{i+1}"
        diagram_sections.append(f'''
        <div class="diagram-container">
            <h2>Diagram {i+1}</h2>
            <div class="mermaid-wrapper">
                <div class="mermaid" id="{diagram_id}">
{diagram.strip()}
                </div>
            </div>
        </div>
        ''')
    
    diagram_content = '\n'.join(diagram_sections)
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        /* Modern, professional styling */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .header .source {{
            font-size: 0.9em;
            opacity: 0.7;
            font-style: italic;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .diagram-container {{
            margin-bottom: 50px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }}
        
        .diagram-container h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .mermaid-wrapper {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            overflow-x: auto;
        }}
        
        .mermaid {{
            text-align: center;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Mermaid diagram styling */
        .mermaid svg {{
            max-width: 100%;
            height: auto;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        
        .navigation {{
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .nav-button {{
            display: inline-block;
            padding: 12px 24px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 0 10px;
            transition: background-color 0.3s ease;
        }}
        
        .nav-button:hover {{
            background: #2980b9;
        }}
        
        .diagram-count {{
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: 10px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 8px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .diagram-container {{
                padding: 20px;
                margin-bottom: 30px;
            }}
        }}
        
        /* Print styles */
        @media print {{
            body {{
                background: white;
            }}
            
            .container {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
            
            .nav-button {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">Interactive Mermaid Diagrams</div>
            <div class="source">Source: {source_file}</div>
            <span class="diagram-count">{len(mermaid_diagrams)} Diagram{'s' if len(mermaid_diagrams) != 1 else ''}</span>
        </div>
        
        <div class="content">
            <div class="navigation">
                <a href="index.html" class="nav-button">📋 All Diagrams</a>
                <a href="#" onclick="window.print()" class="nav-button">🖨️ Print</a>
                <a href="#" onclick="location.reload()" class="nav-button">🔄 Refresh</a>
            </div>
            
            {diagram_content}
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
            <p>Powered by <a href="https://mermaid.js.org/" target="_blank">Mermaid.js</a></p>
        </div>
    </div>

    <script>
        // Initialize Mermaid with custom configuration
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                primaryColor: '#3498db',
                primaryTextColor: '#2c3e50',
                primaryBorderColor: '#2980b9',
                lineColor: '#34495e',
                sectionBkgColor: '#ecf0f1',
                altSectionBkgColor: '#ffffff',
                gridColor: '#95a5a6',
                secondaryColor: '#e74c3c',
                tertiaryColor: '#f39c12'
            }},
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            sequence: {{
                useMaxWidth: true,
                diagramMarginX: 50,
                diagramMarginY: 10
            }},
            gantt: {{
                useMaxWidth: true,
                gridLineStartPadding: 350,
                fontSize: 12
            }}
        }});
        
        // Error handling for failed diagram renders
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                const diagrams = document.querySelectorAll('.mermaid');
                diagrams.forEach(function(diagram, index) {{
                    if (diagram.innerHTML.trim() && !diagram.querySelector('svg')) {{
                        diagram.innerHTML = '<div style="padding: 20px; text-align: center; color: #e74c3c; border: 2px dashed #e74c3c; border-radius: 8px;">' +
                                          '<h3>⚠️ Diagram Render Error</h3>' +
                                          '<p>Unable to render this Mermaid diagram. Please check the syntax.</p>' +
                                          '<details style="margin-top: 10px; text-align: left;">' +
                                          '<summary style="cursor: pointer;">Show Raw Diagram Code</summary>' +
                                          '<pre style="background: #f8f9fa; padding: 10px; margin-top: 10px; border-radius: 4px; font-size: 12px;">' + 
                                          diagram.getAttribute('data-original') + '</pre>' +
                                          '</details></div>';
                    }}
                }});
            }}, 2000);
        }});
    </script>
</body>
</html>'''
    
    return html_template

def create_index_html(output_folder, converted_files):
    """Create an index page listing all converted diagrams"""
    
    file_links = []
    for file_info in converted_files:
        filename = file_info['filename']
        title = file_info['title']
        diagram_count = file_info['diagram_count']
        source = file_info['source']
        
        file_links.append(f'''
        <div class="diagram-card">
            <h3><a href="{filename}">{title}</a></h3>
            <div class="diagram-info">
                <span class="diagram-count">{diagram_count} diagram{'s' if diagram_count != 1 else ''}</span>
                <span class="source-file">Source: {source}</span>
            </div>
            <p class="diagram-description">Interactive Mermaid diagram visualization</p>
            <div class="card-actions">
                <a href="{filename}" class="view-button">View Diagrams</a>
            </div>
        </div>
        ''')
    
    file_list = '\n'.join(file_links)
    
    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagrams Index</title>
    <style>
        /* Modern index page styling */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .diagram-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .diagram-card {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #e9ecef;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .diagram-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .diagram-card h3 {{
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .diagram-card h3 a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        
        .diagram-card h3 a:hover {{
            color: #3498db;
        }}
        
        .diagram-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-size: 0.9em;
        }}
        
        .diagram-count {{
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
        }}
        
        .source-file {{
            color: #6c757d;
            font-style: italic;
        }}
        
        .diagram-description {{
            color: #6c757d;
            margin-bottom: 20px;
            font-size: 0.95em;
        }}
        
        .card-actions {{
            text-align: right;
        }}
        
        .view-button {{
            display: inline-block;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            transition: background-color 0.3s ease;
            font-size: 0.9em;
        }}
        
        .view-button:hover {{
            background: #2980b9;
        }}
        
        .summary {{
            text-align: center;
            padding: 30px;
            background: #e8f4fd;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        
        .summary h2 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .summary .stats {{
            font-size: 1.1em;
            color: #34495e;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        
        @media (max-width: 768px) {{
            .diagram-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
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
            <h1>📊 Mermaid Diagrams</h1>
            <div class="subtitle">Interactive Diagram Collection</div>
        </div>
        
        <div class="content">
            <div class="summary">
                <h2>Diagram Collection Summary</h2>
                <div class="stats">
                    <strong>{len(converted_files)}</strong> diagram files • 
                    <strong>{sum(f['diagram_count'] for f in converted_files)}</strong> total diagrams
                </div>
            </div>
            
            <div class="diagram-grid">
                {file_list}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
            <p>Powered by <a href="https://mermaid.js.org/" target="_blank">Mermaid.js</a></p>
        </div>
    </div>
</body>
</html>'''
    
    return index_html

def convert_mermaid_files(input_folder, output_folder):
    """Convert all mermaid files in input folder to HTML in output folder"""
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        print(f"❌ Error: Input folder '{input_folder}' does not exist")
        return False
    
    # Find all markdown files
    markdown_files = list(input_path.glob("*.md"))
    
    if not markdown_files:
        print(f"❌ No markdown files found in '{input_folder}'")
        return False
    
    print(f"🔍 Found {len(markdown_files)} markdown files")
    
    converted_files = []
    total_diagrams = 0
    
    for md_file in markdown_files:
        print(f"📖 Processing: {md_file.name}")
        
        try:
            # Read markdown file
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract mermaid diagrams
            mermaid_diagrams = extract_mermaid_from_markdown(content)
            
            if not mermaid_diagrams:
                print(f"⚠️  No Mermaid diagrams found in {md_file.name}")
                continue
            
            # Extract title
            title = extract_title_from_markdown(content)
            
            print(f"✨ Found {len(mermaid_diagrams)} diagram(s) in {md_file.name}")
            
            # Create HTML content
            html_content = create_html_template(title, mermaid_diagrams, md_file.name)
            
            # Write HTML file
            output_file = output_path / f"{md_file.stem}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Created: {output_file.name}")
            
            # Track conversion info
            converted_files.append({
                'filename': output_file.name,
                'title': title,
                'diagram_count': len(mermaid_diagrams),
                'source': md_file.name
            })
            
            total_diagrams += len(mermaid_diagrams)
            
        except Exception as e:
            print(f"❌ Error processing {md_file.name}: {e}")
            continue
    
    if converted_files:
        # Create index page
        index_content = create_index_html(output_folder, converted_files)
        index_file = output_path / "index.html"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"📋 Created index: {index_file.name}")
        
        print(f"\n🎉 Conversion complete!")
        print(f"📊 Summary:")
        print(f"   • {len(converted_files)} files converted")
        print(f"   • {total_diagrams} diagrams processed")
        print(f"   • Output folder: {output_folder}")
        print(f"   • Open {output_path}/index.html in your browser")
        
        return True
    else:
        print("❌ No files were successfully converted")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Convert Mermaid diagrams from markdown files to interactive HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s docs/diagrams/mermaid docs/diagrams/html
  %(prog)s input_folder output_folder

Features:
  • Extracts Mermaid diagrams from markdown files
  • Creates responsive HTML pages with Mermaid.js
  • Generates navigation index page
  • Professional styling and error handling
  • Print-friendly layouts
        """
    )
    
    parser.add_argument('input_folder', help='Input folder containing markdown files with Mermaid diagrams')
    parser.add_argument('output_folder', help='Output folder for generated HTML files')
    parser.add_argument('--version', action='version', version='Mermaid to HTML Converter 1.0')
    
    args = parser.parse_args()
    
    print("🚀 Mermaid to HTML Converter")
    print(f"📂 Input:  {args.input_folder}")
    print(f"📂 Output: {args.output_folder}")
    print()
    
    success = convert_mermaid_files(args.input_folder, args.output_folder)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
