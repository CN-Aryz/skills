# Networking Design Checklist

Use before implementing ownership, sync, or network events.

## Choose the Model

- [ ] Installed SDK version and network-call feature support are known.
- [ ] Pure local: `None`.
- [ ] Event-only/local interaction: `NoVariableSync`.
- [ ] Persistent state: `Manual` + `[UdonSynced]`.
- [ ] Frequent approximate value: `Continuous`.
- [ ] One-shot action: `SendCustomNetworkEvent`.

## Ownership

- [ ] Who is allowed to author the state?
- [ ] Does local input need to transfer ownership?
- [ ] Should owner-routed mutation be used instead?
- [ ] Is master gating acceptable if master changes?
- [ ] Is `OnOwnershipRequest` consistent with the user action?

## Serialization

- [ ] Are synced fields compact?
- [ ] Are arrays initialized?
- [ ] Does Manual state call `RequestSerialization()`?
- [ ] Is `OnDeserialization()` implemented when visuals need applying?
- [ ] Are local visuals updated immediately after mutation?

## Network Events

- [ ] Does the event represent a transient action?
- [ ] Is the method `[NetworkCallable]` when the installed SDK supports and requires it?
- [ ] Is the method public, void, non-static, and non-overloaded?
- [ ] Are there no more than 8 parameters?
- [ ] Are parameters network-syncable and small?
- [ ] Is the event not being spammed from `Update`?
- [ ] Is an explicit event rate limit needed and supported by this SDK?
