# selenium_fetcher/utils/file_handler.py

import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import re
import logging


class FileHandler:
    """
    Production-ready file management system.

    Handles all file operations for the recon engine with safety,
    efficiency, and clear organization.
    """

    # Directory structure definition
    DIRECTORIES = {
        'pdfs': 'Downloaded PDF files',
        'screenshots': 'Captured screenshots',
        'metadata': 'JSON metadata files',
        'html': 'HTML snapshots',
        'logs': 'Session logs',
        'exports': 'Exported data',
        'artifacts': 'Other downloaded files'
    }

    def __init__(self, base_path: Union[str, Path]):
        """
        Initialize file handler with base directory.

        Args:
            base_path: Root directory for all file operations
        """
        self.base_path = Path(base_path).resolve()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._ensure_directory_structure()

    def _ensure_directory_structure(self) -> None:
        """Create and verify directory structure."""
        try:
            # Create base directory
            self.base_path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            for dir_name in self.DIRECTORIES:
                dir_path = self.base_path / dir_name
                dir_path.mkdir(exist_ok=True)

            self.logger.debug(f"Directory structure verified at: {self.base_path}")

        except Exception as e:
            self.logger.error(f"Failed to create directory structure: {e}")
            raise

    def sanitize_filename(self,
                          filename: str,
                          max_length: int = 200,
                          preserve_extension: bool = True) -> str:
        """
        Create a safe, cross-platform filename.

        Args:
            filename: Original filename
            max_length: Maximum length (default 200 for safety)
            preserve_extension: Keep file extension intact

        Returns:
            Safe filename string
        """
        # Extract extension if needed
        extension = ""
        if preserve_extension and '.' in filename:
            parts = filename.rsplit('.', 1)
            filename = parts[0]
            extension = f".{parts[1]}"

        # Remove unsafe characters (keep alphanumeric, spaces, dashes, underscores)
        safe = re.sub(r'[^\w\s\-]', '', filename)

        # Replace spaces with underscores
        safe = safe.replace(' ', '_')

        # Remove multiple underscores/dashes
        safe = re.sub(r'[_\-]+', '_', safe)

        # Trim to max length (accounting for extension)
        max_name_length = max_length - len(extension)
        if len(safe) > max_name_length:
            safe = safe[:max_name_length]

        # Clean up edges
        safe = safe.strip('_-')

        # Ensure we have something
        if not safe:
            safe = "unnamed"

        return safe + extension

    def save_file(self,
                  content: Union[bytes, str],
                  filename: str,
                  subdirectory: str,
                  mode: str = 'wb') -> Optional[Path]:
        """
        Save content to file with safety checks.

        Args:
            content: File content
            filename: Desired filename
            subdirectory: Target subdirectory
            mode: File write mode

        Returns:
            Path to saved file or None on failure
        """
        try:
            # Ensure subdirectory exists
            target_dir = self.base_path / subdirectory
            target_dir.mkdir(exist_ok=True)

            # Sanitize filename
            safe_filename = self.sanitize_filename(filename)

            # Handle duplicates
            file_path = self._get_unique_path(target_dir / safe_filename)

            # Write file
            if isinstance(content, str):
                mode = 'w'

            with open(file_path, mode) as f:
                f.write(content)

            self.logger.debug(f"Saved file: {file_path}")
            return file_path

        except Exception as e:
            self.logger.error(f"Failed to save file {filename}: {e}")
            return None

    def move_file(self,
                  source: Union[str, Path],
                  subdirectory: str,
                  new_name: Optional[str] = None) -> Optional[Path]:
        """
        Move file to organized location.

        Args:
            source: Source file path
            subdirectory: Target subdirectory
            new_name: Optional new filename

        Returns:
            New file path or None on failure
        """
        try:
            source = Path(source)
            if not source.exists():
                self.logger.warning(f"Source file not found: {source}")
                return None

            # Determine target
            target_dir = self.base_path / subdirectory
            target_dir.mkdir(exist_ok=True)

            if new_name:
                filename = self.sanitize_filename(new_name)
            else:
                filename = source.name

            target_path = self._get_unique_path(target_dir / filename)

            # Move file
            shutil.move(str(source), str(target_path))

            self.logger.debug(f"Moved {source} -> {target_path}")
            return target_path

        except Exception as e:
            self.logger.error(f"Failed to move file: {e}")
            return None

    def copy_file(self,
                  source: Union[str, Path],
                  subdirectory: str,
                  new_name: Optional[str] = None) -> Optional[Path]:
        """
        Copy file to organized location.

        Args:
            source: Source file path
            subdirectory: Target subdirectory
            new_name: Optional new filename

        Returns:
            Path to copied file or None on failure
        """
        try:
            source = Path(source)
            if not source.exists():
                self.logger.warning(f"Source file not found: {source}")
                return None

            # Determine target
            target_dir = self.base_path / subdirectory
            target_dir.mkdir(exist_ok=True)

            if new_name:
                filename = self.sanitize_filename(new_name)
            else:
                filename = source.name

            target_path = self._get_unique_path(target_dir / filename)

            # Copy file
            shutil.copy2(str(source), str(target_path))

            self.logger.debug(f"Copied {source} -> {target_path}")
            return target_path

        except Exception as e:
            self.logger.error(f"Failed to copy file: {e}")
            return None

    def save_json(self,
                  data: Dict[str, Any],
                  filename: str,
                  subdirectory: str = 'metadata',
                  indent: int = 2) -> Optional[Path]:
        """
        Save data as JSON with proper formatting.

        Args:
            data: Data to save
            filename: Target filename
            subdirectory: Target subdirectory
            indent: JSON indentation

        Returns:
            Path to saved file or None
        """
        try:
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'

            content = json.dumps(data, indent=indent, default=str)
            return self.save_file(content, filename, subdirectory, mode='w')

        except Exception as e:
            self.logger.error(f"Failed to save JSON: {e}")
            return None

    def load_json(self,
                  filename: str,
                  subdirectory: str = 'metadata') -> Optional[Dict[str, Any]]:
        """
        Load JSON data from file.

        Args:
            filename: Filename to load
            subdirectory: Source subdirectory

        Returns:
            Loaded data or None
        """
        try:
            file_path = self.base_path / subdirectory / filename

            if not file_path.exists():
                self.logger.warning(f"JSON file not found: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Failed to load JSON: {e}")
            return None

    def list_files(self,
                   subdirectory: Optional[str] = None,
                   pattern: str = '*',
                   recursive: bool = False) -> List[Path]:
        """
        List files matching pattern.

        Args:
            subdirectory: Specific subdirectory or None for all
            pattern: Glob pattern
            recursive: Search recursively

        Returns:
            List of matching file paths
        """
        try:
            if subdirectory:
                search_dir = self.base_path / subdirectory
            else:
                search_dir = self.base_path

            if not search_dir.exists():
                return []

            if recursive:
                return [f for f in search_dir.rglob(pattern) if f.is_file()]
            else:
                return [f for f in search_dir.glob(pattern) if f.is_file()]

        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get detailed storage statistics.

        Returns:
            Dictionary with storage information
        """
        stats = {
            'total_size': 0,
            'file_count': 0,
            'by_directory': {},
            'by_type': {},
            'oldest_file': None,
            'newest_file': None
        }

        try:
            all_files = []

            # Analyze each directory
            for dir_name in self.DIRECTORIES:
                dir_path = self.base_path / dir_name
                if not dir_path.exists():
                    continue

                files = list(dir_path.rglob('*') if dir_path.is_dir() else [])
                files = [f for f in files if f.is_file()]

                dir_size = sum(f.stat().st_size for f in files)
                stats['by_directory'][dir_name] = {
                    'size': dir_size,
                    'count': len(files),
                    'size_human': self._human_readable_size(dir_size)
                }

                stats['total_size'] += dir_size
                stats['file_count'] += len(files)
                all_files.extend(files)

            # Analyze by file type
            for file in all_files:
                ext = file.suffix.lower()
                if ext not in stats['by_type']:
                    stats['by_type'][ext] = {'count': 0, 'size': 0}

                stats['by_type'][ext]['count'] += 1
                stats['by_type'][ext]['size'] += file.stat().st_size

            # Find oldest/newest
            if all_files:
                all_files.sort(key=lambda f: f.stat().st_mtime)
                stats['oldest_file'] = {
                    'path': str(all_files[0].relative_to(self.base_path)),
                    'modified': datetime.fromtimestamp(all_files[0].stat().st_mtime).isoformat()
                }
                stats['newest_file'] = {
                    'path': str(all_files[-1].relative_to(self.base_path)),
                    'modified': datetime.fromtimestamp(all_files[-1].stat().st_mtime).isoformat()
                }

            # Add human readable total
            stats['total_size_human'] = self._human_readable_size(stats['total_size'])

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {e}")
            return stats

    def cleanup_old_files(self,
                          days: int = 30,
                          subdirectory: Optional[str] = None,
                          dry_run: bool = True,
                          exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Clean up old files with safety features.

        Args:
            days: Age threshold in days
            subdirectory: Specific subdirectory or None for all
            dry_run: Preview without deleting
            exclude_patterns: Patterns to exclude from cleanup

        Returns:
            Cleanup summary
        """
        exclude_patterns = exclude_patterns or ['*.json', 'session_*']
        cutoff_date = datetime.now() - timedelta(days=days)

        summary = {
            'files_found': 0,
            'total_size': 0,
            'files_deleted': 0,
            'space_freed': 0,
            'errors': [],
            'preview': []
        }

        try:
            # Find candidate files
            if subdirectory:
                search_dirs = [self.base_path / subdirectory]
            else:
                search_dirs = [self.base_path / d for d in self.DIRECTORIES]

            candidates = []
            for search_dir in search_dirs:
                if not search_dir.exists():
                    continue

                for file_path in search_dir.rglob('*'):
                    if not file_path.is_file():
                        continue

                    # Check exclusions
                    if any(file_path.match(pattern) for pattern in exclude_patterns):
                        continue

                    # Check age
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        candidates.append(file_path)

            summary['files_found'] = len(candidates)
            summary['total_size'] = sum(f.stat().st_size for f in candidates)

            # Process files
            for file_path in candidates:
                try:
                    size = file_path.stat().st_size

                    if dry_run:
                        summary['preview'].append({
                            'path': str(file_path.relative_to(self.base_path)),
                            'size': self._human_readable_size(size),
                            'age_days': (datetime.now() - datetime.fromtimestamp(
                                file_path.stat().st_mtime)).days
                        })
                    else:
                        file_path.unlink()
                        summary['files_deleted'] += 1
                        summary['space_freed'] += size

                except Exception as e:
                    summary['errors'].append(f"{file_path}: {str(e)}")

            # Add human readable sizes
            summary['total_size_human'] = self._human_readable_size(summary['total_size'])
            summary['space_freed_human'] = self._human_readable_size(summary['space_freed'])

            # Log results
            if dry_run:
                self.logger.info(f"Cleanup preview: {summary['files_found']} files "
                                 f"({summary['total_size_human']}) would be deleted")
            else:
                self.logger.info(f"Cleanup complete: deleted {summary['files_deleted']} files, "
                                 f"freed {summary['space_freed_human']}")

            return summary

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            summary['errors'].append(str(e))
            return summary

    def calculate_file_hash(self,
                            file_path: Union[str, Path],
                            algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate cryptographic hash of file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, md5, etc)

        Returns:
            Hex digest or None
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return None

            hash_func = hashlib.new(algorithm)

            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)

            return hash_func.hexdigest()

        except Exception as e:
            self.logger.error(f"Failed to calculate hash: {e}")
            return None

    def _get_unique_path(self, base_path: Path) -> Path:
        """
        Get unique file path, adding number suffix if needed.

        Args:
            base_path: Desired file path

        Returns:
            Unique file path
        """
        if not base_path.exists():
            return base_path

        # Split name and extension
        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent

        # Try numbered versions
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

            # Safety limit
            if counter > 1000:
                raise ValueError(f"Cannot find unique path for {base_path}")

    def _human_readable_size(self, size_bytes: int) -> str:
        """
        Convert bytes to human readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human readable string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} PB"


# Quick test
if __name__ == "__main__":
    # Test basic functionality
    handler = FileHandler('./test_downloads')

    # Test file operations
    test_data = {"test": "data", "timestamp": datetime.now()}
    saved = handler.save_json(test_data, "test_file")
    print(f"Saved: {saved}")

    # Get stats
    stats = handler.get_storage_stats()
    print(f"\nStorage Stats:")
    print(f"Total: {stats['total_size_human']}")
    print(f"Files: {stats['file_count']}")

    # Test cleanup
    cleanup = handler.cleanup_old_files(days=7, dry_run=True)
    print(f"\nCleanup Preview:")
    print(f"Would delete: {cleanup['files_found']} files")
    print(f"Would free: {cleanup['total_size_human']}")

