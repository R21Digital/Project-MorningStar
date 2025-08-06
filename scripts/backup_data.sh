#!/bin/bash

# Batch 194 - Backup & Restore Scripts
# Backup Data Script
# Goal: Ensure daily backups of all user-submitted data

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/backup_config.json"
LOG_FILE="$PROJECT_ROOT/logs/backup.log"
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
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Create uploads directory if it doesn't exist
    mkdir -p "$UPLOADS_DIR"
    
    # Check if data directory exists
    if [[ ! -d "$DATA_DIR" ]]; then
        error_exit "Data directory does not exist: $DATA_DIR"
    fi
    
    log "INFO" "All required directories verified"
}

# Load configuration
load_config() {
    log "INFO" "Loading backup configuration..."
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        error_exit "Backup configuration file not found: $CONFIG_FILE"
    fi
    
    # Check if jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        log "WARNING" "jq not found, using basic configuration"
        return
    fi
    
    # Load configuration using jq
    BACKUP_ENABLED=$(jq -r '.backup.enabled' "$CONFIG_FILE" 2>/dev/null || echo "true")
    COMPRESSION_ENABLED=$(jq -r '.backup.compression.enabled' "$CONFIG_FILE" 2>/dev/null || echo "true")
    COMPRESSION_FORMAT=$(jq -r '.backup.compression.format' "$CONFIG_FILE" 2>/dev/null || echo "tar.gz")
    VERIFICATION_ENABLED=$(jq -r '.backup.verification.enabled' "$CONFIG_FILE" 2>/dev/null || echo "true")
    DISCORD_ENABLED=$(jq -r '.notifications.discord.enabled' "$CONFIG_FILE" 2>/dev/null || echo "false")
    DISCORD_WEBHOOK=$(jq -r '.notifications.discord.webhook_url' "$CONFIG_FILE" 2>/dev/null || echo "")
    
    log "INFO" "Configuration loaded successfully"
}

# Generate timestamp
get_timestamp() {
    date '+%Y%m%d_%H%M%S'
}

# Create backup filename
get_backup_filename() {
    local timestamp=$(get_timestamp)
    local date_folder=$(date '+%Y/%m/%d')
    echo "${date_folder}/backup_${timestamp}"
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
        "title": "🔄 MS11 Backup System",
        "description": "$message",
        "color": $color,
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
        "footer": {
            "text": "MorningStar SWG Backup System"
        }
    }]
}
EOF
)
        
        curl -s -H "Content-Type: application/json" -d "$payload" "$DISCORD_WEBHOOK" || log "WARNING" "Failed to send Discord notification"
    fi
}

# Create backup
create_backup() {
    local backup_filename="$1"
    local backup_path="$BACKUP_DIR/$backup_filename"
    
    log "INFO" "Creating backup: $backup_filename"
    
    # Create backup directory
    mkdir -p "$(dirname "$backup_path")"
    
    # Create temporary directory for backup
    local temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT
    
    # Copy data directory
    log "INFO" "Backing up data directory..."
    if [[ -d "$DATA_DIR" ]]; then
        cp -r "$DATA_DIR" "$temp_dir/"
    fi
    
    # Copy uploads directory
    log "INFO" "Backing up uploads directory..."
    if [[ -d "$UPLOADS_DIR" ]]; then
        cp -r "$UPLOADS_DIR" "$temp_dir/"
    fi
    
    # Create metadata file
    cat > "$temp_dir/backup_metadata.json" <<EOF
{
    "backup_id": "$(get_timestamp)",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
    "version": "1.0",
    "directories": {
        "data": "$(realpath "$DATA_DIR")",
        "uploads": "$(realpath "$UPLOADS_DIR")"
    },
    "system_info": {
        "hostname": "$(hostname)",
        "user": "$(whoami)",
        "script_version": "1.0"
    }
}
EOF
    
    # Compress backup
    if [[ "$COMPRESSION_ENABLED" == "true" ]]; then
        log "INFO" "Compressing backup..."
        case "$COMPRESSION_FORMAT" in
            "tar.gz")
                tar -czf "${backup_path}.tar.gz" -C "$temp_dir" .
                backup_file="${backup_path}.tar.gz"
                ;;
            "tar.bz2")
                tar -cjf "${backup_path}.tar.bz2" -C "$temp_dir" .
                backup_file="${backup_path}.tar.bz2"
                ;;
            "zip")
                (cd "$temp_dir" && zip -r "${backup_path}.zip" .)
                backup_file="${backup_path}.zip"
                ;;
            *)
                tar -czf "${backup_path}.tar.gz" -C "$temp_dir" .
                backup_file="${backup_path}.tar.gz"
                ;;
        esac
    else
        # No compression, just copy
        cp -r "$temp_dir" "$backup_path"
        backup_file="$backup_path"
    fi
    
    # Verify backup
    if [[ "$VERIFICATION_ENABLED" == "true" ]]; then
        log "INFO" "Verifying backup integrity..."
        if [[ -f "$backup_file" ]]; then
            local checksum
            case "$COMPRESSION_FORMAT" in
                "tar.gz"|"tar.bz2")
                    checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
                    ;;
                "zip")
                    checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
                    ;;
                *)
                    checksum=$(find "$backup_file" -type f -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)
                    ;;
            esac
            echo "$checksum" > "${backup_file}.sha256"
            log "INFO" "Backup checksum: $checksum"
        fi
    fi
    
    # Get backup size
    local backup_size=$(du -h "$backup_file" | cut -f1)
    log "INFO" "Backup completed: $backup_file ($backup_size)"
    
    echo "$backup_file"
}

