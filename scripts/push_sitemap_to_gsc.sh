#!/bin/bash

# Google Search Console Sitemap Submission Script
# Part of MorningStar SEO Enhancement System Batch 188
# Automatically submits sitemaps to Google Search Console and performs SEO health checks

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/src/_data/seo.json"
SITE_URL=""
GSC_API_KEY=""
GSC_PROPERTY=""
SITEMAP_URL=""
SLACK_WEBHOOK=""
DISCORD_WEBHOOK=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Google Search Console Sitemap Submission Script

Usage: $0 [OPTIONS]

OPTIONS:
    -u, --url           Site URL (required)
    -k, --api-key       Google Search Console API key
    -p, --property      GSC property URL
    -s, --sitemap       Sitemap URL (defaults to {site_url}/sitemap.xml)
    -c, --config        Path to SEO config file
    --slack-webhook     Slack webhook URL for notifications
    --discord-webhook   Discord webhook URL for notifications
    --dry-run          Show what would be done without executing
    --generate-only    Only generate sitemap, don't submit
    --health-check     Run SEO health check only
    -v, --verbose      Verbose output
    -h, --help         Show this help

EXAMPLES:
    # Basic sitemap submission
    $0 -u "https://morningstar-swg.com" -k "your-api-key"
    
    # Full submission with notifications
    $0 -u "https://morningstar-swg.com" -k "your-api-key" --slack-webhook "https://hooks.slack.com/..."
    
    # Generate sitemap only
    $0 -u "https://morningstar-swg.com" --generate-only
    
    # SEO health check
    $0 -u "https://morningstar-swg.com" --health-check

ENVIRONMENT VARIABLES:
    GSC_API_KEY          Google Search Console API key
    SITE_URL            Site URL
    SLACK_WEBHOOK_URL   Slack webhook URL
    DISCORD_WEBHOOK_URL Discord webhook URL

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--url)
                SITE_URL="$2"
                shift 2
                ;;
            -k|--api-key)
                GSC_API_KEY="$2"
                shift 2
                ;;
            -p|--property)
                GSC_PROPERTY="$2"
                shift 2
                ;;
            -s|--sitemap)
                SITEMAP_URL="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --slack-webhook)
                SLACK_WEBHOOK="$2"
                shift 2
                ;;
            --discord-webhook)
                DISCORD_WEBHOOK="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --generate-only)
                GENERATE_ONLY=true
                shift
                ;;
            --health-check)
                HEALTH_CHECK=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Load configuration from environment or config file
load_config() {
    # Load from environment variables first
    SITE_URL="${SITE_URL:-${SITE_URL_ENV:-}}"
    GSC_API_KEY="${GSC_API_KEY:-${GSC_API_KEY_ENV:-}}"
    SLACK_WEBHOOK="${SLACK_WEBHOOK:-${SLACK_WEBHOOK_URL:-}}"
    DISCORD_WEBHOOK="${DISCORD_WEBHOOK:-${DISCORD_WEBHOOK_URL:-}}"
    
    # Load from config file if it exists
    if [[ -f "$CONFIG_FILE" ]]; then
        log_info "Loading configuration from $CONFIG_FILE"
        
        if command -v jq >/dev/null 2>&1; then
            if [[ -z "$SITE_URL" ]]; then
                SITE_URL=$(jq -r '.site.url // empty' "$CONFIG_FILE")
            fi
        else
            log_warning "jq not found. Install jq for config file parsing."
        fi
    fi
    
    # Set defaults
    GSC_PROPERTY="${GSC_PROPERTY:-$SITE_URL}"
    SITEMAP_URL="${SITEMAP_URL:-${SITE_URL}/sitemap.xml}"
    
    # Validate required parameters
    if [[ -z "$SITE_URL" ]]; then
        log_error "Site URL is required. Use -u option or set SITE_URL environment variable."
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for required tools
    command -v curl >/dev/null 2>&1 || missing_deps+=("curl")
    command -v node >/dev/null 2>&1 || missing_deps+=("node")
    
    # Check for optional tools
    if ! command -v jq >/dev/null 2>&1; then
        log_warning "jq not found. JSON parsing will be limited."
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install the missing tools and try again."
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

# Generate sitemap using our sitemap generator
generate_sitemap() {
    log_info "Generating sitemap..."
    
    local sitemap_script="$PROJECT_ROOT/src/utils/sitemap-generator.js"
    
    if [[ ! -f "$sitemap_script" ]]; then
        log_error "Sitemap generator not found at $sitemap_script"
        exit 1
    fi
    
    # Set environment variables for the generator
    export SITE_URL="$SITE_URL"
    export OUTPUT_DIR="$PROJECT_ROOT/dist"
    export SOURCE_DIR="$PROJECT_ROOT/src"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would generate sitemap using: node $sitemap_script"
        return 0
    fi
    
    # Run the sitemap generator
    cd "$PROJECT_ROOT"
    if node "$sitemap_script"; then
        log_success "Sitemap generated successfully"
        
        # Check if sitemap was created
        local sitemap_file="$PROJECT_ROOT/dist/sitemap.xml"
        if [[ -f "$sitemap_file" ]]; then
            local page_count
            page_count=$(grep -c '<url>' "$sitemap_file" || echo "0")
            log_info "Sitemap contains $page_count pages"
        fi
    else
        log_error "Failed to generate sitemap"
        exit 1
    fi
}

# Submit sitemap to Google Search Console
submit_to_gsc() {
    if [[ -z "$GSC_API_KEY" ]]; then
        log_warning "No Google Search Console API key provided. Skipping GSC submission."
        return 0
    fi
    
    log_info "Submitting sitemap to Google Search Console..."
    
    local gsc_url="https://www.googleapis.com/webmasters/v3/sites/${GSC_PROPERTY}/sitemaps/${SITEMAP_URL}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would submit sitemap: $SITEMAP_URL to GSC property: $GSC_PROPERTY"
        return 0
    fi
    
    # Submit sitemap
    local response
    response=$(curl -s -w "%{http_code}" \
        -X PUT \
        -H "Authorization: Bearer $GSC_API_KEY" \
        -H "Content-Type: application/json" \
        "$gsc_url" \
        -o /tmp/gsc_response.json)
    
    local http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]] || [[ "$http_code" == "204" ]]; then
        log_success "Sitemap submitted to Google Search Console successfully"
    else
        log_error "Failed to submit sitemap to GSC. HTTP code: $http_code"
        if [[ -f "/tmp/gsc_response.json" ]]; then
            log_error "Response: $(cat /tmp/gsc_response.json)"
        fi
        exit 1
    fi
}

