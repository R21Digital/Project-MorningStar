#!/usr/bin/env python3
"""
Script to verify Google Analytics integration in all HTML files.
This script checks that the tracking code is present and properly formatted.
"""

import os
import re
from pathlib import Path

def verify_google_analytics_in_file(file_path):
    """Verify Google Analytics tracking code in a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the tracking ID
        if 'G-Q4ZZ5SFJC0' not in content:
            return False, "Tracking ID not found"
        
        # Check for the gtag script
        if 'googletagmanager.com/gtag/js' not in content:
            return False, "gtag script not found"
        
        # Check for the dataLayer initialization
        if 'window.dataLayer' not in content:
            return False, "dataLayer not initialized"
        
        # Check for the gtag config (handle both simple and complex configurations)
        if 'gtag(\'config\', \'G-Q4ZZ5SFJC0\')' not in content and 'gtag(\'config\', \'G-Q4ZZ5SFJC0\',' not in content:
            return False, "gtag config not found"
        
        # Check for noscript fallback
        if 'noscript' not in content or 'googletagmanager.com/ns.html' not in content:
            return False, "noscript fallback not found"
        
        return True, "All checks passed"
        
    except Exception as e:
        return False, f"Error reading file: {e}"

def find_html_files(directory):
    """Find all HTML files in the given directory and subdirectories."""
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def main():
    """Main function to verify Google Analytics integration."""
    swgdb_site_dir = Path("swgdb_site")
    
    if not swgdb_site_dir.exists():
        print("✗ swgdb_site directory not found!")
        return
    
    html_files = find_html_files(swgdb_site_dir)
    
    if not html_files:
        print("✗ No HTML files found in swgdb_site directory!")
        return
    
    print(f"Verifying Google Analytics integration in {len(html_files)} HTML files...")
    print()
    
    passed_count = 0
    failed_count = 0
    failed_files = []
    
    for html_file in html_files:
        is_valid, message = verify_google_analytics_in_file(html_file)
        
        if is_valid:
            print(f"✓ {html_file}")
            passed_count += 1
        else:
            print(f"✗ {html_file} - {message}")
            failed_count += 1
            failed_files.append((html_file, message))
    
    print()
    print("=" * 50)
    print("VERIFICATION SUMMARY:")
    print(f"✓ Files with valid GA integration: {passed_count}")
    print(f"✗ Files with issues: {failed_count}")
    print(f"Total files checked: {len(html_files)}")
    
    if failed_files:
        print()
        print("Files with issues:")
        for file_path, message in failed_files:
            print(f"  - {file_path}: {message}")
    
    print()
    if failed_count == 0:
        print("🎉 All files have proper Google Analytics integration!")
        print()
        print("Next steps for verification:")
        print("1. Deploy the site to production")
        print("2. Visit the site and check Google Analytics Real-Time reports")
        print("3. Verify tracking in Google Search Console")
        print("4. Test the noscript fallback by disabling JavaScript")
    else:
        print("⚠️  Some files need attention. Please check the issues above.")

if __name__ == "__main__":
    main() 