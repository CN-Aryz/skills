# FieldChangeCallback and Program Variables

`[FieldChangeCallback(nameof(PropertyName))]` routes synced field changes and `SetProgramVariable()` assignments through a property setter.

## Pattern

```csharp
[FieldChangeCallback(nameof(Health))]
[UdonSynced] private int health;

public int Health
{
    get => health;
    set
    {
        health = value;
        UpdateHealthUi();
    }
}
```

## Rules

- Property type must match field type.
- Setter must assign the backing field if the value should change.
- Keep setter side effects idempotent.
- Prefer mutating the property locally, not the backing field, when you want local and remote paths to match.
- Avoid complex logic in setters if initialization order is uncertain.

## Program Variables

Use `nameof(...)`:

```csharp
SetProgramVariable(nameof(health), 10);
object raw = GetProgramVariable(nameof(health));
```

Be careful: incompatible value types passed to `SetProgramVariable` can cause runtime errors.

## Good Use Cases

- Updating UI when synced health changes.
- Applying visual state when a synced field deserializes.
- Keeping local and remote state-application paths unified.

## Avoid

- Using callbacks to hide ownership logic.
- Heavy allocations in setters.
- Mutating other synced fields from a callback unless the ownership/serialization path is clear.
