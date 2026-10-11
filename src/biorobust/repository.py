"""Deterministic, read-only repository inspection helpers."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


IGNORED_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".biorobust"}


class Repository:
    def __init__(self, root: Path) -> None:
        # Avoid Path.resolve() here because some Windows workspace junctions
        # resolve to a duplicated path. The scanner does not need symlink
        # resolution and remains read-only.
        self.root = root.absolute()
        if not self.root.is_dir():
            raise ValueError(f"Target is not a directory: {root}")

    def files(self) -> list[Path]:
        """Return regular files, excluding generated/dependency directories.

        Symlinked files and directories are skipped deliberately: following
        them could inspect data outside the requested repository boundary.
        """
        paths: list[Path] = []
        for directory, dirnames, filenames in os.walk(self.root, followlinks=False):
            dirnames[:] = sorted(
                name
                for name in dirnames
                if name not in IGNORED_DIRS and not (Path(directory) / name).is_symlink()
            )
            for name in sorted(filenames):
                path = Path(directory) / name
                if path.is_symlink() or not path.is_file():
                    continue
                paths.append(path)
        return sorted(paths)

    def relative(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def names(self) -> set[str]:
        return {path.name.lower() for path in self.files()}

    def text(self, path: Path, limit: int = 200_000) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")[:limit]
        except OSError:
            return ""

    def all_text(self, max_files: int = 250) -> str:
        chunks: list[str] = []
        for path in self.files()[:max_files]:
            try:
                if path.stat().st_size > 1_000_000:
                    continue
            except OSError:
                continue
            chunks.append(self.text(path))
        return "\n".join(chunks)

    def find(self, *names: str) -> list[Path]:
        wanted = {name.lower() for name in names}
        return [path for path in self.files() if path.name.lower() in wanted]

    def manifest_hash(self) -> str:
        """Hash relative paths and complete file contents deterministically."""
        digest = hashlib.sha256()
        for path in self.files():
            digest.update(self.relative(path).encode("utf-8"))
            digest.update(b"\0")
            try:
                with path.open("rb") as stream:
                    while chunk := stream.read(1024 * 1024):
                        digest.update(chunk)
            except OSError:
                digest.update(b"<unreadable>")
            digest.update(b"\n")
        return digest.hexdigest()

    def find_path(self, value: str) -> Path | None:
        """Resolve a repository-relative path without escaping the root."""
        cleaned = value.strip().strip("'\"").replace("\\", "/")
        if not cleaned or cleaned.startswith(("$", "http://", "https://", "s3://", "/")):
            return None
        candidate = (self.root / Path(cleaned)).absolute()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            return None
        return candidate


