---
name: vrchat-udonsharp
description: Develop, scaffold, debug, review, and migrate VRChat Worlds UdonSharp/U# behaviours across Unity projects and VRChat SDK versions. Use for UdonSharpBehaviour scripts, project and SDK discovery, sync modes, ownership, UdonSynced state, late joiners, SendCustomNetworkEvent, NetworkCallable version compatibility, Program Assets, ClientSim-testable logic, custom inspectors, performance checks, and UdonSharp compile or runtime issues.
---

# VRChat UdonSharp

Build UdonSharp code for the Unity project currently in scope. Treat `UdonShrap` as a typo for UdonSharp.

## Adapt to the Current Project

1. Identify the target Unity project from the user's task or active workspace, then locate its root from `Assets`, `Packages`, and `ProjectSettings`. Do not treat the skill's own parent directory as the target project merely because the skill is stored there.
2. Read the project's instruction files before editing, including applicable `AGENTS.md`, `CLAUDE.md`, or local equivalents.
3. Inspect, rather than assume:
   - Unity version from `ProjectSettings/ProjectVersion.txt`.
   - VRChat package versions from `Packages/vpm-manifest.json`, package manifests, and the resolved package's `package.json`.
   - UdonSharp source location under embedded packages, `Library/PackageCache`, a legacy package, or `Assets/UdonSharp`.
   - Existing runtime/editor directories, namespaces, assembly definitions, serialized-field style, prefabs, and related behaviours.
4. Follow the current project's conventions and constraints. Do not carry names, paths, namespaces, Unity versions, or design rules from another project.
5. Prefer the installed SDK source and local examples over remembered APIs. Use current official VRChat documentation when local evidence is unavailable.

If the target project is hypothetical, unavailable, or ambiguous, do not borrow conventions from an unrelated visible project. Use clearly labeled placeholders or state the missing project facts; require a concrete target root before writing files.

Read [references/vrchat-sdk-local-paths.md](references/vrchat-sdk-local-paths.md) when locating a project, resolving an SDK layout, or checking a migrated project.

## Route the Task

For any implementation, migration, non-trivial review, networking task, compiler error, or custom inspector, read [references/udonsharp-development.md](references/udonsharp-development.md).

Load focused guidance as needed:

- Sync choice or mixed sync modes: [references/sync-modes.md](references/sync-modes.md)
- Ownership and state authority: [references/ownership.md](references/ownership.md)
- Network events and SDK feature gates: [references/network-events.md](references/network-events.md)
- Synced callbacks and program variables: [references/field-change-callback.md](references/field-change-callback.md)
- Compiler/runtime restrictions: [references/compiler-rules.md](references/compiler-rules.md)
- Networking design review: [checklists/networking-design.md](checklists/networking-design.md)
- Late-joiner review: [checklists/late-joiner-state.md](checklists/late-joiner-state.md)
- Final code review: [checklists/code-review.md](checklists/code-review.md)

Treat files in `examples/` as adaptable patterns, not project-ready drop-ins. Match the target project's namespace, naming, folder layout, UI system, SDK version, and authority model.

## Core Workflow

1. Inspect the closest existing behaviour and its scene or prefab usage.
2. Classify the logic before coding:
   - Purely local logic: `None` or `NoVariableSync`.
   - Persistent late-joiner state: `[UdonSynced]` with `Manual` or, when justified, `Continuous`.
   - Transient action: a network event.
   - Shared mutation: define who may author state and how ownership is obtained or routed.
3. Verify version-sensitive APIs in the installed SDK. In particular, `[NetworkCallable]` and parameterized network events require a compatible SDK; use only parameterless legacy events when maintaining an older SDK.
4. Implement the smallest behaviour that fits the project's architecture.
5. Validate exact event signatures, attributes, program-asset linkage, null handling, sync ownership, late joiners, and per-frame cost.
6. Test in proportion to the change: Unity import/compile, ClientSim, Build & Test, and multi-client or VR checks when relevant and available.
7. Report files changed, required hierarchy or prefab setup, Inspector assignments, tests performed, manual tests, and uncovered edge cases when the project or user expects that handoff.

## Create a Behaviour Safely

Prefer Unity's `Create > U# Script` flow when the editor is available. It creates the C# script and matching UdonSharp Program Asset using the installed SDK's format.

When only filesystem editing is available, prefer editing an existing paired U# script. For a new file-only scaffold, run the bundled generator from the skill root:

```bash
python scripts/create_udonsharp_behaviour.py DoorController --project-root . --output-dir Assets/MyWorld/Scripts --sync-mode no-variable --interact --namespace MyWorld
```

The generator writes only the `.cs` scaffold and never hand-authors Unity `.meta` or Program Asset YAML. Open Unity afterward and create or verify the matching Program Asset before considering the behaviour usable. If the installed UdonSharp editor cannot safely pair an external script, create the U# script in Unity and move the scaffold's class body into that paired script. Do not fabricate Program Asset serialization across SDK versions.

Common options:

- `--project-root <path>`
- `--output-dir Assets/<Project>/Scripts`
- `--sync-mode no-variable|manual|continuous|none|any`
- `--interact`
- `--namespace <Namespace>`
- `--dry-run`

## Universal Guardrails

- Inherit `UdonSharpBehaviour` and import `UdonSharp`.
- Declare an explicit sync mode unless the existing project intentionally uses `Any`.
- Keep `[UdonSynced]` compatible with the selected sync mode.
- Mutate Manual synced state only on the owner, then call `RequestSerialization()`.
- Store persistent late-joiner state in synced variables; do not rely on past events.
- Import and use `[NetworkCallable]` only when the installed SDK supports it.
- Keep network entry points public, `void`, non-static, non-overloaded, and parameter-safe.
- Use `nameof(...)` for event and program-variable names when supported by the call site.
- Prefer Inspector references and cached lookups over repeated runtime searches.
- Validate `Networking.LocalPlayer`, `VRCPlayerApi`, and Inspector references where editor or initialization timing can make them invalid.
- Keep expensive searches, allocations, ownership transfers, serialization, and network-event spam out of `Update`.
- Keep editor-only APIs out of runtime assemblies and build output.
- Avoid reflection, threads, async/await, dynamic code generation, ordinary file/network I/O, and unsupported general-purpose .NET patterns.
- Preserve existing user changes and avoid unrelated scene, prefab, or package edits.
