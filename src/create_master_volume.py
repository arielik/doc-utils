#!/usr/bin/env python3
"""
Master Volume Generator

This script creates a unified master document by combining multiple markdown files
from a folder, generating both an EPUB (Kindle) version and an HTML version.

Features:
- Automatically organizes chapters in a logical sequence
- Generates a table of contents
- Creates both EPUB and HTML outputs
- Customizable title, author, and metadata
- Preserves chapter structure and formatting
- Supports custom chapter ordering and filtering

Requirements:
    pip install ebooklib lxml

Usage:
    python3 create_master_volume.py --dir <chapters_folder> [options]

Options:
    --title       Title for the master volume
    --author      Author name
    --output      Output directory for generated files
    --prefix      Only include files with this prefix (e.g., "chapter-")
    --order-file  Path to a file listing chapter filenames in desired order
    --html-only   Generate only HTML output (no EPUB)
    --epub-only   Generate only EPUB output (no HTML)
    
Example:
    python3 create_master_volume.py --dir docs/book-chapters --title "My Complete Guide" --author "John Smith"
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
import uuid

# Import shared functions from generate_kindle.py
try:
    from generate_kindle import (
        simple_markdown_to_html,
        create_anchor_id,
        escape_html,
        wrap_list_items,
        is_html_block,
        contains_block_elements,
        convert_tables,
        extract_title_from_content,
        create_kindle_styles,
        create_epub_book
    )
except ImportError:
    print("❌ Error: Could not import functions from generate_kindle.py")
    print("   Make sure generate_kindle.py is in the same directory")
    sys.exit(1)


def generate_html_master_volume(markdown_files, output_file, title, author):
    """Generate a master HTML file from multiple markdown files"""
    
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        f'<title>{escape_html(title)}</title>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<meta name="author" content="{escape_html(author)}">',
        '<style>',
        create_kindle_styles(),
        # Additional HTML-specific styling
        '''
        /* Additional HTML-specific styles */
        body {
            max-width: 900px;
            margin: 0 auto;
            padding: 2em;
            font-family: "Bookerly", Georgia, serif;
        }
        
        .toc-link {
            display: block;
            margin-top: 1.5em;
        }
        
        .chapter-title {
            margin-top: 3em;
            padding-top: 1em;
            border-top: 1px solid #ccc;
        }
        
        .chapter:first-child .chapter-title {
            border-top: none;
        }
        
        #table-of-contents {
            background-color: #f9f9f9;
            padding: 1em;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 2em;
        }
        
        #table-of-contents h2 {
            margin-top: 0;
        }
        
        @media print {
            body {
                font-size: 12pt;
                max-width: none;
                padding: 1em;
            }
            
            a {
                color: #000;
                text-decoration: none;
            }
            
            .chapter {
                page-break-before: always;
            }
            
            .chapter:first-child {
                page-break-before: avoid;
            }
        }
        ''',
        '</style>',
        '</head>',
        '<body>',
        f'<h1 id="title">{escape_html(title)}</h1>',
        f'<p class="author">by {escape_html(author)}</p>',
    ]
    
    # Collect all headers for the table of contents
    all_headers = []
    toc_entries = []
    
    # Process files and collect headers
    for i, (file_path, content) in enumerate(markdown_files):
        # Extract title from content or filename
        chapter_title = extract_title_from_content(content)
        if chapter_title == "Document":
            chapter_title = Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()
        
        # Extract headers for TOC
        headers = []
        lines = content.split('\n')
        for line in lines:
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                anchor_id = f"chapter-{i+1}-{create_anchor_id(title)}"
                headers.append((level, title, anchor_id))
        
        all_headers.append((chapter_title, str(file_path), headers))
        
        # Create TOC entry
        chapter_anchor = f"chapter-{i+1}"
        toc_entries.append((1, chapter_title, chapter_anchor))
        
        # Add nested headers to TOC 
        for level, title, anchor_id in headers:
            if level > 1 and level <= 3:  # Only include h2 and h3 in TOC
                toc_entries.append((level, title, anchor_id))
    
    # Generate table of contents
    html_parts.append('<div id="table-of-contents">')
    html_parts.append('<h2>Table of Contents</h2>')
    html_parts.append('<ul>')
    
    current_level = 1
    list_stack = [1]  # Start with the main list level
    
    for level, title, anchor_id in toc_entries:
        # Handle list nesting
        while level > current_level:
            html_parts.append('<ul>')
            list_stack.append(current_level)
            current_level += 1
        
        while level < current_level:
            html_parts.append('</ul>')
            current_level = list_stack.pop()
        
        html_parts.append(f'<li><a href="#{anchor_id}">{escape_html(title)}</a></li>')
    
    # Close any remaining lists
    while len(list_stack) > 0:
        html_parts.append('</ul>')
        list_stack.pop()
    
    html_parts.append('</div>')  # End table of contents
    
    # Process each file and add content
    for i, (file_path, content) in enumerate(markdown_files):
        # Extract title
        chapter_title = extract_title_from_content(content)
        if chapter_title == "Document":
            chapter_title = Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()
        
        # Start new chapter
        chapter_anchor = f"chapter-{i+1}"
        html_parts.append(f'<div class="chapter" id="{chapter_anchor}">')
        
        # Replace h1 headings with h2 to maintain hierarchy
        content_modified = re.sub(r'^# (.+)$', '', content, flags=re.MULTILINE, count=1)
        content_modified = re.sub(r'^# (.+)$', r'## \1', content_modified, flags=re.MULTILINE)
        
        # Add chapter heading
        html_parts.append(f'<h1 class="chapter-title">{escape_html(chapter_title)}</h1>')
        
        # Convert the content to HTML
        chapter_html = simple_markdown_to_html(content_modified)
        
        # Fix anchor IDs to be chapter-specific
        for level, title, anchor_id in all_headers[i][2]:
            old_id = create_anchor_id(title)
            new_id = f"chapter-{i+1}-{old_id}"
            chapter_html = chapter_html.replace(f'id="{old_id}"', f'id="{new_id}"')
        
        html_parts.append(chapter_html)
        html_parts.append('</div>')  # End chapter div
        
        # Add back-to-top link
        html_parts.append('<p><a href="#table-of-contents" class="toc-link">↑ Back to Table of Contents</a></p>')
    
    # Add footer
    html_parts.append('<footer>')
    html_parts.append(f'<p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>')
    html_parts.append('</footer>')
    
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    # Write the final HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    
    print(f"✅ Generated HTML master volume: {output_file}")
    return output_file


def read_order_file(order_file_path):
    """Read a file containing chapter filenames in the desired order"""
    try:
        with open(order_file_path, 'r', encoding='utf-8') as f:
            # Remove whitespace and empty lines
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines
    except Exception as e:
        print(f"❌ Error reading order file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Create a master volume from a folder of markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dir docs/chapters --title "Complete Guide"
  %(prog)s --dir docs/book --output ./published --title "My Book" --author "Jane Doe"
  %(prog)s --dir manuscript --prefix "chapter-" --order-file chapter-order.txt
  %(prog)s --dir course-notes --html-only --title "Course Materials"
        """
    )
    parser.add_argument('--dir', required=True, help='Directory containing markdown chapter files')
    parser.add_argument('--output', help='Output directory (default: same as input directory)')
    parser.add_argument('--title', help='Master volume title (default: directory name)')
    parser.add_argument('--author', default='Generated Document', help='Author name')
    parser.add_argument('--prefix', help='Only include files with this prefix')
    parser.add_argument('--order-file', help='File containing chapter filenames in desired order')
    parser.add_argument('--html-only', action='store_true', help='Generate only HTML output')
    parser.add_argument('--epub-only', action='store_true', help='Generate only EPUB output')
    parser.add_argument('--version', action='version', version='Master Volume Generator 1.0')
    
    args = parser.parse_args()
    
    # Validate directory
    dir_path = Path(args.dir)
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"❌ Directory not found: {dir_path}")
        sys.exit(1)
    
    # Set output directory
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True, parents=True)
    else:
        output_dir = dir_path
    
    # Set title
    title = args.title or dir_path.name.replace('-', ' ').replace('_', ' ').title()
    
    print(f"📚 Creating master volume from: {dir_path}")
    print(f"📊 Title: {title}")
    print(f"✍️  Author: {args.author}")
    
    # Find all markdown files
    markdown_files = []
    for pattern in ['*.md', '*.markdown']:
        files = list(dir_path.glob(pattern))
        if args.prefix:
            # Filter by prefix
            files = [f for f in files if f.name.startswith(args.prefix)]
        markdown_files.extend(files)
    
    if not markdown_files:
        print(f"❌ No markdown files found in {dir_path}" + 
              (f" with prefix '{args.prefix}'" if args.prefix else ""))
        sys.exit(1)
    
    # Use custom ordering if specified
    if args.order_file:
        order_file_path = Path(args.order_file)
        if not order_file_path.exists():
            print(f"❌ Order file not found: {order_file_path}")
            sys.exit(1)
        
        ordered_filenames = read_order_file(order_file_path)
        if ordered_filenames:
            # Map filenames to full paths and filter to include only existing files
            ordered_files = []
            for filename in ordered_filenames:
                matching_files = [f for f in markdown_files if f.name == filename]
                if matching_files:
                    ordered_files.append(matching_files[0])
                else:
                    print(f"⚠️  Warning: File in order list not found: {filename}")
            
            # Add any files that weren't in the order file at the end
            ordered_filenames_set = set(ordered_filenames)
            remaining_files = [f for f in markdown_files if f.name not in ordered_filenames_set]
            
            if remaining_files:
                print(f"ℹ️  {len(remaining_files)} files not in order file will be added at the end")
                ordered_files.extend(sorted(remaining_files))
            
            markdown_files = ordered_files
        else:
            # Fall back to default sorting
            markdown_files.sort()
    else:
        # Default: sort alphabetically
        markdown_files.sort()
    
    print(f"📄 Found {len(markdown_files)} markdown files")
    for i, file_path in enumerate(markdown_files):
        print(f"   {i+1}. {file_path.name}")
    
    # Read all files
    file_contents = []
    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content or len(content.strip()) < 10:
                    print(f"⚠️  Warning: File appears empty or too short: {file_path}")
                    continue
                file_contents.append((str(file_path), content))
        except Exception as e:
            print(f"⚠️  Warning: Could not read {file_path}: {e}")
    
    if not file_contents:
        print("❌ No valid markdown files could be read")
        sys.exit(1)
    
    output_files = []
    
    # Generate HTML output
    if not args.epub_only:
        html_filename = output_dir / f"{title.replace(' ', '_')}.html"
        html_file = generate_html_master_volume(file_contents, html_filename, title, args.author)
        output_files.append(("HTML", html_file))
    
    # Generate EPUB output
    if not args.html_only:
        epub_filename = output_dir / f"{title.replace(' ', '_')}.epub"
        epub_file = create_epub_book(file_contents, epub_filename, title, args.author)
        output_files.append(("EPUB", epub_file))
    
    # Show summary
    print("\n🎉 Master volume creation complete!")
    for file_type, file_path in output_files:
        file_size = Path(file_path).stat().st_size / 1024  # Size in KB
        if file_size > 1024:
            size_str = f"{file_size / 1024:.1f} MB"
        else:
            size_str = f"{file_size:.1f} KB"
        print(f"📄 {file_type} file: {file_path} ({size_str})")


if __name__ == "__main__":
    main()
