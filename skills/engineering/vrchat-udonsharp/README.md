# VRChat UdonSharp Skill

A skill package for developing, scaffolding, debugging, and reviewing VRChat Worlds UdonSharp behaviours.

## Structure

```text
vrchat-udonsharp/
├── SKILL.md
├── references/
│   ├── udonsharp-development.md
│   ├── sync-modes.md
│   ├── ownership.md
│   ├── network-events.md
│   ├── field-change-callback.md
│   ├── compiler-rules.md
│   └── vrchat-sdk-local-paths.md
├── examples/
│   ├── no-variable-sync-toggle.cs
│   ├── manual-synced-toggle.cs
│   ├── network-callable-event.cs
│   ├── owner-routed-mutation.cs
│   ├── master-gated-toggle.cs
│   └── field-change-callback-health.cs
├── checklists/
│   ├── code-review.md
│   ├── late-joiner-state.md
│   └── networking-design.md
└── scripts/
    └── create_udonsharp_behaviour.py
```

## Usage

Place the `vrchat-udonsharp` folder in your agent's skills directory.

For a file-only scaffold, run the script from the skill root and point it at the current Unity project:

```bash
python scripts/create_udonsharp_behaviour.py DoorController --project-root . --output-dir Assets/MyWorld/Scripts --sync-mode no-variable --interact
```

The generator writes only C# source. Create or verify the matching UdonSharp Program Asset in Unity; do not copy serialized Program Asset YAML or GUIDs between projects.

Avoid hard-coding host-specific paths, project names, namespaces, Unity versions, or SDK layouts in reusable instructions.
