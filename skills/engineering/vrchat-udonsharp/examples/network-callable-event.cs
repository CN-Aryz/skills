using UdonSharp;
using UnityEngine;
using VRC.SDK3.UdonNetworkCalling;
using VRC.Udon.Common.Interfaces;

// Requires an SDK that provides NetworkCallableAttribute (Worlds SDK 3.8.1 or newer).
[UdonBehaviourSyncMode(BehaviourSyncMode.NoVariableSync)]
public class NetworkCallableEffect : UdonSharpBehaviour
{
    [SerializeField] private ParticleSystem effect;

    public void PlayForEveryone()
    {
        SendCustomNetworkEvent(NetworkEventTarget.All, nameof(ReceivePlayEffect));
    }

    [NetworkCallable]
    public void ReceivePlayEffect()
    {
        if (effect != null)
            effect.Play();
    }
}
