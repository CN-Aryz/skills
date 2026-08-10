#!/usr/bin/env python3
"""Validate the portable structure and frontmatter of every repository skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def frontmatter(text: str) -> tuple[str | None, str | None, str | None]:
    if not text.startswith("---\n"):
        return None, None, "missing YAML frontmatter"

    end = text.find("\n---\n", 4)
    if end == -1:
        return None, None, "unterminated YAML frontmatter"

    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            return None, None, f"invalid frontmatter line: {line}"
        values[key.strip()] = value.strip().strip('"\'')

    return values.get("name"), values.get("description"), None


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skills_root = root / "skills"
    skill_files = sorted(skills_root.rglob("SKILL.md")) if skills_root.exists() else []

    if not skill_files:
        errors.append("no skills found under skills/")
        return errors

    for skill_file in skill_files:
        skill_name, description, error = frontmatter(skill_file.read_text(encoding="utf-8"))
        relative = skill_file.relative_to(root).as_posix()
        if error:
            errors.append(f"{relative}: {error}")
            continue
        if not skill_name:
            errors.append(f"{relative}: missing name")
        elif not SKILL_NAME.fullmatch(skill_name):
            errors.append(f"{relative}: invalid name '{skill_name}'")
        elif skill_file.parent.name != skill_name:
            errors.append(
                f"{relative}: folder '{skill_file.parent.name}' does not match name '{skill_name}'"
            )
        if not description:
            errors.append(f"{relative}: missing description")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    count = len(list((root / "skills").rglob("SKILL.md")))
    print(f"Validated {count} skill(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
