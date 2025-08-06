#!/usr/bin/env python3
"""
Demo script for Batch 108 - Mods & Plugin Hub (Public)

This script demonstrates the mods hub functionality:
- Mod submission and approval workflow
- Category management
- File upload and storage
- Public browsing and downloading
- Admin approval system
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from core.mods_hub_manager import (
    mods_hub_manager,
    ModCategory,
    ModType,
    ModStatus
)


def create_sample_mods():
    """Create sample mods for demonstration."""
    
    sample_mods = [
        {
            "title": "Enhanced UI Pack",
            "description": "A comprehensive UI enhancement pack that improves the visual appearance and usability of the SWG interface. Includes custom icons, improved layouts, and better color schemes.",
            "category": ModCategory.UI_ENHANCEMENTS,
            "mod_type": ModType.FILE,
            "author": "SWGModder",
            "author_email": "swgmodder@example.com",
            "version": "2.1.0",
            "swg_version": "NGE",
            "tags": ["ui", "enhancement", "visual", "interface"],
            "dependencies": ["SWG Base Client"],
            "installation_notes": "1. Extract the ZIP file to your SWG directory\n2. Run the installer.bat file\n3. Restart SWG\n4. Enjoy your enhanced UI!",
            "changelog": "v2.1.0 - Added new icon set\nv2.0.0 - Complete UI overhaul\nv1.0.0 - Initial release",
            "status": ModStatus.APPROVED,
            "featured": True,
            "views": 1250,
            "downloads": 342,
            "rating": 4.5,
            "rating_count": 28
        },
        {
            "title": "Combat Macro Collection",
            "description": "A collection of advanced combat macros for different professions. Includes macros for Jedi, Bounty Hunters, Commandos, and more.",
            "category": ModCategory.MACROS_KEYBINDS,
            "mod_type": ModType.TEXT,
            "author": "CombatMaster",
            "author_email": "combat@example.com",
            "version": "1.3.2",
            "swg_version": "NGE",
            "content": """
# Jedi Combat Macros
/script JediCombatMacro()

# Bounty Hunter Macros
/script BountyHunterMacro()

# Commando Macros
/script CommandoMacro()

# Installation Instructions
1. Copy the macro text
2. Paste into your macro editor
3. Save and assign to hotkeys
            """,
            "tags": ["combat", "macros", "jedi", "bounty hunter", "commando"],
            "dependencies": [],
            "installation_notes": "Copy and paste the macro text into your SWG macro editor.",
            "changelog": "v1.3.2 - Added Commando macros\nv1.3.0 - Added Bounty Hunter macros\nv1.0.0 - Initial Jedi macros",
            "status": ModStatus.APPROVED,
            "featured": False,
            "views": 890,
            "downloads": 156,
            "rating": 4.2,
            "rating_count": 15
        },
        {
            "title": "Crafting Helper Tool",
            "description": "A comprehensive crafting calculator and resource tracker. Helps optimize crafting recipes and track resource costs.",
            "category": ModCategory.CRAFTING_HELPERS,
            "mod_type": ModType.LINK,
            "author": "CraftingGuru",
            "author_email": "crafting@example.com",
            "version": "1.0.0",
            "swg_version": "NGE",
            "download_url": "https://example.com/crafting-helper.zip",
            "tags": ["crafting", "calculator", "resources", "optimization"],
            "dependencies": ["Excel or Google Sheets"],
            "installation_notes": "Download the file from the provided link and follow the included README.",
            "changelog": "v1.0.0 - Initial release with basic crafting calculations",
            "status": ModStatus.APPROVED,
            "featured": True,
            "views": 2100,
            "downloads": 567,
            "rating": 4.8,
            "rating_count": 45
        },
        {
            "title": "Realistic Shader Pack",
            "description": "High-quality shader pack that adds realistic lighting, shadows, and visual effects to SWG. Compatible with most graphics cards.",
            "category": ModCategory.VISUAL_MODS,
            "mod_type": ModType.FILE,
            "author": "GraphicsWizard",
            "author_email": "graphics@example.com",
            "version": "3.0.1",
            "swg_version": "NGE",
            "tags": ["shaders", "graphics", "lighting", "realistic"],
            "dependencies": ["DirectX 9.0c or higher"],
            "installation_notes": "1. Backup your SWG installation\n2. Extract shader files to SWG directory\n3. Run shader_installer.exe\n4. Configure graphics settings",
            "changelog": "v3.0.1 - Performance optimizations\nv3.0.0 - Complete shader overhaul\nv2.0.0 - Added new lighting effects",
            "status": ModStatus.APPROVED,
            "featured": True,
            "views": 3400,
            "downloads": 892,
            "rating": 4.7,
            "rating_count": 67
        },
        {
            "title": "Server Status Tracker",
            "description": "A utility tool that tracks server status, population, and performance metrics for various SWG servers.",
            "category": ModCategory.UTILITIES,
            "mod_type": ModType.SCRIPT,
            "author": "ServerTracker",
            "author_email": "server@example.com",
            "version": "1.2.0",
            "swg_version": "All",
            "content": """
