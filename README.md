# Agent Skills

Small, composable skills for coding agents. Each skill is an ordinary folder you can read, edit, version, and share across projects.

This repository follows the useful parts of Matt Pocock's style: keep skills focused, organize them by audience, make the trigger description do the routing work, and use progressive disclosure for deeper material.

## Layout

```text
agent-skills/
├── skills/
│   ├── engineering/
│   └── productivity/
├── scripts/validate_skills.py
├── AGENTS.md
├── CONTEXT.md
└── README.md
```

Use `engineering/` for software-development workflows and `productivity/` for general workflows. Add more categories only when they clarify discovery.

## Install into a project

After publishing this repository to GitHub, install all or selected skills with:

```bash
npx skills@latest add <github-user>/agent-skills
```

Keep this repository as the canonical source. Install, copy, or symlink selected skills into each project using the agent manager that project already uses.

## Add a skill

1. Create `skills/<category>/<skill-name>/SKILL.md`.
2. Add only the resource folders the skill needs: `scripts/`, `references/`, or `assets/`.
3. Add `agents/openai.yaml` when the skill needs UI metadata.
4. Run the validator from the repository root:

```bash
python scripts/validate_skills.py
```

5. Test the skill with a realistic request before sharing it.

## Invocation model

Prefer model-invoked skills for reusable discipline that can be selected automatically. Use user-invoked skills for explicit workflows, routers, or commands that should run only when requested.

## Design rules

- Keep `SKILL.md` concise; move detailed variants to directly linked references.
- Use lowercase hyphenated skill names.
- Make descriptions specific enough to trigger reliably.
- Include concrete decision points and validation checks.
- Do not add documentation to an individual skill unless the agent needs it to do the work.

## Inspiration

The organization and writing principles are informed by [mattpocock/skills](https://github.com/mattpocock/skills).
