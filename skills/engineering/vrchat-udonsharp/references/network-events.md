# Network Events

Use network events for transient actions, not persistent state. Verify the installed SDK before using modern network-call features.

## Choose the Compatible Event Model

- If the SDK contains `VRC.SDK3.UdonNetworkCalling.NetworkCallableAttribute`, prefer `[NetworkCallable]` receivers and use parameterized events when needed.
- If it does not, use only supported parameterless legacy events. Keep receivers public, do not prefix their names with `_`, and do not add the modern namespace or attribute.
- Do not silently upgrade a project's SDK to use a newer event model.

## Basic Pattern

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

## Targets

- `NetworkEventTarget.All`: sender and remote clients.
- `NetworkEventTarget.Others`: remote clients only.
- `NetworkEventTarget.Owner`: current owner only.
- `NetworkEventTarget.Self`: local loopback.

## Parameterized Events

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

Rules:

- Confirm the installed SDK provides the parameterized overload and `[NetworkCallable]`.
- Up to 8 parameters.
- Parameters must be network-syncable types.
- Receiver should be `[NetworkCallable]`.
- Method must be public and return void.
- Do not overload network-callable methods by name.
- Keep payloads small.
- Avoid network event spam in `Update`.
- Use `[NetworkCallable(maxEventsPerSecond: X)]` when the installed SDK supports it and the call needs an explicit safety limit.

## Persistent State Warning

Bad for late joiners:

```csharp
SendCustomNetworkEvent(NetworkEventTarget.All, nameof(OpenDoor));
```

Better:

```csharp
[UdonSynced] private bool isOpen;
```

Use network events for one-shot actions; use synced variables for state that must exist for late joiners.
