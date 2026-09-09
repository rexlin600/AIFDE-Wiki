from pathlib import Path

from scripts.validate_wiki import validate


VALID = """---
type: concept
domain: [RAG]
depth: L3
importance: core
maturity: reviewed
created: 2026-09-09
updated: 2026-09-09
---
# 混合检索
"""


def write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_valid_note_passes(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/RAG-MOC.md", VALID)
    assert validate(tmp_path) == []


def test_missing_property_fails(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/RAG-MOC.md", VALID.replace("depth: L3\n", ""))
    assert any("depth" in error for error in validate(tmp_path))


def test_invalid_enum_fails(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/RAG-MOC.md", VALID.replace("importance: core", "importance: rare"))
    assert any("importance" in error for error in validate(tmp_path))


def test_invalid_filename_fails(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/坏#文件.md", VALID)
    assert any("文件名" in error for error in validate(tmp_path))


def test_broken_relative_link_fails(tmp_path: Path) -> None:
    write(tmp_path, "06-RAG/RAG-MOC.md", VALID + "\n[缺失](./missing.md)\n")
    assert any("失效链接" in error for error in validate(tmp_path))


def test_public_meta_files_and_templates_are_ignored(tmp_path: Path) -> None:
    write(tmp_path, "README.md", "# Home\n")
    write(tmp_path, "90-Templates/Template-Concept.md", "# Template\n")
    write(tmp_path, "docs/superpowers/specs/design.md", "# Design\n")
    assert validate(tmp_path) == []


def test_dependency_files_are_ignored(tmp_path: Path) -> None:
    write(tmp_path, "node_modules/package/README.md", "# Dependency\n")
    assert validate(tmp_path) == []
