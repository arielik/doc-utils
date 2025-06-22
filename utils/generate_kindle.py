#!/usr/bin/env python3
"""
Flexible script to generate Kindle-ready EPUB documents from markdown files.
Can handle single files or multiple files from a directory.

Requirements:
    pip install ebooklib lxml

EPUB vs MOBI:
    - EPUB is the modern standard supported by newer Kindles and most e-readers
    - MOBI is the legacy format (Amazon has deprecated it in favor of EPUB)
    - This script generates EPUB files which work on all modern Kindles

Usage Examples:
    # Single file
    python3 generate_kindle.py docs/INTRO.md
    
    # Single file with custom title and author
    python3 generate_kindle.py docs/INTRO.md --title "My Book" --author "John Doe"
    
    # Directory of files
    python3 generate_kindle.py --dir docs/patents
    
    # Directory with custom output location
    python3 generate_kindle.py --dir docs/implementation-guidelines --output ./ebooks --title "Implementation Guide"
    
Transfer to Kindle:
    1. Email: Send the .epub file to your Kindle email address (find it in Amazon account settings)
    2. USB: Connect Kindle to computer and copy file to Documents folder
    3. Send to Kindle app: Use Amazon's desktop/mobile app
    4. Cloud: Some newer Kindles support direct upload via web interface
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from ebooklib import epub
import uuid

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

def extract_title_from_content(content):
    """Extract the first heading as title"""
    match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Document"

def extract_headers_for_toc(content):
    """Extract headers for table of contents"""
    headers = []
    lines = content.split('\n')
    
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            anchor_id = create_anchor_id(title)
            headers.append((level, title, anchor_id))
    
    return headers

def create_kindle_styles():
    """Create CSS styles optimized for Kindle"""
    return """
/* Kindle-optimized CSS */
body {
    font-family: "Bookerly", "Times New Roman", serif;
    font-size: 1em;
    line-height: 1.6;
    margin: 1em;
    text-align: justify;
}

