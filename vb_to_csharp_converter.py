#!/usr/bin/env python3
"""
VB.NET to C# Converter Module

This module provides functionality to convert VB.NET code snippets to C# using
the ICSharpCode converter web service at https://icsharpcode.github.io/CodeConverter/.
It can be used both as a library and as a command-line tool.
"""

import asyncio
from playwright.async_api import async_playwright
from typing import Optional, List, Dict
import logging
import json
import sys
import os
from pathlib import Path
import argparse
import glob
from tqdm import tqdm
import time


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for validation
MAX_FILE_SIZE_BYTES = 50000  # 50KB limit for ICSharpCode converter
MAX_CODE_LENGTH_CHARS = 40000  # 40K characters limit
VB_FILE_EXTENSIONS = ['.vb', '.vbx', '.vbs']  # Supported VB file extensions


class ConversionExample:
    """Represents a VB.NET to C# conversion example."""
    
    def __init__(self, vb_code: str, csharp_code: str, title: str = "", 
                 description: str = "", source: str = "icsharpcode_converter"):
        self.vb_code = vb_code.strip()
        self.csharp_code = csharp_code.strip()
        self.title = title.strip()
        self.description = description.strip()
        self.source = source
        self.converted_automatically = True  # Flag to identify auto-converted examples
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "vb_code": self.vb_code,
            "csharp_code": self.csharp_code,
            "source_url": self.source,
            "title": self.title,
            "description": self.description,
            "converted_automatically": self.converted_automatically
        }
    
    def is_valid(self) -> bool:
        """Check if the conversion example is valid."""
        return (len(self.vb_code) > 10 and 
                len(self.csharp_code) > 10 and 
                self.vb_code != self.csharp_code)


def validate_file_size(file_path: str) -> bool:
    """Validate that the file size is within acceptable limits."""
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            print(f"⚠️  File {file_path} is too large ({file_size} bytes > {MAX_FILE_SIZE_BYTES} bytes)")
            return False
        return True
    except Exception as e:
        print(f"❌ Error checking file size for {file_path}: {e}")
        return False


def validate_code_length(vb_code: str) -> bool:
    """Validate that the VB.NET code length is within acceptable limits."""
    code_length = len(vb_code)
    if code_length > MAX_CODE_LENGTH_CHARS:
        print(f"⚠️  Code is too long ({code_length} chars > {MAX_CODE_LENGTH_CHARS} chars)")
        return False
    return True


def load_vb_files_from_directory(directory: str, recursive: bool = True) -> List[str]:
    """Load VB file paths from a directory."""
    vb_files = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"❌ Directory {directory} does not exist")
        return vb_files
    
    if not directory_path.is_dir():
        print(f"❌ {directory} is not a directory")
        return vb_files
    
    # Build glob pattern
    pattern = "**/*" if recursive else "*"
    for ext in VB_FILE_EXTENSIONS:
        glob_pattern = str(directory_path / (pattern + ext))
        vb_files.extend(glob.glob(glob_pattern, recursive=recursive))
    
    # Remove duplicates and sort
    vb_files = sorted(list(set(vb_files)))
    
    print(f"📁 Found {len(vb_files)} VB files in {directory}")
    return vb_files


def load_vb_files_from_list(file_path: str) -> List[str]:
    """Load VB file paths from a text file (one path per line)."""
    vb_files = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check if file exists and has valid extension
                    file_path_obj = Path(line)
                    if file_path_obj.exists() and file_path_obj.suffix.lower() in VB_FILE_EXTENSIONS:
                        vb_files.append(line)
                    else:
                        print(f"⚠️  Skipping invalid file: {line}")
    except Exception as e:
        print(f"❌ Error reading file list {file_path}: {e}")
    
    print(f"📄 Loaded {len(vb_files)} VB files from {file_path}")
    return vb_files


def process_vb_file(file_path: str) -> Optional[ConversionExample]:
    """Process a single VB file and convert it to C#."""
    try:
        # Validate file size
        if not validate_file_size(file_path):
            return None
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            vb_code = f.read()
        
        # Validate code length
        if not validate_code_length(vb_code):
            return None
        
        # Validate VB code
        if not validate_vb_code(vb_code):
            print(f"⚠️  Invalid VB.NET code in {file_path}")
            return None
        
        # Convert to C#
        print(f"🔄 Converting {file_path}...")
        csharp_code = convert_vb_to_csharp(vb_code)
        
        # Create example
        example = ConversionExample(
            vb_code=vb_code,
            csharp_code=csharp_code,
            title=f"File: {Path(file_path).name}",
            description=f"Converted from file: {file_path}"
        )
        
        if example.is_valid():
            print(f"✅ Successfully converted {file_path}")
            return example
        else:
            print(f"❌ Invalid conversion result for {file_path}")
            return None
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return None


