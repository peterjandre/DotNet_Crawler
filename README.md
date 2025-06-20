# VB.NET to C# Translation Web Crawler

A Python-based web crawler designed to extract VB.NET to C# translation examples from websites for building training datasets to fine-tune language models.

## Features

- **BeautifulSoup Integration**: Uses BeautifulSoup for HTML parsing and content extraction
- **Playwright Support**: Optional Playwright integration for JavaScript-heavy websites
- **Progress Tracking**: Uses tqdm for progress bars during crawling
- **Flexible Input**: Accept URLs via command line arguments or text files
- **JSONL Output**: Saves translation examples in JSONL format for easy processing
- **Incremental Building**: Append new examples to existing datasets
- **Smart Detection**: Automatically identifies VB.NET and C# code blocks
- **Translation Pairing**: Intelligently pairs VB.NET and C# code that likely represent translations
- **Interactive Cleaning**: Review and clean datasets example by example

## Installation

1. **Clone or download this repository**
   ```bash
   cd DotNet_Crawler
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers** (optional, only if using Playwright)
   ```bash
   playwright install
   ```

## Usage

### Basic Usage

Crawl a single URL:
```bash
python crawler.py --urls "https://example.com/vb-csharp-translation"
```

Crawl multiple URLs:
```bash
python crawler.py --urls "https://site1.com" "https://site2.com" "https://site3.com"
```

### Using URL Files

Create a text file with URLs (one per line):
```bash
python crawler.py --url-file sample_urls.txt
```

### Building Datasets Incrementally

**Append new examples to an existing dataset:**
```bash
python crawler.py --url-file new_urls.txt --output dataset.jsonl --append
```

**Create a new dataset (overwrites existing file):**
```bash
python crawler.py --url-file urls.txt --output dataset.jsonl
```

### Advanced Options

Use Playwright for JavaScript-heavy sites:
```bash
python crawler.py --url-file urls.txt --use-playwright --append
```

Specify custom output file:
```bash
python crawler.py --urls "https://example.com" --output my_translations.jsonl --append
```

Enable verbose logging:
```bash
python crawler.py --urls "https://example.com" --verbose --append
```

### Command Line Arguments

- `--urls`, `-u`: Space-separated list of URLs to crawl
- `--url-file`, `-f`: Path to a text file containing URLs (one per line)
- `--output`, `-o`: Output JSONL file path (default: `translations.jsonl`)
- `--append`, `-a`: Append to existing file instead of overwriting
- `--use-playwright`: Use Playwright for JavaScript-heavy websites
- `--headless`: Run browser in headless mode (default: True)
- `--verbose`, `-v`: Enable verbose logging

## Dataset Cleaning

The `clean_dataset.py` script provides an interactive way to review and clean your translation examples, removing poor quality or irrelevant entries.

### Features

- **Interactive Review**: Examine each translation example one by one
- **Full Text Viewing**: Toggle between preview and full text mode
- **Issue Detection**: Automatically flags potential problems
- **Progress Tracking**: Resume cleaning from where you left off
- **Quality Assessment**: Statistics and metrics for each example

### Usage

**Basic cleaning:**
```bash
python clean_dataset.py dataset.jsonl
```

**With custom output file:**
```bash
python clean_dataset.py dataset.jsonl --output cleaned_dataset.jsonl
```

**Resume from a specific example:**
```bash
python clean_dataset.py dataset.jsonl --start-from 10
```

### Interactive Commands

When reviewing examples, you can use these commands:

- `k` - **Keep**: This example is good quality, keep it in the dataset
- `d` - **Delete**: This example is poor quality, remove it from the dataset
- `s` - **Skip**: Skip this example for now (keep it but mark as reviewed)
- `f` - **Full text**: Toggle between preview and full text view
- `q` - **Quit**: Save progress and exit
- `h` - **Help**: Show help information

### Command Line Arguments

- `input_file`: Input JSONL file to clean (required)
- `--output`, `-o`: Output file (default: `input_cleaned.jsonl`)
- `--start-from`, `-s`: Start from example number (0-indexed)
- `--exclude-manual`: Exclude manually curated examples from cleaning
- `--manual-only`: Only clean manually curated examples

### Example Workflow

1. **Crawl websites to build initial dataset:**
   ```bash
   python crawler.py --url-file urls.txt --output raw_dataset.jsonl
   ```

2. **Clean the dataset interactively:**
   ```bash
   python clean_dataset.py raw_dataset.jsonl --output clean_dataset.jsonl
   ```

3. **Analyze the cleaned dataset:**
   ```bash
   python analyze_data.py clean_dataset.jsonl --stats-only
   ```

4. **Review only manual examples:**
   ```bash
   python clean_dataset.py clean_dataset.jsonl --manual-only
   ```

## Manual Curation

The `manual_curation.py` script allows you to manually add VB.NET to C# translation examples by copying and pasting them directly into the terminal. This is useful for adding high-quality examples that you find through other means.

### Features

- **Interactive Input**: Copy and paste VB.NET and C# code directly into the terminal
- **Multiline Support**: Properly handles code with multiple lines and line breaks
- **Validation**: Checks that input looks like valid VB.NET and C# code
- **Preview**: Shows a preview of your example before saving
- **Append Mode**: Add examples to existing JSONL files
- **Manual Flagging**: Automatically marks examples as manually curated
- **Metadata Support**: Add optional titles and descriptions

### Usage

**Create a new manual curation file:**
```bash
python manual_curation.py --output manual_examples.jsonl
```

**Append to existing file:**
```bash
python manual_curation.py --output dataset.jsonl --append
```

**With custom output file:**
```bash
python manual_curation.py --output my_manual_examples.jsonl
```

### Interactive Commands

When adding examples, you can use these commands:

- `a` - **Add**: Add a new VB.NET to C# translation example
- `s` - **Save**: Save all examples to the JSONL file and exit
- `q` - **Quit**: Exit without saving (you'll be warned if you have unsaved examples)
- `h` - **Help**: Show help information

### Input Process

1. **Title** (optional): Add a descriptive title for the example
2. **Description** (optional): Add additional context or notes
3. **VB.NET Code**: Paste your VB.NET code (press Enter twice to finish)
4. **C# Code**: Paste your C# code (press Enter twice to finish)
5. **Preview**: Review your example with statistics
6. **Confirm**: Choose to save or discard the example

### Command Line Arguments

- `--output`, `-o`: Output JSONL file (default: `manual_translations.jsonl`)
- `--append`, `-a`: Append to existing file instead of overwriting
- `--interactive`, `-i`: Run in interactive mode (default)

### Manual Curation in Cleaning

When using the cleaning script, manually curated examples are clearly marked and can be filtered:

**Exclude manually curated examples:**
```bash
python clean_dataset.py dataset.jsonl --exclude-manual
```

**Only clean manually curated examples:**
```bash
python clean_dataset.py dataset.jsonl --manual-only
```

### Example Workflow with Manual Curation

1. **Start with web crawling:**
   ```bash
   python crawler.py --url-file urls.txt --output dataset.jsonl
   ```

2. **Add manual examples:**
   ```bash
   python manual_curation.py --output dataset.jsonl --append
   ```

3. **Clean the combined dataset:**
   ```bash
   python clean_dataset.py dataset.jsonl --output clean_dataset.jsonl
   ```

4. **Review only manual examples:**
   ```bash
   python clean_dataset.py clean_dataset.jsonl --manual-only
   ```

## Testing

The project includes several test scripts located in the `test_scripts/` folder to verify functionality:

### Available Tests

- **`test_manual_curation.py`**: Tests the manual curation functionality, including validation, JSON serialization, and file saving
- **`test_crawler.py`**: Tests the web crawler with a real URL to verify extraction and translation pairing
- **`test_table_extraction.py`**: Tests the table extraction logic using the included Test_Comparison.html file

### Running Tests

**Run all tests:**
```bash
python test_scripts/test_manual_curation.py
python test_scripts/test_crawler.py
python test_scripts/test_table_extraction.py
```

**Test manual curation functionality:**
```bash
python test_scripts/test_manual_curation.py
```

**Test web crawler with real URL:**
```bash
python test_scripts/test_crawler.py
```

**Test table extraction logic:**
```bash
python test_scripts/test_table_extraction.py
```

### Test Coverage

The tests verify:
- Manual curation example creation and validation
- JSON serialization with proper line break handling
- Web crawler functionality with real URLs
- Table-based code extraction from HTML files
- Translation pairing algorithms
- File I/O operations

## Output Format

The crawler generates a JSONL file where each line contains a JSON object with the following structure:

```json
{
  "vb_code": "Dim message As String = \"Hello World\"\nConsole.WriteLine(message)",
  "csharp_code": "string message = \"Hello World\";\nConsole.WriteLine(message);",
  "source_url": "https://example.com/translation-page",
  "title": "String Variable Declaration",
  "description": "How to declare and use string variables",
  "manually_curated": false
}
```

**Field Descriptions:**
- `vb_code`: The VB.NET code snippet (line breaks preserved as `\n`)
- `csharp_code`: The C# code snippet (line breaks preserved as `\n`)
- `source_url`: The URL where the example was found (or "manual_curation" for manually added examples)
- `title`: Optional title or heading for the example
- `description`: Optional description or context for the example
- `manually_curated`: Boolean flag indicating if the example was manually curated (only present for manual examples)

## How It Works

1. **Content Fetching**: Uses either `requests` (default) or `Playwright` to fetch web page content
2. **Content Analysis**: Checks if the page likely contains translation content using keyword detection
3. **Code Extraction**: Uses regex patterns and BeautifulSoup to extract VB.NET and C# code blocks
4. **Translation Pairing**: Intelligently pairs VB.NET and C# code that likely represent translations
5. **Validation**: Ensures extracted examples are valid (sufficient length, different content)
6. **Output**: Saves valid translation examples to JSONL format (overwrite or append)

## Code Detection Patterns

The crawler looks for VB.NET and C# code using various patterns:

### VB.NET Patterns
- Markdown code blocks: ````vb` or ````vb.net`
- HTML code blocks with `vb` or `vb.net` class
- Text patterns like "VB.NET:" or "Visual Basic:"
- Keywords: `Dim`, `Sub`, `Function`, `End Sub`, `End Function`

### C# Patterns
- Markdown code blocks: ````csharp` or ````cs`
- HTML code blocks with `csharp` class
- Text patterns like "C#:"
- Keywords: `var`, `public`, `private`, `class`, `namespace`

## Example Workflow

1. **Initial Dataset Creation**:
   ```bash
   python crawler.py --url-file initial_urls.txt --output dataset.jsonl
   ```

2. **Add More Examples** (append mode):
   ```bash
   python crawler.py --url-file more_urls.txt --output dataset.jsonl --append
   ```

3. **Clean the Dataset**:
   ```bash
   python clean_dataset.py dataset.jsonl --output clean_dataset.jsonl
   ```