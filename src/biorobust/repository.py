"""Small, deterministic repository inspection helpers."""

from __future__ import annotations

from pathlib import Path


IGNORED_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}


class Repository:
    def __init__(self, root: Path) -> None:
        # ``Path.resolve()`` can follow the workspace junction incorrectly on
        # some Windows Python installations. ``absolute()`` is sufficient for
        # this read-only scanner and avoids changing the target path.
        self.root = root.absolute()
        if not self.root.is_dir():
            raise ValueError(f"Target is not a directory: {root}")

    def files(self) -> list[Path]:
        paths: list[Path] = []
        for path in self.root.rglob("*"):
            if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
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
            if path.stat().st_size > 1_000_000:
                continue
            chunks.append(self.text(path))
        return "\n".join(chunks)

    def find(self, *names: str) -> list[Path]:
        wanted = {name.lower() for name in names}
        return [path for path in self.files() if path.name.lower() in wanted]

    def has_dir(self, *names: str) -> bool:
        wanted = {name.lower() for name in names}
        return any(path.is_dir() and path.name.lower() in wanted for path in self.root.rglob("*"))

