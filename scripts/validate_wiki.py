from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml


TYPES = {
    "moc",
    "concept",
    "pattern",
    "experiment",
    "project",
    "source",
    "interview",
    "decision",
    "retrospective",
}
DEPTHS = {"L1", "L2", "L3", "L4"}
IMPORTANCE = {"core", "common", "extension"}
MATURITY = {"draft", "reviewed", "stable", "needs-update"}
REQUIRED = {"type", "domain", "depth", "importance", "maturity", "created", "updated"}
SKIP_DIRS = {
    ".git",
    ".github",
    ".obsidian",
    "90-Templates",
    "99-Assets",
    "docs",
    "node_modules",
}
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
INVALID_NAME = re.compile(r"[\\:#?]")


def wiki_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if len(relative.parts) == 1:
            continue
        if any(part in SKIP_DIRS or part.startswith(".") for part in relative.parts[:-1]):
            continue
        files.append(path)
    return sorted(files)


def load_properties(path: Path) -> tuple[dict[str, object] | None, str | None]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        return None, "缺少 YAML Front Matter"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, f"YAML 无法解析: {exc}"
    if not isinstance(data, dict):
        return None, "YAML Front Matter 必须是对象"
    return data, None


def validate_properties(path: Path, properties: dict[str, object]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED - properties.keys())
    if missing:
        errors.append(f"{path}: 缺少属性 {', '.join(missing)}")
    if properties.get("type") not in TYPES:
        errors.append(f"{path}: type 非法")
    if properties.get("depth") not in DEPTHS:
        errors.append(f"{path}: depth 非法")
    if properties.get("importance") not in IMPORTANCE:
        errors.append(f"{path}: importance 非法")
    if properties.get("maturity") not in MATURITY:
        errors.append(f"{path}: maturity 非法")
    domain = properties.get("domain")
    if not isinstance(domain, list) or not domain:
        errors.append(f"{path}: domain 必须是非空列表")
    return errors


def validate_links(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        decoded = unquote(target)
        resolved = (path.parent / decoded).resolve()
        if not resolved.exists():
            errors.append(f"{path}: 失效链接 {raw_target}")
    return errors


def validate(root: Path) -> list[str]:
    """返回仓库内全部 Wiki 结构错误；无错误时返回空列表。"""
    errors: list[str] = []
    for path in wiki_files(root):
        if INVALID_NAME.search(path.name):
            errors.append(f"{path}: 文件名包含非法字符")
        properties, parse_error = load_properties(path)
        if parse_error:
            errors.append(f"{path}: {parse_error}")
        elif properties is not None:
            errors.extend(validate_properties(path, properties))
        errors.extend(validate_links(path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AIFDE Wiki content")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Wiki validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
