# Compiler and Runtime Compatibility Rules

Use this when fixing UdonSharp compile errors, reviewing generated code, or adapting normal C# to UdonSharp.

## Check Local SDK First

Resolve the installed UdonSharp root first, then locate:

```text
UdonSharpBehaviour.cs
UdonSharpAttributes.cs
UdonSharpProgramAsset.cs
Editor/Compiler
Tests~
```

The root may be inside `Packages/com.vrchat.worlds`, `Library/PackageCache`, a separate legacy UdonSharp package, or `Assets/UdonSharp`.

## Built-In Events

Built-in event signatures must match exactly.

Common signatures:

```csharp
public override void Interact() {}
public override void OnPlayerJoined(VRCPlayerApi player) {}
public override void OnPlayerLeft(VRCPlayerApi player) {}
public override void OnOwnershipTransferred(VRCPlayerApi player) {}
public override bool OnOwnershipRequest(VRCPlayerApi requestingPlayer, VRCPlayerApi requestedOwner) { return true; }
public override void OnPreSerialization() {}
public override void OnPostSerialization(VRC.Udon.Common.SerializationResult result) {}
public override void OnDeserialization() {}
public override void OnPickup() {}
public override void OnDrop() {}
public override void OnPickupUseDown() {}
public override void OnPickupUseUp() {}
public override void InputJump(bool value, VRC.Udon.Common.UdonInputEventArgs args) {}
```

Do not create methods with built-in event names and incompatible parameters.

## NetworkCallable Safety Rules

Apply this section only when the installed SDK contains `NetworkCallableAttribute`. Older SDKs require compatible parameterless legacy events.

A network-callable method should be:

- `public`
- `void`
- non-static
- non-overloaded by name
- not generic
- not async
- no `ref`
- no `out`
- no `params`
- no default parameter values
- no more than 8 parameters
- only network-syncable parameter types

## C# Patterns to Avoid

Avoid or heavily review:

- async/await
- threads
- reflection
- LINQ-heavy code
- file or network I/O through ordinary .NET APIs
- constructors for behaviour state
- complex custom classes
- jagged arrays
- allocation-heavy `Update`
- runtime `Find` repeated every frame
- APIs or namespaces copied from a different SDK version without local verification

## Safer Alternatives

- Use field initializers, `Start`, `OnEnable`, or explicit setup methods.
- Use `[SerializeField] private` references.
- Cache runtime lookups.
- Use simple arrays and primitive fields.
- Split behaviours by responsibility.
- Keep editor APIs in editor-only folders or assemblies.
