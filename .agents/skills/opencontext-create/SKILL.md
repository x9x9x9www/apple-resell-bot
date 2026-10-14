---
name: opencontext-create
description: Create a new idea or problem statement inside OpenContext
---

# /opencontext-create

Safety: You may read from `.idea`, but do NOT write inside `.idea`.
OpenContext docs must live under the global contexts root; never create or edit docs in the project workspace.

0. **Blocking requirement**: Do NOT answer the user’s broader question until the document has been created and minimally populated.
1. Infer the target space from recent context; if unclear, ask the user to specify the space (no default).
2. Derive a concise idea title & summary from the current conversation, then generate a slug (kebab-case; fallback to `idea-<YYYYMMDDHHmm>`). Only ask the user if information is insufficient.
3. Determine the target folder path under OpenContext (do NOT assume fixed subfolders like `ideas/`):
   - If the user gave a target folder, use it.
   - Otherwise, infer a sensible default and confirm with the user (or ask the user to choose).
   - If you are unsure what folders exist, run `oc folder ls --all` and pick/ask accordingly.
4. Ensure the target folder exists by running `oc folder create <folder_path> -d "<folder description>"` (safe to rerun).
5. **[CRITICAL - DO NOT SKIP]** You MUST run: `oc doc create <folder_path> <slug>.md -d "<title>"` to create the document.
   - This command registers the document in the OpenContext database.
   - DO NOT directly create the file with Write tool - you MUST use `oc doc create` first.
   - The command will output the file path after successful creation.
6. After `oc doc create` succeeds, set `CONTEXTS_ROOT=${OPENCONTEXT_CONTEXTS_ROOT:-$HOME/.opencontext/contexts}` and edit `${CONTEXTS_ROOT}/<folder_path>/<slug>.md` directly - do not mirror it inside the project repo.
7. Populate that file with:
   - Title / problem statement
   - Initial description/background
   - “Related Requests” list (can be empty placeholders)
8. Return the document path and immediately keep organizing content (no follow-up questions unless critical info is missing).
