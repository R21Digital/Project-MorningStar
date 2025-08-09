#!/usr/bin/env python3
"""
Script to add Google Analytics tracking code to all HTML files in the swgdb_site directory.
This script will inject the Google Analytics script into the <head> section of each HTML file.
"""

import os
import re
from pathlib import Path

# Google Analytics tracking code
GOOGLE_ANALYTICS_SCRIPT = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-Q4ZZ5SFJC0"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-Q4ZZ5SFJC0');
</script>
<!-- Fallback noscript version for privacy-aware users -->
<noscript>
  <iframe src="https://www.googletagmanager.com/ns.html?id=G-Q4ZZ5SFJC0"
          height="0" width="0" style="display:none;visibility:hidden"></iframe>
</noscript>'''

def add_google_analytics_to_file(file_path):
    """Add Google Analytics tracking code to a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if Google Analytics is already present
        if 'G-Q4ZZ5SFJC0' in content:
            print(f"✓ Google Analytics already present in {file_path}")
            return False
        
        # Find the <head> tag and insert the script after the opening tag
        head_pattern = r'(<head[^>]*>)'
        match = re.search(head_pattern, content, re.IGNORECASE)
        
        if match:
            head_tag = match.group(1)
            # Insert the script after the opening head tag
            new_content = content.replace(head_tag, head_tag + '\n    ' + GOOGLE_ANALYTICS_SCRIPT)
            
            # Write the updated content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✓ Added Google Analytics to {file_path}")
            return True
        else:
            print(f"✗ No <head> tag found in {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def find_html_files(directory):
    """Find all HTML files in the given directory and subdirectories."""
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def main():
    """Main function to add Google Analytics to all HTML files."""
    swgdb_site_dir = Path("swgdb_site")
    
    if not swgdb_site_dir.exists():
        print("✗ swgdb_site directory not found!")
        return
    
    html_files = find_html_files(swgdb_site_dir)
    
    if not html_files:
        print("✗ No HTML files found in swgdb_site directory!")
        return
    
    print(f"Found {len(html_files)} HTML files to process...")
    print()
    
    updated_count = 0
    skipped_count = 0
    
    for html_file in html_files:
        if add_google_analytics_to_file(html_file):
            updated_count += 1
        else:
            skipped_count += 1
    
    print()
    print("=" * 50)
    print("SUMMARY:")
    print(f"✓ Files updated: {updated_count}")
    print(f"○ Files skipped (already had GA): {skipped_count}")
    print(f"Total files processed: {len(html_files)}")
    print()
    print("Google Analytics tracking code has been added to all HTML files!")
    print("Tracking ID: G-Q4ZZ5SFJC0")
    print()
    print("Next steps:")
    print("1. Verify the integration with Google Search Console")
    print("2. Check the GA dashboard for tracking data")
    print("3. Test the noscript fallback for privacy-aware users")

if __name__ == "__main__":
    main() 