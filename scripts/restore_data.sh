#!/bin/bash

# Batch 194 - Backup & Restore Scripts
# Restore Data Script
# Goal: Restore data from backups with verification and safety checks

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/backup_config.json"
LOG_FILE="$PROJECT_ROOT/logs/restore.log"
BACKUP_DIR="$PROJECT_ROOT/backups"
DATA_DIR="$PROJECT_ROOT/data"
UPLOADS_DIR="$PROJECT_ROOT/uploads"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    exit 1
}

# Check if required directories exist
check_directories() {
    log "INFO" "Checking required directories..."
    
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Check if backup directory exists
    if [[ ! -d "$BACKUP_DIR" ]]; then
        error_exit "Backup directory does not exist: $BACKUP_DIR"
    fi
    
    # Create data and uploads directories if they don't exist
    mkdir -p "$DATA_DIR"
    mkdir -p "$UPLOADS_DIR"
    
    log "INFO" "All required directories verified"
}

# Load configuration
load_config() {
    log "INFO" "Loading restore configuration..."
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        error_exit "Backup configuration file not found: $CONFIG_FILE"
    fi
    
    # Check if jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        log "WARNING" "jq not found, using basic configuration"
        return
    fi
    
    # Load configuration using jq
    RESTORE_ENABLED=$(jq -r '.restore.enabled' "$CONFIG_FILE" 2>/dev/null || echo "true")
    CONFIRMATION_REQUIRED=$(jq -r '.restore.confirmation_required' "$CONFIG_FILE" 2>/dev/null || echo "true")
    DRY_RUN=$(jq -r '.restore.dry_run' "$CONFIG_FILE" 2>/dev/null || echo "false")
    BACKUP_VERIFICATION=$(jq -r '.restore.backup_verification' "$CONFIG_FILE" 2>/dev/null || echo "true")
    DISCORD_ENABLED=$(jq -r '.notifications.discord.enabled' "$CONFIG_FILE" 2>/dev/null || echo "false")
    DISCORD_WEBHOOK=$(jq -r '.notifications.discord.webhook_url' "$CONFIG_FILE" 2>/dev/null || echo "")
    
    log "INFO" "Configuration loaded successfully"
}

# Send Discord notification
send_discord_notification() {
    local status="$1"
    local message="$2"
    
    if [[ "$DISCORD_ENABLED" == "true" && -n "$DISCORD_WEBHOOK" ]]; then
        local color
        case "$status" in
            "success") color="3066993" ;;
            "error") color="15158332" ;;
            "warning") color="16776960" ;;
            *) color="7506394" ;;
        esac
        
        local payload=$(cat <<EOF
{
    "embeds": [{
        "title": "🔄 MS11 Restore System",
        "description": "$message",
        "color": $color,
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
        "footer": {
            "text": "MorningStar SWG Restore System"
        }
    }]
}
EOF
)
        
        curl -s -H "Content-Type: application/json" -d "$payload" "$DISCORD_WEBHOOK" || log "WARNING" "Failed to send Discord notification"
    fi
}

# List available backups
list_backups() {
    log "INFO" "Available backups:"
    echo -e "${BLUE}📁 Available Backups:${NC}"
    
    local backup_count=0
    while IFS= read -r -d '' backup_file; do
        local filename=$(basename "$backup_file")
        local size=$(du -h "$backup_file" 2>/dev/null | cut -f1 || echo "Unknown")
        local date=$(stat -c %y "$backup_file" 2>/dev/null | cut -d' ' -f1 || echo "Unknown")
        
        echo -e "  ${GREEN}✅${NC} $filename ($size) - $date"
        ((backup_count++))
    done < <(find "$BACKUP_DIR" -name "backup_*.tar.gz" -o -name "backup_*.tar.bz2" -o -name "backup_*.zip" -print0 2>/dev/null | sort -z)
    
    if [[ $backup_count -eq 0 ]]; then
        echo -e "  ${YELLOW}⚠️  No backups found${NC}"
    fi
    
    echo ""
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    
    log "INFO" "Verifying backup integrity: $backup_file"
    
    # Check if backup file exists
    if [[ ! -f "$backup_file" ]]; then
        error_exit "Backup file not found: $backup_file"
    fi
    
    # Check if checksum file exists
    local checksum_file="${backup_file}.sha256"
    if [[ -f "$checksum_file" ]]; then
        log "INFO" "Verifying checksum..."
        local expected_checksum=$(cat "$checksum_file")
        local actual_checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
        
        if [[ "$expected_checksum" == "$actual_checksum" ]]; then
            log "INFO" "✅ Checksum verification passed"
        else
            error_exit "❌ Checksum verification failed"
        fi
    else
        log "WARNING" "No checksum file found, skipping verification"
    fi
    
    # Test archive integrity
    log "INFO" "Testing archive integrity..."
    case "$backup_file" in
        *.tar.gz)
            if tar -tzf "$backup_file" > /dev/null 2>&1; then
                log "INFO" "✅ Archive integrity verified"
            else
                error_exit "❌ Archive integrity check failed"
            fi
            ;;
        *.tar.bz2)
            if tar -tjf "$backup_file" > /dev/null 2>&1; then
                log "INFO" "✅ Archive integrity verified"
            else
                error_exit "❌ Archive integrity check failed"
            fi
            ;;
        *.zip)
            if unzip -t "$backup_file" > /dev/null 2>&1; then
                log "INFO" "✅ Archive integrity verified"
            else
                error_exit "❌ Archive integrity check failed"
            fi
            ;;
        *)
            log "WARNING" "Unknown archive format, skipping integrity check"
            ;;
    esac
}