# Clean old backups
clean_old_backups() {
    log "INFO" "Cleaning old backups..."
    
    # Keep daily backups for 7 days
    find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "backup_*.tar.bz2" -mtime +7 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "backup_*.zip" -mtime +7 -delete 2>/dev/null || true
    
    # Keep weekly backups for 4 weeks (keep one backup per week)
    find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +28 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "backup_*.tar.bz2" -mtime +28 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "backup_*.zip" -mtime +28 -delete 2>/dev/null || true
    
    log "INFO" "Old backups cleaned"
}

# Push to remote storage
push_to_remote() {
    local backup_file="$1"
    
    log "INFO" "Pushing backup to remote storage..."
    
    # Git repository backup
    if [[ "$(jq -r '.remote.git.enabled' "$CONFIG_FILE" 2>/dev/null || echo 'false')" == "true" ]]; then
        push_to_git "$backup_file"
    fi
    
    # Google Drive backup
    if [[ "$(jq -r '.remote.google_drive.enabled' "$CONFIG_FILE" 2>/dev/null || echo 'false')" == "true" ]]; then
        push_to_google_drive "$backup_file"
    fi
    
    # S3 backup
    if [[ "$(jq -r '.remote.s3.enabled' "$CONFIG_FILE" 2>/dev/null || echo 'false')" == "true" ]]; then
        push_to_s3 "$backup_file"
    fi
    
    # FTP backup
    if [[ "$(jq -r '.remote.ftp.enabled' "$CONFIG_FILE" 2>/dev/null || echo 'false')" == "true" ]]; then
        push_to_ftp "$backup_file"
    fi
}

# Push to Git repository
push_to_git() {
    local backup_file="$1"
    local repo_url=$(jq -r '.remote.git.repository' "$CONFIG_FILE" 2>/dev/null || echo "")
    local branch=$(jq -r '.remote.git.branch' "$CONFIG_FILE" 2>/dev/null || echo "backups")
    
    if [[ -n "$repo_url" ]]; then
        log "INFO" "Pushing to Git repository: $repo_url"
        
        # Create temporary directory for git operations
        local git_temp_dir=$(mktemp -d)
        trap "rm -rf '$git_temp_dir'" EXIT
        
        # Clone repository
        git clone -b "$branch" "$repo_url" "$git_temp_dir" 2>/dev/null || {
            # If branch doesn't exist, create it
            git clone "$repo_url" "$git_temp_dir"
            cd "$git_temp_dir"
            git checkout -b "$branch" 2>/dev/null || git checkout "$branch"
        }
        
        # Copy backup file
        cp "$backup_file" "$git_temp_dir/"
        if [[ -f "${backup_file}.sha256" ]]; then
            cp "${backup_file}.sha256" "$git_temp_dir/"
        fi
        
        # Commit and push
        cd "$git_temp_dir"
        git add .
        git commit -m "Backup: $(date '+%Y-%m-%d %H:%M:%S') - $(basename "$backup_file")"
        git push origin "$branch"
        
        log "INFO" "Successfully pushed to Git repository"
    fi
}

