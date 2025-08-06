#!/usr/bin/env python3
"""MS11 Batch 082 - Public SWGDB Mods/Addons Section Demo

This demo showcases the comprehensive mods section implementation including:
- Mods manager functionality
- Upload handling and validation
- SWGDB integration
- Website interface
- Statistics and reporting
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from core.mods import ModsManager, create_mods_manager
from core.mods.swgdb_integration import ModsSWGDBIntegration, create_mods_swgdb_integration
from website_sync.sync_to_swgdb import SWGDBSync, WebsiteConfig


class ModsSectionDemo:
    """Demo class for the SWGDB Mods Section."""

    def __init__(self):
        """Initialize the demo."""
        self.mods_manager = create_mods_manager()
        self.swgdb_integration = create_mods_swgdb_integration(self.mods_manager)
        self.demo_files = []
        self.demo_uploads = []
        
        print("🎮 MS11 Batch 082 - SWGDB Mods Section Demo")
        print("=" * 60)

    def run_full_demo(self):
        """Run the complete demo."""
        print("\n🚀 Starting comprehensive mods section demo...")
        
        try:
            # Setup demo environment
            self._setup_demo_environment()
            
            # Run individual demos
            self._demo_mods_manager()
            self._demo_upload_functionality()
            self._demo_validation_system()
            self._demo_swgdb_integration()
            self._demo_statistics_and_reporting()
            self._demo_website_interface()
            self._demo_cleanup_and_maintenance()
            
            # Generate final report
            self._generate_demo_report()
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
        finally:
            self._cleanup_demo_files()

    def _setup_demo_environment(self):
        """Setup demo environment with sample files."""
        print("\n📁 Setting up demo environment...")
        
        # Create temporary demo files
        self._create_demo_files()
        
        # Create sample mods
        self._create_sample_mods()
        
        print("✅ Demo environment ready")

    def _create_demo_files(self):
        """Create demo files for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create UI Skin demo file
        ui_skin_file = temp_dir / "dark_ui_theme.zip"
        with open(ui_skin_file, 'w') as f:
            f.write("Mock UI skin content")
        self.demo_files.append(str(ui_skin_file))
        
        # Create Macro Pack demo file
        macro_file = temp_dir / "combat_macros.txt"
        with open(macro_file, 'w') as f:
            f.write("/macro combat_rotation\n/attack\n/pause 2\n/attack")
        self.demo_files.append(str(macro_file))
        
        # Create Addon Tool demo file
        tool_file = temp_dir / "performance_optimizer.exe"
        with open(tool_file, 'w') as f:
            f.write("Mock executable content")
        self.demo_files.append(str(tool_file))
        
        # Create Visual Modpack demo file
        texture_file = temp_dir / "hd_textures.zip"
        with open(texture_file, 'w') as f:
            f.write("Mock texture pack content")
        self.demo_files.append(str(texture_file))

    def _create_sample_mods(self):
        """Create sample mods for demonstration."""
        sample_mods = [
            {
                "file_path": self.demo_files[0],
                "metadata": {
                    "title": "Dark UI Theme",
                    "description": "A sleek dark theme for the SWG interface with improved readability and modern aesthetics.",
                    "category": "ui_skins",
                    "subcategory": "dark_themes",
                    "version": "1.0",
                    "tags": ["dark", "modern", "ui"],
                    "compatibility": {
                        "swg_versions": ["SWGEmu", "SWG Legends"],
                        "client_versions": ["14.1", "14.1.1"]
                    }
                },
                "author": "SWGDesigner"
            },
            {
                "file_path": self.demo_files[1],
                "metadata": {
                    "title": "Combat Macro Pack",
                    "description": "Comprehensive collection of combat macros for all professions with auto-targeting and skill rotation.",
                    "category": "macro_packs",
                    "subcategory": "combat_macros",
                    "version": "2.1",
                    "tags": ["combat", "macros", "auto-target"],
                    "compatibility": {
                        "swg_versions": ["SWGEmu"],
                        "client_versions": ["14.1"]
                    }
                },
                "author": "CombatMaster"
            },
            {
                "file_path": self.demo_files[2],
                "metadata": {
                    "title": "Performance Optimizer",
                    "description": "Advanced tool for optimizing SWG performance with FPS boost and memory management.",
                    "category": "addon_tools",
                    "subcategory": "performance_tools",
                    "version": "1.5",
                    "tags": ["performance", "fps", "optimization"],
                    "compatibility": {
                        "swg_versions": ["SWGEmu", "SWG Legends", "SWG Restoration"],
                        "client_versions": ["14.1", "14.1.1", "14.1.2"]
                    }
                },
                "author": "TechWizard"
            },
            {
                "file_path": self.demo_files[3],
                "metadata": {
                    "title": "Enhanced Textures Pack",
                    "description": "High-resolution texture pack for weapons and armor with detailed PBR materials.",
                    "category": "visual_modpacks",
                    "subcategory": "texture_packs",
                    "version": "3.0",
                    "tags": ["textures", "hd", "weapons"],
                    "compatibility": {
                        "swg_versions": ["SWGEmu", "SWG Legends"],
                        "client_versions": ["14.1", "14.1.1"]
                    }
                },
                "author": "TextureArtist"
            }
        ]
        
        self.sample_mods = sample_mods

    def _demo_mods_manager(self):
        """Demo the mods manager functionality."""
        print("\n🔧 Demo: Mods Manager Functionality")
        print("-" * 40)
        
        # Test category initialization
        print(f"📂 Categories loaded: {len(self.mods_manager.categories)}")
        for category_id, category in self.mods_manager.categories.items():
            print(f"  - {category.name} ({category_id}): {category.description}")
        
        # Test configuration loading
        print(f"⚙️ Configuration loaded: {self.mods_manager.config['mods_section']['version']}")
        
        # Test storage paths
        print(f"📁 Storage path: {self.mods_manager.storage_path}")
        print(f"📁 Backup path: {self.mods_manager.backup_path}")
        
        print("✅ Mods manager demo completed")

    def _demo_upload_functionality(self):
        """Demo upload functionality."""
        print("\n📤 Demo: Upload Functionality")
        print("-" * 40)
        
        for i, sample_mod in enumerate(self.sample_mods, 1):
            print(f"\n📦 Uploading mod {i}: {sample_mod['metadata']['title']}")
            
            success, message, upload_id = self.mods_manager.upload_mod(
                sample_mod['file_path'],
                sample_mod['metadata'],
                sample_mod['author']
            )
            
            if success:
                print(f"  ✅ Upload successful: {upload_id}")
                self.demo_uploads.append(upload_id)
                
                # Update status to approved for demo
                self.mods_manager.update_mod_status(upload_id, "approved")
                print(f"  ✅ Status updated to approved")
                
                # Simulate some activity
                self.mods_manager.increment_view_count(upload_id)
                self.mods_manager.increment_download_count(upload_id)
                self.mods_manager.rate_mod(upload_id, 4.5, "demo_user")
                
            else:
                print(f"  ❌ Upload failed: {message}")
        
        print(f"✅ Upload demo completed: {len(self.demo_uploads)} mods uploaded")

    def _demo_validation_system(self):
        """Demo the validation system."""
        print("\n🔍 Demo: Validation System")
        print("-" * 40)
        
        # Test validation for each upload
        for upload_id in self.demo_uploads:
            upload = self.mods_manager.get_mod_by_id(upload_id)
            if upload:
                print(f"\n🔍 Validating: {upload.title}")
                
                # Test file integrity
                file_path = Path(upload.file_path)
                if file_path.exists():
                    print(f"  ✅ File exists: {file_path.name}")
                    print(f"  📏 File size: {file_path.stat().st_size} bytes")
                else:
                    print(f"  ❌ File missing: {upload.file_path}")
                
                # Test metadata validation
                if len(upload.title) >= 3:
                    print(f"  ✅ Title valid: {upload.title}")
                else:
                    print(f"  ❌ Title too short: {upload.title}")
                
                if len(upload.description) >= 10:
                    print(f"  ✅ Description valid: {len(upload.description)} chars")
                else:
                    print(f"  ❌ Description too short: {len(upload.description)} chars")
                
                # Test category validation
                if upload.category in self.mods_manager.categories:
                    print(f"  ✅ Category valid: {upload.category}")
                else:
                    print(f"  ❌ Invalid category: {upload.category}")
        
        print("✅ Validation demo completed")

    def _demo_swgdb_integration(self):
        """Demo SWGDB integration."""
        print("\n🌐 Demo: SWGDB Integration")
        print("-" * 40)
        
        # Test sync functionality
        print("🔄 Syncing mods to SWGDB...")
        sync_result = self.swgdb_integration.sync_mods_to_swgdb(force_sync=True)
        
        print(f"  📊 Sync Status: {sync_result.status}")
        print(f"  📁 Files synced: {len(sync_result.files_synced)}")
        print(f"  ⏱️ Sync duration: {sync_result.sync_duration:.2f}s")
        print(f"  📈 Total mods: {sync_result.total_mods}")
        print(f"  ✅ Approved mods: {sync_result.approved_mods}")
        
        # Test sync status
        status = self.swgdb_integration.get_sync_status()
        print(f"  📊 SWGDB Status: {status.get('swgdb_sync_status', {}).get('total_syncs', 0)} total syncs")
        
        # Test validation
        validation = self.swgdb_integration.validate_mods_data()
        print(f"  🔍 Validation: {validation.get('valid_mods', 0)} valid, {validation.get('invalid_mods', 0)} invalid")
        
        print("✅ SWGDB integration demo completed")

    def _demo_statistics_and_reporting(self):
        """Demo statistics and reporting functionality."""
        print("\n📊 Demo: Statistics and Reporting")
        print("-" * 40)
        
        # Get comprehensive statistics
        stats = self.mods_manager.get_mods_statistics()
        
        print(f"📈 Overall Statistics:")
        print(f"  📦 Total uploads: {stats['total_uploads']}")
        print(f"  ✅ Approved: {stats['approved_uploads']}")
        print(f"  ⏳ Pending: {stats['pending_uploads']}")
        print(f"  ❌ Rejected: {stats['rejected_uploads']}")
        print(f"  📥 Total downloads: {stats['total_downloads']}")
        print(f"  👁️ Total views: {stats['total_views']}")
        print(f"  ⭐ Average rating: {stats['average_rating']:.1f}")
        
        print(f"\n📂 Category Statistics:")
        for category_id, category_stats in stats['category_stats'].items():
            print(f"  {category_id}: {category_stats['total']} mods, {category_stats['approved']} approved")
        
        # Test search functionality
        print(f"\n🔍 Search Functionality:")
        search_results = self.mods_manager.search_mods("combat")
        print(f"  Search 'combat': {len(search_results)} results")
        
        search_results = self.mods_manager.search_mods("dark", "ui_skins")
        print(f"  Search 'dark' in UI skins: {len(search_results)} results")
        
        # Test category filtering
        print(f"\n📂 Category Filtering:")
        for category_id in self.mods_manager.categories:
            mods = self.mods_manager.get_mods_by_category(category_id)
            print(f"  {category_id}: {len(mods)} mods")
        
        print("✅ Statistics and reporting demo completed")

    def _demo_website_interface(self):
        """Demo website interface functionality."""
        print("\n🌐 Demo: Website Interface")
        print("-" * 40)
        
        # Check if HTML file exists
        html_file = Path("web/mods_section.html")
        if html_file.exists():
            print(f"✅ Mods section HTML: {html_file}")
            print(f"  📏 File size: {html_file.stat().st_size} bytes")
            
            # Check for key sections in HTML
            with open(html_file, 'r') as f:
                content = f.read()
                
            sections = [
                "SWG Mods & Addons",
                "search-form",
                "categories-grid",
                "mods-grid",
                "upload-section"
            ]
            
            for section in sections:
                if section in content:
                    print(f"  ✅ Section found: {section}")
                else:
                    print(f"  ❌ Section missing: {section}")
        else:
            print(f"❌ Mods section HTML not found: {html_file}")
        
        # Test configuration
        config_file = Path("config/mods_config.json")
        if config_file.exists():
            print(f"✅ Mods configuration: {config_file}")
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"  📊 Categories configured: {len(config['categories'])}")
            print(f"  ⚙️ Upload enabled: {config['upload_settings']['enabled']}")
            print(f"  🔍 Validation enabled: {config['validation_settings']['enabled']}")
        else:
            print(f"❌ Mods configuration not found: {config_file}")
        
        print("✅ Website interface demo completed")

    def _demo_cleanup_and_maintenance(self):
        """Demo cleanup and maintenance functionality."""
        print("\n🧹 Demo: Cleanup and Maintenance")
        print("-" * 40)
        
        # Test cleanup of old uploads
        print("🗑️ Cleaning up old uploads...")
        removed_count = self.mods_manager.cleanup_old_uploads(days_to_keep=365)
        print(f"  📦 Removed {removed_count} old uploads")
        
        # Test cleanup of old exports
        print("🗑️ Cleaning up old exports...")
        removed_exports = self.swgdb_integration.cleanup_old_exports(days_to_keep=7)
        print(f"  📁 Removed {removed_exports} old export files")
        
        # Test data validation
        print("🔍 Validating mods data...")
        validation = self.swgdb_integration.validate_mods_data()
        print(f"  ✅ Valid mods: {validation.get('valid_mods', 0)}")
        print(f"  ❌ Invalid mods: {validation.get('invalid_mods', 0)}")
        
        if validation.get('errors'):
            print(f"  ⚠️ Validation errors: {len(validation['errors'])}")
            for error in validation['errors'][:3]:  # Show first 3 errors
                print(f"    - {error}")
        
        print("✅ Cleanup and maintenance demo completed")

    def _generate_demo_report(self):
        """Generate a comprehensive demo report."""
        print("\n📋 Demo Report")
        print("=" * 60)
        
        # Collect final statistics
        stats = self.mods_manager.get_mods_statistics()
        sync_status = self.swgdb_integration.get_sync_status()
        
        report = {
            "demo_timestamp": datetime.now().isoformat(),
            "demo_duration": "Completed",
            "mods_manager": {
                "total_uploads": stats['total_uploads'],
                "approved_uploads": stats['approved_uploads'],
                "categories_configured": len(self.mods_manager.categories),
                "storage_path": str(self.mods_manager.storage_path)
            },
            "swgdb_integration": {
                "sync_status": sync_status.get('swgdb_sync_status', {}).get('status', 'unknown'),
                "export_path": sync_status.get('export_path', 'unknown'),
                "target_path": sync_status.get('target_path', 'unknown')
            },
            "demo_uploads": {
                "total_created": len(self.demo_uploads),
                "upload_ids": self.demo_uploads
            },
            "features_tested": [
                "Mods Manager Initialization",
                "Upload Functionality",
                "Validation System",
                "SWGDB Integration",
                "Statistics and Reporting",
                "Website Interface",
                "Cleanup and Maintenance"
            ],
            "configuration": {
                "config_file": "config/mods_config.json",
                "html_file": "web/mods_section.html",
                "categories": list(self.mods_manager.categories.keys())
            }
        }
        
        # Print report
        print(f"📊 Final Statistics:")
        print(f"  📦 Total mods: {report['mods_manager']['total_uploads']}")
        print(f"  ✅ Approved: {report['mods_manager']['approved_uploads']}")
        print(f"  📂 Categories: {report['mods_manager']['categories_configured']}")
        print(f"  🔄 Sync status: {report['swgdb_integration']['sync_status']}")
        
        print(f"\n✅ Features Tested:")
        for feature in report['features_tested']:
            print(f"  ✅ {feature}")
        
        print(f"\n📁 Files Created:")
        print(f"  ⚙️ Configuration: {report['configuration']['config_file']}")
        print(f"  🌐 HTML Interface: {report['configuration']['html_file']}")
        print(f"  📂 Categories: {', '.join(report['configuration']['categories'])}")
        
        # Save report
        report_file = Path("demo_batch_082_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved: {report_file}")
        
        print("\n🎉 Demo completed successfully!")
        print("The SWGDB Mods Section is ready for use.")

    def _cleanup_demo_files(self):
        """Clean up demo files."""
        print("\n🧹 Cleaning up demo files...")
        
        # Remove temporary files
        for file_path in self.demo_files:
            try:
                Path(file_path).unlink()
                print(f"  🗑️ Removed: {file_path}")
            except Exception as e:
                print(f"  ⚠️ Could not remove {file_path}: {e}")
        
        print("✅ Cleanup completed")


def main():
    """Main demo function."""
    demo = ModsSectionDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main() 