# UdonSharp Code Review Checklist

Use this checklist before returning generated or edited UdonSharp code.

## Script Shape

- [ ] Follows current project instructions, directories, namespace, naming, and assembly layout.
- [ ] Inherits `UdonSharpBehaviour`.
- [ ] Imports `UdonSharp`.
- [ ] Uses explicit `[UdonBehaviourSyncMode(...)]`.
- [ ] Uses `[SerializeField] private` for inspector references unless public access is required.
- [ ] Avoids constructors for behaviour state.

## Sync and Networking

- [ ] `[UdonSynced]` only appears on `Manual` or `Continuous` behaviours.
- [ ] Manual synced mutation happens on the owner.
- [ ] `RequestSerialization()` is called after Manual synced mutation.
- [ ] Late-joiner persistent state uses synced fields.
- [ ] Transient actions use network events.
- [ ] Network callable methods are public, void, non-static, non-overloaded, and parameter-safe.
- [ ] Installed SDK supports every network attribute, namespace, overload, and event signature used.
- [ ] Event names use `nameof(...)`.

## Runtime Safety

- [ ] Inspector references are null-checked.
- [ ] `Networking.LocalPlayer` and `VRCPlayerApi` values are null/validity-checked when needed.
- [ ] Expensive lookups are cached.
- [ ] No repeated `Find` / `GetComponent` in `Update`.
- [ ] No allocation-heavy per-frame code.

## Compatibility

- [ ] Built-in event signatures match `UdonSharpBehaviour.cs`.
- [ ] Attributes are supported by the installed SDK.
- [ ] The script is linked to a valid UdonSharp Program Asset after import.
- [ ] Editor-only APIs stay out of runtime assemblies and builds.
- [ ] Code avoids unsupported .NET patterns.
- [ ] Result can be tested in ClientSim, Build & Test, or Unity compile/import.
