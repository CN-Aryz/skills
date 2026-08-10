# VRChat Project and SDK Discovery

Use this reference before relying on paths, versions, or APIs from a different VRChat project. Resolve the target from the task or active workspace, not from the location where this skill happens to be installed.

## Confirm the Unity Project Root

Treat a directory as a Unity project when it contains:

```text
Assets/
Packages/
ProjectSettings/
```

If multiple Unity roots are visible, select only the one placed in scope by the user. If no target root is available, provide project-neutral guidance and do not infer a namespace or output path from the skill's containing repository.

Read applicable project instructions before editing. Then inspect:

```text
ProjectSettings/ProjectVersion.txt
Packages/vpm-manifest.json
Packages/manifest.json
Packages/packages-lock.json
```

Use `vpm-manifest.json` as the usual source for installed VRChat package versions. Confirm the resolved package's own `package.json` when present.

## Resolve the Package Instead of Assuming a Path

Check these layouts in order, stopping at the one the project actually uses:

```text
Packages/com.vrchat.worlds
Library/PackageCache/com.vrchat.worlds@<version>
Packages/com.vrchat.udonsharp
Library/PackageCache/com.vrchat.udonsharp@<version>
Assets/UdonSharp
```

Modern Worlds SDK packages usually integrate UdonSharp below:

```text
<worlds-package>/Integrations/UdonSharp
```

Do not require the modern layout when maintaining a legacy project. Do not upgrade or move packages unless the user asks.

## Useful Local Evidence

Within the resolved UdonSharp root, locate files by name instead of relying on one fixed directory layout:

```text
UdonSharpBehaviour.cs
UdonSharpAttributes.cs
UdonSharpProgramAsset.cs
Editor/Compiler/
Tests~/
Samples~/
```

Also inspect project-authored examples and imported samples under `Assets`. A common legacy example directory is `Assets/UdonSharp/UtilityScripts`, but it may not exist and is not a required convention.

## Feature Detection

For version-sensitive code, search the installed SDK for the actual symbol:

- `NetworkCallableAttribute` and `VRC.SDK3.UdonNetworkCalling` for modern network calls.
- The requested built-in event in `UdonSharpBehaviour.cs` for its exact signature.
- `BehaviourSyncMode` in `UdonSharpAttributes.cs` for sync behavior.
- Compiler diagnostics or tests for restricted language features.

Use package versions as a hint; use the installed symbol and compiler as the final authority.

## Program Asset Handling

Create U# scripts and Program Assets through the installed Unity/UdonSharp editor integration whenever possible. Program Asset YAML and metadata are SDK-owned serialization details. Do not copy GUIDs or hand-written Program Asset YAML from another project.
