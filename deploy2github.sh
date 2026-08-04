#!/usr/bin/env bash
set -euo pipefail

########################################
# CONFIG — LexiaTek (Pixel chassis pattern)
########################################
GITHUB_USER="rdebiasec"
REPO_NAME="lexiatek-website"
PRIVATE=false
DEFAULT_BRANCH="main"

########################################
# UTIL FUNCTIONS
########################################

log() {
  echo "[INFO  $(date '+%H:%M:%S')] $*"
}

warn() {
  echo "[WARN  $(date '+%H:%M:%S')] $*" >&2
}

err() {
  echo "[ERROR $(date '+%H:%M:%S')] $*" >&2
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Required command '$1' is not installed or not in PATH."
    exit 1
  fi
}

get_pat() {
  if [[ -n "${GITHUB_PAT:-}" ]]; then
    PAT="$GITHUB_PAT"
    log "Using PAT from GITHUB_PAT environment variable."
  elif [[ -n "${GH_TOKEN:-}" ]]; then
    PAT="$GH_TOKEN"
    log "Using PAT from GH_TOKEN environment variable."
  else
    read -r -s -p "Enter your GitHub PAT (will not be echoed): " PAT
    echo
  fi

  if [[ -z "$PAT" ]]; then
    err "GitHub PAT cannot be empty. Export GITHUB_PAT or GH_TOKEN, or enter at prompt."
    exit 1
  fi
}

########################################
# PRECHECKS
########################################

require_cmd git
require_cmd curl

log "Starting deployment for repo '$REPO_NAME' under user '$GITHUB_USER'."

get_pat

########################################
# CHECK IF GITHUB REPO ALREADY EXISTS
########################################

log "Checking if GitHub repository already exists..."

REPO_CHECK_STATUS=$(
  curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $PAT" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME"
)

if [[ "$REPO_CHECK_STATUS" == "200" ]]; then
  log "GitHub repo '$GITHUB_USER/$REPO_NAME' already exists. Skipping creation."
elif [[ "$REPO_CHECK_STATUS" == "404" ]]; then
  log "GitHub repo does not exist. Creating it now..."

  CREATE_STATUS=$(
    curl -s -o /tmp/github_repo_create_$$.json -w "%{http_code}" \
      -H "Authorization: token $PAT" \
      -H "Accept: application/vnd.github+json" \
      https://api.github.com/user/repos \
      -d "{\"name\": \"$REPO_NAME\", \"private\": $PRIVATE, \"description\": \"LexiaTek — landing penal Colombia (IA + abogado humano)\"}"
  )

  if [[ "$CREATE_STATUS" != "201" ]]; then
    err "Failed to create GitHub repository. HTTP status: $CREATE_STATUS"
    warn "Response body:"
    cat "/tmp/github_repo_create_$$.json" >&2 || true
    rm -f "/tmp/github_repo_create_$$.json"
    exit 1
  fi

  log "GitHub repository '$GITHUB_USER/$REPO_NAME' created successfully."
  rm -f "/tmp/github_repo_create_$$.json"
else
  err "Unexpected HTTP status when checking repo: $REPO_CHECK_STATUS"
  exit 1
fi

########################################
# INITIALIZE / UPDATE LOCAL GIT REPO
########################################

if [[ -d .git ]]; then
  log "Existing Git repository detected in current directory."
else
  log "No .git directory found. Initializing new Git repository..."
  git init
fi

log "Setting default branch to '$DEFAULT_BRANCH'..."
git symbolic-ref HEAD "refs/heads/$DEFAULT_BRANCH" 2>/dev/null || git branch -M "$DEFAULT_BRANCH"

if git rev-parse HEAD >/dev/null 2>&1; then
  log "Existing commits detected. Skipping git add/commit."
else
  log "Staging files..."
  git add .

  if git diff --cached --quiet; then
    log "No changes to commit (index is clean)."
  else
    log "Creating commit..."
    git commit -m "Initial LexiaTek site (Pixel chassis + Aegis visual)"
  fi
fi

########################################
# CONFIGURE REMOTE (WITHOUT STORING PAT)
########################################

REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

if git remote get-url origin >/dev/null 2>&1; then
  CURRENT_REMOTE=$(git remote get-url origin)
  if [[ "$CURRENT_REMOTE" != "$REMOTE_URL" ]]; then
    log "Updating 'origin' remote to $REMOTE_URL"
    git remote set-url origin "$REMOTE_URL"
  else
    log "'origin' remote already set correctly."
  fi
else
  log "Setting 'origin' remote to $REMOTE_URL"
  git remote add origin "$REMOTE_URL"
fi

########################################
# PUSH USING PAT IN THE PUSH URL ONLY
########################################

log "Pushing branch '$DEFAULT_BRANCH' to GitHub..."

PUSH_URL="https://$PAT@github.com/$GITHUB_USER/$REPO_NAME.git"

if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
  git push "$PUSH_URL" "$DEFAULT_BRANCH"
else
  git push -u "$PUSH_URL" "$DEFAULT_BRANCH"
fi

########################################
# ENABLE GITHUB PAGES (ACTIONS SOURCE)
########################################

log "Enabling GitHub Pages (GitHub Actions source)..."

PAGES_STATUS=$(
  curl -s -o /tmp/github_pages_$$.json -w "%{http_code}" \
    -X PUT \
    -H "Authorization: token $PAT" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/pages" \
    -d '{"build_type":"workflow"}'
)

if [[ "$PAGES_STATUS" == "200" || "$PAGES_STATUS" == "201" || "$PAGES_STATUS" == "204" ]]; then
  log "GitHub Pages configured to use GitHub Actions."
else
  warn "Pages API returned HTTP $PAGES_STATUS — enable manually: Settings → Pages → GitHub Actions."
  cat "/tmp/github_pages_$$.json" >&2 || true
fi
rm -f "/tmp/github_pages_$$.json" 2>/dev/null || true

log "Deployment complete."
log "Repository: https://github.com/$GITHUB_USER/$REPO_NAME"
log "Site (after Actions run): https://$GITHUB_USER.github.io/$REPO_NAME/"

rm -f /tmp/github_repo_create_$$.json 2>/dev/null || true
