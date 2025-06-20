#!/usr/bin/env python3
"""
Setup script for VB.NET to C# Translation Web Crawler
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("Setting up VB.NET to C# Translation Web Crawler")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Failed to install dependencies. Please check your pip installation.")
        sys.exit(1)
    
    # Install Playwright browsers (optional)
    print("\nInstalling Playwright browsers (optional, for JavaScript-heavy sites)...")
    if run_command("playwright install", "Installing Playwright browsers"):
        print("✓ Playwright browsers installed successfully")
    else:
        print("⚠ Playwright installation failed. You can still use the crawler with BeautifulSoup only.")
    
    # Make scripts executable
    scripts = ["crawler.py", "example_usage.py", "test_crawler.py"]
    for script in scripts:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            print(f"✓ Made {script} executable")
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Test the crawler: python test_crawler.py")
    print("2. Run the crawler: python crawler.py --help")
    print("3. Add URLs to sample_urls.txt and run: python crawler.py --url-file sample_urls.txt")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 