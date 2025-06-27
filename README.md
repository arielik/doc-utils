# doc-utils

A collection of Python utilities for managing and converting different document types, especially for academic, technical, and patent writing workflows.

## Features
- Convert ASCII art diagrams to HTML
- Convert Mermaid diagrams to standalone HTML
- Generate combined HTML from markdown guidelines
- Flexible markdown-to-HTML conversion (single file or directory)
- Generate Kindle-ready EPUB documents from markdown
- Create master volumes from multiple chapter files (HTML and EPUB)

## Main Utilities
- `convert_ascii_to_html.py`: ASCII art to HTML converter
- `convert_mermaid_to_html.py`: Mermaid diagrams to HTML
- `generate_html.py`: Combine guideline markdowns into one HTML
- `generate_html_flexible.py`: Flexible markdown to HTML
- `generate_kindle.py`: Markdown to EPUB for Kindle
- `create_master_volume.py`: Create unified master volumes from chapter files (both HTML and EPUB)

## Usage
See [`docs/how_to_use.md`](docs/how_to_use.md) for detailed instructions on using each script.

## Requirements
- Python 3.x
- For Kindle EPUB generation: `pip install ebooklib lxml`

## License
See [LICENSE](LICENSE)