#!/usr/bin/env python3
# Server Status Tracker
import requests
import json

def check_server_status(server_name):
    # Implementation here
    pass

def get_population_data():
    # Implementation here
    pass

# Usage instructions
print("Run this script to check server status")
            """,
            "tags": ["server", "status", "population", "utility"],
            "dependencies": ["Python 3.6+", "requests library"],
            "installation_notes": "1. Install Python 3.6 or higher\n2. Install requests: pip install requests\n3. Run the script: python server_tracker.py",
            "changelog": "v1.2.0 - Added population tracking\nv1.1.0 - Added performance metrics\nv1.0.0 - Basic server status",
            "status": ModStatus.PENDING,
            "featured": False,
            "views": 0,
            "downloads": 0,
            "rating": 0.0,
            "rating_count": 0
        }
    ]
    
    return sample_mods


def demo_mod_submission():
    """Demonstrate mod submission process."""
    print("\n" + "="*60)
    print("DEMO: Mod Submission Process")
    print("="*60)
    
    # Create a sample mod submission
    mod_id = mods_hub_manager.submit_mod(
        title="Demo Combat Enhancement",
        description="A demonstration combat enhancement mod for testing purposes.",
        category=ModCategory.UTILITIES,
        mod_type=ModType.TEXT,
        author="DemoUser",
        author_email="demo@example.com",
        version="1.0.0",
        swg_version="NGE",
        content="This is a demo mod content for testing the submission system.",
        tags=["demo", "combat", "test"],
        dependencies=[],
        installation_notes="This is a demo mod. No installation required.",
        changelog="v1.0.0 - Initial demo release"
    )
    
    print(f"[DEMO] Submitted mod with ID: {mod_id}")
    
    # Get the submitted mod
    mod = mods_hub_manager.get_mod(mod_id)
    if mod:
        print(f"[DEMO] Mod details:")
        print(f"  Title: {mod.title}")
        print(f"  Author: {mod.author}")
        print(f"  Status: {mod.status.value}")
        print(f"  Category: {mod.category.value}")
    
    return mod_id


def demo_mod_approval(mod_id):
    """Demonstrate mod approval process."""
    print("\n" + "="*60)
    print("DEMO: Mod Approval Process")
    print("="*60)
    
    # Approve the mod
    success = mods_hub_manager.approve_mod(mod_id, "demo_admin")
    
    if success:
        print(f"[DEMO] Successfully approved mod: {mod_id}")
        
        # Get updated mod
        mod = mods_hub_manager.get_mod(mod_id)
        if mod:
            print(f"[DEMO] Updated status: {mod.status.value}")
            print(f"[DEMO] Approved by: {mod.approved_by}")
            print(f"[DEMO] Approved at: {mod.approved_at}")
    else:
        print(f"[DEMO] Failed to approve mod: {mod_id}")


def demo_mod_browsing():
    """Demonstrate mod browsing functionality."""
    print("\n" + "="*60)
    print("DEMO: Mod Browsing")
    print("="*60)
    
    # Get approved mods
    approved_mods = mods_hub_manager.get_approved_mods()
    print(f"[DEMO] Found {len(approved_mods)} approved mods")
    
    # Get mods by category
    ui_mods = mods_hub_manager.get_approved_mods(category=ModCategory.UI_ENHANCEMENTS)
    print(f"[DEMO] Found {len(ui_mods)} UI enhancement mods")
    
    # Get popular mods
    popular_mods = mods_hub_manager.get_popular_mods(limit=5)
    print(f"[DEMO] Top 5 popular mods:")
    for i, mod in enumerate(popular_mods, 1):
        print(f"  {i}. {mod.title} by {mod.author} ({mod.downloads} downloads)")
    
    # Get featured mods
    featured_mods = mods_hub_manager.get_featured_mods()
    print(f"[DEMO] Found {len(featured_mods)} featured mods")


def demo_mod_rating(mod_id):
    """Demonstrate mod rating functionality."""
    print("\n" + "="*60)
    print("DEMO: Mod Rating")
    print("="*60)
    
    # Rate the mod
    success = mods_hub_manager.rate_mod(mod_id, 4.5, "demo_user_1")
    if success:
        print(f"[DEMO] Successfully rated mod {mod_id} with 4.5 stars")
    
    # Rate again
    success = mods_hub_manager.rate_mod(mod_id, 5.0, "demo_user_2")
    if success:
        print(f"[DEMO] Successfully rated mod {mod_id} with 5.0 stars")
    
    # Get updated mod
    mod = mods_hub_manager.get_mod(mod_id)
    if mod:
        print(f"[DEMO] Updated rating: {mod.rating:.1f} ({mod.rating_count} ratings)")


def demo_mod_management():
    """Demonstrate mod management functionality."""
    print("\n" + "="*60)
    print("DEMO: Mod Management")
    print("="*60)
    
    # Get pending mods
    pending_mods = mods_hub_manager.get_pending_mods()
    print(f"[DEMO] Found {len(pending_mods)} pending mods")
    
    # Get categories
    categories = mods_hub_manager.get_categories()
    print(f"[DEMO] Available categories:")
    for cat_id, cat_info in categories.items():
        print(f"  {cat_info.name}: {cat_info.mod_count} mods")
    
    # Get stats
    stats = mods_hub_manager.get_stats()
    print(f"[DEMO] Hub Statistics:")
    print(f"  Total mods: {stats['total_mods']}")
    print(f"  Approved: {stats['approved_mods']}")
    print(f"  Pending: {stats['pending_mods']}")
    print(f"  Featured: {stats['featured_mods']}")
    print(f"  Total downloads: {stats['total_downloads']}")


def demo_file_upload():
    """Demonstrate file upload functionality."""
    print("\n" + "="*60)
    print("DEMO: File Upload")
    print("="*60)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a demo mod file content.")
        temp_file_path = f.name
    
    try:
        # Validate file
        is_valid, error_msg = mods_hub_manager.validate_file_upload(temp_file_path)
        print(f"[DEMO] File validation: {'Valid' if is_valid else 'Invalid'}")
        if not is_valid:
            print(f"[DEMO] Error: {error_msg}")
        
        # Save uploaded file
        saved_path = mods_hub_manager.save_uploaded_file(temp_file_path, "demo_mod.txt")
        print(f"[DEMO] File saved to: {saved_path}")
        
        # Check if file exists
        if os.path.exists(saved_path):
            print(f"[DEMO] File successfully saved and verified")
        else:
            print(f"[DEMO] Error: File not found at saved location")
            
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def demo_search_and_filter():
    """Demonstrate search and filter functionality."""
    print("\n" + "="*60)
    print("DEMO: Search and Filter")
    print("="*60)
    
    # Search for mods
    search_results = mods_hub_manager.get_approved_mods(search="enhancement")
    print(f"[DEMO] Search for 'enhancement': {len(search_results)} results")
    
    # Filter by author
    author_mods = mods_hub_manager.get_approved_mods(author="SWGModder")
    print(f"[DEMO] Mods by SWGModder: {len(author_mods)} results")
    
    # Filter by category
    visual_mods = mods_hub_manager.get_approved_mods(category=ModCategory.VISUAL_MODS)
    print(f"[DEMO] Visual mods: {len(visual_mods)} results")


def demo_mod_operations():
    """Demonstrate various mod operations."""
    print("\n" + "="*60)
    print("DEMO: Mod Operations")
    print("="*60)
    
    # Get a mod to work with
    approved_mods = mods_hub_manager.get_approved_mods(limit=1)
    if approved_mods:
        mod = approved_mods[0]
        mod_id = mod.id
        
        # Increment views
        mods_hub_manager.increment_views(mod_id)
        print(f"[DEMO] Incremented views for mod: {mod_id}")
        
        # Increment downloads
        mods_hub_manager.increment_downloads(mod_id)
        print(f"[DEMO] Incremented downloads for mod: {mod_id}")
        
        # Set as featured
        mods_hub_manager.set_featured(mod_id, True)
        print(f"[DEMO] Set mod as featured: {mod_id}")
        
        # Get updated mod
        updated_mod = mods_hub_manager.get_mod(mod_id)
        if updated_mod:
            print(f"[DEMO] Updated mod stats:")
            print(f"  Views: {updated_mod.views}")
            print(f"  Downloads: {updated_mod.downloads}")
            print(f"  Featured: {updated_mod.featured}")


def create_sample_data():
    """Create sample mods data for demonstration."""
    print("\n" + "="*60)
    print("DEMO: Creating Sample Data")
    print("="*60)
    
    sample_mods = create_sample_mods()
    
    for mod_data in sample_mods:
        # Extract mod type specific data
        content = mod_data.pop('content', None)
        download_url = mod_data.pop('download_url', None)
        
        # Submit mod
        mod_id = mods_hub_manager.submit_mod(
            content=content,
            download_url=download_url,
            **mod_data
        )
        
        print(f"[DEMO] Created sample mod: {mod_data['title']} (ID: {mod_id})")
        
        # If it's a pending mod, approve it
        if mod_data['status'] == ModStatus.APPROVED:
            mods_hub_manager.approve_mod(mod_id, "demo_admin")
            print(f"[DEMO] Approved mod: {mod_id}")
        
        # Set featured status
        if mod_data.get('featured', False):
            mods_hub_manager.set_featured(mod_id, True)
            print(f"[DEMO] Set mod as featured: {mod_id}")
        
        # Set stats
        mod = mods_hub_manager.get_mod(mod_id)
        if mod:
            mod.views = mod_data.get('views', 0)
            mod.downloads = mod_data.get('downloads', 0)
            mod.rating = mod_data.get('rating', 0.0)
            mod.rating_count = mod_data.get('rating_count', 0)
            mods_hub_manager._save_mods()
    
    print(f"[DEMO] Created {len(sample_mods)} sample mods")


def main():
    """Run the complete demonstration."""
    print("Mods & Plugin Hub (Batch 108) - Demonstration")
    print("="*60)
    
    # Create sample data
    create_sample_data()
    
    # Run demonstrations
    demo_mod_submission()
    demo_mod_approval("demo_combat_enhancement_20250101_120000")
    demo_mod_browsing()
    demo_mod_rating("demo_combat_enhancement_20250101_120000")
    demo_mod_management()
    demo_file_upload()
    demo_search_and_filter()
    demo_mod_operations()
    
    print("\n" + "="*60)
    print("DEMO: Web Interface Integration")
    print("="*60)
    
    print("[DEMO] The mods hub integrates with the web interface:")
    print("  - Main hub page: /mods")
    print("  - Submit mods: /mods/submit")
    print("  - View mod details: /mods/{mod_id}")
    print("  - Admin panel: /admin/mods")
    print("  - API endpoints: /api/mods/*")
    
    print("\n[DEMO] Key Features:")
    print("  - Public mod browsing and downloading")
    print("  - Mod submission with approval workflow")
    print("  - File upload and validation")
    print("  - Rating and review system")
    print("  - Category-based organization")
    print("  - Search and filter functionality")
    print("  - Admin approval and management")
    print("  - Featured mods system")
    
    print("\n[DEMO] To use in production:")
    print("  1. Access the mods hub at /mods")
    print("  2. Submit mods through the web interface")
    print("  3. Approve mods through the admin panel")
    print("  4. Browse and download approved mods")
    
    print("\n[DEMO] Demonstration completed successfully!")


if __name__ == "__main__":
    main() 