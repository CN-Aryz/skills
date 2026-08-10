#!/usr/bin/env python3
"""Create a project-relative UdonSharp C# scaffold without fabricating Unity assets.

Examples:

  python scripts/create_udonsharp_behaviour.py DoorController --project-root . --output-dir Assets/MyWorld/Scripts --interact
  python scripts/create_udonsharp_behaviour.py ScoreManager --project-root D:/Worlds/MyWorld --sync-mode manual --namespace MyWorld

Unity/UdonSharp must import the script and create or verify its matching Program Asset.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


SYNC_MODE_MAP = {
    "no-variable": "NoVariableSync",
    "manual": "Manual",
    "continuous": "Continuous",
    "none": "None",
    "any": "Any",
}


def write_text(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {path}")


def is_unity_project(path: Path) -> bool:
    return all((path / marker).is_dir() for marker in ("Assets", "Packages", "ProjectSettings"))


def find_project_root(start: Path) -> Optional[Path]:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if is_unity_project(candidate):
            return candidate
    return None


def resolve_project_root(explicit_root: Optional[str]) -> Optional[Path]:
    if explicit_root:
        candidate = Path(explicit_root).resolve()
        return candidate if is_unity_project(candidate) else None
    return find_project_root(Path.cwd())


def resolve_output_dir(project_root: Path, output_dir: str) -> Optional[Path]:
    requested = Path(output_dir)
    resolved = (requested if requested.is_absolute() else project_root / requested).resolve()
    assets_root = (project_root / "Assets").resolve()
    if resolved != assets_root and assets_root not in resolved.parents:
        return None
    return resolved


def find_udonsharp_root(project_root: Path) -> Optional[Path]:
    candidates = [
        project_root / "Packages" / "com.vrchat.worlds" / "Integrations" / "UdonSharp",
        project_root / "Packages" / "com.vrchat.udonsharp",
        project_root / "Assets" / "UdonSharp",
    ]
    package_cache = project_root / "Library" / "PackageCache"
    if package_cache.is_dir():
        candidates.extend(package_cache.glob("com.vrchat.worlds@*/Integrations/UdonSharp"))
        candidates.extend(package_cache.glob("com.vrchat.udonsharp@*"))

    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def valid_namespace(namespace: str) -> bool:
    return all(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", part) for part in namespace.split("."))


def class_template(class_name: str, sync_mode: str, include_interact: bool, namespace: Optional[str]) -> str:
    body_lines = [
        "using UdonSharp;",
        "using UnityEngine;",
        "",
        f"[UdonBehaviourSyncMode(BehaviourSyncMode.{sync_mode})]",
        f"public class {class_name} : UdonSharpBehaviour",
        "{",
        "    [SerializeField] private GameObject target;",
        "",
    ]

    if include_interact:
        body_lines.extend([
            "    public override void Interact()",
            "    {",
            "        if (target == null)",
            "            return;",
            "",
            "        target.SetActive(!target.activeSelf);",
            "    }",
        ])
    else:
        body_lines.extend([
            "    private void Start()",
            "    {",
            "        // Initialize behaviour state here.",
            "    }",
        ])

    body_lines.append("}")
    code = "\n".join(body_lines) + "\n"

    if namespace:
        indented = "\n".join(("    " + line if line else "") for line in code.splitlines())
        code = f"namespace {namespace}\n{{\n{indented}\n}}\n"

    return code


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create a UdonSharp C# scaffold inside a Unity project's Assets folder.")
    parser.add_argument("class_name", help="C# class name, e.g. DoorController")
    parser.add_argument("--project-root", default=None, help="Unity project root; auto-detected from the current directory when omitted")
    parser.add_argument("--output-dir", required=True, help="Existing project convention under Assets, e.g. Assets/MyWorld/Scripts")
    parser.add_argument("--sync-mode", choices=sorted(SYNC_MODE_MAP), default="no-variable")
    parser.add_argument("--interact", action="store_true", help="Include a basic Interact override")
    parser.add_argument("--namespace", default=None, help="Optional C# namespace")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", args.class_name):
        print(f"Invalid C# class name: {args.class_name}", file=sys.stderr)
        return 2

    if args.namespace and not valid_namespace(args.namespace):
        print(f"Invalid C# namespace: {args.namespace}", file=sys.stderr)
        return 2

    project_root = resolve_project_root(args.project_root)
    if project_root is None:
        print("Could not find a Unity project root containing Assets, Packages, and ProjectSettings.", file=sys.stderr)
        return 1

    output_dir = resolve_output_dir(project_root, args.output_dir)
    if output_dir is None:
        print("Output directory must be inside the selected project's Assets folder.", file=sys.stderr)
        return 2

    cs_path = output_dir / f"{args.class_name}.cs"

    if cs_path.exists():
        print(f"Refusing to overwrite existing script: {cs_path}", file=sys.stderr)
        return 1

    udonsharp_root = find_udonsharp_root(project_root)
    if udonsharp_root is None:
        print("warning: no local UdonSharp installation was found; verify that this is a VRChat Worlds project.", file=sys.stderr)

    sync_mode = SYNC_MODE_MAP[args.sync_mode]
    write_text(cs_path, class_template(args.class_name, sync_mode, args.interact, args.namespace), args.dry_run)

    if not args.dry_run:
        print(f"project root: {project_root}")
        if udonsharp_root is not None:
            print(f"UdonSharp root: {udonsharp_root}")
        print("done. Open Unity, import the script, and create or verify its UdonSharp Program Asset.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
