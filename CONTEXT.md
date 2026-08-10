# Agent Skills

## Language

- **Skill**: A self-contained folder whose primary entry point is `SKILL.md`.
- **Skill pack**: This repository and the set of skills it contains.
- **Model-invoked**: A skill the agent may select automatically when the request fits.
- **User-invoked**: A skill the user explicitly requests by name or command.
- **Reference**: Detailed material loaded only when a skill needs it.

## Relationships

- A skill belongs to one category under `skills/`.
- A skill may link to references and may bundle scripts or assets.
- The repository validator checks every `SKILL.md` under `skills/`.
