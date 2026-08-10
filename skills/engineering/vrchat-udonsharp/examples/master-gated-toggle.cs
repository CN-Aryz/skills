using UdonSharp;
using UnityEngine;
using VRC.SDKBase;

// Use only when the world explicitly accepts master changes. Master is not a security boundary.
[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class MasterGatedToggle : UdonSharpBehaviour
{
    [SerializeField] private GameObject target;

    [UdonSynced] private bool isEnabled;

    public override bool OnOwnershipRequest(VRCPlayerApi requestingPlayer, VRCPlayerApi requestedOwner)
    {
        return requestedOwner != null && requestedOwner.isMaster;
    }

    public override void Interact()
    {
        if (!Networking.IsMaster)
            return;

        VRCPlayerApi localPlayer = Networking.LocalPlayer;
        if (!Utilities.IsValid(localPlayer))
            return;

        if (!Networking.IsOwner(gameObject))
            Networking.SetOwner(localPlayer, gameObject);

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
