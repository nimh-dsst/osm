#!/bin/bash
#
# Dashboard Parquet Refresh Script
# Automates the process of updating the dashboard data file and deploying to staging/production.
#
# Prerequisites:
#   - AWS CLI configured with appropriate credentials
#   - GitHub CLI (gh) authenticated
#   - Git configured with push access to nimh-dsst/osm
#
# Usage:
#   ./scripts/refresh_dashboard.sh <parquet_file> [--deploy staging|production]
#
# Examples:
#   # Upload and deploy to staging (default)
#   ./scripts/refresh_dashboard.sh dashboard_251210-1430.parquet
#
#   # Upload and deploy to production
#   ./scripts/refresh_dashboard.sh dashboard_251210-1430.parquet --deploy production
#
#   # Just upload and create PR (no deployment trigger)
#   ./scripts/refresh_dashboard.sh dashboard_251210-1430.parquet --no-deploy

set -euo pipefail

# Configuration
S3_BUCKET="osm-terraform-storage"
S3_PATH="dashboard_data"
WORKFLOW_FILE=".github/workflows/build-docker.yml"
REPO="nimh-dsst/osm"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEPLOY_ENV="staging"
AUTO_DEPLOY=true
AUTO_MERGE=false

usage() {
    echo "Usage: $0 <parquet_file> [options]"
    echo ""
    echo "Options:"
    echo "  --deploy <env>    Deploy to 'staging' or 'production' (default: staging)"
    echo "  --no-deploy       Create PR but don't trigger deployment"
    echo "  --auto-merge      Automatically merge the PR after creation"
    echo "  --help            Show this help message"
    exit 1
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Install it from https://aws.amazon.com/cli/"
        exit 1
    fi

    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI not found. Install it from https://cli.github.com/"
        exit 1
    fi

    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI not authenticated. Run 'gh auth login'"
        exit 1
    fi

    log_success "All prerequisites met"
}

