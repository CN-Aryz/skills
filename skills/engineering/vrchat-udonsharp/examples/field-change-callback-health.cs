using UdonSharp;
using UnityEngine;
using UnityEngine.UI;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class SyncedHealthDisplay : UdonSharpBehaviour
{
    [SerializeField] private Text healthText;

    [FieldChangeCallback(nameof(Health))]
    [UdonSynced] private int health = 100;

    public int Health
    {
        get => health;
        set
        {
            health = value;
            UpdateHealthUi();
        }
    }

    private void Start()
    {
        UpdateHealthUi();
    }

    public void Damage(int amount)
    {
        VRCPlayerApi localPlayer = Networking.LocalPlayer;
        if (!Utilities.IsValid(localPlayer))
            return;

        if (!Networking.IsOwner(gameObject))
            Networking.SetOwner(localPlayer, gameObject);

        Health = Mathf.Max(0, Health - amount);
        RequestSerialization();
    }

    private void UpdateHealthUi()
    {
        if (healthText != null)
            healthText.text = health.ToString();
    }
}
