#!/usr/bin/env python3
"""
Interactive JSONL Dataset Cleaner

This script allows you to review and clean translation examples from a JSONL file
by evaluating each example one by one in the terminal.
"""

import json
import sys
import os
from typing import List, Dict
import argparse


def load_jsonl(file_path: str) -> List[Dict]:
    """Load translation examples from a JSONL file."""
    examples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    example = json.loads(line)
                    example['_line_number'] = line_num  # Keep track of original line
                    examples.append(example)
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
    return examples


def save_jsonl(examples: List[Dict], file_path: str):
    """Save translation examples to a JSONL file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for example in examples:
            # Remove the internal line number before saving
            clean_example = {k: v for k, v in example.items() if not k.startswith('_')}
            f.write(json.dumps(clean_example, ensure_ascii=False) + '\n')


def format_code(code: str, max_length: int = 80, show_full: bool = False) -> str:
    """Format code for display with line breaks."""
    if show_full or len(code) <= max_length:
        return code
    
    # Try to break at natural points
    lines = code.split('\n')
    if len(lines) > 1:
        return '\n'.join(lines[:3]) + ('\n...' if len(lines) > 3 else '')
    
    # Break at spaces if too long
    words = code.split()
    formatted = []
    current_line = ""
    
    for word in words:
        if len(current_line + word) < max_length:
            current_line += (word + " ")
        else:
            if current_line:
                formatted.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        formatted.append(current_line.strip())
    
    return '\n'.join(formatted)


def display_example(example: Dict, index: int, total: int, show_full: bool = False) -> None:
    """Display a single translation example."""
    print(f"\n{'='*80}")
    print(f"Example {index + 1} of {total} (Line {example.get('_line_number', 'unknown')})")
    if show_full:
        print("📖 FULL TEXT MODE")
    
    # Show curation status
    if example.get('manually_curated'):
        print("✋ MANUALLY CURATED")
    
    print(f"{'='*80}")
    
    print(f"\n📄 Source: {example.get('source_url', 'N/A')}")
    if example.get('title'):
        print(f"📝 Title: {example['title']}")
    if example.get('description'):
        print(f"📋 Description: {example['description']}")
    
    print(f"\n🔵 VB.NET Code ({len(example['vb_code'])} chars):")
    print("-" * 40)
    print(format_code(example['vb_code'], show_full=show_full))
    
    print(f"\n🟢 C# Code ({len(example['csharp_code'])} chars):")
    print("-" * 40)
    print(format_code(example['csharp_code'], show_full=show_full))
    
    # Show some statistics
    vb_lines = len(example['vb_code'].split('\n'))
    cs_lines = len(example['csharp_code'].split('\n'))
    print(f"\n📊 Stats: VB.NET: {vb_lines} lines, C#: {cs_lines} lines")
    
    # Check for potential issues
    issues = []
    if len(example['vb_code']) < 20:
        issues.append("VB.NET code too short")
    if len(example['csharp_code']) < 20:
        issues.append("C# code too short")
    if example['vb_code'] == example['csharp_code']:
        issues.append("VB.NET and C# code are identical")
    if len(example['vb_code'].split('\n')) < 2 and len(example['csharp_code'].split('\n')) < 2:
        issues.append("Both codes are single lines")
    
    if issues:
        print(f"\n⚠️  Potential issues: {', '.join(issues)}")


def get_user_decision() -> str:
    """Get user decision for an example."""
    while True:
        print(f"\n🤔 What would you like to do?")
        print("  [k] Keep this example")
        print("  [d] Delete this example")
        print("  [s] Skip for now (keep but mark as reviewed)")
        print("  [f] View full text (toggle)")
        print("  [q] Quit and save progress")
        print("  [h] Show help")
        
        choice = input("\nEnter your choice: ").lower().strip()
        
        if choice in ['k', 'd', 's', 'f', 'q', 'h']:
            return choice
        else:
            print("❌ Invalid choice. Please try again.")


def show_help():
    """Show help information."""
    print(f"\n📖 Help:")
    print("  k - Keep: This example is good quality, keep it in the dataset")
    print("  d - Delete: This example is poor quality, remove it from the dataset")
    print("  s - Skip: Skip this example for now (keep it but mark as reviewed)")
    print("  f - Full text: Toggle between preview and full text view")
    print("  q - Quit: Save progress and exit")
    print("  h - Help: Show this help message")
    print(f"\n💡 Tips:")
    print("  - Look for meaningful translations, not just syntax differences")
    print("  - Avoid examples where VB.NET and C# code are nearly identical")
    print("  - Prefer examples with multiple lines and meaningful logic")
    print("  - Check that the translation actually makes sense")
    print("  - Use 'f' to see the full code when preview is too short")


def interactive_clean(input_file: str, output_file: str = None, start_from: int = 0, 
                     include_manual: bool = True, exclude_manual: bool = False):
    """Interactively clean the JSONL file."""
    if output_file is None:
        output_file = input_file.replace('.jsonl', '_cleaned.jsonl')
    
    print(f"🔍 Loading examples from {input_file}...")
    examples = load_jsonl(input_file)
    
    if not examples:
        print("❌ No examples found in the file.")
        return
    
    # Filter examples based on manual curation preferences
    original_count = len(examples)
    if exclude_manual:
        examples = [ex for ex in examples if not ex.get('manually_curated', False)]
        print(f"🚫 Excluded {original_count - len(examples)} manually curated examples")
    elif not include_manual:
        examples = [ex for ex in examples if not ex.get('manually_curated', False)]
        print(f"🚫 Excluded {original_count - len(examples)} manually curated examples")
    
    if not examples:
        print("❌ No examples remain after filtering.")
        return
    
    print(f"✅ Loaded {len(examples)} examples for review")
    
    # Count manually curated examples
    manual_count = sum(1 for ex in examples if ex.get('manually_curated', False))
    if manual_count > 0:
        print(f"✋ {manual_count} manually curated examples included")
    
    # Filter out already reviewed examples if starting from a specific point
    if start_from > 0:
        examples = examples[start_from:]
        print(f"📍 Starting from example {start_from + 1}")
    
    kept_examples = []
    deleted_count = 0
    skipped_count = 0
    
    for i, example in enumerate(examples):
        show_full = False  # Reset for each example
        
        while True:
            display_example(example, i, len(examples), show_full=show_full)
            
            decision = get_user_decision()
            
            if decision == 'h':
                show_help()
                # Redisplay the example after help
                display_example(example, i, len(examples), show_full=show_full)
                decision = get_user_decision()
            
            if decision == 'f':
                # Toggle full text view
                show_full = not show_full
                print(f"\n🔄 {'Showing full text' if show_full else 'Showing preview'}")
                continue  # Redisplay the example with new view mode
            
            # Handle other decisions
            if decision == 'k':
                kept_examples.append(example)
                print("✅ Kept")
                break
            elif decision == 'd':
                deleted_count += 1
                print("🗑️  Deleted")
                break
            elif decision == 's':
                kept_examples.append(example)
                skipped_count += 1
                print("⏭️  Skipped")
                break
            elif decision == 'q':
                print(f"\n💾 Saving progress...")
                return  # Exit the function
    
    # Save the cleaned dataset
    save_jsonl(kept_examples, output_file)
    
    print(f"\n🎉 Cleaning completed!")
    print(f"📊 Results:")
    print(f"  - Kept: {len(kept_examples)} examples")
    print(f"  - Deleted: {deleted_count} examples")
    print(f"  - Skipped: {skipped_count} examples")
    print(f"  - Output file: {output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Interactive JSONL Dataset Cleaner')
    parser.add_argument('input_file', help='Input JSONL file to clean')
    parser.add_argument('--output', '-o', help='Output file (default: input_cleaned.jsonl)')
    parser.add_argument('--start-from', '-s', type=int, default=0, 
                       help='Start from example number (0-indexed)')
    parser.add_argument('--exclude-manual', action='store_true',
                       help='Exclude manually curated examples from cleaning')
    parser.add_argument('--manual-only', action='store_true',
                       help='Only clean manually curated examples')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"❌ Input file {args.input_file} not found.")
        sys.exit(1)
    
    # Handle mutually exclusive options
    if args.exclude_manual and args.manual_only:
        print("❌ Cannot use both --exclude-manual and --manual-only")
        sys.exit(1)
    
    try:
        interactive_clean(args.input_file, args.output, args.start_from, 
                         include_manual=not args.exclude_manual, 
                         exclude_manual=args.manual_only)
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Interrupted by user. Progress may be lost.")
        sys.exit(1)


if __name__ == "__main__":
    main() 