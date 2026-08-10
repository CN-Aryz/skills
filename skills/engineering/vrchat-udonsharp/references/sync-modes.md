# Sync Modes

Use explicit `[UdonBehaviourSyncMode(...)]` on every UdonSharp behaviour.

## Decision Table

| Situation | Use |
|---|---|
| Pure local behaviour; no network event | `BehaviourSyncMode.None` |
| Local behaviour or event-only behaviour; no synced fields | `BehaviourSyncMode.NoVariableSync` |
| Persistent state for late joiners | `BehaviourSyncMode.Manual` |
| Small frequently-changing synced value | `BehaviourSyncMode.Continuous` |
| Script intentionally flexible | `BehaviourSyncMode.Any`, but avoid by default |

Also inspect every UdonBehaviour, `VRCObjectSync`, and position-sync component on the same GameObject. Mixed Manual and Continuous requirements can conflict even when each script looks valid in isolation.

## None

Use only for behaviours that do not need synced variables or network events.

```csharp
[UdonBehaviourSyncMode(BehaviourSyncMode.None)]
public class PureLocalBehaviour : UdonSharpBehaviour
{
}
```

## NoVariableSync

Use when there are no `[UdonSynced]` fields but custom/network events may be used.

```csharp
[UdonBehaviourSyncMode(BehaviourSyncMode.NoVariableSync)]
public class EventOnlyBehaviour : UdonSharpBehaviour
{
}
```

## Manual

Use for authoritative persistent state.

```csharp
[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class ManualState : UdonSharpBehaviour
{
    [UdonSynced] private int score;
}
```

Manual rules:

1. Owner mutates synced fields.
2. Owner applies local visuals.
3. Owner calls `RequestSerialization()`.
4. Remote clients apply changes in `OnDeserialization()` or through `FieldChangeCallback`.

## Continuous

Use only for small values that update frequently. Avoid for arrays, large state, scoreboards, or exact game logic.

## Anti-Patterns

- `[UdonSynced]` with `None` or `NoVariableSync`.
- Using network events as the only source of persistent state.
- Calling `RequestSerialization()` from a non-owner.
- Using `Continuous` for large or exact state.
