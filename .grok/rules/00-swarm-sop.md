# Swarm SOP (always on)

You operate in a multi-agent (Skeleton Swarm) repository. Native Grok rules
are loaded; also obey root `AGENTS.md`.

## Priority

`project_spec.md` > `AGENTS.md` > `.crules/modes/*` > this file

## Personas

| Mode | When | File |
|------|------|------|
| Manager | planning, backlog, commit/branch/release | `.crules/modes/MANAGER.md` |
| Coder | implementation and tests | `.crules/modes/CODER.md` |
| Git policy | any VCS mutation | `.crules/modes/GIT_POLICY.md` |
| Bootstrapper | only if `AGENTS.md` is `[TEMPLATE]` | `.crules/modes/BOOTSTRAPPER.md` |

Default for coding requests: **Coder**.  
Default for “commit” / “release” / roadmap: **Manager**.

## Session checklist

1. Read `AGENTS.md` and `project_spec.md` when starting non-trivial work.
2. Track non-trivial work as Markdown under `.crules/tasks/wip/` with acceptance criteria.
3. Do not implement speculative features outside the request or active task.
4. Never use `--break-system-packages`. Prefer `pipx`, venv, or `PYTHONPATH=src python3 -m tinfo.cli --version`.

## Important files

| File | Use |
|------|-----|
| `project_spec.md` | Scope, stack, conventions |
| `AGENTS.md` | Hard boundaries and coding rules |
| `GROK.md` | Grok entrypoint |
| `.grok/agents/` | Optional named agent profiles |

## Verification

Before claiming done:

- Smoke: `PYTHONPATH=src python3 -m tinfo.cli --version`
- Tests: no automated suite yet — add/run targeted checks when introducing tests
- If version touched: runtime version matches metadata (`pyproject.toml`)