# Check sitemap accessibility
check_sitemap_accessibility() {
    log_info "Checking sitemap accessibility..."
    
    local response
    response=$(curl -s -w "%{http_code}" -o /tmp/sitemap_check.xml "$SITEMAP_URL")
    local http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]]; then
        log_success "Sitemap is accessible at $SITEMAP_URL"
        
        # Basic validation
        if command -v xmllint >/dev/null 2>&1; then
            if xmllint --noout /tmp/sitemap_check.xml 2>/dev/null; then
                log_success "Sitemap XML is well-formed"
            else
                log_warning "Sitemap XML may have formatting issues"
            fi
        fi
    else
        log_error "Sitemap not accessible. HTTP code: $http_code"
        exit 1
    fi
}

# Run SEO health check
run_seo_health_check() {
    log_info "Running SEO health check..."
    
    local issues=()
    local warnings=()
    
    # Check robots.txt
    log_info "Checking robots.txt..."
    local robots_response
    robots_response=$(curl -s -w "%{http_code}" -o /tmp/robots.txt "${SITE_URL}/robots.txt")
    local robots_code="${robots_response: -3}"
    
    if [[ "$robots_code" == "200" ]]; then
        log_success "robots.txt is accessible"
        
        # Check if sitemap is referenced in robots.txt
        if grep -q "Sitemap:" /tmp/robots.txt; then
            log_success "Sitemap referenced in robots.txt"
        else
            warnings+=("Sitemap not referenced in robots.txt")
        fi
    else
        issues+=("robots.txt not accessible (HTTP $robots_code)")
    fi
    
    # Check meta tags on homepage
    log_info "Checking homepage meta tags..."
    local homepage_content
    homepage_content=$(curl -s "$SITE_URL")
    
    if echo "$homepage_content" | grep -q "<title>"; then
        log_success "Title tag found"
    else
        issues+=("Missing title tag on homepage")
    fi
    
    if echo "$homepage_content" | grep -q 'name="description"'; then
        log_success "Meta description found"
    else
        issues+=("Missing meta description on homepage")
    fi
    
    if echo "$homepage_content" | grep -q 'rel="canonical"'; then
        log_success "Canonical URL found"
    else
        warnings+=("Missing canonical URL on homepage")
    fi
    
    # Check for schema.org structured data
    if echo "$homepage_content" | grep -q "application/ld+json"; then
        log_success "Structured data found"
    else
        warnings+=("No structured data found on homepage")
    fi
    
    # Report results
    log_info "SEO Health Check Results:"
    
    if [[ ${#issues[@]} -eq 0 ]] && [[ ${#warnings[@]} -eq 0 ]]; then
        log_success "✅ No issues found!"
    else
        if [[ ${#issues[@]} -gt 0 ]]; then
            log_error "❌ Issues found:"
            for issue in "${issues[@]}"; do
                log_error "  - $issue"
            done
        fi
        
        if [[ ${#warnings[@]} -gt 0 ]]; then
            log_warning "⚠️  Warnings:"
            for warning in "${warnings[@]}"; do
                log_warning "  - $warning"
            done
        fi
    fi
    
    return ${#issues[@]}
}

# Send notification to Slack
send_slack_notification() {
    local message="$1"
    local status="$2"
    
    if [[ -z "$SLACK_WEBHOOK" ]]; then
        return 0
    fi
    
    local color="good"
    local emoji="✅"
    
    if [[ "$status" == "error" ]]; then
        color="danger"
        emoji="❌"
    elif [[ "$status" == "warning" ]]; then
        color="warning"
        emoji="⚠️"
    fi
    
    local payload
    payload=$(cat << EOF
{
    "attachments": [
        {
            "color": "$color",
            "title": "$emoji SEO System Update",
            "text": "$message",
            "fields": [
                {
                    "title": "Site",
                    "value": "$SITE_URL",
                    "short": true
                },
                {
                    "title": "Timestamp",
                    "value": "$(date -u +"%Y-%m-%d %H:%M:%S UTC")",
                    "short": true
                }
            ]
        }
    ]
}
EOF
    )
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would send Slack notification: $message"
        return 0
    fi
    
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$SLACK_WEBHOOK" > /dev/null
}

# Send notification to Discord
send_discord_notification() {
    local message="$1"
    local status="$2"
    
    if [[ -z "$DISCORD_WEBHOOK" ]]; then
        return 0
    fi
    
    local color=3066993  # Green
    local emoji="✅"
    
    if [[ "$status" == "error" ]]; then
        color=15158332  # Red
        emoji="❌"
    elif [[ "$status" == "warning" ]]; then
        color=15105570  # Orange
        emoji="⚠️"
    fi
    
    local payload
    payload=$(cat << EOF
{
    "embeds": [
        {
            "title": "$emoji SEO System Update",
            "description": "$message",
            "color": $color,
            "fields": [
                {
                    "name": "Site",
                    "value": "$SITE_URL",
                    "inline": true
                },
                {
                    "name": "Timestamp",
                    "value": "$(date -u +"%Y-%m-%d %H:%M:%S UTC")",
                    "inline": true
                }
            ]
        }
    ]
}
EOF
    )
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would send Discord notification: $message"
        return 0
    fi
    
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$DISCORD_WEBHOOK" > /dev/null
}

# Main execution function
main() {
    local start_time
    start_time=$(date +%s)
    
    log_info "🚀 Starting MorningStar SEO Enhancement System"
    log_info "Site: $SITE_URL"
    
    # Run health check if requested
    if [[ "${HEALTH_CHECK:-false}" == "true" ]]; then
        if run_seo_health_check; then
            send_slack_notification "SEO health check completed successfully" "success"
            send_discord_notification "SEO health check completed successfully" "success"
        else
            send_slack_notification "SEO health check found issues" "warning"
            send_discord_notification "SEO health check found issues" "warning"
        fi
        return 0
    fi
    
    # Generate sitemap
    generate_sitemap
    
    # Exit if only generating
    if [[ "${GENERATE_ONLY:-false}" == "true" ]]; then
        log_success "Sitemap generation completed"
        send_slack_notification "Sitemap generated successfully" "success"
        send_discord_notification "Sitemap generated successfully" "success"
        return 0
    fi
    
    # Check sitemap accessibility
    check_sitemap_accessibility
    
    # Submit to Google Search Console
    submit_to_gsc
    
    # Calculate execution time
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "🎉 SEO Enhancement System completed successfully in ${duration}s"
    
    # Send success notifications
    local message="Sitemap submitted successfully to Google Search Console in ${duration}s"
    send_slack_notification "$message" "success"
    send_discord_notification "$message" "success"
}

# Initialize variables
DRY_RUN=false
GENERATE_ONLY=false
HEALTH_CHECK=false
VERBOSE=false

# Parse arguments and run
parse_args "$@"
load_config
check_dependencies

# Set verbose output if requested
if [[ "$VERBOSE" == "true" ]]; then
    set -x
fi

# Trap errors and send notifications
trap 'log_error "Script failed"; send_slack_notification "SEO script failed" "error"; send_discord_notification "SEO script failed" "error"' ERR

# Run main function
main

log_info "✨ All done!"