#!/bin/bash
set -e

# Determine version bump type based on production dependency changes in pyproject.toml
# Compares dependency versions between main and release branches
# Returns: major, minor, or patch

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to compare semantic versions
# Returns: major, minor, patch, or none
compare_versions() {
    local old_ver="$1"
    local new_ver="$2"
    local dep_name="$3"

    # Remove any leading 'v' and extract major.minor.patch
    old_ver=$(echo "$old_ver" | sed 's/^v//' | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' || echo "$old_ver")
    new_ver=$(echo "$new_ver" | sed 's/^v//' | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' || echo "$new_ver")

    if [ "$old_ver" = "$new_ver" ]; then
        echo "none"
        return
    fi

    # Split versions into components
    IFS='.' read -r old_major old_minor old_patch <<< "$old_ver"
    IFS='.' read -r new_major new_minor new_patch <<< "$new_ver"

    # Compare major versions
    if [ "$new_major" -gt "$old_major" ]; then
        echo -e "${GREEN}[INFO]${NC} $dep_name: Major version bump detected ($old_ver → $new_ver)" >&2
        echo "major"
        return
    fi

    # Compare minor versions
    if [ "$new_major" -eq "$old_major" ] && [ "$new_minor" -gt "$old_minor" ]; then
        echo -e "${GREEN}[INFO]${NC} $dep_name: Minor version bump detected ($old_ver → $new_ver)" >&2
        echo "minor"
        return
    fi

    # Compare patch versions
    if [ "$new_major" -eq "$old_major" ] && [ "$new_minor" -eq "$old_minor" ] && [ "$new_patch" -gt "$old_patch" ]; then
        echo -e "${GREEN}[INFO]${NC} $dep_name: Patch version bump detected ($old_ver → $new_ver)" >&2
        echo "patch"
        return
    fi

    # Version decreased or invalid
    echo -e "${YELLOW}[WARN]${NC} $dep_name: Version changed but not a standard bump ($old_ver → $new_ver)" >&2
    echo "none"
}

# Function to extract dependency version from pyproject.toml
# Args: dependency name, file content
extract_dependency_version() {
    local dep_name="$1"
    local content="$2"

    # Match patterns like: "pydantic>=2.8.2,<3.0" or "requests>=2.32.3,<3.0"
    # Extract the minimum version requirement
    version=$(echo "$content" | grep -E "^[[:space:]]*\"$dep_name" | sed -E "s/.*${dep_name}[><=]*([0-9]+\.[0-9]+\.[0-9]+).*/\1/")

    if [ -z "$version" ]; then
        echo "0.0.0"
    else
        echo "$version"
    fi
}

echo -e "${GREEN}[INFO]${NC} Analyzing dependency changes between release and main branches..."

# Get pyproject.toml content from both branches
echo -e "${GREEN}[INFO]${NC} Fetching pyproject.toml from release branch..."
release_content=$(git show origin/release:pyproject.toml 2>/dev/null || echo "")

echo -e "${GREEN}[INFO]${NC} Fetching pyproject.toml from main branch..."
main_content=$(git show origin/main:pyproject.toml 2>/dev/null || echo "")

if [ -z "$release_content" ]; then
    echo -e "${RED}[ERROR]${NC} Could not fetch pyproject.toml from release branch" >&2
    echo "patch"  # Default to patch if release branch doesn't exist yet
    exit 0
fi

if [ -z "$main_content" ]; then
    echo -e "${RED}[ERROR]${NC} Could not fetch pyproject.toml from main branch" >&2
    exit 1
fi

# Production dependencies to check
DEPENDENCIES=("pydantic" "requests")

# Default bump type
bump_type="patch"

echo -e "${GREEN}[INFO]${NC} Checking production dependencies..."

# Check each dependency
for dep in "${DEPENDENCIES[@]}"; do
    old_version=$(extract_dependency_version "$dep" "$release_content")
    new_version=$(extract_dependency_version "$dep" "$main_content")

    echo -e "${GREEN}[INFO]${NC} $dep: $old_version (release) vs $new_version (main)"

    if [ "$old_version" != "$new_version" ]; then
        dep_bump=$(compare_versions "$old_version" "$new_version" "$dep")

        # Priority: major > minor > patch
        if [ "$dep_bump" = "major" ]; then
            bump_type="major"
        elif [ "$dep_bump" = "minor" ] && [ "$bump_type" != "major" ]; then
            bump_type="minor"
        elif [ "$dep_bump" = "patch" ] && [ "$bump_type" = "patch" ]; then
            bump_type="patch"
        fi
    fi
done

echo -e "${GREEN}[INFO]${NC} Determined bump type: ${YELLOW}${bump_type}${NC}"

# Output for GitHub Actions
echo "$bump_type"