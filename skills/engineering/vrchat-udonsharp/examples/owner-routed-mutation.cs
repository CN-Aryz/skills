using UdonSharp;
using UnityEngine;
using VRC.SDK3.UdonNetworkCalling;
using VRC.SDKBase;
using VRC.Udon.Common.Interfaces;

// Requires an SDK that provides NetworkCallableAttribute (Worlds SDK 3.8.1 or newer).
[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class OwnerRoutedScore : UdonSharpBehaviour
{
    [UdonSynced] private int score;

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
}
