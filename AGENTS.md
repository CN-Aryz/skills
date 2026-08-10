# Repository instructions

- Treat `skills/` as the source of truth for shared agent capabilities.
- Keep each skill independently useful; do not require hidden conversation context.
- Put routing information in frontmatter and procedural guidance in the body.
- Add references, scripts, or assets only when they reduce repeated work.
- Run `python scripts/validate_skills.py` after changing a skill.
- Use the vocabulary in `CONTEXT.md` consistently.
