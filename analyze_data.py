#!/usr/bin/env python3
"""
Data analysis script for VB.NET to C# translation examples

This script helps analyze and filter the collected translation examples.
"""

import json
import argparse
from collections import Counter
from typing import List, Dict
import re

def load_jsonl(file_path: str) -> List[Dict]:
    """Load translation examples from a JSONL file."""
    examples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples

def save_jsonl(examples: List[Dict], file_path: str):
    """Save translation examples to a JSONL file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

def analyze_examples(examples: List[Dict]) -> Dict:
    """Analyze the translation examples and return statistics."""
    stats = {
        'total_examples': len(examples),
        'avg_vb_length': 0,
        'avg_csharp_length': 0,
        'source_domains': Counter(),
        'vb_keywords': Counter(),
        'csharp_keywords': Counter(),
        'length_distribution': Counter()
    }
    
    if not examples:
        return stats
    
    total_vb_length = 0
    total_csharp_length = 0
    
    vb_keywords = ['dim', 'sub', 'function', 'end sub', 'end function', 'byval', 'byref', 'as']
    csharp_keywords = ['var', 'public', 'private', 'class', 'namespace', 'using', 'return']
    
    for example in examples:
        # Length statistics
        vb_len = len(example['vb_code'])
        csharp_len = len(example['csharp_code'])
        total_vb_length += vb_len
        total_csharp_length += csharp_len
        
        # Length distribution
        length_range = f"{(min(vb_len, csharp_len) // 100) * 100}-{(min(vb_len, csharp_len) // 100) * 100 + 99}"
        stats['length_distribution'][length_range] += 1
        
        # Source domain
        try:
            from urllib.parse import urlparse
            domain = urlparse(example['source_url']).netloc
            stats['source_domains'][domain] += 1
        except:
            stats['source_domains']['unknown'] += 1
        
        # Keyword analysis
        vb_lower = example['vb_code'].lower()
        cs_lower = example['csharp_code'].lower()
        
        for keyword in vb_keywords:
            if keyword in vb_lower:
                stats['vb_keywords'][keyword] += 1
        
        for keyword in csharp_keywords:
            if keyword in cs_lower:
                stats['csharp_keywords'][keyword] += 1
    
    stats['avg_vb_length'] = total_vb_length / len(examples)
    stats['avg_csharp_length'] = total_csharp_length / len(examples)
    
    return stats

def filter_examples(examples: List[Dict], min_length: int = 0, max_length: int = None, 
                   min_ratio: float = 0.0, max_ratio: float = None) -> List[Dict]:
    """Filter examples based on various criteria."""
    filtered = []
    
    for example in examples:
        vb_len = len(example['vb_code'])
        cs_len = len(example['csharp_code'])
        
        # Length filters
        if vb_len < min_length or cs_len < min_length:
            continue
        
        if max_length and (vb_len > max_length or cs_len > max_length):
            continue
        
        # Length ratio filter (to avoid very unbalanced translations)
        if cs_len > 0:
            ratio = vb_len / cs_len
            if ratio < min_ratio or (max_ratio and ratio > max_ratio):
                continue
        
        filtered.append(example)
    
    return filtered

def print_stats(stats: Dict):
    """Print analysis statistics."""
    print("=== Translation Examples Analysis ===")
    print(f"Total examples: {stats['total_examples']}")
    print(f"Average VB.NET code length: {stats['avg_vb_length']:.1f} characters")
    print(f"Average C# code length: {stats['avg_csharp_length']:.1f} characters")
    
    print("\n=== Source Domains ===")
    for domain, count in stats['source_domains'].most_common(10):
        print(f"  {domain}: {count}")
    
    print("\n=== VB.NET Keywords ===")
    for keyword, count in stats['vb_keywords'].most_common(10):
        print(f"  {keyword}: {count}")
    
    print("\n=== C# Keywords ===")
    for keyword, count in stats['csharp_keywords'].most_common(10):
        print(f"  {keyword}: {count}")
    
    print("\n=== Length Distribution ===")
    for length_range, count in sorted(stats['length_distribution'].items()):
        print(f"  {length_range} chars: {count}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Analyze VB.NET to C# translation examples')
    parser.add_argument('input_file', help='Input JSONL file')
    parser.add_argument('--output', '-o', help='Output filtered JSONL file')
    parser.add_argument('--min-length', type=int, default=0, help='Minimum code length')
    parser.add_argument('--max-length', type=int, help='Maximum code length')
    parser.add_argument('--min-ratio', type=float, default=0.0, help='Minimum VB/C# length ratio')
    parser.add_argument('--max-ratio', type=float, help='Maximum VB/C# length ratio')
    parser.add_argument('--stats-only', action='store_true', help='Only show statistics, no filtering')
    
    args = parser.parse_args()
    
    # Load examples
    print(f"Loading examples from {args.input_file}...")
    examples = load_jsonl(args.input_file)
    print(f"Loaded {len(examples)} examples")
    
    # Analyze
    stats = analyze_examples(examples)
    print_stats(stats)
    
    if args.stats_only:
        return
    
    # Filter if requested
    if any([args.min_length > 0, args.max_length, args.min_ratio > 0, args.max_ratio]):
        print(f"\nFiltering examples...")
        original_count = len(examples)
        examples = filter_examples(
            examples, 
            min_length=args.min_length,
            max_length=args.max_length,
            min_ratio=args.min_ratio,
            max_ratio=args.max_ratio
        )
        print(f"Filtered from {original_count} to {len(examples)} examples")
        
        # Show filtered stats
        if examples:
            filtered_stats = analyze_examples(examples)
            print("\n=== Filtered Examples Statistics ===")
            print(f"Total examples: {filtered_stats['total_examples']}")
            print(f"Average VB.NET code length: {filtered_stats['avg_vb_length']:.1f} characters")
            print(f"Average C# code length: {filtered_stats['avg_csharp_length']:.1f} characters")
    
    # Save if output specified
    if args.output and examples:
        save_jsonl(examples, args.output)
        print(f"\nSaved {len(examples)} examples to {args.output}")

if __name__ == "__main__":
    main() 