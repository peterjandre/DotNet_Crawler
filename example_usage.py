#!/usr/bin/env python3
"""
Example usage of the VB.NET to C# Translation Web Crawler

This script demonstrates how to use the crawler programmatically
instead of using the command line interface.
"""

from crawler import WebCrawler, save_to_jsonl

def main():
    """Example of programmatic usage of the crawler."""
    
    # Example URLs that might contain VB.NET to C# translations
    urls = [
        "https://docs.microsoft.com/en-us/dotnet/visual-basic/programming-guide/language-features/data-types/",
        "https://stackoverflow.com/questions/tagged/vb.net+c%23",
        # Add more URLs here
    ]
    
    print("Starting VB.NET to C# translation crawler...")
    print(f"Will crawl {len(urls)} URLs")
    
    # Use the crawler with BeautifulSoup (faster for static sites)
    print("\n=== Using BeautifulSoup (requests) ===")
    with WebCrawler(use_playwright=False) as crawler:
        examples = crawler.crawl_urls(urls)
        
        if examples:
            print(f"Found {len(examples)} translation examples")
            save_to_jsonl(examples, "translations_beautifulsoup.jsonl")
            
            # Show first example
            if examples:
                first_example = examples[0]
                print(f"\nFirst example from: {first_example.source_url}")
                print(f"VB.NET code length: {len(first_example.vb_code)} characters")
                print(f"C# code length: {len(first_example.csharp_code)} characters")
        else:
            print("No translation examples found with BeautifulSoup")
    
    # Use the crawler with Playwright (for JavaScript-heavy sites)
    print("\n=== Using Playwright ===")
    with WebCrawler(use_playwright=True, headless=True) as crawler:
        examples = crawler.crawl_urls(urls)
        
        if examples:
            print(f"Found {len(examples)} translation examples")
            save_to_jsonl(examples, "translations_playwright.jsonl")
        else:
            print("No translation examples found with Playwright")
    
    print("\nCrawling completed!")

if __name__ == "__main__":
    main() 