# Late Joiner State Checklist

Use this when reviewing whether state should persist for players who join after an event happened.

## Questions

- [ ] Does the player need to see the current state after joining late?
- [ ] Would relying on a past network event lose this state?
- [ ] Can the state be represented as small synced fields?
- [ ] Does the owner serialize the state after mutation?
- [ ] Does `OnDeserialization()` or `FieldChangeCallback` apply visuals/UI?

## Use Synced Variables For

- Door open/closed.
- Game phase.
- Score.
- Current round.
- Object enabled/disabled state.
- Selected option.
- Player-ready state.

## Use Network Events For

- Playing a sound once.
- Particle effects.
- Hit flash.
- Animation trigger that does not need replay for late joiners.
- Short UI notification.

## Common Fix

Replace this:

```csharp
SendCustomNetworkEvent(NetworkEventTarget.All, nameof(OpenDoor));
```

with this:

```csharp
[UdonSynced] private bool isOpen;

private void SetOpen(bool value)
{
    isOpen = value;
    ApplyDoor();
    RequestSerialization();
}

public override void OnDeserialization()
{
    ApplyDoor();
}
```