def batch_convert_vb_files(vb_files: List[str], output_file: str, append: bool = False, 
                          delay: float = 1.0) -> List[ConversionExample]:
    """Convert multiple VB files in batch."""
    examples = []
    successful = 0
    failed = 0
    
    print(f"🚀 Starting batch conversion of {len(vb_files)} VB files...")
    print(f"📁 Output file: {output_file}")
    print(f"📝 Mode: {'Append' if append else 'Create new'}")
    print(f"⏱️  Delay between conversions: {delay} seconds")
    
    for i, file_path in enumerate(tqdm(vb_files, desc="Converting VB files")):
        try:
            example = process_vb_file(file_path)
            if example:
                examples.append(example)
                successful += 1
            else:
                failed += 1
            
            # Add delay to be respectful to the ICSharpCode service
            if i < len(vb_files) - 1:  # Don't delay after the last file
                time.sleep(delay)
                
        except Exception as e:
            print(f"❌ Unexpected error processing {file_path}: {str(e)}")
            failed += 1
    
    # Save results
    if examples:
        save_to_jsonl(examples, output_file, append=append)
        print(f"🎉 Batch conversion completed!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total saved: {len(examples)}")
    else:
        print("❌ No successful conversions to save")
    
    return examples


async def convert_vb_to_csharp_async(vb_code: str) -> str:
    """
    Convert VB.NET code to C# using the ICSharpCode converter.
    
    Args:
        vb_code (str): The VB.NET code to convert
        
    Returns:
        str: The converted C# code
        
    Raises:
        Exception: If conversion fails or browser encounters an error
    """
    browser = None
    page = None
    
    try:
        async with async_playwright() as p:
            # Launch headless Chromium browser with more human-like settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create context with human-like settings
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Add script to hide automation
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Navigate to the converter
            logger.info("Navigating to ICSharpCode CodeConverter...")
            await page.goto("https://icsharpcode.github.io/CodeConverter/", wait_until='networkidle')
            
            # Wait for the page to load and add some human-like delay
            await asyncio.sleep(2)
            
            # Simulate human-like scrolling
            await page.evaluate("window.scrollTo(0, 100)")
            await asyncio.sleep(1)
            
            # Find and fill the input field (VB.NET code)
            logger.info("Looking for input field...")
            
            # Target the specific textarea within the Monaco editor for input
            input_selectors = [
                "textarea.inputarea.monaco-mouse-cursor-text",
                "textarea[data-mprt='6']",
                "textarea[aria-label*='Editor content']",
                "textarea[role='textbox']",
                "textarea"
            ]
            
            input_field = None
            for selector in input_selectors:
                try:
                    input_field = await page.wait_for_selector(selector, timeout=3000)
                    if input_field:
                        logger.info(f"Found input field with selector: {selector}")
                        break
                except:
                    continue
            
            if not input_field:
                # Try to find the Monaco editor textarea specifically
                textareas = await page.query_selector_all("textarea.inputarea.monaco-mouse-cursor-text")
                if textareas:
                    input_field = textareas[0]
                    logger.info("Using Monaco editor textarea")
                else:
                    # Fallback to any textarea
                    textareas = await page.query_selector_all("textarea")
                    if textareas:
                        input_field = textareas[0]
                        logger.info("Using first textarea found on page")
                    else:
                        raise Exception("Could not find input field for VB.NET code")
            
            # Clear any existing content and paste the VB.NET code with human-like behavior
            logger.info("Pasting VB.NET code...")
            
            # Focus the Monaco editor container before any input attempts
            try:
                input_editor_container = await page.query_selector('div.monaco-editor[data-uri="inmemory://model/1"]')
                if input_editor_container:
                    await input_editor_container.click()
                    logger.info("Clicked on input Monaco editor container to focus it")
                    await asyncio.sleep(0.5)
            except Exception as e:
                logger.warning(f"Could not click on input editor container: {e}")

            # Always use Monaco API for input
            try:
                monaco_api_success = await page.evaluate(f"""
                    (code) => {{
                        if (window.monaco && window.monaco.editor && window.monaco.editor.getModels().length > 0) {{
                            window.monaco.editor.getModels()[0].setValue(code);
                            return true;
                        }}
                        return false;
                    }}
                """, vb_code)
                if monaco_api_success:
                    logger.info("Successfully set code using Monaco API for input")
                else:
                    raise Exception("Monaco API setValue failed for input editor")
            except Exception as e:
                logger.error(f"Monaco API setValue failed for input editor: {e}")
                raise Exception("Could not input VB.NET code into editor using Monaco API")
            
            # Final verification - check all possible content sources
            final_input = await page.evaluate("""
                () => {
                    console.log('Verifying input content...');
                    
                    // Check the specific input Monaco editor textarea first
                    const inputTextarea = document.querySelector('div.monaco-editor[data-uri="inmemory://model/1"] textarea.inputarea.monaco-mouse-cursor-text');
                    if (inputTextarea) {
                        console.log('Found input textarea, value length:', inputTextarea.value.length);
                        return inputTextarea.value;
                    }
                    
                    // Check input Monaco editor API
                    const inputEditor = document.querySelector('div.monaco-editor[data-uri="inmemory://model/1"]');
                    if (inputEditor && inputEditor.__monaco) {
                        const model = inputEditor.__monaco.getModel();
                        if (model) {
                            const value = model.getValue();
                            console.log('Found input Monaco model, value length:', value.length);
                            return value;
                        }
                    }
                    
                    // Check global Monaco instance for first model
                    if (window.monaco) {
                        const models = window.monaco.editor.getModels();
                        if (models.length > 0) {
                            const value = models[0].getValue();
                            console.log('Found global Monaco first model, value length:', value.length);
                            return value;
                        }
                    }
                    
                    // Check first Monaco editor (fallback)
                    const editors = document.querySelectorAll('.monaco-editor');
                    if (editors.length > 0) {
                        const firstEditor = editors[0];
                        if (firstEditor.__monaco) {
                            const model = firstEditor.__monaco.getModel();
                            if (model) {
                                const value = model.getValue();
                                console.log('Found first Monaco editor model, value length:', value.length);
                                return value;
                            }
                        }
                        
                        // Check for textarea inside first Monaco editor
                        const editorTextarea = firstEditor.querySelector('textarea.inputarea.monaco-mouse-cursor-text');
                        if (editorTextarea) {
                            console.log('Found first editor textarea, value length:', editorTextarea.value.length);
                            return editorTextarea.value;
                        }
                    }
                    
                    // Check any Monaco textarea (last resort)
                    const textareas = document.querySelectorAll('textarea.inputarea.monaco-mouse-cursor-text');
                    if (textareas.length > 0) {
                        console.log('Found any Monaco textarea, value length:', textareas[0].value.length);
                        return textareas[0].value;
                    }
                    
                    console.log('No input content found');
                    return null;
                }
            """)
            
            logger.info(f"Final input verification: {len(final_input) if final_input else 0} characters")
            if not final_input or len(final_input) < 10:
                logger.error("Input verification failed - editor appears to be empty")
                logger.error("This might indicate the page structure has changed or Monaco Editor is not accessible")
                raise Exception("Failed to input VB.NET code - editor is empty")
            
            # Additional verification: check if we got the full code
            expected_length = len(vb_code)
            actual_length = len(final_input) if final_input else 0
            if actual_length < expected_length * 0.8:  # Allow 20% tolerance for whitespace differences
                logger.warning(f"Input verification shows incomplete code: {actual_length} chars vs expected {expected_length} chars")
                logger.warning("Attempting to retry input with different method...")
                
                # Try keyboard simulation as a retry
                try:
                    # Click the Monaco editor container to focus it
                    input_editor_container = await page.query_selector('div.monaco-editor[data-uri="inmemory://model/1"]')
                    if input_editor_container:
                        await input_editor_container.click()
                        await asyncio.sleep(0.5)
                        
                        # Try Monaco API first
                        monaco_api_success = await page.evaluate(f"""
                            (code) => {{
                                if (window.monaco && window.monaco.editor && window.monaco.editor.getModels().length > 0) {{
                                    window.monaco.editor.getModels()[0].setValue(code);
                                    return true;
                                }}
                                return false;
                            }}
                        """, vb_code)
                        
                        if monaco_api_success:
                            logger.info("Retry: Successfully set code using Monaco API")
                        else:
                            # Fallback to textarea typing
                            input_textarea = await page.query_selector('div.monaco-editor[data-uri="inmemory://model/1"] textarea.inputarea.monaco-mouse-cursor-text')
                            if input_textarea:
                                await input_textarea.focus()
                                await asyncio.sleep(0.2)
                                
                                # Clear existing content with Ctrl+A, Delete
                                await page.keyboard.press('Control+a')
                                await asyncio.sleep(0.1)
                                await page.keyboard.press('Delete')
                                await asyncio.sleep(0.1)
                                
                                # Type the code character by character (slower but more reliable)
                                await input_textarea.type(vb_code, delay=5)  # 5ms delay between characters
                                logger.info("Retry: Used keyboard simulation to input code")
                            else:
                                raise Exception("Could not find input textarea for retry")
                    else:
                        raise Exception("Could not find input editor container for retry")
                        
                        # Wait a bit for the input to settle
                        await asyncio.sleep(1)
                        
                        # Verify again
                        retry_input = await page.evaluate("""
                            () => {
                                if (window.monaco && window.monaco.editor && window.monaco.editor.getModels().length > 0) {
                                    return window.monaco.editor.getModels()[0].getValue();
                                }
                                const inputTextarea = document.querySelector('div.monaco-editor[data-uri="inmemory://model/1"] textarea.inputarea.monaco-mouse-cursor-text');
                                return inputTextarea ? inputTextarea.value : null;
                            }
                        """)
                        
                        if retry_input and len(retry_input) >= expected_length * 0.8:
                            logger.info(f"Retry successful: {len(retry_input)} characters entered")
                            final_input = retry_input
                        else:
                            logger.error(f"Retry failed: still only {len(retry_input) if retry_input else 0} characters")
                            raise Exception("Failed to input complete VB.NET code even after retry")
                except Exception as retry_error:
                    logger.error(f"Retry input failed: {retry_error}")
                    raise Exception(f"Failed to input VB.NET code - only {actual_length} of {expected_length} characters entered")
            else:
                logger.info(f"Input verification passed: {actual_length} characters entered (expected ~{expected_length})")
            
            await asyncio.sleep(1)
            
            # Find and click the convert button
            logger.info("Looking for convert button...")
            
            # Target the specific convert button
            convert_selectors = [
                "#convert-button",
                "button#convert-button",
                "button.btn.btn-default.horizontal-spaced",
                "button:has-text('Convert Code')",
                "button[class*='btn'][class*='horizontal-spaced']",
                "button"
            ]
            
            convert_button = None
            for selector in convert_selectors:
                try:
                    convert_button = await page.wait_for_selector(selector, timeout=3000)
                    if convert_button:
                        # Check if button is visible and clickable
                        is_visible = await convert_button.is_visible()
                        if is_visible:
                            logger.info(f"Found convert button with selector: {selector}")
                            break
                        else:
                            convert_button = None
                except:
                    continue
            
            if not convert_button:
                # Try to find the specific convert button by ID or text
                buttons = await page.query_selector_all("button")
                for button in buttons:
                    try:
                        is_visible = await button.is_visible()
                        if is_visible:
                            button_text = await button.text_content()
                            button_id = await button.get_attribute('id')
                            
                            # Check for the specific convert button
                            if button_id == 'convert-button' or button_text == 'Convert Code':
                                convert_button = button
                                logger.info(f"Found convert button: {button_text} (ID: {button_id})")
                                break
                            elif button_text and any(keyword in button_text.lower() for keyword in ['convert', 'transform', 'go', 'submit']):
                                convert_button = button
                                logger.info(f"Using fallback button with text: {button_text}")
                                break
                    except:
                        continue
            
            if not convert_button:
                raise Exception("Could not find convert button")
            
            # Click the convert button using JavaScript to avoid Monaco Editor interference
            logger.info("Clicking convert button...")
            
            # Use JavaScript to click the convert button, bypassing Monaco Editor interference
            click_success = await page.evaluate("""
                () => {
                    // Try the specific convert button first
                    const convertButton = document.querySelector('#convert-button');
                    if (convertButton) {
                        convertButton.click();
                        return { success: true, method: 'id_selector' };
                    }
                    
                    // Try by class combination
                    const classButton = document.querySelector('button.btn.btn-default.horizontal-spaced');
                    if (classButton) {
                        classButton.click();
                        return { success: true, method: 'class_selector' };
                    }
                    
                    // Try by text content
                    const buttons = document.querySelectorAll('button');
                    for (const button of buttons) {
                        if (button.textContent.trim() === 'Convert Code') {
                            button.click();
                            return { success: true, method: 'text_selector' };
                        }
                    }
                    
                    return { success: false, method: 'none' };
                }
            """)
            
            if not click_success or not click_success.get('success'):
                # Fallback: try to click using Playwright with force option
                try:
                    await convert_button.click(force=True, timeout=5000)
                    logger.info("Used force click as fallback")
                except Exception as e:
                    logger.error(f"Force click also failed: {e}")
                    raise Exception("Could not click convert button")
            else:
                logger.info(f"Successfully clicked convert button using method: {click_success.get('method')}")
            
            await asyncio.sleep(1)
            
            # Wait for the conversion to complete and output to appear
            logger.info("Waiting for conversion to populate output...")
            
            # Target the specific output Monaco editor (second Monaco editor)
            output_selectors = [
                "div.monaco-editor[data-uri='inmemory://model/2'] textarea.inputarea.monaco-mouse-cursor-text",
                "div.monaco-editor[data-uri*='model/2'] textarea",
                "div.monaco-editor:nth-child(2) textarea.inputarea.monaco-mouse-cursor-text",
                "div.monaco-editor:nth-child(2) textarea",
                "textarea[data-mprt='6']",
                "textarea.inputarea.monaco-mouse-cursor-text",
                "textarea"
            ]
            
            output_field = None
            for selector in output_selectors:
                try:
                    output_field = await page.wait_for_selector(selector, timeout=8000)
                    if output_field:
                        logger.info(f"Found output field with selector: {selector}")
                        break
                except:
                    continue
            
            if not output_field:
                # Try to find the specific output Monaco editor
                output_editors = await page.query_selector_all("div.monaco-editor[data-uri='inmemory://model/2']")
                if output_editors:
                    output_textarea = await output_editors[0].query_selector("textarea.inputarea.monaco-mouse-cursor-text")
                    if output_textarea:
                        output_field = output_textarea
                        logger.info("Using output Monaco editor textarea")
                    else:
                        # Try any textarea within the output editor
                        output_textarea = await output_editors[0].query_selector("textarea")
                        if output_textarea:
                            output_field = output_textarea
                            logger.info("Using textarea from output Monaco editor")
                else:
                    # Fallback: try to find any textarea that's not the input
                    textareas = await page.query_selector_all("textarea")
                    if len(textareas) > 1:
                        # Use the second textarea (assuming first is input, second is output)
                        output_field = textareas[1]
                        logger.info("Using second textarea as output field")
                    else:
                        raise Exception("Could not find output field for C# code")
            
            # Wait for the conversion to complete - check for content in the output field
            max_wait_time = 15  # Maximum wait time in seconds
            wait_interval = 1   # Check every second
            waited_time = 0
            
            # Track previous content to detect when conversion is stable
            previous_content = None
            stable_count = 0
            required_stable_checks = 3  # Need 3 consecutive stable reads
            
            while waited_time < max_wait_time:
                try:
                    # Always use Monaco API for output extraction first
                    csharp_code = await page.evaluate("""
                        () => {
                            if (window.monaco && window.monaco.editor && window.monaco.editor.getModels().length > 1) {
                                return window.monaco.editor.getModels()[1].getValue();
                            }
                            // fallback to textarea if needed
                            const outputTextarea = document.querySelector('div.monaco-editor[data-uri=\"inmemory://model/2\"] textarea.inputarea.monaco-mouse-cursor-text');
                            return outputTextarea ? outputTextarea.value : null;
                        }
                    """)
                    if csharp_code and csharp_code.strip():
                        csharp_code = csharp_code.strip()
                        # Check if content is stable (not changing)
                        if previous_content == csharp_code:
                            stable_count += 1
                            logger.info(f"Content stable for {stable_count} consecutive checks")
                        else:
                            stable_count = 0
                            logger.info("Content changed, resetting stability counter")
                        previous_content = csharp_code
                        # Validate the content looks like proper C# code
                        if len(csharp_code) > 100 and 'using' in csharp_code.lower() and '{' in csharp_code and '}' in csharp_code:
                            # Content looks good and is stable
                            if stable_count >= required_stable_checks:
                                logger.info(f"Conversion complete and stable after {waited_time} seconds")
                                break
                        elif len(csharp_code) > 50:
                            logger.info(f"Content found but still converting... ({len(csharp_code)} chars)")
                        else:
                            logger.warning(f"Content too short, might be corrupted: {len(csharp_code)} chars")
                    await asyncio.sleep(wait_interval)
                    waited_time += wait_interval
                    if waited_time % 5 == 0:
                        logger.info(f"Still waiting for conversion... ({waited_time}s elapsed)")
                except Exception as e:
                    logger.warning(f"Error checking output: {e}")
                    await asyncio.sleep(wait_interval)
                    waited_time += wait_interval
            # Final check for content - try all methods one more time
            if not csharp_code or not csharp_code.strip():
                logger.info("Trying final extraction methods...")
                # Try all extraction methods one final time
                extraction_methods = [
                    ("monaco_api_output", lambda: page.evaluate("""
                        () => {
                            if (window.monaco && window.monaco.editor && window.monaco.editor.getModels().length > 1) {
                                return window.monaco.editor.getModels()[1].getValue();
                            }
                            return null;
                        }
                    """)),
                    ("output_textarea", lambda: page.evaluate("""
                        () => {
                            const outputTextarea = document.querySelector('div.monaco-editor[data-uri=\"inmemory://model/2\"] textarea.inputarea.monaco-mouse-cursor-text');
                            return outputTextarea ? outputTextarea.value : null;
                        }
                    """)),
                    ("text_content", lambda: output_field.text_content()),
                    ("input_value", lambda: output_field.input_value()),
                ]
                for method_name, method_func in extraction_methods:
                    try:
                        csharp_code = await method_func()
                        if csharp_code and csharp_code.strip():
                            logger.info(f"Final extraction succeeded using {method_name}")
                            break
                    except Exception as e:
                        logger.warning(f"Final extraction method {method_name} failed: {e}")
                        continue
            
            # Validate the extracted C# code
            if csharp_code:
                csharp_code = csharp_code.strip()
                logger.info(f"Extracted C# code length: {len(csharp_code)} characters")
                
                # Check if the code looks complete and valid
                if len(csharp_code) < 100:
                    logger.warning("Extracted C# code seems too short, might be incomplete")
                elif not ('using' in csharp_code.lower() or 'namespace' in csharp_code.lower()):
                    logger.warning("Extracted C# code doesn't contain expected C# keywords")
                elif not ('{' in csharp_code and '}' in csharp_code):
                    logger.warning("Extracted C# code doesn't contain braces, might be incomplete")
                elif csharp_code.count('{') != csharp_code.count('}'):
                    logger.warning("Extracted C# code has mismatched braces, might be incomplete")
                elif 'end class' in csharp_code.lower() or 'end namespace' in csharp_code.lower():
                    logger.warning("Extracted C# code contains VB.NET keywords, conversion may have failed")
                else:
                    logger.info("C# code validation passed - looks like complete, valid C# code")
            
            logger.info("Conversion completed successfully")
            return csharp_code
            
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        raise
    finally:
        # Ensure browser is closed even if an error occurs
        if page:
            try:
                await page.close()
            except:
                pass
        if context:
            try:
                await context.close()
            except:
                pass
        if browser:
            try:
                await browser.close()
            except:
                pass