h1, h2, h3, h4, h5, h6 {
    font-family: "Amazon Ember", "Helvetica Neue", sans-serif;
    font-weight: bold;
    color: #000;
    page-break-after: avoid;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h1 {
    font-size: 1.8em;
    text-align: center;
    page-break-before: always;
}

h2 {
    font-size: 1.5em;
    border-bottom: 2px solid #333;
    padding-bottom: 0.3em;
}

h3 {
    font-size: 1.3em;
    color: #555;
}

h4 {
    font-size: 1.1em;
    color: #666;
}

h5, h6 {
    font-size: 1em;
    color: #777;
}

p {
    margin: 1em 0;
    text-indent: 1.5em;
}

p:first-child, 
h1 + p, h2 + p, h3 + p, h4 + p, h5 + p, h6 + p,
blockquote p,
li p {
    text-indent: 0;
}

code {
    font-family: "Courier New", monospace;
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 0.9em;
}

pre {
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 1em;
    overflow-x: auto;
    page-break-inside: avoid;
    margin: 1em 0;
}

pre code {
    background: none;
    padding: 0;
    border-radius: 0;
}

blockquote {
    border-left: 4px solid #ccc;
    margin: 1em 0;
    padding-left: 1em;
    color: #666;
    font-style: italic;
}

ul, ol {
    margin: 1em 0;
    padding-left: 2em;
}

li {
    margin: 0.5em 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
    vertical-align: top;
}

th {
    background-color: #f2f2f2;
    font-weight: bold;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 2em 0;
}

a {
    color: #0066cc;
    text-decoration: underline;
}

strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

.toc {
    page-break-after: always;
}

.toc h2 {
    text-align: center;
    border-bottom: none;
}

.toc ol {
    list-style-type: none;
    padding-left: 0;
}

.toc li {
    margin: 0.5em 0;
    padding-left: 1em;
    text-indent: -1em;
}

.toc a {
    text-decoration: none;
    color: #333;
}

.toc .level-1 { font-weight: bold; }
.toc .level-2 { padding-left: 1em; }
.toc .level-3 { padding-left: 2em; }
.toc .level-4 { padding-left: 3em; }

.chapter-break {
    page-break-before: always;
}

@media amzn-mobi {
    /* Mobi-specific styles */
    body { 
        font-size: medium;
        line-height: 1.4;
    }
}

@media amzn-kf8 {
    /* KF8-specific styles */
    body {
        font-size: 1em;
        line-height: 1.6;
    }
}
"""

def create_epub_book(markdown_files, output_filename, book_title=None, author="Generated Document"):
    """Create an EPUB book from markdown files"""
    
    # Create the book
    book = epub.EpubBook()
    
    # Set book metadata
    book_title = book_title or f"Generated Book - {datetime.now().strftime('%Y-%m-%d')}"
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(book_title)
    book.set_language('en')
    book.add_author(author)
    book.add_metadata('DC', 'description', 'Generated from markdown files')
    book.add_metadata('DC', 'publisher', 'Markdown to EPUB Converter')
    book.add_metadata('DC', 'date', datetime.now().isoformat())
    
    # Add CSS style
    style = epub.EpubItem(
        uid="style_default",
        file_name="style/default.css",
        media_type="text/css",
        content=create_kindle_styles()
    )
    book.add_item(style)
    
    # Process markdown files
    chapters = []
    
    for i, (file_path, content) in enumerate(markdown_files):
        if not content or len(content.strip()) < 10:  # Allow very short content but not completely empty
            print(f"⚠️  Skipping empty or very short file: {file_path}")
            continue
            
        print(f"📝 Processing chapter {i+1}: {Path(file_path).name} ({len(content)} chars)")
            
        # Extract title from content or filename
        chapter_title = extract_title_from_content(content)
        if chapter_title == "Document":
            chapter_title = Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()
        
        print(f"📑 Chapter title: {chapter_title}")
        
        # Convert markdown to HTML
        html_content = simple_markdown_to_html(content)
        
        # Ensure the HTML content is not empty and properly formatted
        if not html_content or html_content.strip() == "":
            html_content = f"<h1>{chapter_title}</h1><p>Content could not be processed.</p>"
        
        print(f"🔄 Converted to HTML ({len(html_content)} chars)")
        
        # Create chapter HTML with proper structure
        escaped_title = escape_html(chapter_title)
        chapter_html = f"""<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.1//EN' 'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd'>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{escaped_title}</title>
    <link href="style/default.css" type="text/css" rel="stylesheet"/>
</head>
<body>
    <div class="chapter">
        {html_content}
    </div>
</body>
</html>"""
        
        # Create chapter
        chapter_filename = f"chapter_{i+1:02d}.xhtml"
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=chapter_filename,
            lang='en'
        )
        
        # Set content with proper encoding
        chapter.set_content(chapter_html.encode('utf-8'))
        chapter.add_item(style)
        
        book.add_item(chapter)
        chapters.append(chapter)
    
    if not chapters:
        raise ValueError(f"No valid chapters were created from {len(markdown_files)} input files")
    
    print(f"📚 Created {len(chapters)} chapters")
    
    # Set up the table of contents using the chapters directly
    book.toc = chapters
    
    # Add only NCX navigation (disable EpubNav which is causing issues)
    book.add_item(epub.EpubNcx())
    
    # Create simple spine with just chapters
    book.spine = chapters
    
    # Save the book with proper error handling
    try:
        epub.write_epub(output_filename, book, {})
        print(f"✅ Successfully wrote EPUB file: {output_filename}")
    except Exception as e:
        print(f"❌ Error writing EPUB file: {e}")
        raise
    
    return output_filename

def create_toc_html(all_headers):
    """Create HTML for table of contents"""
    toc_html = ['<div class="toc">', '<h2>Table of Contents</h2>', '<ol>']
    
    for chapter_title, file_path, headers in all_headers:
        toc_html.append(f'<li class="level-1"><strong>{chapter_title}</strong></li>')
        
        for level, title, anchor_id in headers:
            if level <= 4:  # Only include up to h4 in TOC
                indent_class = f"level-{level}"
                toc_html.append(f'<li class="{indent_class}"><a href="#{anchor_id}">{title}</a></li>')
    
    toc_html.extend(['</ol>', '</div>'])
    return '\n'.join(toc_html)

def process_single_file(file_path, output_dir=None, title=None, author="Generated Document"):
    """Process a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content or len(content.strip()) < 10:
            print(f"❌ Error: File appears to be empty or too short: {file_path}")
            print(f"   Content length: {len(content)} characters")
            return None
        
        print(f"📖 Processing file: {file_path} ({len(content)} characters)")
        
        # Determine output filename
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            epub_filename = output_dir / f"{Path(file_path).stem}.epub"
        else:
            epub_filename = Path(file_path).with_suffix('.epub')
        
        # Extract title if not provided
        if not title:
            title = extract_title_from_content(content)
            if title == "Document":
                title = Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()
        
        # Create EPUB
        markdown_files = [(file_path, content)]
        output_file = create_epub_book(markdown_files, epub_filename, title, author)
        
        print(f"✅ Generated EPUB: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def process_directory(dir_path, output_dir=None, title=None, author="Generated Document"):
    """Process all markdown files in a directory"""
    dir_path = Path(dir_path)
    
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"❌ Directory not found: {dir_path}")
        return None
    
    # Find all markdown files
    markdown_files = []
    for pattern in ['*.md', '*.markdown']:
        markdown_files.extend(dir_path.glob(pattern))
    
    if not markdown_files:
        print(f"❌ No markdown files found in {dir_path}")
        return None
    
    # Sort files for consistent ordering
    markdown_files.sort()
    
    # Read all files
    file_contents = []
    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_contents.append((str(file_path), content))
                print(f"📖 Reading: {file_path.name}")
        except Exception as e:
            print(f"⚠️  Warning: Could not read {file_path}: {e}")
    
    if not file_contents:
        print("❌ No valid markdown files could be read")
        return None
    
    # Determine output filename
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        epub_filename = output_dir / f"{dir_path.name}.epub"
    else:
        epub_filename = dir_path / f"{dir_path.name}.epub"
    
    # Extract title if not provided
    if not title:
        title = dir_path.name.replace('-', ' ').replace('_', ' ').title()
    
    # Create EPUB
    output_file = create_epub_book(file_contents, epub_filename, title, author)
    
    print(f"✅ Generated EPUB: {output_file}")
    print(f"📚 Included {len(file_contents)} markdown files")
    return output_file

def main():
    parser = argparse.ArgumentParser(
        description='Generate Kindle-ready EPUB documents from markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s docs/README.md
  %(prog)s docs/README.md --title "My Book" --author "John Doe"
  %(prog)s --dir docs/patents --title "Patent Documentation"
  %(prog)s --dir docs --output ./ebooks --author "Technical Team"

Transfer to Kindle:
  • Email the .epub file to your Kindle email address
  • Copy via USB to Kindle's Documents folder  
  • Use Amazon's Send to Kindle app or website
        """
    )
    parser.add_argument('input', nargs='?', help='Input markdown file or use --dir for directory')
    parser.add_argument('--dir', help='Process all markdown files in directory')
    parser.add_argument('--output', help='Output directory (default: same as input)')
    parser.add_argument('--title', help='Book title (default: extracted from content or filename)')
    parser.add_argument('--author', default='Generated Document', help='Book author (default: "Generated Document")')
    parser.add_argument('--version', action='version', version='Kindle Generator 1.0')
    
    args = parser.parse_args()
    
    if not args.input and not args.dir:
        parser.print_help()
        print(f"\n📱 Kindle EPUB Generator - Convert markdown to Kindle-ready books")
        print(f"💡 Tip: Start with a single file to test: python3 {sys.argv[0]} your-file.md")
        sys.exit(1)
    
    # Show what we're doing
    if args.dir:
        print(f"📚 Processing directory: {args.dir}")
        print(f"📖 Book title: {args.title or 'Auto-detected'}")
        print(f"✍️  Author: {args.author}")
        if args.output:
            print(f"💾 Output directory: {args.output}")
        print()
    else:
        print(f"📄 Processing file: {args.input}")
        print(f"📖 Book title: {args.title or 'Auto-detected'}")
        print(f"✍️  Author: {args.author}")
        if args.output:
            print(f"💾 Output directory: {args.output}")
        print()
    
    if args.dir:
        # Process directory
        result = process_directory(args.dir, args.output, args.title, args.author)
    else:
        # Process single file
        if not os.path.exists(args.input):
            print(f"❌ File not found: {args.input}")
            sys.exit(1)
        result = process_single_file(args.input, args.output, args.title, args.author)
    
    if result:
        print(f"\n🎉 Success! EPUB file created: {result}")
        print(f"📱 This file can be transferred to Kindle via:")
        print(f"   • Email to your Kindle email address")
        print(f"   • USB transfer to Kindle device")
        print(f"   • Amazon's Send to Kindle app")
        print(f"   • Kindle Cloud Reader (for some devices)")
        
        # Show file size
        try:
            file_size = os.path.getsize(result)
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{file_size / 1024:.1f} KB"
            print(f"   • File size: {size_str}")
        except:
            pass
            
    else:
        print("\n❌ Failed to generate EPUB file")
        sys.exit(1)

if __name__ == "__main__":
    main()
