# UdonSharp Development Reference

Use this reference only after discovering the target project's rules, Unity version, SDK layout, directory conventions, and related behaviours. The target comes from the task or active workspace, not automatically from the skill's installation directory.

## Ground the Work in the Current Project

- Read applicable project instruction files before editing.
- Inspect nearby UdonSharp scripts, assembly definitions, prefabs, scenes, and editor tools.
- Read `ProjectSettings/ProjectVersion.txt` and the package manifests under `Packages`.
- Resolve the actual Worlds/UdonSharp package root. Support embedded packages, `Library/PackageCache`, separate legacy UdonSharp packages, and old `Assets/UdonSharp` layouts.
- Locate `UdonSharpBehaviour.cs`, `UdonSharpAttributes.cs`, compiler sources, tests, and samples by name instead of assuming one fixed path.
- Mirror the current project's namespace, file placement, serialized-field style, Inspector UX, and validation requirements.

When the target project is not accessible, keep examples project-neutral and label namespace, path, or version assumptions instead of borrowing them from another visible repository.

Do not carry project names, paths, Unity versions, render-pipeline choices, or authority models from the skill's source project. When local SDK code and remembered or online examples disagree, prefer the installed SDK.

## Behaviour Skeleton

```csharp
using UdonSharp;
using UnityEngine;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.NoVariableSync)]
public class ExampleBehaviour : UdonSharpBehaviour
{
    [SerializeField] private GameObject target;

    public override void Interact()
    {
        if (target == null)
            return;

        target.SetActive(!target.activeSelf);
    }
}
```

Prefer inspector references over runtime searches. If runtime lookup is unavoidable, cache the result, guard nulls, and avoid repeated `Find` or `GetComponent` work in `Update`.

## Script and Program Asset Creation

Prefer Unity's `Create > U# Script` flow for a new behaviour. It creates the `.cs` file and matching UdonSharp Program Asset using the installed SDK's serialization.

When only filesystem editing is available, prefer an existing paired script. If a new `.cs` scaffold is necessary, create only the source file and require a later Unity import plus Program Asset linkage check. If the installed editor cannot safely pair an external script, create a U# script through Unity and move the implementation into that paired file. Do not copy `.meta` GUIDs or hand-author Program Asset YAML from another project.

## State Model First

Before writing networked code, decide what kind of behaviour is needed:

| Need | Preferred mechanism |
|---|---|
| Pure local behaviour | `BehaviourSyncMode.None` or `NoVariableSync` |
| Local interaction with possible network event | `NoVariableSync` |
| Persistent state for late joiners | `[UdonSynced]` + `Manual` |
| Frequent small changing value | `Continuous`, only if exactness is not critical |
| One-shot visual/audio/action | `SendCustomNetworkEvent` |
| Owner-authoritative mutation | Owner-routed network event or ownership transfer |

Do not use only network events for persistent world state. Late joiners receive synced variables, not past network events.

## Sync Modes

Use `[UdonBehaviourSyncMode(...)]` deliberately:

- `NoVariableSync`: no synced variables, but custom/network events can still be used. Good default for local interactions and event-only behaviours.
- `None`: no synced variables and no network events on this behaviour. Use for pure local logic.
- `Manual`: use `[UdonSynced]` fields and call `RequestSerialization()` from the object owner after mutation.
- `Continuous`: for small frequently-changing synced values where interpolation or approximate freshness is acceptable. Keep payloads small.
- `Any`: avoid unless the script is intentionally flexible.

`[UdonSynced]` fields are rejected on `None` and `NoVariableSync`.

Manual sync pattern:

```csharp
using UdonSharp;
using UnityEngine;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class SyncedToggle : UdonSharpBehaviour
{
    [SerializeField] private GameObject target;

    [UdonSynced] private bool isEnabled;

    private void Start()
    {
        if (target != null)
            ApplyState();
    }

    public override void Interact()
    {
        if (!Networking.IsOwner(gameObject))
            Networking.SetOwner(Networking.LocalPlayer, gameObject);

        isEnabled = !isEnabled;
        ApplyState();
        RequestSerialization();
    }

    public override void OnDeserialization()
    {
        ApplyState();
    }

    private void ApplyState()
    {
        if (target != null)
            target.SetActive(isEnabled);
    }
}
```

If initial state must be authoritative, initialize it only on the owner or set it intentionally in editor-authored synced fields.

## Synced Variables

Rules:

