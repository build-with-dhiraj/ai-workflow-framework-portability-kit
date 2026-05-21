---
name: managing-skills-library
description: Audit and clean the local agent skills directory for necessity and redundancy. Primary governance skill for the library.
---

# Managing Skills Library

You are the maintainer of the local Antigravity Skills Master repository. Your objective is to ensure the library remains lean, highly-fidelity, and free of redundant capabilities.

## 1. Tracking Additions
Whenever a new skill is added (either via `npx skills add` or manual synthesis):
- **Log the Installation**: Mentally or via artifacts document the skill's purpose and its directory.
- **Trigger Guard**: Automatically invoke the `evaluating-skill-necessity` protocol to assess its true value.

## 2. Redundancy Audits
Periodically run audits on the `.agent/skills/` directory.

### Audit Workflow:
1. List all current directories using `list_dir`.
2. Group skills by domain (e.g., Frontend, Testing, Architecture, Project Management).
3. Identify overlaps. For example, if two skills exist for "React Animation" and "UI Animation", read both `SKILL.md` files.
4. **Research Cross-Reference**: Use the `notebooklm_notebook_query` tool on the 'Antigravity Skills Mastery Audit' notebook to verify if the skill's core knowledge is already redundant with the 300+ high-fidelity research sources.

## 3. Pruning Process
If you identify a skill that is entirely duplicated by a superior Master Skill:
1.  **Notify the User**: Present the redundancy to the user, explaining which skills overlap and why the superior skill renders the older one unnecessary.
2.  **Execute Deletion**: Upon user approval, use the `run_command` tool to safely `rm -rf` the redundant skill directory.
3.  **Update Artifacts**: Remove any references to the deleted skill from `walkthrough.md` or `task.md`.

## Integration with Primary Guard
This skill works _in tandem_ with `evaluating-skill-necessity`. `evaluating-skill-necessity` prevents bad skills from entering; `managing-skills-library` ensures the existing ecosystem remains cohesive over time.