def convert_vb_to_csharp(vb_code: str) -> str:
    """
    Synchronous wrapper for the async conversion function.
    
    Args:
        vb_code (str): The VB.NET code to convert
        
    Returns:
        str: The converted C# code
        
    Raises:
        Exception: If conversion fails
    """
    if not vb_code or not vb_code.strip():
        raise ValueError("VB.NET code cannot be empty")
    
    try:
        return asyncio.run(convert_vb_to_csharp_async(vb_code))
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        raise


def load_existing_examples(file_path: str) -> List[Dict]:
    """Load existing conversion examples from a JSONL file."""
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


def save_to_jsonl(examples: List[ConversionExample], output_file: str, append: bool = False):
    """Save conversion examples to a JSONL file."""
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


def validate_vb_code(vb_code: str) -> bool:
    """Validate that the input looks like valid VB.NET code."""
    if len(vb_code.strip()) < 10:
        print("❌ VB.NET code is too short. Please provide more substantial code.")
        return False
    
    # Check for basic VB.NET indicators
    vb_lower = vb_code.lower()
    vb_indicators = ['dim ', 'sub ', 'function ', 'end sub', 'end function', 
                    'if ', 'then', 'else', 'for ', 'next', 'while ', 'wend',
                    'try ', 'catch ', 'finally ', 'end try', 'with ', 'end with']
    
    if not any(indicator in vb_lower for indicator in vb_indicators):
        print("⚠️  Warning: This doesn't look like typical VB.NET code.")
        print("   Common VB.NET keywords: Dim, Sub, Function, End Sub, If, Then, etc.")
    
    return True


