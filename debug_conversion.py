#!/usr/bin/env python3
"""
Debug script for VB.NET to C# conversion
"""

import asyncio
import logging
from vb_to_csharp_converter import convert_vb_to_csharp

# Configure logging to see all debug information
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# NOTE: The underlying converter now always uses the Monaco API for both input and output, ensuring full and accurate code extraction and insertion. No Playwright or DOM simulation is used in this script directly.

def test_conversion():
    """Test the conversion with a simple VB.NET example."""
    
    # Simple VB.NET code for testing
    vb_code = """Imports System.IO
Imports Newtonsoft.Json

Namespace Classes
    Public Class FileOperations
        Public Shared FileName As String = "appSetting.json"
        Public Shared Sub Save(storageList As List(Of ApplicationStorage))
            Using streamWriter = File.CreateText(FileName)

                Dim serializer = New JsonSerializer With {.Formatting = Formatting.Indented}
                serializer.Serialize(streamWriter, storageList)

            End Using

        End Sub
        Public Shared Function Load() As List(Of ApplicationStorage)

            Using streamReader = New StreamReader(FileName)
                Dim json = streamReader.ReadToEnd()
                Return JsonConvert.DeserializeObject(Of List(Of ApplicationStorage))(json)
            End Using

        End Function

    End Class
End Namespace"""

    csharpcode_solution = """using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;

namespace Classes
{
    public partial class FileOperations
    {
        public static string FileName = "appSetting.json";
        public static void Save(List<ApplicationStorage> storageList)
        {
            using (var streamWriter = File.CreateText(FileName))
            {

                var serializer = new JsonSerializer() { Formatting = Formatting.Indented };
                serializer.Serialize(streamWriter, storageList);

            }

        }
        public static List<ApplicationStorage> Load()
        {

            using (var streamReader = new StreamReader(FileName))
            {
                string json = streamReader.ReadToEnd();
                return JsonConvert.DeserializeObject<List<ApplicationStorage>>(json);
            }

        }

    }
}"""
    
    print("🔵 Input VB.NET Code:")
    print("-" * 40)
    print(vb_code)
    print("-" * 40)
    print(f"Code length: {len(vb_code)} characters")
    print()
    
    try:
        print("🔄 Converting VB.NET to C#...")
        csharp_code = convert_vb_to_csharp(vb_code)
        
        print("✅ Conversion successful!")
        print()
        print("🟢 Output C# Code:")
        print("-" * 40)
        print(csharp_code)
        print("-" * 40)
        print(f"Code length: {len(csharp_code)} characters")
        
        # Check if output is truncated
        if "..." in csharp_code:
            print("⚠️  WARNING: Output appears to be truncated (contains '...')")
        
        # Show raw output for debugging
        print("\n🔍 Raw output analysis:")
        print(f"Contains '...': {'...' in csharp_code}")
        print(f"Contains 'using': {'using' in csharp_code}")
        print(f"Contains 'namespace': {'namespace' in csharp_code}")
        print(f"Contains 'class': {'class' in csharp_code}")
        print(f"Contains 'public static': {'public static' in csharp_code}")
        print(f"Contains 'Save(': {'Save(' in csharp_code}")
        print(f"Contains 'Load(': {'Load(' in csharp_code}")
        print(f"Contains 'JsonSerializer': {'JsonSerializer' in csharp_code}")
        print(f"Contains 'StreamReader': {'StreamReader' in csharp_code}")
        print(f"\n[DEBUG] Raw Monaco API output (first 500 chars):\n{csharp_code[:500]}")
        
        # Check for conversion errors
        if "EmptyStatementSyntax" in csharp_code or "CONVERSION ERROR" in csharp_code:
            print("❌ CONVERSION ERROR DETECTED!")
            print("The conversion appears to have failed. This might indicate:")
            print("1. The input code wasn't properly entered into the editor")
            print("2. The Monaco editor didn't receive the code correctly")
            print("3. The conversion service encountered an error")
        else:
            print("✅ Conversion appears successful!")
            
            # Test: Compare with expected solution
            print("\n🧪 Testing conversion accuracy...")
            
            # Normalize both strings for comparison (remove extra whitespace, normalize line endings)
            def normalize_code(code):
                # Remove extra whitespace and normalize line endings
                lines = [line.strip() for line in code.split('\n') if line.strip()]
                return '\n'.join(lines)
            
            normalized_actual = normalize_code(csharp_code)
            normalized_expected = normalize_code(csharpcode_solution)
            
            if normalized_actual == normalized_expected:
                print("✅ CONVERSION TEST PASSED!")
                print("The converted code matches the expected solution exactly.")
            else:
                print("❌ CONVERSION TEST FAILED!")
                print("The converted code does not match the expected solution.")
                print("\nExpected solution:")
                print("-" * 40)
                print(csharpcode_solution)
                print("-" * 40)
                print("\nActual conversion:")
                print("-" * 40)
                print(csharp_code)
                print("-" * 40)
                
                # Show differences
                print("\n🔍 Differences analysis:")
                actual_lines = normalized_actual.split('\n')
                expected_lines = normalized_expected.split('\n')
                
                max_lines = max(len(actual_lines), len(expected_lines))
                for i in range(max_lines):
                    actual_line = actual_lines[i] if i < len(actual_lines) else ""
                    expected_line = expected_lines[i] if i < len(expected_lines) else ""
                    
                    if actual_line != expected_line:
                        print(f"Line {i+1}:")
                        print(f"  Expected: {expected_line}")
                        print(f"  Actual:   {actual_line}")
                        print()
            
    except Exception as e:
        print(f"❌ Conversion failed with error: {str(e)}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    test_conversion() 