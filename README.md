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

## Output Format

The crawler generates a JSONL file where each line contains a JSON object with the following structure:

```json
{
  "vb_code": "Dim message As String = \"Hello World\"\nConsole.WriteLine(message)",
  "csharp_code": "string message = \"Hello World\";\nConsole.WriteLine(message);",
  "source_url": "https://example.com/translation-page",
  "title": "String Variable Declaration",
  "description": "How to declare and use string variables"
}
```

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

4. **Check Dataset Size**:
   ```bash
   wc -l clean_dataset.jsonl  # Count number of examples
   ```

5. **Analyze Dataset**:
   ```bash
   python analyze_data.py clean_dataset.jsonl --stats-only
   ```

## Tips for Better Results

1. **Target Specific Sites**: Focus on sites known to have VB.NET to C# translations
2. **Use Playwright**: For JavaScript-heavy sites, use the `--use-playwright` flag
3. **Be Patient**: The crawler includes delays to be respectful to servers
4. **Review Output**: Always review the generated examples for quality
5. **Filter Results**: Post-process the JSONL file to remove low-quality examples
6. **Build Incrementally**: Use `--append` to build your dataset over time
7. **Clean Regularly**: Use the cleaning script to maintain dataset quality

## Troubleshooting

### Common Issues

**"No translation examples found"**
- The URLs might not contain VB.NET to C# translations
- Try using `--verbose` to see what content is being detected
- Check if the site requires JavaScript (use `--use-playwright`)

**"Failed to fetch URL"**
- Check your internet connection
- The site might be blocking automated requests
- Try using `--use-playwright` for JavaScript-heavy sites

**Playwright Installation Issues**
- Make sure you have the latest version of Playwright
- Run `playwright install` to install browser binaries
- On some systems, you might need to install additional dependencies

### Performance Tips

- Use `--headless` for faster execution (default)
- Process URLs in batches if you have many URLs
- Consider using a proxy if you're crawling many sites
- Use `--append` to build datasets incrementally without losing previous work

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the crawler.

## License

This project is open source and available under the MIT License. 