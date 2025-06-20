#!/usr/bin/env python3
"""
Manual Curation Script for VB.NET to C# Translation Examples

This script allows you to manually add VB.NET to C# translation examples
by copying and pasting them directly into the terminal. Examples are saved
to a JSONL file with a flag indicating they were manually curated.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import argparse


class ManualTranslationExample:
    """Represents a manually curated VB.NET to C# translation example."""
    
    def __init__(self, vb_code: str, csharp_code: str, title: str = "", 
                 description: str = "", source: str = "manual_curation"):
        self.vb_code = vb_code.strip()
        self.csharp_code = csharp_code.strip()
        self.title = title.strip()
        self.description = description.strip()
        self.source = source
        self.manually_curated = True  # Flag to identify manually curated examples
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "vb_code": self.vb_code,
            "csharp_code": self.csharp_code,
            "source_url": self.source,
            "title": self.title,
            "description": self.description,
            "manually_curated": self.manually_curated
        }
    
    def is_valid(self) -> bool:
        """Check if the translation example is valid."""
        return (len(self.vb_code) > 10 and 
                len(self.csharp_code) > 10 and 
                self.vb_code != self.csharp_code)


def load_existing_examples(file_path: str) -> List[Dict]:
    """Load existing translation examples from a JSONL file."""
    examples = []
    if Path(file_path).exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        examples.append(json.loads(line))
            print(f"✅ Loaded {len(examples)} existing examples from {file_path}")
        except Exception as e:
            print(f"⚠️  Could not load existing file {file_path}: {e}")
    return examples


def save_to_jsonl(examples: List[ManualTranslationExample], output_file: str, append: bool = False):
    """Save translation examples to a JSONL file."""
    mode = 'a' if append else 'w'
    
    with open(output_file, mode, encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example.to_dict(), ensure_ascii=False) + '\n')
    
    action = "Appended" if append else "Saved"
    print(f"✅ {action} {len(examples)} examples to {output_file}")


def get_multiline_input(prompt: str) -> str:
    """Get multiline input from user with proper line break handling."""
    print(f"\n{prompt}")
    print("(Press Enter twice to finish input)")
    
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            # Two consecutive empty lines means end of input
            lines.pop()  # Remove the last empty line
            break
        lines.append(line)
    
    return '\n'.join(lines)


def validate_code_input(code: str, language: str) -> bool:
    """Validate that the input looks like valid code."""
    if len(code.strip()) < 10:
        print(f"❌ {language} code is too short. Please provide more substantial code.")
        return False
    
    # Check for basic code indicators
    code_lower = code.lower()
    
    if language == "VB.NET":
        vb_indicators = ['dim ', 'sub ', 'function ', 'end sub', 'end function', 
                        'if ', 'then', 'else', 'for ', 'next', 'while ', 'wend',
                        'try ', 'catch ', 'finally ', 'end try', 'with ', 'end with']
        if not any(indicator in code_lower for indicator in vb_indicators):
            print(f"⚠️  Warning: This doesn't look like typical VB.NET code.")
            print("   Common VB.NET keywords: Dim, Sub, Function, End Sub, If, Then, etc.")
    else:  # C#
        cs_indicators = ['using ', 'namespace ', 'class ', 'public ', 'private ', 
                        'static ', 'void ', 'int ', 'string ', 'var ', 'if ', 'else',
                        'for ', 'while ', 'try ', 'catch ', 'finally ', 'using ']
        if not any(indicator in code_lower for indicator in cs_indicators):
            print(f"⚠️  Warning: This doesn't look like typical C# code.")
            print("   Common C# keywords: using, namespace, class, public, static, etc.")
    
    return True


