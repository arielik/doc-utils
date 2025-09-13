#!/usr/bin/env python3
"""
Confluence to Markdown Converter

This script downloads a Confluence page and converts it to Markdown format,
including images and attachments, organized in a structured folder.

Requirements:
- requests
- markdownify
- beautifulsoup4

Install with: pip install requests markdownify beautifulsoup4

Usage:
python confluence_to_md.py --url <confluence_page_url> --output <output_folder> [--token <api_token>] [--username <username>] [--password <password>]
"""

import argparse
import os
import sys
import re
import json
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify


class ConfluenceToMarkdown:
    def __init__(self, base_url: str, auth: Optional[Tuple[str, str]] = None, token: Optional[str] = None):
        """
        Initialize the converter.
        
        Args:
            base_url: Base URL of Confluence instance (e.g., https://company.atlassian.net/wiki)
            auth: Tuple of (username, password) for basic auth
            token: API token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        elif auth:
            self.session.auth = auth
        else:
            print("Warning: No authentication provided. Only public pages will be accessible.")
        
        # Set common headers
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def extract_page_info_from_url(self, page_url: str) -> Tuple[str, str]:
        """Extract space key and page ID from Confluence URL."""
        # Handle different Confluence URL formats
        patterns = [
            r'/spaces/([^/]+)/pages/(\d+)',  # New format: /spaces/SPACE/pages/123456
            r'/display/([^/]+)/([^/]+)',     # Old format: /display/SPACE/Page+Title
            r'/pages/viewpage.action\?pageId=(\d+)',  # Direct page ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_url)
            if match:
                if 'pageId=' in pattern:
                    # Direct page ID, need to get space info
                    page_id = match.group(1)
                    space_key = self._get_space_from_page_id(page_id)
                    return space_key, page_id
                elif 'pages/' in pattern:
                    # New format with space key and page ID
                    return match.group(1), match.group(2)
                else:
                    # Old display format, need to resolve to page ID
                    space_key = match.group(1)
                    page_title = urllib.parse.unquote(match.group(2).replace('+', ' '))
                    page_id = self._get_page_id_from_title(space_key, page_title)
                    return space_key, page_id
        
        raise ValueError(f"Could not extract page information from URL: {page_url}")

    def _get_space_from_page_id(self, page_id: str) -> str:
        """Get space key from page ID."""
        url = f"{self.base_url}/rest/api/content/{page_id}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return data['space']['key']

    def _get_page_id_from_title(self, space_key: str, page_title: str) -> str:
        """Get page ID from space key and page title."""
        url = f"{self.base_url}/rest/api/content"
        params = {
            'spaceKey': space_key,
            'title': page_title,
            'expand': 'space'
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data['results']:
            raise ValueError(f"Page not found: {page_title} in space {space_key}")
        
        return data['results'][0]['id']

    def get_page_content(self, page_id: str) -> Dict:
        """Retrieve page content from Confluence API."""
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {
            'expand': 'body.storage,space,version,ancestors'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_page_attachments(self, page_id: str) -> List[Dict]:
        """Get list of attachments for a page."""
        url = f"{self.base_url}/rest/api/content/{page_id}/child/attachment"
        params = {'expand': 'version'}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()['results']

    def download_attachment(self, attachment: Dict, output_dir: Path) -> str:
        """Download an attachment and return the local filename."""
        download_url = self.base_url + attachment['_links']['download']
        filename = attachment['title']
        
        # Sanitize filename
        filename = re.sub(r'[^\w\s-.]', '', filename).strip()
        
        filepath = output_dir / filename
        
        response = self.session.get(download_url)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded attachment: {filename}")
        return filename

    def download_image(self, img_url: str, output_dir: Path, img_name: str) -> str:
        """Download an image and return the local filename."""
        # Handle relative URLs
        if img_url.startswith('/'):
            img_url = self.base_url + img_url
        
        # Sanitize filename
        img_name = re.sub(r'[^\w\s-.]', '', img_name).strip()
        if not img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
            img_name += '.png'  # Default extension
        
        filepath = output_dir / img_name
        
        try:
            response = self.session.get(img_url)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded image: {img_name}")
            return img_name
        except Exception as e:
            print(f"Failed to download image {img_url}: {e}")
            return img_url  # Return original URL if download fails

    def process_images_in_html(self, html_content: str, images_dir: Path) -> str:
        """Process images in HTML content and download them."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        img_counter = 1
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
            
            # Generate a filename for the image
            alt_text = img.get('alt', f'image_{img_counter}')
            img_name = f"{alt_text}_{img_counter}"
            
            # Download the image
            local_filename = self.download_image(src, images_dir, img_name)
            
            # Update the src to point to local file
            img['src'] = f"./images/{local_filename}"
            img_counter += 1
        
        return str(soup)

    def clean_confluence_html(self, html_content: str) -> str:
        """Clean Confluence-specific HTML elements."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove Confluence-specific elements
        for element in soup.find_all(['ac:structured-macro', 'ac:parameter', 'ri:attachment']):
            element.decompose()
        
        # Convert Confluence sections to proper HTML sections
        for section in soup.find_all('ac:layout-section'):
            section.name = 'div'
            section['class'] = 'section'
        
        for column in soup.find_all('ac:layout-cell'):
            column.name = 'div'
            column['class'] = 'column'
        
        return str(soup)

    def convert_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to Markdown."""
        # Configure markdownify options
        markdown_content = markdownify(
            html_content,
            heading_style="ATX",  # Use # for headings
            bullets="-",  # Use - for bullets
            strip=['script', 'style'],  # Remove scripts and styles
            convert=['div', 'span', 'section'],  # Convert these tags
        )
        
        # Clean up the markdown
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)  # Remove excessive newlines
        markdown_content = markdown_content.strip()
        
        return markdown_content

    def create_output_structure(self, output_dir: str) -> Tuple[Path, Path, Path]:
        """Create the output directory structure."""
        base_dir = Path(output_dir)
        base_dir.mkdir(exist_ok=True)
        
        images_dir = base_dir / "images"
        attachments_dir = base_dir / "attachments"
        
        images_dir.mkdir(exist_ok=True)
        attachments_dir.mkdir(exist_ok=True)
        
        return base_dir, images_dir, attachments_dir

    def convert_page(self, page_url: str, output_dir: str):
        """Main method to convert a Confluence page to Markdown."""
        try:
            # Extract page information
            space_key, page_id = self.extract_page_info_from_url(page_url)
            print(f"Processing page ID: {page_id} in space: {space_key}")
            
            # Create output structure
            base_dir, images_dir, attachments_dir = self.create_output_structure(output_dir)
            
            # Get page content
            page_data = self.get_page_content(page_id)
            
            page_title = page_data['title']
            html_content = page_data['body']['storage']['value']
            
            print(f"Converting page: {page_title}")
            
            # Process images in HTML content
            html_content = self.process_images_in_html(html_content, images_dir)
            
            # Clean Confluence-specific HTML
            html_content = self.clean_confluence_html(html_content)
            
            # Convert to Markdown
            markdown_content = self.convert_to_markdown(html_content)
            
            # Add metadata header
            metadata = f"""# {page_title}

**Space:** {space_key}  
**Page ID:** {page_id}  
**Last Updated:** {page_data['version']['when']}  
**Version:** {page_data['version']['number']}

---

"""
            markdown_content = metadata + markdown_content
            
            # Save markdown file
            md_filename = re.sub(r'[^\w\s-]', '', page_title).strip() + '.md'
            md_filepath = base_dir / md_filename
            
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Saved markdown: {md_filepath}")
            
            # Download attachments
            attachments = self.get_page_attachments(page_id)
            if attachments:
                print(f"Found {len(attachments)} attachments")
                for attachment in attachments:
                    self.download_attachment(attachment, attachments_dir)
            
            # Create a summary file
            summary = {
                'page_title': page_title,
                'space_key': space_key,
                'page_id': page_id,
                'page_url': page_url,
                'markdown_file': md_filename,
                'images_count': len(list(images_dir.glob('*'))) if images_dir.exists() else 0,
                'attachments_count': len(attachments),
                'converted_at': page_data['version']['when']
            }
            
            with open(base_dir / 'conversion_summary.json', 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            print(f"\nConversion completed successfully!")
            print(f"Output directory: {base_dir}")
            print(f"Markdown file: {md_filename}")
            print(f"Images: {summary['images_count']}")
            print(f"Attachments: {summary['attachments_count']}")
            
        except Exception as e:
            print(f"Error during conversion: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Convert Confluence page to Markdown')
    parser.add_argument('--url', required=True, help='Confluence page URL')
    parser.add_argument('--output', required=True, help='Output folder name')
    parser.add_argument('--base-url', help='Confluence base URL (if different from page URL)')
    parser.add_argument('--username', help='Confluence username')
    parser.add_argument('--password', help='Confluence password')
    parser.add_argument('--token', help='API token (alternative to username/password)')
    
    args = parser.parse_args()
    
    # Determine base URL
    if args.base_url:
        base_url = args.base_url
    else:
        # Extract base URL from page URL
        parsed_url = urllib.parse.urlparse(args.url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        if '/wiki' in parsed_url.path:
            base_url += '/wiki'
    
    # Setup authentication
    auth = None
    token = args.token
    
    if args.username and args.password:
        auth = (args.username, args.password)
    elif not token:
        print("Warning: No authentication provided. Only public pages will be accessible.")
    
    # Create converter and run
    converter = ConfluenceToMarkdown(base_url, auth, token)
    converter.convert_page(args.url, args.output)


if __name__ == '__main__':
    main()
