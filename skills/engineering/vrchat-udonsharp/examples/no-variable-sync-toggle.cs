using UdonSharp;
using UnityEngine;

[UdonBehaviourSyncMode(BehaviourSyncMode.NoVariableSync)]
public class LocalToggle : UdonSharpBehaviour
{
    [SerializeField] private GameObject target;

    public override void Interact()
    {
        if (target == null)
            return;

        target.SetActive(!target.activeSelf);
    }
}
