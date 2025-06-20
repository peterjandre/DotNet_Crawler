#!/usr/bin/env python3
"""
Test script to verify table extraction logic for VB.NET to C# comparisons.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup
from crawler import WebCrawler

def test_table_extraction():
    """Test the table extraction logic on Test_Comparison.html."""
    
    # Read the HTML file
    html_file = Path(__file__).parent.parent / "Test_Comparison_files/Test_Comparison.html"
    if not html_file.exists():
        print(f"Error: {html_file} not found")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"Loaded HTML file: {html_file}")
    print(f"File size: {len(html_content)} characters")
    
    # Create a crawler instance to test the extraction
    crawler = WebCrawler()
    
    # Test the table extraction
    soup = BeautifulSoup(html_content, 'html.parser')
    vb_blocks, csharp_blocks = crawler._extract_from_table_layout(soup)
    
    print(f"\nExtracted {len(vb_blocks)} VB.NET blocks and {len(csharp_blocks)} C# blocks")
    
    # Show some examples
    for i, (vb, cs) in enumerate(zip(vb_blocks, csharp_blocks)):
        print(f"\n--- Example {i+1} ---")
        print("VB.NET:")
        print(vb[:200] + "..." if len(vb) > 200 else vb)
        print("\nC#:")
        print(cs[:200] + "..." if len(cs) > 200 else cs)
        print("-" * 50)
        
        if i >= 4:  # Show first 5 examples
            break
    
    # Test the full extraction
    print("\n" + "="*60)
    print("Testing full extraction...")
    
    all_vb, all_cs = crawler.extract_code_blocks(html_content)
    print(f"Total extracted: {len(all_vb)} VB.NET blocks, {len(all_cs)} C# blocks")
    
    # Test translation pair finding
    pairs = crawler.find_translation_pairs(all_vb, all_cs)
    print(f"Found {len(pairs)} translation pairs")
    
    # Create translation examples
    examples = []
    for vb_code, csharp_code in pairs:
        from crawler import TranslationExample
        example = TranslationExample(
            vb_code=vb_code,
            csharp_code=csharp_code,
            source_url="Test_Comparison.html"
        )
        if example.is_valid():
            examples.append(example)
    
    print(f"Valid translation examples: {len(examples)}")
    
    # Show a few examples
    for i, example in enumerate(examples[:3]):
        print(f"\n--- Valid Example {i+1} ---")
        print(f"VB.NET ({len(example.vb_code)} chars):")
        print(example.vb_code[:150] + "..." if len(example.vb_code) > 150 else example.vb_code)
        print(f"\nC# ({len(example.csharp_code)} chars):")
        print(example.csharp_code[:150] + "..." if len(example.csharp_code) > 150 else example.csharp_code)

if __name__ == "__main__":
    test_table_extraction() 