import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import yaml
from urllib.parse import urlparse


class ObsidianExporter:
    """Exports research data to Obsidian vault with proper organization"""

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize Obsidian exporter

        Args:
            vault_path: Path to Obsidian vault selenium folder
                       Falls back to OBSIDIAN_VAULT_PATH env var
        """
        # Path resolution: parameter > env var > disabled
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            env_path = os.getenv('OBSIDIAN_VAULT_PATH')
            if env_path:
                self.vault_path = Path(env_path) / 'selenium'
            else:
                self.vault_path = None

        self.enabled = self.vault_path and self.vault_path.exists()

        if self.enabled:
            self._setup_folders()
        elif self.vault_path:
            print(f"[INFO] Obsidian vault not found at {self.vault_path}")
            print("[TIP] Create the vault or update OBSIDIAN_VAULT_PATH")

    def _setup_folders(self):
        """Create folder structure"""
        self.sessions_folder = self.vault_path / "Research_Sessions"
        self.by_source_folder = self.vault_path / "By_Source"
        self.index_folder = self.vault_path / "_Index"

        # Create all folders
        for folder in [self.sessions_folder, self.by_source_folder, self.index_folder]:
            folder.mkdir(parents=True, exist_ok=True)

    def export_research_session(self, report: Dict[str, Any],
                                artifacts_path: Optional[Path] = None) -> Optional[Path]:
        """
        Export research session to Obsidian vault

        Args:
            report: Research report from report_builder
            artifacts_path: Path to artifacts folder (optional, uses report metadata)

        Returns:
            Path to created session folder or None
        """
        if not self.enabled:
            return None

        # Get artifacts path from report if not provided
        if not artifacts_path and report.get('metadata', {}).get('artifacts_path'):
            artifacts_path = Path(report['metadata']['artifacts_path'])

        # Create session folder
        session_id = report['metadata']['analysis_id']
        session_folder = self.sessions_folder / session_id
        session_folder.mkdir(exist_ok=True)

        # Create subfolders
        (session_folder / "screenshots").mkdir(exist_ok=True)
        (session_folder / "data").mkdir(exist_ok=True)

        # 1. Save main report
        readme_content = self._generate_session_readme(report)
        (session_folder / "README.txt.md").write_text(readme_content, encoding='utf-8')

        # 2. Save data files
        (session_folder / "data" / "full_report.json").write_text(
            json.dumps(report, indent=2, default=str), encoding='utf-8'
        )

        if 'extraction_config' in report:
            (session_folder / "data" / "extraction_config.yaml").write_text(
                yaml.dump(report['extraction_config'], default_flow_style=False),
                encoding='utf-8'
            )

        # 3. Copy screenshots
        screenshots_copied = self._copy_screenshots(report, session_folder, artifacts_path)

        # 4. Create cross-references
        self._create_cross_references(report, session_folder)

        # 5. Update recent sessions
        self._update_recent_sessions(report, session_folder)

        print(f"[SUCCESS] Exported to: {session_folder}")
        print(f"  - Screenshots: {screenshots_copied}")

        return session_folder

    def _copy_screenshots(self, report: Dict, session_folder: Path,
                          artifacts_path: Optional[Path]) -> int:
        """Copy screenshots to Obsidian vault"""
        screenshots_copied = 0
        screenshots = report.get('artifacts', {}).get('screenshots', [])

        if not artifacts_path:
            print("[WARNING] No artifacts path - skipping screenshots")
            return 0

        for screenshot_info in screenshots:
            # Get source path
            src_path = Path(screenshot_info.get('path', ''))

            # Try absolute path first
            if not src_path.is_absolute():
                src_path = artifacts_path / src_path

            if src_path.exists():
                dst_path = session_folder / "screenshots" / src_path.name
                try:
                    shutil.copy2(src_path, dst_path)
                    screenshots_copied += 1
                    # Update report with Obsidian path
                    screenshot_info['obsidian_path'] = f"screenshots/{src_path.name}"
                except Exception as e:
                    print(f"[ERROR] Failed to copy {src_path.name}: {e}")

        return screenshots_copied

    def _generate_session_readme(self, report: Dict) -> str:
        """Generate README.txt for session"""
        metadata = report['metadata']
        domain = urlparse(metadata['url']).netloc

        readme = f"""# Research Session: {domain}"""
        return readme

