#!/usr/bin/env python3
"""
VB.NET to C# Translation Web Crawler

This module provides functionality to crawl websites and extract VB.NET to C# 
translation examples for building training datasets.
"""

import json
import re
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from playwright.sync_api import sync_playwright, Page, Browser
import argparse


class TranslationExample:
    """Represents a VB.NET to C# translation example."""
    
    def __init__(self, vb_code: str, csharp_code: str, source_url: str, 
                 title: str = "", description: str = ""):
        self.vb_code = vb_code.strip()
        self.csharp_code = csharp_code.strip()
        self.source_url = source_url
        self.title = title.strip()
        self.description = description.strip()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "vb_code": self.vb_code,
            "csharp_code": self.csharp_code,
            "source_url": self.source_url,
            "title": self.title,
            "description": self.description
        }
    
    def is_valid(self) -> bool:
        """Check if the translation example is valid."""
        return (len(self.vb_code) > 10 and 
                len(self.csharp_code) > 10 and 
                self.vb_code != self.csharp_code)


class WebCrawler:
    """Web crawler for extracting VB.NET to C# translation examples."""
    
    def __init__(self, use_playwright: bool = False, headless: bool = True):
        self.use_playwright = use_playwright
        self.headless = headless
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # Common patterns for VB.NET and C# code
        self.vb_patterns = [
            r'```vb(?:\.net)?\s*\n(.*?)\n```',
            r'<pre><code class="vb(?:\.net)?">(.*?)</code></pre>',
            r'<code class="vb(?:\.net)?">(.*?)</code>',
            r'<pre class="vb(?:\.net)?">(.*?)</pre>',
            r'VB\.NET:\s*\n(.*?)(?=\nC#:|$)',
            r'Visual Basic:\s*\n(.*?)(?=\nC#:|$)'
        ]
        
        self.csharp_patterns = [
            r'```csharp\s*\n(.*?)\n```',
            r'```cs\s*\n(.*?)\n```',
            r'<pre><code class="csharp">(.*?)</code></pre>',
            r'<code class="csharp">(.*?)</code>',
            r'<pre class="csharp">(.*?)</pre>',
            r'C#:\s*\n(.*?)(?=\nVB\.NET:|$)'
        ]
        
        # Keywords that suggest translation content
        self.translation_keywords = [
            'vb.net', 'visual basic', 'c#', 'csharp', 'translation', 'convert',
            'equivalent', 'comparison', 'migration', 'port'
        ]
    
    def __enter__(self):
        if self.use_playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        self.session.close()
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Get page content using either requests or Playwright."""
        try:
            if self.use_playwright:
                self.page.goto(url, wait_until='networkidle', timeout=30000)
                return self.page.content()
            else:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logging.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_code_blocks(self, html_content: str) -> Tuple[List[str], List[str]]:
        """Extract VB.NET and C# code blocks from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        vb_blocks = []
        csharp_blocks = []
        
        # First try to extract from table-based layouts (older HTML format)
        table_vb, table_cs = self._extract_from_table_layout(soup)
        vb_blocks.extend(table_vb)
        csharp_blocks.extend(table_cs)
        
        # Then try modern code block patterns
        for pattern in self.vb_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            vb_blocks.extend(matches)
        
        for pattern in self.csharp_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            csharp_blocks.extend(matches)
        
        # Also look for code blocks in <pre> and <code> tags
        for code_block in soup.find_all(['pre', 'code']):
            text = code_block.get_text()
            if any(keyword in text.lower() for keyword in ['dim ', 'sub ', 'function ', 'end sub', 'end function']):
                vb_blocks.append(text)
            elif any(keyword in text.lower() for keyword in ['var ', 'public ', 'private ', 'class ', 'namespace ']):
                csharp_blocks.append(text)
        
        return vb_blocks, csharp_blocks
    
    def _extract_from_table_layout(self, soup: BeautifulSoup) -> Tuple[List[str], List[str]]:
        """Extract VB.NET and C# code from table-based layouts (older HTML format)."""
        vb_blocks = []
        csharp_blocks = []
        
        # Look for tables that might contain VB.NET vs C# comparisons
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this table has a header row indicating VB.NET vs C# comparison
            header_row = table.find('tr')
            if not header_row:
                continue
                
            header_cells = header_row.find_all(['td', 'th'])
            if len(header_cells) < 2:
                continue
            
            # Check if header contains VB.NET and C# indicators
            header_text = ' '.join([cell.get_text().strip() for cell in header_cells]).lower()
            if not ('vb.net' in header_text or 'visual basic' in header_text) or 'c#' not in header_text:
                continue
            
            # Find the data rows (skip the header row)
            data_rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in data_rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # First cell is VB.NET, second cell is C#
                    vb_cell = cells[0]
                    cs_cell = cells[1]
                    
                    vb_text = self._clean_table_cell_text(vb_cell)
                    cs_text = self._clean_table_cell_text(cs_cell)
                    
                    # Only add if both cells contain substantial code
                    if self._looks_like_vb_code(vb_text) and self._looks_like_csharp_code(cs_text):
                        vb_blocks.append(vb_text)
                        csharp_blocks.append(cs_text)
        
        return vb_blocks, csharp_blocks
    
    def _clean_table_cell_text(self, cell) -> str:
        """Clean and format text from a table cell."""
        # Remove HTML tags but preserve line breaks
        text = cell.get_text()
        
        # Replace common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        # Clean up whitespace and line breaks
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:  # Only add non-empty lines
                lines.append(line)
        
        return '\n'.join(lines)
    
    def _looks_like_vb_code(self, text: str) -> bool:
        """Check if text looks like VB.NET code."""
        text_lower = text.lower()
        
        # VB.NET keywords and patterns
        vb_indicators = [
            'dim ', 'sub ', 'function ', 'end sub', 'end function', 'end class',
            'namespace ', 'imports ', 'byval ', 'byref ', 'as ', 'if ', 'then ',
            'elseif ', 'else ', 'end if', 'for ', 'next ', 'while ', 'end while',
            'do ', 'loop ', 'select case', 'end select', 'class ', 'structure ',
            'interface ', 'enum ', 'end enum', 'property ', 'end property',
            'public ', 'private ', 'protected ', 'friend ', 'shared ', 'overridable ',
            'overrides ', 'mustoverride ', 'notinheritable ', 'mustinherit ',
            'const ', 'readonly ', 'new ', 'nothing ', 'true ', 'false ',
            'console.writeline', 'console.read', 'string.format', 'convert.to',
            'try ', 'catch ', 'finally ', 'end try', 'throw ', 'on error ',
            'with ', 'end with', 'using ', 'end using', 'synclock ', 'end synclock'
        ]
        
        return any(indicator in text_lower for indicator in vb_indicators)
    
    def _looks_like_csharp_code(self, text: str) -> bool:
        """Check if text looks like C# code."""
        text_lower = text.lower()
        
        # C# keywords and patterns
        cs_indicators = [
            'using ', 'namespace ', 'class ', 'public ', 'private ', 'protected ',
            'internal ', 'static ', 'void ', 'int ', 'string ', 'bool ', 'var ',
            'if ', 'else ', 'for ', 'while ', 'do ', 'switch ', 'case ', 'default ',
            'break ', 'continue ', 'return ', 'new ', 'null ', 'true ', 'false ',
            'try ', 'catch ', 'finally ', 'throw ', 'using ', 'lock ', 'async ',
            'await ', 'interface ', 'enum ', 'struct ', 'delegate ', 'event ',
            'property ', 'get ', 'set ', 'virtual ', 'override ', 'abstract ',
            'sealed ', 'partial ', 'const ', 'readonly ', 'out ', 'ref ', 'params ',
            'this ', 'base ', 'typeof ', 'is ', 'as ', 'in ', 'where ', 'select ',
            'from ', 'orderby ', 'group ', 'join ', 'let ', 'into ', 'by ',
            'console.writeline', 'console.read', 'string.format', 'convert.to',
            'math.', 'system.', 'list<', 'dictionary<', 'ienumerable<', 'task<'
        ]
        
        return any(indicator in text_lower for indicator in cs_indicators)
    
    def is_translation_page(self, html_content: str) -> bool:
        """Check if the page likely contains translation content."""
        content_lower = html_content.lower()
        return any(keyword in content_lower for keyword in self.translation_keywords)
    
    def find_translation_pairs(self, vb_blocks: List[str], csharp_blocks: List[str]) -> List[Tuple[str, str]]:
        """Find pairs of VB.NET and C# code that likely represent translations."""
        pairs = []
        
        # For table-based layouts, we expect the blocks to be already paired
        # (same index in both lists represents a translation pair)
        if len(vb_blocks) == len(csharp_blocks) and len(vb_blocks) > 0:
            for vb, cs in zip(vb_blocks, csharp_blocks):
                if self._looks_like_translation_pair(vb, cs):
                    pairs.append((vb, cs))
        
        # If we don't have equal numbers, try to find pairs based on similar structure or content
        if not pairs:
            for vb_block in vb_blocks:
                for cs_block in csharp_blocks:
                    if self._looks_like_translation_pair(vb_block, cs_block):
                        pairs.append((vb_block, cs_block))
        
        return pairs
    
    def _looks_like_translation_pair(self, vb_code: str, csharp_code: str) -> bool:
        """Check if two code blocks look like they could be translations of each other."""
        vb_lower = vb_code.lower()
        cs_lower = csharp_code.lower()
        
        # Check for similar function names or comments
        vb_words = set(re.findall(r'\b\w+\b', vb_lower))
        cs_words = set(re.findall(r'\b\w+\b', cs_lower))
        
        # If they share significant common words, they might be translations
        common_words = vb_words.intersection(cs_words)
        if len(common_words) >= 3:
            return True
        
        # Check for similar structure (similar number of lines)
        vb_lines = len(vb_code.split('\n'))
        cs_lines = len(csharp_code.split('\n'))
        if abs(vb_lines - cs_lines) <= 2 and vb_lines > 2:
            return True
        
        return False
    
    def crawl_url(self, url: str) -> List[TranslationExample]:
        """Crawl a single URL and extract translation examples."""
        logging.info(f"Crawling: {url}")
        
        content = self.get_page_content(url)
        if not content:
            return []
        
        if not self.is_translation_page(content):
            logging.debug(f"Skipping {url} - doesn't appear to contain translation content")
            return []
        
        vb_blocks, csharp_blocks = self.extract_code_blocks(content)
        pairs = self.find_translation_pairs(vb_blocks, csharp_blocks)
        
        examples = []
        for vb_code, csharp_code in pairs:
            example = TranslationExample(
                vb_code=vb_code,
                csharp_code=csharp_code,
                source_url=url
            )
            if example.is_valid():
                examples.append(example)
        
        logging.info(f"Found {len(examples)} translation examples from {url}")
        return examples
    
    def crawl_urls(self, urls: List[str]) -> List[TranslationExample]:
        """Crawl multiple URLs and collect all translation examples."""
        all_examples = []
        
        for url in tqdm(urls, desc="Crawling URLs"):
            try:
                examples = self.crawl_url(url)
                all_examples.extend(examples)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logging.error(f"Error crawling {url}: {e}")
        
        return all_examples