# Push to Google Drive
push_to_google_drive() {
    local backup_file="$1"
    local folder_id=$(jq -r '.remote.google_drive.folder_id' "$CONFIG_FILE" 2>/dev/null || echo "")
    local credentials_file=$(jq -r '.remote.google_drive.credentials_file' "$CONFIG_FILE" 2>/dev/null || echo "")
    
    if [[ -n "$folder_id" && -f "$credentials_file" ]]; then
        log "INFO" "Pushing to Google Drive..."
        
        # Check if gdrive is available
        if command -v gdrive &> /dev/null; then
            gdrive upload --parent "$folder_id" "$backup_file"
            log "INFO" "Successfully pushed to Google Drive"
        else
            log "WARNING" "gdrive command not found, skipping Google Drive upload"
        fi
    fi
}

# Push to S3
push_to_s3() {
    local backup_file="$1"
    local bucket=$(jq -r '.remote.s3.bucket' "$CONFIG_FILE" 2>/dev/null || echo "")
    local region=$(jq -r '.remote.s3.region' "$CONFIG_FILE" 2>/dev/null || echo "us-east-1")
    
    if [[ -n "$bucket" ]]; then
        log "INFO" "Pushing to S3 bucket: $bucket"
        
        # Check if aws CLI is available
        if command -v aws &> /dev/null; then
            aws s3 cp "$backup_file" "s3://$bucket/$(basename "$backup_file")"
            if [[ -f "${backup_file}.sha256" ]]; then
                aws s3 cp "${backup_file}.sha256" "s3://$bucket/$(basename "$backup_file").sha256"
            fi
            log "INFO" "Successfully pushed to S3"
        else
            log "WARNING" "AWS CLI not found, skipping S3 upload"
        fi
    fi
}

# Push to FTP
push_to_ftp() {
    local backup_file="$1"
    local host=$(jq -r '.remote.ftp.host' "$CONFIG_FILE" 2>/dev/null || echo "")
    local port=$(jq -r '.remote.ftp.port' "$CONFIG_FILE" 2>/dev/null || echo "21")
    local username=$(jq -r '.remote.ftp.username' "$CONFIG_FILE" 2>/dev/null || echo "")
    local password=$(jq -r '.remote.ftp.password' "$CONFIG_FILE" 2>/dev/null || echo "")
    local path=$(jq -r '.remote.ftp.path' "$CONFIG_FILE" 2>/dev/null || echo "/")
    
    if [[ -n "$host" && -n "$username" ]]; then
        log "INFO" "Pushing to FTP server: $host"
        
        # Use curl for FTP upload
        curl -T "$backup_file" "ftp://$host:$port$path/" --user "$username:$password"
        if [[ -f "${backup_file}.sha256" ]]; then
            curl -T "${backup_file}.sha256" "ftp://$host:$port$path/" --user "$username:$password"
        fi
        
        log "INFO" "Successfully pushed to FTP"
    fi
}

# Main backup function
main() {
    log "INFO" "Starting backup process..."
    
    # Check if backup is enabled
    if [[ "$BACKUP_ENABLED" != "true" ]]; then
        log "INFO" "Backup is disabled in configuration"
        exit 0
    fi
    
    # Initialize
    check_directories
    load_config
    
    # Create backup
    local backup_filename=$(get_backup_filename)
    local backup_file=$(create_backup "$backup_filename")
    
    # Clean old backups
    clean_old_backups
    
    # Push to remote storage
    push_to_remote "$backup_file"
    
    # Send success notification
    local backup_size=$(du -h "$backup_file" | cut -f1)
    local success_message="✅ Backup completed successfully\n📁 File: $(basename "$backup_file")\n📊 Size: $backup_size\n⏰ Time: $(date '+%Y-%m-%d %H:%M:%S')"
    send_discord_notification "success" "$success_message"
    
    log "INFO" "Backup process completed successfully"
    echo -e "${GREEN}✅ Backup completed successfully${NC}"
    echo -e "${BLUE}📁 Backup file: $backup_file${NC}"
    echo -e "${BLUE}📊 Size: $backup_size${NC}"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --dry-run      Show what would be backed up without creating backup"
        echo "  --force        Force backup even if disabled in config"
        echo "  --clean-only   Only clean old backups"
        echo ""
        echo "This script creates daily backups of data and uploads directories."
        exit 0
        ;;
    --dry-run)
        echo "DRY RUN MODE - No backup will be created"
        BACKUP_ENABLED="true"
        main
        exit 0
        ;;
    --force)
        BACKUP_ENABLED="true"
        main
        exit 0
        ;;
    --clean-only)
        check_directories
        load_config
        clean_old_backups
        echo -e "${GREEN}✅ Old backups cleaned${NC}"
        exit 0
        ;;
    "")
        main
        exit 0
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 