# Parse arguments
if [[ $# -lt 1 ]]; then
    usage
fi

PARQUET_FILE="$1"
shift

while [[ $# -gt 0 ]]; do
    case $1 in
        --deploy)
            DEPLOY_ENV="$2"
            if [[ "$DEPLOY_ENV" != "staging" && "$DEPLOY_ENV" != "production" ]]; then
                log_error "Deploy environment must be 'staging' or 'production'"
                exit 1
            fi
            shift 2
            ;;
        --no-deploy)
            AUTO_DEPLOY=false
            shift
            ;;
        --auto-merge)
            AUTO_MERGE=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate parquet file
if [[ ! -f "$PARQUET_FILE" ]]; then
    log_error "Parquet file not found: $PARQUET_FILE"
    exit 1
fi

PARQUET_BASENAME=$(basename "$PARQUET_FILE")
S3_URL="s3://${S3_BUCKET}/${S3_PATH}/${PARQUET_BASENAME}"

check_prerequisites

# Step 1: Upload to S3
log_info "Uploading $PARQUET_BASENAME to S3..."
aws s3 cp "$PARQUET_FILE" "$S3_URL"
log_success "Uploaded to $S3_URL"

# Step 2: Create GitHub issue
log_info "Creating GitHub issue..."
ISSUE_TITLE="Upload new parquet file for dashboard: $PARQUET_BASENAME"
ISSUE_BODY="Automated update to refresh dashboard data with new parquet file.

**S3 Location:** \`$S3_URL\`

**Actions:**
- [ ] Update S3 URL in build-docker.yml
- [ ] Deploy to staging
- [ ] Verify dashboard at https://dev.opensciencemetrics.org
- [ ] Deploy to production (if staging is successful)
- [ ] Verify dashboard at https://opensciencemetrics.org"

ISSUE_URL=$(gh issue create --repo "$REPO" --title "$ISSUE_TITLE" --body "$ISSUE_BODY")
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
log_success "Created issue #$ISSUE_NUMBER: $ISSUE_URL"

# Step 3: Create and checkout branch
BRANCH_NAME="${ISSUE_NUMBER}-upload-new-parquet-file-for-dashboard"
log_info "Creating branch: $BRANCH_NAME"

# Ensure we're on main and up to date
git fetch origin main
git checkout main
git pull origin main

# Create and switch to new branch
git checkout -b "$BRANCH_NAME"
log_success "Created and checked out branch: $BRANCH_NAME"

# Step 4: Update the S3 URL in build-docker.yml
log_info "Updating S3 URL in $WORKFLOW_FILE..."

# Find the current S3 URL line and replace it
CURRENT_URL=$(grep -oP 's3://osm-terraform-storage/dashboard_data/[^\s]+' "$WORKFLOW_FILE" | head -1)
if [[ -z "$CURRENT_URL" ]]; then
    log_error "Could not find S3 URL in $WORKFLOW_FILE"
    exit 1
fi

log_info "Replacing: $CURRENT_URL"
log_info "With: $S3_URL"

sed -i "s|$CURRENT_URL|$S3_URL|g" "$WORKFLOW_FILE"
log_success "Updated $WORKFLOW_FILE"

# Step 5: Commit and push
log_info "Committing changes..."
git add "$WORKFLOW_FILE"
git commit -m "Update dashboard S3 URL to $PARQUET_BASENAME

Closes #$ISSUE_NUMBER

$(cat <<'EOF'
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

log_info "Pushing to origin..."
git push -u origin "$BRANCH_NAME"
log_success "Pushed branch to origin"

# Step 6: Create PR
log_info "Creating pull request..."
PR_TITLE="Update dashboard parquet file: $PARQUET_BASENAME"
PR_BODY="## Summary
- Updated S3 URL in build-docker.yml to use new parquet file
- S3 Location: \`$S3_URL\`

## Test plan
- [ ] Deploy to staging and verify dashboard at https://dev.opensciencemetrics.org
- [ ] If staging looks good, deploy to production
- [ ] Verify production dashboard at https://opensciencemetrics.org

Closes #$ISSUE_NUMBER

$(cat <<'EOF'
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

PR_URL=$(gh pr create --repo "$REPO" --title "$PR_TITLE" --body "$PR_BODY" --base main)
PR_NUMBER=$(echo "$PR_URL" | grep -oE '[0-9]+$')
log_success "Created PR #$PR_NUMBER: $PR_URL"

# Step 7: Auto-merge if requested
if [[ "$AUTO_MERGE" == true ]]; then
    log_info "Waiting for CI checks before merging..."

    # Wait for checks to pass (with timeout)
    TIMEOUT=300
    ELAPSED=0
    while [[ $ELAPSED -lt $TIMEOUT ]]; do
        STATUS=$(gh pr checks "$PR_NUMBER" --repo "$REPO" 2>/dev/null | grep -c "pass" || echo "0")
        PENDING=$(gh pr checks "$PR_NUMBER" --repo "$REPO" 2>/dev/null | grep -c "pending\|queued" || echo "0")

        if [[ "$PENDING" == "0" ]]; then
            break
        fi

        log_info "Waiting for CI checks... ($ELAPSED/$TIMEOUT seconds)"
        sleep 10
        ELAPSED=$((ELAPSED + 10))
    done

    log_info "Merging PR #$PR_NUMBER..."
    gh pr merge "$PR_NUMBER" --repo "$REPO" --squash --delete-branch
    log_success "Merged PR #$PR_NUMBER"
fi

# Step 8: Trigger deployment workflow
if [[ "$AUTO_DEPLOY" == true ]]; then
    log_info "Triggering deployment to $DEPLOY_ENV..."

    # If not auto-merged, wait for user to merge
    if [[ "$AUTO_MERGE" != true ]]; then
        log_warn "PR needs to be merged before deployment can proceed."
        echo ""
        echo "Options:"
        echo "  1. Merge the PR manually at: $PR_URL"
        echo "  2. Press Enter to trigger deployment workflow anyway (will use current main)"
        echo "  3. Press Ctrl+C to exit"
        echo ""
        read -p "Press Enter to continue or Ctrl+C to exit: "
    fi

    gh workflow run deploy-docker.yml \
        --repo "$REPO" \
        --field development-environment="$DEPLOY_ENV"

    log_success "Triggered deployment workflow for $DEPLOY_ENV"

    # Get the workflow run URL
    sleep 3  # Give GitHub a moment to register the run
    RUN_URL=$(gh run list --repo "$REPO" --workflow=deploy-docker.yml --limit 1 --json url --jq '.[0].url')
    log_info "Monitor deployment at: $RUN_URL"

    echo ""
    log_info "Monitoring deployment progress..."
    gh run watch --repo "$REPO" --exit-status || {
        log_error "Deployment failed! Check the workflow run for details."
        exit 1
    }

    log_success "Deployment to $DEPLOY_ENV completed successfully!"

    if [[ "$DEPLOY_ENV" == "staging" ]]; then
        echo ""
        log_info "Verify the dashboard at: https://dev.opensciencemetrics.org"
        echo ""
        echo "To deploy to production after verification, run:"
        echo "  gh workflow run deploy-docker.yml --repo $REPO -f development-environment=production"
    else
        echo ""
        log_info "Verify the dashboard at: https://opensciencemetrics.org"
    fi
else
    log_success "PR created. Manual steps remaining:"
    echo ""
    echo "1. Review and merge the PR: $PR_URL"
    echo ""
    echo "2. After merge, trigger deployment:"
    echo "   gh workflow run deploy-docker.yml --repo $REPO -f development-environment=staging"
    echo ""
    echo "3. Monitor the deployment:"
    echo "   gh run watch --repo $REPO"
    echo ""
    echo "4. After staging verification, deploy to production:"
    echo "   gh workflow run deploy-docker.yml --repo $REPO -f development-environment=production"
fi

# Return to main branch
git checkout main

log_success "Dashboard refresh process complete!"
