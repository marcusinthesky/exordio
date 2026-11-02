# Agent contract

- Read the nearest README.md for commands and ARCHITECTURE.md for design decisions.
- Use the pinned devenv environment and repository just commands.
- Run Python commands through the appropriate locked uv project.
- Authored records own state. Use explicit creation and synchronization commands; never edit generated Insitu regions by hand.
- Task parents expose immediate children. Put supporting evidence in separate records and preserve stable paths.
- Checks validate without repair; use just fmt and just sync for explicit changes.
- Run just check before handoff and report any checks that could not run.
- Resolve secrets only for commands that need them. Never place credentials in tracked files.
