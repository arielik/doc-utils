# How to Use the doc-utils Scripts

This document provides usage instructions for each main script in the `src/` directory of the `doc-utils` repository. These utilities help manage and convert various document types for academic, technical, and patent writing workflows.

---

## 1. convert_ascii_to_html.py
**Purpose:** Converts ASCII art diagrams from text or markdown files to academic-style HTML pages.

**Usage:**
```
python convert_ascii_to_html.py <input_folder> <output_folder>
```
- `<input_folder>`: Directory containing text/markdown files with ASCII art diagrams.
- `<output_folder>`: Directory where HTML files will be saved.

---

## 2. convert_mermaid_to_html.py
**Purpose:** Converts Mermaid diagrams from markdown files to standalone HTML files viewable in browsers.

**Usage:**
```
python3 convert_mermaid_to_html.py <input_folder> <output_folder>
```
- `<input_folder>`: Directory with markdown files containing Mermaid diagrams.
- `<output_folder>`: Directory for the generated HTML files.

**Features:**
- Extracts Mermaid diagrams
- Creates responsive HTML with Mermaid.js
- Generates an index page

---

## 3. generate_html.py
**Purpose:** Generates a single HTML file from all implementation guideline markdown files (for easy PDF export via browser).

**Usage:**
```
python3 generate_html.py
```
- Looks for markdown files in `docs/implementation-guidelines/` (in a specific order).
- Outputs a combined HTML file for printing or PDF export.

---

## 4. generate_html_flexible.py
**Purpose:** Flexible script to generate HTML from markdown files (single file or directory).

**Usage:**
```
python3 generate_html_flexible.py <file.md>
python3 generate_html_flexible.py --dir <directory>
```
- `<file.md>`: Convert a single markdown file to HTML.
- `--dir <directory>`: Convert all markdown files in a directory.

---

## 5. generate_kindle.py
**Purpose:** Generates Kindle-ready EPUB documents from markdown files (single file or directory).

**Requirements:**
- Install dependencies: `pip install ebooklib lxml`

**Usage:**
```
# Single file
python3 generate_kindle.py <file.md>

# Single file with custom title/author
python3 generate_kindle.py <file.md> --title "My Book" --author "John Doe"

# Directory
python3 generate_kindle.py --dir <directory>

# Directory with custom output
python3 generate_kindle.py --dir <directory> --output <output_dir> --title "Title"
```

**Transfer to Kindle:**
- Email the .epub file to your Kindle address
- Copy via USB
- Use Amazon's "Send to Kindle" app

---

## 6. create_master_volume.py
**Purpose:** Creates a unified master document by combining multiple markdown files from a folder, generating both HTML and EPUB outputs.

**Requirements:**
- Install dependencies: `pip install ebooklib lxml`

**Usage:**
```
python3 create_master_volume.py --dir <chapters_folder> [options]
```

**Options:**
- `--dir`: Directory containing markdown chapter files (required)
- `--output`: Output directory for generated files
- `--title`: Master volume title (default: directory name)
- `--author`: Author name (default: "Generated Document")
- `--prefix`: Only include files with this prefix (e.g., "chapter-")
- `--order-file`: Path to a file listing chapter filenames in desired order
- `--html-only`: Generate only HTML output (no EPUB)
- `--epub-only`: Generate only EPUB output (no HTML)

**Examples:**
```
# Basic usage
python3 create_master_volume.py --dir docs/chapters --title "Complete Guide"

# Custom output location and author
python3 create_master_volume.py --dir docs/book --output ./published --title "My Book" --author "Jane Doe"

# Custom chapter ordering
python3 create_master_volume.py --dir manuscript --prefix "chapter-" --order-file chapter-order.txt

# Generate only HTML
python3 create_master_volume.py --dir course-notes --html-only --title "Course Materials"
```

**Features:**
- Automatically organizes chapters in sequence
- Creates a navigable table of contents
- Generates both EPUB (for Kindle) and HTML formats
- Supports custom chapter ordering via a text file
- Preserves chapter structure and heading hierarchy

---

For more details, see the script docstrings or run each script with `--help`.
