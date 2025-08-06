#!/usr/bin/env python3
"""
SWGDB Analytics Integration Script
Automatically adds Google Analytics and SEO meta tags to all HTML pages
"""

import os
import re
import glob
from pathlib import Path

def add_analytics_to_html(file_path):
    """Add analytics include to HTML files"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if analytics is already included
    if '<!-- Google Analytics v4 -->' in content:
        print(f"Analytics already present in {file_path}")
        return False
    
    # Find the head tag and add analytics before closing head
    head_pattern = r'(<head[^>]*>)(.*?)(</head>)'
    match = re.search(head_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if match:
        head_open = match.group(1)
        head_content = match.group(2)
        head_close = match.group(3)
        
        # Add analytics include
        analytics_include = '\n  <%- include(\'../_includes/analytics.html\') %>\n  '
        
        new_head = head_open + head_content + analytics_include + head_close
        new_content = content.replace(match.group(0), new_head)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Added analytics to {file_path}")
        return True
    
    return False

def update_meta_tags(file_path):
    """Update meta tags for better SEO"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract page title for dynamic meta description
    title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
    if title_match:
        page_title = title_match.group(1).strip()
        
        # Generate meta description based on page content
        if 'heroics' in file_path.lower():
            meta_desc = f"SWGDB Heroics - {page_title} - Star Wars Galaxies heroic instance information and strategies"
        elif 'loot' in file_path.lower():
            meta_desc = f"SWGDB Loot - {page_title} - Star Wars Galaxies loot drops and item information"
        elif 'builds' in file_path.lower():
            meta_desc = f"SWGDB Builds - {page_title} - Star Wars Galaxies character builds and optimization"
        else:
            meta_desc = f"SWGDB - {page_title} - Star Wars Galaxies database and tools"
        
        # Add or update meta description
        meta_desc_pattern = r'<meta[^>]*name=["\']description["\'][^>]*>'
        new_meta_desc = f'<meta name="description" content="{meta_desc}">'
        
        if re.search(meta_desc_pattern, content):
            content = re.sub(meta_desc_pattern, new_meta_desc, content)
        else:
            # Add after title tag
            content = re.sub(r'(<title[^>]*>.*?</title>)', r'\1\n  ' + new_meta_desc, content, flags=re.IGNORECASE | re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated meta tags in {file_path}")

def main():
    """Main deployment function"""
    
    print("SWGDB Analytics Integration")
    print("=" * 40)
    
    # Find all HTML files
    html_files = glob.glob('**/*.html', recursive=True)
    
    analytics_added = 0
    meta_updated = 0
    
    for html_file in html_files:
        # Skip _includes directory
        if '_includes' in html_file:
            continue
            
        print(f"\nProcessing: {html_file}")
        
        # Add analytics
        if add_analytics_to_html(html_file):
            analytics_added += 1
        
        # Update meta tags
        update_meta_tags(html_file)
        meta_updated += 1
    
    print(f"\nDeployment Summary:")
    print(f"- Analytics added to {analytics_added} files")
    print(f"- Meta tags updated in {meta_updated} files")
    print(f"\nNext Steps:")
    print("1. Replace 'G-XXXXXXX' with your actual Google Analytics ID")
    print("2. Replace 'your-verification-code-here' with your Google Search Console verification code")
    print("3. Submit sitemap.xml to Google Search Console")
    print("4. Test analytics tracking in Google Analytics")

if __name__ == "__main__":
    main() 