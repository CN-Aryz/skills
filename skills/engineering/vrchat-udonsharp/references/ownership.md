# Ownership

Ownership determines who can serialize Manual synced changes.

## Default Rule

Before mutating synced fields from local input:

```csharp
VRCPlayerApi localPlayer = Networking.LocalPlayer;
if (!Utilities.IsValid(localPlayer))
    return;

if (!Networking.IsOwner(gameObject))
    Networking.SetOwner(localPlayer, gameObject);
```

Then:

```csharp
// mutate synced fields
ApplyState();
RequestSerialization();
```

## Owner-Routed Mutation

Use this when only the owner should change state and the installed SDK supports `[NetworkCallable]`. On older SDKs, adapt it to a compatible parameterless legacy owner event:

```csharp
public void RequestAddScore()
{
    SendCustomNetworkEvent(NetworkEventTarget.Owner, nameof(OwnerAddScore));
}

[NetworkCallable]
public void OwnerAddScore()
{
    if (!Networking.IsOwner(gameObject))
        return;

    score++;
    RequestSerialization();
}
```

## Master-Gated Control

Use only when the world design accepts master changes. Never treat master status as a security boundary:

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

    // mutate synced state
    RequestSerialization();
}
```

## Warnings

- Master can change when players leave.
- Instance owner and master status are gameplay signals, not secure authorization.
- Ownership transfer is not a long-term authority design by itself.
- Gate both `OnOwnershipRequest` and the action method when control is restricted.
- Avoid repeatedly transferring ownership for high-frequency actions.
