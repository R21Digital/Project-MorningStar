#!/usr/bin/env python3
"""
MS11 Backup Management CLI
Command-line interface for database backup and recovery operations
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.advanced_database import get_database_manager, AdvancedDatabaseManager
from core.backup_recovery import BackupType, BackupStatus, create_backup_manager
from core.structured_logging import StructuredLogger

logger = StructuredLogger("backup_cli")

class BackupCLI:
    """Command-line interface for backup operations"""
    
    def __init__(self):
        self.db_manager: Optional[AdvancedDatabaseManager] = None
        self.backup_manager = None
    
    async def initialize(self):
        """Initialize database and backup managers"""
        try:
            self.db_manager = await get_database_manager()
            if self.db_manager.backup_manager:
                self.backup_manager = self.db_manager.backup_manager
            else:
                print("Warning: Backup manager not available")
                return False
            return True
        except Exception as e:
            print(f"Failed to initialize: {e}")
            return False
    
    async def create_backup_command(self, args):
        """Create a database backup"""
        if not await self.initialize():
            return 1
        
        try:
            backup_type = BackupType(args.type)
            tables = args.tables.split(',') if args.tables else None
            
            print(f"Creating {backup_type.value} backup...")
            if tables:
                print(f"Including tables: {', '.join(tables)}")
            
            metadata = await self.backup_manager.create_backup(
                backup_type=backup_type,
                tables=tables,
                upload_to_s3=args.s3_upload
            )
            
            print(f"✅ Backup created successfully!")
            print(f"   Backup ID: {metadata.backup_id}")
            print(f"   File: {metadata.file_path}")
            print(f"   Size: {metadata.file_size / 1024 / 1024:.2f} MB")
            print(f"   Records: {metadata.records_count:,}")
            print(f"   Checksum: {metadata.checksum[:16]}...")
            
            if args.s3_upload and metadata.status == BackupStatus.COMPLETED:
                print(f"   Uploaded to S3: ✅")
            
            return 0
        
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return 1
    
    async def list_backups_command(self, args):
        """List available backups"""
        if not await self.initialize():
            return 1
        
        try:
            backup_type = BackupType(args.type) if args.type else None
            backups = await self.backup_manager.list_backups(
                backup_type=backup_type,
                limit=args.limit
            )
            
            if not backups:
                print("No backups found.")
                return 0
            
            print(f"\nFound {len(backups)} backup(s):\n")
            
            # Print header
            print(f"{'Backup ID':<20} {'Type':<12} {'Status':<10} {'Size (MB)':<10} {'Records':<10} {'Created':<20}")
            print("-" * 90)
            
            for backup in backups:
                size_mb = backup['file_size'] / 1024 / 1024
                created = datetime.fromisoformat(backup['created_at']).strftime("%Y-%m-%d %H:%M")
                
                print(f"{backup['backup_id'][:20]:<20} "
                      f"{backup['backup_type']:<12} "
                      f"{backup['status']:<10} "
                      f"{size_mb:<10.2f} "
                      f"{backup['records_count']:<10,} "
                      f"{created:<20}")
                
                if args.verbose:
                    print(f"    File: {backup['file_path']}")
                    print(f"    Tables: {', '.join(backup['tables']) if backup['tables'] else 'All'}")
                    if backup['error_message']:
                        print(f"    Error: {backup['error_message']}")
                    print()
            
            return 0
        
        except Exception as e:
            print(f"❌ Failed to list backups: {e}")
            return 1
    
    async def restore_backup_command(self, args):
        """Restore a database backup"""
        if not await self.initialize():
            return 1
        
        try:
            print(f"{'[DRY RUN] ' if args.dry_run else ''}Restoring backup {args.backup_id}...")
            
            tables = args.tables.split(',') if args.tables else None
            if tables:
                print(f"Restoring tables: {', '.join(tables)}")
            
            if args.target_database:
                print(f"Target database: {args.target_database}")
            
            result = await self.backup_manager.restore_backup(
                backup_id=args.backup_id,
                target_database=args.target_database,
                tables=tables,
                dry_run=args.dry_run
            )
            
            if args.dry_run:
                print(f"✅ Dry run successful!")
                print(f"   Backup file: {result['backup_file']}")
                print(f"   File size: {result['file_size'] / 1024 / 1024:.2f} MB")
                print(f"   Tables: {', '.join(result['tables']) if result['tables'] else 'All'}")
                print(f"   Records: {result['records_count']:,}")
            else:
                print(f"✅ Restore completed successfully!")
                print(f"   Backup ID: {result['backup_id']}")
                print(f"   Restored at: {result['restored_at']}")
                print(f"   Tables restored: {', '.join(result['tables_restored']) if result['tables_restored'] else 'All'}")
                print(f"   Records restored: {result['records_restored']:,}")
            
            return 0
        
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return 1
    
    async def delete_backup_command(self, args):
        """Delete a backup"""
        if not await self.initialize():
            return 1
        
        try:
            if not args.force:
                response = input(f"Are you sure you want to delete backup {args.backup_id}? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("Operation cancelled.")
                    return 0
            
            success = await self.backup_manager.delete_backup(args.backup_id)
            
            if success:
                print(f"✅ Backup {args.backup_id} deleted successfully")
                return 0
            else:
                print(f"❌ Failed to delete backup {args.backup_id} (not found)")
                return 1
        
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            return 1
    
    async def status_command(self, args):
        """Show backup system status"""
        if not await self.initialize():
            return 1
        
        try:
            status = await self.backup_manager.get_backup_status()
            
            print("MS11 Backup System Status")
            print("=" * 40)
            print(f"Total backups: {status['total_backups']}")
            print(f"Active backups: {status['active_backups']}")
            print(f"Scheduler running: {'✅' if status['scheduler_running'] else '❌'}")
            print(f"Last backup: {status['last_backup'] if status['last_backup'] else 'Never'}")
            print(f"Backup directory: {status['backup_directory']}")
            
            total_size_mb = status['total_backup_size'] / 1024 / 1024
            print(f"Total backup size: {total_size_mb:.2f} MB")
            
            print("\nConfiguration:")
            config = status['config']
            print(f"  Auto backup: {'✅' if config['auto_backup'] else '❌'}")
            print(f"  Compression: {'✅' if config['compression'] else '❌'}")
            print(f"  S3 enabled: {'✅' if config['s3_enabled'] else '❌'}")
            print(f"  Max backups: {config['max_backups']}")
            
            # Database statistics
            db_stats = await self.db_manager.get_database_stats()
            print(f"\nDatabase Information:")
            print(f"  Type: {db_stats['database_type']}")
            print(f"  Size: {db_stats['database_size']}")
            print(f"  Tables: {db_stats['table_count']}")
            
            return 0
        
        except Exception as e:
            print(f"❌ Failed to get status: {e}")
            return 1
    
    async def migrate_command(self, args):
        """Run database migrations"""
        if not await self.initialize():
            return 1
        
        try:
            print("Running database migrations...")
            
            result = await self.db_manager.migration_manager.migrate_to_latest()
            
            if result['up_to_date']:
                print("✅ Database is up to date!")
            else:
                print(f"✅ Applied {result['applied_count']} migration(s)")
                
                if result['failed_count'] > 0:
                    print(f"❌ {result['failed_count']} migration(s) failed")
                    return 1
            
            print(f"Total migrations: {result['total_migrations']}")
            return 0
        
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return 1

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MS11 Database Backup Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a full backup
  python backup_cli.py create --type full
  
  # Create incremental backup of specific tables
  python backup_cli.py create --type incremental --tables users,sessions
  
  # List all backups
  python backup_cli.py list
  
  # Restore a backup (dry run first)
  python backup_cli.py restore backup_id_here --dry-run
  python backup_cli.py restore backup_id_here
  
  # Show system status
  python backup_cli.py status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create backup command
    create_parser = subparsers.add_parser('create', help='Create a database backup')
    create_parser.add_argument('--type', choices=['full', 'incremental', 'differential', 'schema_only'],
                              default='full', help='Backup type (default: full)')
    create_parser.add_argument('--tables', help='Comma-separated list of tables to backup')
    create_parser.add_argument('--s3-upload', action='store_true', help='Upload backup to S3')
    
    # List backups command
    list_parser = subparsers.add_parser('list', help='List available backups')
    list_parser.add_argument('--type', choices=['full', 'incremental', 'differential', 'schema_only'],
                            help='Filter by backup type')
    list_parser.add_argument('--limit', type=int, default=20, help='Maximum number of backups to show')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    
    # Restore backup command
    restore_parser = subparsers.add_parser('restore', help='Restore a database backup')
    restore_parser.add_argument('backup_id', help='Backup ID to restore')
    restore_parser.add_argument('--target-database', help='Target database name')
    restore_parser.add_argument('--tables', help='Comma-separated list of tables to restore')
    restore_parser.add_argument('--dry-run', action='store_true', help='Perform dry run without actual restore')
    
    # Delete backup command
    delete_parser = subparsers.add_parser('delete', help='Delete a backup')
    delete_parser.add_argument('backup_id', help='Backup ID to delete')
    delete_parser.add_argument('--force', '-f', action='store_true', help='Force deletion without confirmation')
    
    # Status command
    subparsers.add_parser('status', help='Show backup system status')
    
    # Migrate command
    subparsers.add_parser('migrate', help='Run database migrations')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = BackupCLI()
    
    # Map commands to methods
    command_map = {
        'create': cli.create_backup_command,
        'list': cli.list_backups_command,
        'restore': cli.restore_backup_command,
        'delete': cli.delete_backup_command,
        'status': cli.status_command,
        'migrate': cli.migrate_command
    }
    
    if args.command in command_map:
        return asyncio.run(command_map[args.command](args))
    else:
        print(f"Unknown command: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())