def load_existing_examples(file_path: str) -> List[Dict]:
    """Load existing translation examples from a JSONL file."""
    examples = []
    if Path(file_path).exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        examples.append(json.loads(line))
            logging.info(f"Loaded {len(examples)} existing examples from {file_path}")
        except Exception as e:
            logging.warning(f"Could not load existing file {file_path}: {e}")
    return examples


def save_to_jsonl(examples: List[TranslationExample], output_file: str, append: bool = False):
    """Save translation examples to a JSONL file."""
    mode = 'a' if append else 'w'
    
    with open(output_file, mode, encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example.to_dict(), ensure_ascii=False) + '\n')
    
    action = "Appended" if append else "Saved"
    print(f"{action} {len(examples)} examples to {output_file}")


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a text file (one URL per line)."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def main():
    """Main function to run the crawler."""
    parser = argparse.ArgumentParser(description='VB.NET to C# Translation Web Crawler')
    parser.add_argument('--urls', '-u', nargs='+', help='URLs to crawl')
    parser.add_argument('--url-file', '-f', help='File containing URLs (one per line)')
    parser.add_argument('--output', '-o', default='translations.jsonl', help='Output JSONL file')
    parser.add_argument('--append', '-a', action='store_true', help='Append to existing file instead of overwriting')
    parser.add_argument('--use-playwright', action='store_true', help='Use Playwright for JavaScript-heavy sites')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Get URLs
    urls = []
    if args.urls:
        urls.extend(args.urls)
    if args.url_file:
        urls.extend(load_urls_from_file(args.url_file))
    
    if not urls:
        print("No URLs provided. Use --urls or --url-file to specify URLs to crawl.")
        return
    
    # Load existing examples if appending
    existing_examples = []
    if args.append:
        existing_examples = load_existing_examples(args.output)
        print(f"Found {len(existing_examples)} existing examples in {args.output}")
    
    # Run crawler
    with WebCrawler(use_playwright=args.use_playwright, headless=args.headless) as crawler:
        examples = crawler.crawl_urls(urls)
        
        if examples:
            save_to_jsonl(examples, args.output, append=args.append)
            total_examples = len(existing_examples) + len(examples)
            print(f"Successfully extracted {len(examples)} new translation examples")
            print(f"Total examples in {args.output}: {total_examples}")
        else:
            print("No translation examples found")


if __name__ == "__main__":
    main() 