# Extract backup metadata
extract_metadata() {
    local backup_file="$1"
    local temp_dir="$2"
    
    log "INFO" "Extracting backup metadata..."
    
    # Extract metadata file if it exists
    case "$backup_file" in
        *.tar.gz)
            tar -xzf "$backup_file" -C "$temp_dir" backup_metadata.json 2>/dev/null || true
            ;;
        *.tar.bz2)
            tar -xjf "$backup_file" -C "$temp_dir" backup_metadata.json 2>/dev/null || true
            ;;
        *.zip)
            unzip -j "$backup_file" backup_metadata.json -d "$temp_dir" 2>/dev/null || true
            ;;
    esac
    
    # Display metadata if available
    if [[ -f "$temp_dir/backup_metadata.json" ]]; then
        log "INFO" "Backup metadata:"
        if command -v jq &> /dev/null; then
            jq '.' "$temp_dir/backup_metadata.json" | log "INFO"
        else
            cat "$temp_dir/backup_metadata.json" | log "INFO"
        fi
    fi
}

# Create backup of current data before restore
create_pre_restore_backup() {
    log "INFO" "Creating pre-restore backup of current data..."
    
    local pre_restore_backup="$BACKUP_DIR/pre_restore_$(date '+%Y%m%d_%H%M%S').tar.gz"
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT
    
    # Copy current data
    if [[ -d "$DATA_DIR" ]]; then
        cp -r "$DATA_DIR" "$temp_dir/"
    fi
    
    if [[ -d "$UPLOADS_DIR" ]]; then
        cp -r "$UPLOADS_DIR" "$temp_dir/"
    fi
    
    # Create metadata
    cat > "$temp_dir/pre_restore_metadata.json" <<EOF
{
    "backup_id": "pre_restore_$(date '+%Y%m%d_%H%M%S')",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
    "type": "pre_restore",
    "reason": "Automatic backup before restore operation"
}
EOF
    
    # Compress
    tar -czf "$pre_restore_backup" -C "$temp_dir" .
    
    log "INFO" "Pre-restore backup created: $pre_restore_backup"
    echo "$pre_restore_backup"
}

# Restore data from backup
restore_data() {
    local backup_file="$1"
    local dry_run="${2:-false}"
    
    log "INFO" "Starting restore from: $backup_file"
    
    # Create temporary directory for extraction
    local temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT
    
    # Extract backup
    log "INFO" "Extracting backup..."
    case "$backup_file" in
        *.tar.gz)
            tar -xzf "$backup_file" -C "$temp_dir"
            ;;
        *.tar.bz2)
            tar -xjf "$backup_file" -C "$temp_dir"
            ;;
        *.zip)
            unzip "$backup_file" -d "$temp_dir"
            ;;
        *)
            error_exit "Unsupported backup format: $backup_file"
            ;;
    esac
    
    # Extract metadata
    extract_metadata "$backup_file" "$temp_dir"
    
    if [[ "$dry_run" == "true" ]]; then
        log "INFO" "DRY RUN - Would restore the following:"
        echo -e "${YELLOW}📁 Files to be restored:${NC}"
        find "$temp_dir" -type f -name "backup_metadata.json" -o -name "pre_restore_metadata.json" | head -10 | while read -r file; do
            echo "  $(basename "$file")"
        done
        
        local data_files=$(find "$temp_dir" -path "*/data/*" -type f | wc -l)
        local uploads_files=$(find "$temp_dir" -path "*/uploads/*" -type f | wc -l)
        
        echo -e "  ${BLUE}Data files: $data_files${NC}"
        echo -e "  ${BLUE}Upload files: $uploads_files${NC}"
        
        return
    fi
    
    # Create pre-restore backup
    local pre_restore_backup=$(create_pre_restore_backup)
    
    # Restore data directory
    if [[ -d "$temp_dir/data" ]]; then
        log "INFO" "Restoring data directory..."
        rm -rf "$DATA_DIR"
        cp -r "$temp_dir/data" "$(dirname "$DATA_DIR")/"
        log "INFO" "✅ Data directory restored"
    fi
    
    # Restore uploads directory
    if [[ -d "$temp_dir/uploads" ]]; then
        log "INFO" "Restoring uploads directory..."
        rm -rf "$UPLOADS_DIR"
        cp -r "$temp_dir/uploads" "$(dirname "$UPLOADS_DIR")/"
        log "INFO" "✅ Uploads directory restored"
    fi
    
    # Set proper permissions
    log "INFO" "Setting file permissions..."
    find "$DATA_DIR" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find "$DATA_DIR" -type d -exec chmod 755 {} \; 2>/dev/null || true
    find "$UPLOADS_DIR" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find "$UPLOADS_DIR" -type d -exec chmod 755 {} \; 2>/dev/null || true
    
    log "INFO" "✅ Restore completed successfully"
    echo "$pre_restore_backup"
}

