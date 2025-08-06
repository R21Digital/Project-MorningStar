"""
MS11 Batch 066 - Keybind Reporter

Generates comprehensive reports showing valid keys, missing keys,
and recommended fixes for keybind configurations.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from .keybind_parser import Keybind, KeybindStatus, KeybindCategory
from .keybind_validator import KeybindValidationResult


@dataclass
class KeybindReport:
    """Complete keybind validation report."""
    summary: Dict[str, int]
    valid_keybinds: List[Keybind]
    missing_keybinds: List[Keybind]
    conflicting_keybinds: List[Keybind]
    unknown_keybinds: List[Keybind]
    recommendations: List[str]
    critical_issues: List[str]
    swg_directory: str
    config_files_found: List[str]
    timestamp: str


class KeybindReporter:
    """Generates comprehensive keybind reports."""
    
    def __init__(self):
        """Initialize the keybind reporter."""
        pass
    
    def generate_report(self, keybinds: Dict[str, Keybind], 
                       validation_result: KeybindValidationResult,
                       swg_directory: str,
                       config_files: List[str]) -> KeybindReport:
        """Generate a comprehensive keybind report.
        
        Args:
            keybinds: Dictionary of detected keybinds
            validation_result: KeybindValidationResult from validation
            swg_directory: SWG installation directory
            config_files: List of config files found
            
        Returns:
            KeybindReport with complete analysis
        """
        import datetime
        
        # Categorize keybinds by status
        valid_keybinds = [kb for kb in keybinds.values() if kb.status == KeybindStatus.VALID]
        missing_keybinds = [kb for kb in keybinds.values() if kb.status == KeybindStatus.MISSING]
        conflicting_keybinds = [kb for kb in keybinds.values() if kb.status == KeybindStatus.CONFLICT]
        unknown_keybinds = [kb for kb in keybinds.values() if kb.status == KeybindStatus.UNKNOWN]
        
        # Create summary
        summary = {
            "total_keybinds": validation_result.total_keybinds,
            "valid_keybinds": validation_result.valid_keybinds,
            "missing_keybinds": validation_result.missing_keybinds,
            "conflicting_keybinds": validation_result.conflicting_keybinds,
            "unknown_keybinds": validation_result.unknown_keybinds
        }
        
        return KeybindReport(
            summary=summary,
            valid_keybinds=valid_keybinds,
            missing_keybinds=missing_keybinds,
            conflicting_keybinds=conflicting_keybinds,
            unknown_keybinds=unknown_keybinds,
            recommendations=validation_result.recommendations,
            critical_issues=validation_result.critical_issues,
            swg_directory=swg_directory,
            config_files_found=config_files,
            timestamp=datetime.datetime.now().isoformat()
        )
    
    def print_report(self, report: KeybindReport, detailed: bool = False) -> None:
        """Print a formatted keybind report to console.
        
        Args:
            report: KeybindReport to print
            detailed: Whether to show detailed information
        """
        print("=" * 60)
        print("MS11 KEYBIND VALIDATION REPORT")
        print("=" * 60)
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  Total Keybinds: {report.summary['total_keybinds']}")
        print(f"  ✅ Valid: {report.summary['valid_keybinds']}")
        print(f"  ❌ Missing: {report.summary['missing_keybinds']}")
        print(f"  ⚠️  Conflicting: {report.summary['conflicting_keybinds']}")
        print(f"  ❓ Unknown: {report.summary['unknown_keybinds']}")
        
        # SWG Directory
        print(f"\n📁 SWG Directory: {report.swg_directory}")
        print(f"📄 Config Files Found: {len(report.config_files_found)}")
        for file in report.config_files_found:
            print(f"    - {file}")
        
        # Valid Keybinds
        if report.valid_keybinds:
            print(f"\n✅ VALID KEYBINDS:")
            for keybind in report.valid_keybinds:
                required_marker = " (REQUIRED)" if keybind.required else ""
                print(f"  {keybind.name}: {keybind.key}{required_marker}")
                if detailed and keybind.description:
                    print(f"    Description: {keybind.description}")
        
        # Missing Keybinds
        if report.missing_keybinds:
            print(f"\n❌ MISSING KEYBINDS:")
            for keybind in report.missing_keybinds:
                required_marker = " (REQUIRED)" if keybind.required else ""
                suggestion = f" → Suggested: {keybind.suggestion}" if keybind.suggestion else ""
                print(f"  {keybind.name}: NOT SET{required_marker}{suggestion}")
                if detailed and keybind.description:
                    print(f"    Description: {keybind.description}")
        
        # Conflicting Keybinds
        if report.conflicting_keybinds:
            print(f"\n⚠️  CONFLICTING KEYBINDS:")
            for keybind in report.conflicting_keybinds:
                print(f"  {keybind.name}: {keybind.key} (CONFLICT)")
                if detailed and keybind.description:
                    print(f"    Description: {keybind.description}")
        
        # Unknown Keybinds
        if report.unknown_keybinds:
            print(f"\n❓ UNKNOWN KEYBINDS:")
            for keybind in report.unknown_keybinds:
                print(f"  {keybind.name}: {keybind.key}")
                if detailed and keybind.description:
                    print(f"    Description: {keybind.description}")
        
        # Critical Issues
        if report.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in report.critical_issues:
                print(f"  • {issue}")
        
        # Recommendations
        if report.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report.recommendations:
                print(f"  • {rec}")
        
        print(f"\n⏰ Report Generated: {report.timestamp}")
        print("=" * 60)
    
    def save_report(self, report: KeybindReport, filepath: str) -> bool:
        """Save report to JSON file.
        
        Args:
            report: KeybindReport to save
            filepath: Path to save report
            
        Returns:
            True if report was saved successfully
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Convert report to dictionary manually to handle enums properly
            report_dict = {
                'summary': report.summary,
                'valid_keybinds': [],
                'missing_keybinds': [],
                'conflicting_keybinds': [],
                'unknown_keybinds': [],
                'recommendations': report.recommendations,
                'critical_issues': report.critical_issues,
                'swg_directory': report.swg_directory,
                'config_files_found': report.config_files_found,
                'timestamp': report.timestamp
            }
            
            # Convert keybind objects to dictionaries
            for keybind_list, key in [
                (report.valid_keybinds, 'valid_keybinds'),
                (report.missing_keybinds, 'missing_keybinds'),
                (report.conflicting_keybinds, 'conflicting_keybinds'),
                (report.unknown_keybinds, 'unknown_keybinds')
            ]:
                for kb in keybind_list:
                    kb_dict = {
                        'name': kb.name,
                        'key': kb.key,
                        'category': kb.category.value,
                        'description': kb.description,
                        'required': kb.required,
                        'status': kb.status.value,
                        'suggestion': kb.suggestion,
                        'file_source': kb.file_source,
                        'line_number': kb.line_number
                    }
                    report_dict[key].append(kb_dict)
            
            with open(filepath, 'w') as f:
                json.dump(report_dict, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving report to {filepath}: {e}")
            return False
    
    def generate_category_report(self, keybinds: Dict[str, Keybind]) -> Dict[str, List[Keybind]]:
        """Generate a report organized by keybind categories.
        
        Args:
            keybinds: Dictionary of keybinds to categorize
            
        Returns:
            Dictionary with categories as keys and lists of keybinds as values
        """
        categories = {}
        
        for keybind in keybinds.values():
            category = keybind.category.value
            if category not in categories:
                categories[category] = []
            categories[category].append(keybind)
        
        return categories
    
    def print_category_report(self, keybinds: Dict[str, Keybind]) -> None:
        """Print a category-organized report.
        
        Args:
            keybinds: Dictionary of keybinds to report
        """
        categories = self.generate_category_report(keybinds)
        
        print("\n📋 KEYBINDS BY CATEGORY:")
        print("=" * 40)
        
        for category, keybinds_list in categories.items():
            print(f"\n{category.upper()}:")
            for keybind in keybinds_list:
                status_icon = {
                    KeybindStatus.VALID: "✅",
                    KeybindStatus.MISSING: "❌",
                    KeybindStatus.CONFLICT: "⚠️",
                    KeybindStatus.UNKNOWN: "❓"
                }.get(keybind.status, "❓")
                
                required_marker = " (REQUIRED)" if keybind.required else ""
                key_display = keybind.key if keybind.key else "NOT SET"
                print(f"  {status_icon} {keybind.name}: {key_display}{required_marker}")
    
    def generate_fix_script(self, report: KeybindReport) -> str:
        """Generate a script to fix keybind issues.
        
        Args:
            report: KeybindReport with issues to fix
            
        Returns:
            String containing fix script
        """
        script_lines = [
            "# MS11 Keybind Fix Script",
            "# Generated automatically based on validation report",
            "",
            "# Add these lines to your options.cfg file:",
            ""
        ]
        
        # Add missing required keybinds
        for keybind in report.missing_keybinds:
            if keybind.required and keybind.suggestion:
                script_lines.append(f"Keybind {keybind.name} {keybind.suggestion}")
        
        # Add missing optional keybinds with suggestions
        for keybind in report.missing_keybinds:
            if not keybind.required and keybind.suggestion:
                script_lines.append(f"# Optional: Keybind {keybind.name} {keybind.suggestion}")
        
        script_lines.extend([
            "",
            "# Instructions:",
            "# 1. Open your SWG options.cfg file",
            "# 2. Add the keybind lines above",
            "# 3. Save the file and restart SWG",
            "# 4. Run MS11 keybind validation again"
        ])
        
        return "\n".join(script_lines)
    
    def save_fix_script(self, report: KeybindReport, filepath: str) -> bool:
        """Save fix script to file.
        
        Args:
            report: KeybindReport to generate script from
            filepath: Path to save script
            
        Returns:
            True if script was saved successfully
        """
        try:
            script_content = self.generate_fix_script(report)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(script_content)
            
            return True
            
        except Exception as e:
            print(f"Error saving fix script to {filepath}: {e}")
            return False 