def add_single_example() -> Optional[ManualTranslationExample]:
    """Add a single translation example through user input."""
    print(f"\n{'='*60}")
    print("📝 Adding New Translation Example")
    print(f"{'='*60}")
    
    # Get title (optional)
    title = input("\n📋 Title (optional, press Enter to skip): ").strip()
    
    # Get description (optional)
    description = input("📄 Description (optional, press Enter to skip): ").strip()
    
    # Get VB.NET code
    vb_code = get_multiline_input("🔵 Please paste your VB.NET code:")
    if not validate_code_input(vb_code, "VB.NET"):
        return None
    
    # Get C# code
    csharp_code = get_multiline_input("🟢 Please paste your C# code:")
    if not validate_code_input(csharp_code, "C#"):
        return None
    
    # Create example
    example = ManualTranslationExample(
        vb_code=vb_code,
        csharp_code=csharp_code,
        title=title,
        description=description
    )
    
    if not example.is_valid():
        print("❌ Invalid example: VB.NET and C# code are too similar or too short.")
        return None
    
    # Show preview
    print(f"\n{'='*60}")
    print("📋 Preview of your example:")
    print(f"{'='*60}")
    
    if title:
        print(f"📝 Title: {title}")
    if description:
        print(f"📄 Description: {description}")
    
    print(f"\n🔵 VB.NET Code ({len(vb_code)} chars, {len(vb_code.split())} words):")
    print("-" * 40)
    lines = vb_code.split('\n')
    for i, line in enumerate(lines[:5], 1):
        print(f"{i:2d}: {line}")
    if len(lines) > 5:
        print(f"    ... ({len(lines) - 5} more lines)")
    
    print(f"\n🟢 C# Code ({len(csharp_code)} chars, {len(csharp_code.split())} words):")
    print("-" * 40)
    lines = csharp_code.split('\n')
    for i, line in enumerate(lines[:5], 1):
        print(f"{i:2d}: {line}")
    if len(lines) > 5:
        print(f"    ... ({len(lines) - 5} more lines)")
    
    # Confirm
    while True:
        confirm = input(f"\n🤔 Save this example? (y/n): ").lower().strip()
        if confirm in ['y', 'yes']:
            return example
        elif confirm in ['n', 'no']:
            return None
        else:
            print("❌ Please enter 'y' or 'n'")


def interactive_curation(output_file: str, append: bool = False):
    """Interactive curation session."""
    examples = []
    
    if append and Path(output_file).exists():
        existing = load_existing_examples(output_file)
        print(f"📊 Found {len(existing)} existing examples")
    
    print(f"\n🎯 Starting manual curation session")
    print(f"📁 Output file: {output_file}")
    print(f"📝 Mode: {'Append' if append else 'Create new'}")
    
    while True:
        print(f"\n{'='*60}")
        print("🤔 What would you like to do?")
        print("  [a] Add a new translation example")
        print("  [s] Save current examples and exit")
        print("  [q] Quit without saving")
        print("  [h] Show help")
        
        choice = input("\nEnter your choice: ").lower().strip()
        
        if choice == 'a':
            example = add_single_example()
            if example:
                examples.append(example)
                print(f"✅ Added example #{len(examples)}")
            else:
                print("❌ Example not added")
        
        elif choice == 's':
            if examples:
                save_to_jsonl(examples, output_file, append=append)
                print(f"🎉 Successfully saved {len(examples)} examples!")
            else:
                print("⚠️  No examples to save")
            break
        
        elif choice == 'q':
            if examples:
                confirm = input(f"⚠️  You have {len(examples)} unsaved examples. Quit anyway? (y/n): ").lower().strip()
                if confirm not in ['y', 'yes']:
                    continue
            print("👋 Goodbye!")
            break
        
        elif choice == 'h':
            show_help()
        
        else:
            print("❌ Invalid choice. Please try again.")


def show_help():
    """Show help information."""
    print(f"\n📖 Manual Curation Help:")
    print("  a - Add: Add a new VB.NET to C# translation example")
    print("  s - Save: Save all examples to the JSONL file and exit")
    print("  q - Quit: Exit without saving (you'll be warned if you have unsaved examples)")
    print("  h - Help: Show this help message")
    print(f"\n💡 Tips for good examples:")
    print("  - Provide meaningful translations, not just syntax differences")
    print("  - Include complete code snippets (functions, classes, etc.)")
    print("  - Add descriptive titles and descriptions when helpful")
    print("  - Make sure the VB.NET and C# code are actually equivalent")
    print("  - Use proper indentation and formatting")
    print("  - Line breaks will be preserved as \\n in the JSON output")
    print(f"\n🔧 Technical details:")
    print("  - Examples are marked with 'manually_curated': true")
    print("  - Source URL is set to 'manual_curation'")
    print("  - Code is automatically stripped of leading/trailing whitespace")


def main():
    """Main function to run the manual curation script."""
    parser = argparse.ArgumentParser(description='Manual Curation for VB.NET to C# Translation Examples')
    parser.add_argument('--output', '-o', default='manual_translations.jsonl', 
                       help='Output JSONL file (default: manual_translations.jsonl)')
    parser.add_argument('--append', '-a', action='store_true', 
                       help='Append to existing file instead of overwriting')
    parser.add_argument('--interactive', '-i', action='store_true', default=True,
                       help='Run in interactive mode (default)')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.interactive:
        interactive_curation(args.output, args.append)
    else:
        print("❌ Non-interactive mode not implemented. Use --interactive or -i flag.")


if __name__ == "__main__":
    main() 