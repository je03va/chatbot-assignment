# Copilot instructions

## Project intent
- This repository is a small Python workspace for experimenting with AI assistant workflows.
- Keep changes readable, explicit, and easy to understand by a teammate or future agent.
- Prefer small, focused additions over broad refactors unless the user specifically asks for a new architecture.

## Important layout
- Use `src/` for application code and package modules.
- Keep tests under `tests/` and validate behavior directly there.
- Treat README and repo docs as the source of truth for user-facing project intent.

## Agent conventions
- This repo includes two custom Copilot agents in `.github/agents/`:
  - `prompt-generator.agent.md`: turns a rough task into a well-structured prompt.
  - `implementation-teacher.agent.md`: explains the implementation in plain language for learning and onboarding.
- Use the prompt-generator when the work is ambiguous or needs a strong task brief before coding.
- Use the implementation-teacher when a stakeholder or teammate needs a walkthrough of what was built and why.

## Coding expectations
- Keep naming clear and domain-oriented.
- Favor direct logic and minimal abstraction until complexity justifies structure.
- Add tests for behavior that matters, especially for new agent or workflow logic.
- Mention trade-offs briefly when a design choice matters.

## Workflow
- Check `pyproject.toml` before adding dependencies or changing tooling.
- Prefer the repo's existing Python environment and test command rather than inventing parallel workflows.
- When explaining code, tie the rationale back to the actual files and responsibilities in `src/` and `tests/`.
