#!/usr/bin/env python3
"""
Test script for manual curation functionality
"""

import json
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from manual_curation import ManualTranslationExample, save_to_jsonl


def test_manual_curation():
    """Test the manual curation functionality."""
    print("🧪 Testing Manual Curation Functionality")
    print("=" * 50)
    
    # Create a test example
    vb_code = """Sub CalculateSum()
    Dim numbers() As Integer = {1, 2, 3, 4, 5}
    Dim sum As Integer = 0
    
    For Each num As Integer In numbers
        sum += num
    Next
    
    Console.WriteLine("Sum: " & sum.ToString())
End Sub"""
    
    csharp_code = """void CalculateSum()
{
    int[] numbers = { 1, 2, 3, 4, 5 };
    int sum = 0;
    
    foreach (int num in numbers)
    {
        sum += num;
    }
    
    Console.WriteLine($"Sum: {sum}");
}"""
    
    # Create manual example
    example = ManualTranslationExample(
        vb_code=vb_code,
        csharp_code=csharp_code,
        title="Array Sum Calculation",
        description="Demonstrates how to calculate the sum of an array in both VB.NET and C#"
    )
    
    print("✅ Created manual translation example")
    print(f"📝 Title: {example.title}")
    print(f"📄 Description: {example.description}")
    print(f"🔵 VB.NET lines: {len(example.vb_code.split())} words")
    print(f"🟢 C# lines: {len(example.csharp_code.split())} words")
    print(f"✋ Manually curated: {example.manually_curated}")
    
    # Test validation
    if example.is_valid():
        print("✅ Example validation passed")
    else:
        print("❌ Example validation failed")
        return False
    
    # Test JSON serialization
    example_dict = example.to_dict()
    print("✅ JSON serialization successful")
    print(f"📊 Dictionary keys: {list(example_dict.keys())}")
    
    # Test saving to file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        temp_file = f.name
    
    try:
        save_to_jsonl([example], temp_file, append=False)
        print(f"✅ Saved to temporary file: {temp_file}")
        
        # Verify the file was created and contains the example
        with open(temp_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) == 1:
            loaded_example = json.loads(lines[0])
            print("✅ Successfully loaded example from file")
            
            # Check that manually_curated flag is present
            if loaded_example.get('manually_curated'):
                print("✅ Manually curated flag is present")
            else:
                print("❌ Manually curated flag is missing")
                return False
            
            # Check that line breaks are preserved
            if '\n' in loaded_example['vb_code'] and '\n' in loaded_example['csharp_code']:
                print("✅ Line breaks are preserved as \\n")
            else:
                print("❌ Line breaks are not properly preserved")
                return False
                
        else:
            print(f"❌ Expected 1 line, got {len(lines)}")
            return False
            
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
            print(f"🧹 Cleaned up temporary file: {temp_file}")
    
    print("\n🎉 All tests passed!")
    return True


if __name__ == "__main__":
    success = test_manual_curation()
    if success:
        print("\n✅ Manual curation functionality is working correctly!")
    else:
        print("\n❌ Manual curation functionality has issues!")
        exit(1) 