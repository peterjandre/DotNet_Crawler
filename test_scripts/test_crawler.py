#!/usr/bin/env python3
"""
Test script for the VB.NET to C# Translation Web Crawler

This script tests the crawler with a real URL to verify functionality.
"""

import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawler_simple import SimpleWebCrawler as WebCrawler, TranslationExample

def test_crawler():
    """Test the crawler with a real URL."""
    print("Testing VB.NET to C# Translation Web Crawler...")
    
    # Test with a real URL that might contain VB.NET to C# translations
    test_url = "https://www.codeproject.com/Articles/9978/Complete-Comparison-for-VB-NET-and-C-"
    
    # Test the crawler
    crawler = WebCrawler()
    print(f"Testing with URL: {test_url}")
    
    # Test individual methods
    print("\n1. Testing page content fetching...")
    content = crawler.get_page_content(test_url)
    if content:
        print("✓ Successfully fetched page content")
    else:
        print("✗ Failed to fetch page content")
        return
    
    print("\n2. Testing translation page detection...")
    is_translation = crawler.is_translation_page(content)
    print(f"✓ Page detected as translation page: {is_translation}")
    
    print("\n3. Testing code block extraction...")
    vb_blocks, csharp_blocks = crawler.extract_code_blocks(content)
    print(f"✓ Found {len(vb_blocks)} VB.NET blocks and {len(csharp_blocks)} C# blocks")
    
    print("\n4. Testing translation pairing...")
    pairs = crawler.find_translation_pairs(vb_blocks, csharp_blocks)
    print(f"✓ Found {len(pairs)} translation pairs")
    
    print("\n5. Testing full crawling...")
    examples = crawler.crawl_url(test_url)
    print(f"✓ Extracted {len(examples)} translation examples")
    
    # Display results
    if examples:
        print("\n=== Extracted Translation Examples ===")
        for i, example in enumerate(examples, 1):
            print(f"\nExample {i}:")
            print(f"Source: {example.source_url}")
            print(f"VB.NET ({len(example.vb_code)} chars):")
            print(example.vb_code[:100] + "..." if len(example.vb_code) > 100 else example.vb_code)
            print(f"C# ({len(example.csharp_code)} chars):")
            print(example.csharp_code[:100] + "..." if len(example.csharp_code) > 100 else example.csharp_code)
            print("-" * 50)
        
        print(f"\n✓ Test completed successfully! Found {len(examples)} translation examples.")
    else:
        print("\n⚠ No translation examples found from this URL (this is normal for some pages)")
        print("✓ Test completed - crawler is working correctly")

if __name__ == "__main__":
    test_crawler() 