#!/usr/bin/env python3
"""
Script to detect TfL API specification changes by rebuilding models and comparing with committed versions.

This script:
1. Fetches the latest TfL API specifications
2. Rebuilds the pydantic models
3. Compares the generated code with the committed version using git
4. Reports any changes detected

The approach is simple but effective: if the TfL API changes in any meaningful way,
the generated models will change, and git diff will show exactly what changed.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class SpecComparator:
    """Compares TfL API specifications by rebuilding and diffing generated code."""

    def __init__(self, repo_root: Path | None = None):
        """Initialize the comparator.

        Args:
            repo_root: Root directory of the git repository. If None, uses the script's parent directory.
        """
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.specs_dir = self.repo_root / "TfL_OpenAPI_specs"
        self.models_dir = self.repo_root / "pydantic_tfl_api" / "models"
        self.endpoints_dir = self.repo_root / "pydantic_tfl_api" / "endpoints"
        self.build_script = self.repo_root / "scripts" / "build_with_coordinator.py"

    def fetch_specs(self) -> bool:
        """Fetch the latest TfL API specifications.

        Returns:
            True if specs were fetched successfully, False otherwise.
        """
        print("📥 Fetching latest TfL API specifications...")
        try:
            # Import and run the spec fetcher
            sys.path.insert(0, str(self.repo_root / "scripts"))
            from fetch_tfl_specs import TfLAPIFetcher  # type: ignore[import-not-found]

            fetcher = TfLAPIFetcher()
            # Ensure specs directory exists
            self.specs_dir.mkdir(parents=True, exist_ok=True)
            fetcher.save_all_specs(str(self.specs_dir))
            print("✅ Specs fetched successfully")
            return True
        except Exception as e:
            print(f"❌ Error fetching specs: {e}")
            return False

    def rebuild_models(self) -> bool:
        """Rebuild the pydantic models from the fetched specs.

        Uses subprocess to invoke the build coordinator script, which:
        - Isolates the build process for clean output capture
        - Matches how the build system is designed to be invoked
        - Provides proper error handling and logging

        Returns:
            True if rebuild was successful, False otherwise.
        """
        print("\n🔨 Rebuilding pydantic models...")
        try:
            # Build command with validated, controlled paths
            # All paths are internal to the repo, no user input
            cmd = [
                sys.executable,  # Python interpreter (trusted)
                str(self.build_script),  # Build script path (validated at __init__)
                str(self.specs_dir),  # Specs directory (created by this script)
                str(self.repo_root / "pydantic_tfl_api"),  # Output dir (fixed path)
            ]

            # Run the build script in isolated subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.repo_root),  # Set working directory explicitly
            )
            print("✅ Models rebuilt successfully")
            if result.stdout:
                print(f"   Output: {result.stdout[:500]}")  # Show first 500 chars
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error rebuilding models: {e}")
            if e.stdout:
                print(f"   stdout: {e.stdout}")
            if e.stderr:
                print(f"   stderr: {e.stderr}")
            return False

    def get_git_diff(self) -> tuple[bool, str]:
        """Get git diff of the models directory.

        Returns:
            Tuple of (has_changes, diff_output).
        """
        print("\n🔍 Checking for changes in generated code...")
        try:
            # Check if there are any changes to tracked files
            result = subprocess.run(
                ["git", "diff", "--stat", str(self.models_dir), str(self.endpoints_dir)],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.repo_root),
            )

            has_changes = bool(result.stdout.strip())

            if has_changes:
                # Get detailed diff
                detailed_result = subprocess.run(
                    ["git", "diff", str(self.models_dir), str(self.endpoints_dir)],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=str(self.repo_root),
                )
                return True, detailed_result.stdout

            return False, ""
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running git diff: {e}")
            return False, ""

    def generate_change_summary(self, diff_output: str) -> dict[str, Any]:
        """Generate a summary of the changes detected.

        Args:
            diff_output: The git diff output.

        Returns:
            Dictionary containing change statistics and metadata.
        """
        lines = diff_output.split("\n")

        # Count changes
        files_changed = set()
        additions = 0
        deletions = 0

        for line in lines:
            if line.startswith("+++") or line.startswith("---"):
                # Extract filename from diff header
                parts = line.split("/", 1)
                if len(parts) > 1:
                    files_changed.add(parts[1])
            elif line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        # Compute hash of the diff for tracking
        diff_hash = hashlib.sha256(diff_output.encode()).hexdigest()[:12]

        return {
            "timestamp": datetime.now(tz=None).astimezone().isoformat(),
            "files_changed": len(files_changed),
            "files_list": sorted(files_changed),
            "additions": additions,
            "deletions": deletions,
            "total_changes": additions + deletions,
            "diff_hash": diff_hash,
        }

    def _cleanup_old_metadata(self, metadata_dir: Path, keep_count: int = 10) -> None:
        """Remove old metadata files, keeping only the most recent ones.

        Args:
            metadata_dir: Directory containing metadata files
            keep_count: Number of most recent files to keep
        """
        if not metadata_dir.exists():
            return

        # Get all JSON files, sort by modification time (newest first)
        metadata_files = sorted(
            metadata_dir.glob("change_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        # Remove files beyond keep_count
        for old_file in metadata_files[keep_count:]:
            old_file.unlink()
            print(f"   Cleaned up old metadata: {old_file.name}")

    def save_change_metadata(self, summary: dict[str, Any]) -> None:
        """Save change metadata to a JSON file and cleanup old files.

        Metadata is saved locally for the GitHub workflow to upload as artifacts.
        Old files are automatically cleaned up to prevent unbounded growth.

        Args:
            summary: The change summary dictionary.
        """
        metadata_dir = self.repo_root / ".github" / "spec_changes"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        timestamp = summary["timestamp"].replace(":", "-").replace(".", "-")
        filename = f"change_{timestamp}_{summary['diff_hash']}.json"
        filepath = metadata_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n📝 Change metadata saved to: {filepath!s}")

        # Cleanup old metadata files (keep last 10)
        self._cleanup_old_metadata(metadata_dir, keep_count=10)

    def compare(self, save_metadata: bool = True) -> tuple[bool, dict[str, Any] | None]:
        """Run the full comparison workflow.

        Args:
            save_metadata: Whether to save change metadata to a JSON file.

        Returns:
            Tuple of (changes_detected, change_summary).
        """
        # Step 1: Fetch latest specs
        if not self.fetch_specs():
            return False, None

        # Step 2: Rebuild models
        if not self.rebuild_models():
            return False, None

        # Step 3: Check for changes
        has_changes, diff_output = self.get_git_diff()

        if not has_changes:
            print("\n✅ No changes detected - TfL API specifications are unchanged")
            return False, None

        # Step 4: Generate change summary
        print("\n⚠️  Changes detected in generated code!")
        summary = self.generate_change_summary(diff_output)

        print("\n📊 Change Summary:")
        print(f"   Files changed: {summary['files_changed']}")
        print(f"   Additions: +{summary['additions']}")
        print(f"   Deletions: -{summary['deletions']}")
        print(f"   Diff hash: {summary['diff_hash']}")

        # Save metadata if requested
        if save_metadata:
            self.save_change_metadata(summary)

        return True, summary


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Detect TfL API specification changes by rebuilding and comparing models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Don't save change metadata to JSON file",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Root directory of the git repository (default: parent of script directory)",
    )

    args = parser.parse_args()

    comparator = SpecComparator(repo_root=args.repo_root)
    changes_detected, _summary = comparator.compare(save_metadata=not args.no_metadata)

    # Exit with code 1 if changes detected (useful for CI/CD)
    sys.exit(1 if changes_detected else 0)


if __name__ == "__main__":
    main()