# Get user confirmation
get_confirmation() {
    local backup_file="$1"
    
    if [[ "$CONFIRMATION_REQUIRED" != "true" ]]; then
        return 0
    fi
    
    echo -e "${YELLOW}⚠️  WARNING: This will overwrite current data!${NC}"
    echo -e "${YELLOW}📁 Backup file: $backup_file${NC}"
    echo -e "${YELLOW}📊 Size: $(du -h "$backup_file" | cut -f1)${NC}"
    echo ""
    echo -e "${YELLOW}Are you sure you want to proceed? (yes/no):${NC} "
    read -r confirmation
    
    if [[ "$confirmation" != "yes" ]]; then
        echo -e "${RED}❌ Restore cancelled by user${NC}"
        exit 0
    fi
    
    echo -e "${YELLOW}Type 'CONFIRM' to proceed with restore:${NC} "
    read -r final_confirmation
    
    if [[ "$final_confirmation" != "CONFIRM" ]]; then
        echo -e "${RED}❌ Restore cancelled by user${NC}"
        exit 0
    fi
}

# Main restore function
main() {
    local backup_file="$1"
    local dry_run="${2:-false}"
    
    log "INFO" "Starting restore process..."
    
    # Check if restore is enabled
    if [[ "$RESTORE_ENABLED" != "true" ]]; then
        error_exit "Restore is disabled in configuration"
    fi
    
    # Initialize
    check_directories
    load_config
    
    # Verify backup if enabled
    if [[ "$BACKUP_VERIFICATION" == "true" ]]; then
        verify_backup "$backup_file"
    fi
    
    # Get user confirmation
    if [[ "$dry_run" != "true" ]]; then
        get_confirmation "$backup_file"
    fi
    
    # Restore data
    local pre_restore_backup=$(restore_data "$backup_file" "$dry_run")
    
    if [[ "$dry_run" != "true" ]]; then
        # Send success notification
        local backup_size=$(du -h "$backup_file" | cut -f1)
        local success_message="✅ Restore completed successfully\n📁 From: $(basename "$backup_file")\n📊 Size: $backup_size\n⏰ Time: $(date '+%Y-%m-%d %H:%M:%S')"
        send_discord_notification "success" "$success_message"
        
        log "INFO" "Restore process completed successfully"
        echo -e "${GREEN}✅ Restore completed successfully${NC}"
        echo -e "${BLUE}📁 Restored from: $backup_file${NC}"
        echo -e "${BLUE}📊 Size: $backup_size${NC}"
        echo -e "${YELLOW}💾 Pre-restore backup: $pre_restore_backup${NC}"
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [OPTIONS] <backup_file>"
    echo ""
    echo "Options:"
    echo "  --help, -h           Show this help message"
    echo "  --dry-run            Show what would be restored without actually restoring"
    echo "  --force              Skip confirmation prompts"
    echo "  --list               List available backups"
    echo "  --verify <file>      Verify backup integrity"
    echo ""
    echo "Examples:"
    echo "  $0 backups/2024/01/15/backup_20240115_020000.tar.gz"
    echo "  $0 --dry-run backups/2024/01/15/backup_20240115_020000.tar.gz"
    echo "  $0 --list"
    echo "  $0 --verify backups/2024/01/15/backup_20240115_020000.tar.gz"
    echo ""
    echo "This script restores data from backup files with verification and safety checks."
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --list)
        check_directories
        list_backups
        exit 0
        ;;
    --verify)
        if [[ -z "${2:-}" ]]; then
            echo "Error: No backup file specified for verification"
            exit 1
        fi
        check_directories
        load_config
        verify_backup "$2"
        echo -e "${GREEN}✅ Backup verification completed${NC}"
        exit 0
        ;;
    --dry-run)
        if [[ -z "${2:-}" ]]; then
            echo "Error: No backup file specified"
            exit 1
        fi
        DRY_RUN="true"
        CONFIRMATION_REQUIRED="false"
        main "$2" "true"
        exit 0
        ;;
    --force)
        if [[ -z "${2:-}" ]]; then
            echo "Error: No backup file specified"
            exit 1
        fi
        CONFIRMATION_REQUIRED="false"
        main "$2" "false"
        exit 0
        ;;
    "")
        echo "Error: No backup file specified"
        echo "Use --help for usage information"
        exit 1
        ;;
    *)
        if [[ "$1" == --* ]]; then
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
        fi
        main "$1" "false"
        exit 0
        ;;
esac 