def add_single_conversion() -> Optional[ConversionExample]:
    """Add a single conversion example through user input."""
    print(f"\n{'='*60}")
    print("📝 Adding New VB.NET to C# Conversion")
    print(f"{'='*60}")
    
    # Get title (optional)
    title = input("\n📋 Title (optional, press Enter to skip): ").strip()
    
    # Get description (optional)
    description = input("📄 Description (optional, press Enter to skip): ").strip()
    
    # Get VB.NET code
    vb_code = get_multiline_input("🔵 Please paste your VB.NET code:")
    if not validate_vb_code(vb_code):
        return None
    
    # Convert to C#
    print("\n🔄 Converting VB.NET to C#...")
    try:
        csharp_code = convert_vb_to_csharp(vb_code)
        print("✅ Conversion successful!")
    except Exception as e:
        print(f"❌ Conversion failed: {str(e)}")
        return None
    
    # Create example
    example = ConversionExample(
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
    print("📋 Preview of your conversion:")
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
        confirm = input(f"\n🤔 Save this conversion? (y/n): ").lower().strip()
        if confirm in ['y', 'yes']:
            return example
        elif confirm in ['n', 'no']:
            return None
        else:
            print("❌ Please enter 'y' or 'n'")


def interactive_conversion(output_file: str, append: bool = False):
    """Interactive conversion session."""
    examples = []
    
    if append and Path(output_file).exists():
        existing = load_existing_examples(output_file)
        print(f"📊 Found {len(existing)} existing examples")
    
    print(f"\n🎯 Starting VB.NET to C# conversion session")
    print(f"📁 Output file: {output_file}")
    print(f"📝 Mode: {'Append' if append else 'Create new'}")
    
    while True:
        print(f"\n{'='*60}")
        print("🤔 What would you like to do?")
        print("  [c] Convert VB.NET to C#")
        print("  [s] Save current conversions and exit")
        print("  [q] Quit without saving")
        print("  [h] Show help")
        
        choice = input("\nEnter your choice: ").lower().strip()
        
        if choice == 'c':
            example = add_single_conversion()
            if example:
                examples.append(example)
                print(f"✅ Added conversion #{len(examples)}")
            else:
                print("❌ Conversion not added")
        
        elif choice == 's':
            if examples:
                save_to_jsonl(examples, output_file, append=append)
                print(f"🎉 Successfully saved {len(examples)} conversions!")
            else:
                print("⚠️  No conversions to save")
            break
        
        elif choice == 'q':
            if examples:
                confirm = input(f"⚠️  You have {len(examples)} unsaved conversions. Quit anyway? (y/n): ").lower().strip()
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
    print(f"\n📖 VB.NET to C# Converter Help:")
    print("  c - Convert: Convert VB.NET code to C# using ICSharpCode converter")
    print("  s - Save: Save all conversions to the JSONL file and exit")
    print("  q - Quit: Exit without saving (you'll be warned if you have unsaved conversions)")
    print("  h - Help: Show this help message")
    print(f"\n💡 Tips for good conversions:")
    print("  - Provide complete VB.NET code snippets (functions, classes, etc.)")
    print("  - Add descriptive titles and descriptions when helpful")
    print("  - The converter will automatically convert your VB.NET code to C#")
    print("  - Review the conversion before saving")
    print("  - Use proper indentation and formatting in your VB.NET code")
    print(f"\n🔧 Technical details:")
    print("  - Conversions are marked with 'converted_automatically': true")
    print("  - Source URL is set to 'icsharpcode_converter'")
    print("  - Code is automatically stripped of leading/trailing whitespace")
    print("  - Uses headless browser automation for reliable conversion")
    print(f"  - File size limit: {MAX_FILE_SIZE_BYTES} bytes")
    print(f"  - Code length limit: {MAX_CODE_LENGTH_CHARS} characters")


def convert_file(input_file: str, output_file: str, append: bool = False):
    """Convert VB.NET code from a file to C# and save to JSONL."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            vb_code = f.read()
        
        print(f"📖 Reading VB.NET code from {input_file}...")
        print(f"📝 Code length: {len(vb_code)} characters")
        
        if not validate_vb_code(vb_code):
            print("❌ Invalid VB.NET code in file")
            return
        
        print("🔄 Converting VB.NET to C#...")
        csharp_code = convert_vb_to_csharp(vb_code)
        print("✅ Conversion successful!")
        
        # Create example
        example = ConversionExample(
            vb_code=vb_code,
            csharp_code=csharp_code,
            title=f"File: {Path(input_file).name}",
            description=f"Converted from file: {input_file}"
        )
        
        if example.is_valid():
            save_to_jsonl([example], output_file, append=append)
            print(f"🎉 Successfully saved conversion to {output_file}")
        else:
            print("❌ Invalid conversion result")
            
    except Exception as e:
        print(f"❌ Error processing file {input_file}: {str(e)}")


def main():
    """Main function to run the VB.NET to C# converter."""
    parser = argparse.ArgumentParser(description='VB.NET to C# Converter using ICSharpCode')
    parser.add_argument('--output', '-o', default='conversions.jsonl', 
                       help='Output JSONL file (default: conversions.jsonl)')
    parser.add_argument('--append', '-a', action='store_true', 
                       help='Append to existing file instead of overwriting')
    parser.add_argument('--interactive', '-i', action='store_true', default=True,
                       help='Run in interactive mode (default)')
    parser.add_argument('--file', '-f', help='Convert VB.NET code from a file')
    parser.add_argument('--code', '-c', help='Convert VB.NET code string directly')
    
    # New batch processing arguments
    parser.add_argument('--directory', '-d', help='Convert all VB files in a directory')
    parser.add_argument('--file-list', '-l', help='Convert VB files listed in a text file (one path per line)')
    parser.add_argument('--recursive', '-r', action='store_true', default=True,
                       help='Search directories recursively for VB files (default: True)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between conversions in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.directory:
        # Batch convert from directory
        vb_files = load_vb_files_from_directory(args.directory, args.recursive)
        if vb_files:
            batch_convert_vb_files(vb_files, args.output, args.append, args.delay)
        else:
            print("❌ No VB files found in directory")
    
    elif args.file_list:
        # Batch convert from file list
        vb_files = load_vb_files_from_list(args.file_list)
        if vb_files:
            batch_convert_vb_files(vb_files, args.output, args.append, args.delay)
        else:
            print("❌ No valid VB files found in file list")
    
    elif args.file:
        # Convert from file
        convert_file(args.file, args.output, args.append)
    
    elif args.code:
        # Convert from command line argument
        try:
            print("🔄 Converting VB.NET to C#...")
            csharp_code = convert_vb_to_csharp(args.code)
            print("✅ Conversion successful!")
            print(f"\n🟢 C# Code:")
            print("-" * 40)
            print(csharp_code)
            
            # Save to file if requested
            if args.output:
                example = ConversionExample(
                    vb_code=args.code,
                    csharp_code=csharp_code,
                    title="Command line conversion",
                    description="Converted from command line input"
                )
                save_to_jsonl([example], args.output, args.append)
                
        except Exception as e:
            print(f"❌ Conversion failed: {str(e)}")
    
    elif args.interactive:
        # Interactive mode
        interactive_conversion(args.output, args.append)
    
    else:
        print("❌ No mode specified. Use --interactive, --file, --code, --directory, or --file-list")
        print("\n📖 Available modes:")
        print("  --interactive, -i     : Interactive mode (default)")
        print("  --file, -f <file>     : Convert single VB file")
        print("  --code, -c <code>     : Convert VB code string")
        print("  --directory, -d <dir> : Convert all VB files in directory")
        print("  --file-list, -l <file>: Convert VB files listed in text file")


if __name__ == "__main__":
    main() 