- Use `[UdonSynced]` only with `Manual` or `Continuous`.
- The owner is the source of truth for synced fields.
- For Manual sync, mutate synced fields on the owner, then call `RequestSerialization()`.
- Late joiners receive the latest synced field state.
- Arrays used as synced fields should be initialized. Do not leave synced arrays as `null`.
- Keep synced data compact. Avoid large arrays and frequently-changing complex state.

Example:

```csharp
[UdonSynced] private int score;
[UdonSynced] private bool isOpen;
[UdonSynced] private int[] scores = new int[0];
```

## Ownership Rules

Only the owner can serialize Manual synced changes.

Before changing synced state from local input, validate the local player when the code may run in editor-like contexts:

```csharp
VRCPlayerApi localPlayer = Networking.LocalPlayer;
if (!Utilities.IsValid(localPlayer))
    return;

if (!Networking.IsOwner(gameObject))
    Networking.SetOwner(localPlayer, gameObject);
```

Then mutate synced fields, apply local visuals, and call:

```csharp
RequestSerialization();
```

Only use master-gated gameplay when the world design explicitly accepts authority changing as players leave. Gate both the ownership request and the action, and never treat master status as a security boundary:

```csharp
public override bool OnOwnershipRequest(VRCPlayerApi requestingPlayer, VRCPlayerApi requestedOwner)
{
    return requestedOwner != null && requestedOwner.isMaster;
}

public override void Interact()
{
    if (!Networking.IsMaster)
        return;

    if (!Networking.IsOwner(gameObject))
        Networking.SetOwner(Networking.LocalPlayer, gameObject);

    // mutate synced state, apply locally, RequestSerialization()
}
```

Prefer owner-routed state mutation or an explicit synced authority model when it fits the feature.

## Network Events

Use network events for transient actions.

```csharp
using UdonSharp;
using UnityEngine;
using VRC.SDK3.UdonNetworkCalling;
using VRC.Udon.Common.Interfaces;

[UdonBehaviourSyncMode(BehaviourSyncMode.NoVariableSync)]
public class EffectBroadcaster : UdonSharpBehaviour
{
    [SerializeField] private ParticleSystem effect;

    public void PlayForEveryone()
    {
        SendCustomNetworkEvent(NetworkEventTarget.All, nameof(ReceivePlay));
    }

    [NetworkCallable]
    public void ReceivePlay()
    {
        if (effect != null)
            effect.Play();
    }
}
```

Common targets:

- `NetworkEventTarget.All`
- `NetworkEventTarget.Others`
- `NetworkEventTarget.Owner`
- `NetworkEventTarget.Self`

Use `nameof(...)` for event names.

## Parameterized Network Events

Parameterized network events and `[NetworkCallable]` are version-sensitive. Before using them, verify that the installed SDK exposes `VRC.SDK3.UdonNetworkCalling.NetworkCallableAttribute` and the required `SendCustomNetworkEvent` overload. Older SDKs support only parameterless legacy events; do not import modern types into them.

Rules:

- Up to 8 parameters.
- Parameters must use network-syncable types.
- The receiving method should be `[NetworkCallable]`.
- Method name overload conflicts are unsafe; avoid overloaded network-callable names.
- Keep payloads small and avoid repeated event spam.

```csharp
using UdonSharp;
using UnityEngine;
using VRC.SDK3.UdonNetworkCalling;
using VRC.Udon.Common.Interfaces;

[UdonBehaviourSyncMode(BehaviourSyncMode.NoVariableSync)]
public class PingRelay : UdonSharpBehaviour
{
    public void PingAll(int value)
    {
        SendCustomNetworkEvent(NetworkEventTarget.All, nameof(ReceivePing), value);
    }

    [NetworkCallable]
    public void ReceivePing(int value)
    {
        Debug.Log(value);
    }
}
```

Minimum `[NetworkCallable]` safety rules:

- public
- void return
- non-static
- non-virtual
- non-override
- non-overloaded by name
- no `ref`, `out`, `params`, default parameter values, generic methods, async methods, operators, or explicit interface implementations
- no more than eight parameters

Methods whose names start with `_` are not callable through legacy `SendCustomNetworkEvent` unless a compatible SDK marks them with `[NetworkCallable]`. Use an underscore prefix for public methods that must not be legacy network entry points.

## Built-In Events

Override signatures from `UdonSharpBehaviour.cs`. Common events include:

- `Interact()`
- `OnPlayerJoined(VRCPlayerApi player)`
- `OnPlayerLeft(VRCPlayerApi player)`
- `OnOwnershipTransferred(VRCPlayerApi player)`
- `OnOwnershipRequest(VRCPlayerApi requestingPlayer, VRCPlayerApi requestedOwner)`
- `OnPreSerialization()`
- `OnPostSerialization(SerializationResult result)`
- `OnDeserialization()`
- `OnDeserialization(DeserializationResult result)`
- `OnPickup()`, `OnDrop()`, `OnPickupUseDown()`, `OnPickupUseUp()`
- `InputJump(bool value, UdonInputEventArgs args)` and other input events

Do not create a method with a built-in event name but incompatible parameters; the compiler can report this as a built-in event signature conflict.

## FieldChangeCallback and Program Variables

`[FieldChangeCallback(nameof(PropertyName))]` makes network sync and `SetProgramVariable()` call the target property setter instead of directly assigning the field. The property type must match the field type, and the setter must assign the backing field if the value should change.

```csharp
[FieldChangeCallback(nameof(Health))]
[UdonSynced] private int health;

public int Health
{
    get => health;
    set
    {
        health = value;
        UpdateHealthUi();
    }
}
```

Prefer mutating the property locally too, so local and remote paths share logic:

```csharp
Health = Mathf.Max(0, Health - amount);
RequestSerialization();
```

Use `nameof(field)` with `GetProgramVariable` and `SetProgramVariable` to avoid string drift. Be careful with `SetProgramVariable`: incompatible value types can cause runtime errors.

## Supported C# Shape

UdonSharp supports a useful subset of C#, but code must still be Udon-compatible.

Generally safe:

- properties and backing fields
- field initializers
- simple arrays
- enums
- string formatting/interpolation
- many Unity and VRC component APIs
- `nameof(...)`

Use with caution:

- recursive methods
- custom classes
- jagged arrays
- complex inheritance
- complex Unity serialization
- `SetProgramVariable`
- allocation-heavy per-frame logic

Avoid:

- async/await
- threads
- file/network I/O through ordinary .NET APIs
- reflection-heavy designs
- LINQ-heavy logic
- constructors for behaviour state
- general .NET APIs that are not exposed to Udon

Initialize behaviour state in field initializers, `Start`, `OnEnable`, or explicit setup methods.

Use `Utilities.IsValid(obj)` or null checks for VRChat objects and players.

## Inspector and Serialization

- Public fields are inspector-exposed by default.
- Prefer `[SerializeField] private` for authored references.
- Use `[System.NonSerialized]` for runtime-only fields that should not be serialized into the behaviour.
- Use `[HideInInspector]`, `[Tooltip]`, `[Header]`, and `[AddComponentMenu]` when they improve Unity authoring.
- Complex Unity serialization may not behave like ordinary MonoBehaviours; inspect existing tests before using jagged arrays, custom classes, or unusual collections.

## Performance Rules

Avoid expensive work in `Update`.

Bad:

```csharp
private void Update()
{
    GameObject.Find("Target");
}
```

Better:

```csharp
[SerializeField] private GameObject target;
```

or cache once:

```csharp
private Transform cachedTarget;

private void Start()
{
    if (target != null)
        cachedTarget = target.transform;
}
```

Networking performance rules:

- Sync only what must be shared.
- Keep payloads compact.
- Avoid repeated ownership transfers.
- Avoid `RequestSerialization()` spam.
- Avoid network events in `Update`.
- Use events for transient effects and synced variables for persistent state.

## Review Checklist

- Does the implementation follow the current project's path, namespace, style, dependency, and validation rules?
- Does the script inherit `UdonSharpBehaviour` and import `UdonSharp`?
- Is the sync mode explicit and compatible with fields/network events?
- Are all synced mutations made by the owner before `RequestSerialization()`?
- Does late-joiner state need `[UdonSynced]` instead of only network events?
- Does the installed SDK support every version-sensitive network attribute and overload used?
- Are network callable methods public, non-overloaded, void, non-static, and parameter-safe?
- Are built-in event signatures exact?
- Are null/editor cases handled for `Networking.LocalPlayer`, player APIs, and inspector references?
- Is expensive work kept out of `Update` or cached?
- Are strings for events/program variables protected with `nameof(...)`?
- Is the C# script linked to a valid Program Asset after Unity import?
- Is the change testable in ClientSim, Build & Test, or at least Unity compile/import?
