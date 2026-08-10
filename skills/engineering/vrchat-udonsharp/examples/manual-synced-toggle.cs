using UdonSharp;
using UnityEngine;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class ManualSyncedToggle : UdonSharpBehaviour
{
    [SerializeField] private GameObject target;

    [UdonSynced] private bool isEnabled;

    private void Start()
    {
        ApplyState();
    }

    public override void Interact()
    {
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
