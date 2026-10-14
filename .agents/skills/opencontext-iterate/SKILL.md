---
name: opencontext-iterate
description: Enrich an existing idea with additional context from OpenContext
---

# /opencontext-iterate

Safety: You may read from `.idea`, but do NOT write inside `.idea`.
OpenContext docs must live under the global contexts root; never create or edit docs in the project workspace.

1. Identify the target idea document from the current discussion (ask only if ambiguous). Set `CONTEXTS_ROOT=${OPENCONTEXT_CONTEXTS_ROOT:-$HOME/.opencontext/contexts}` and load `${CONTEXTS_ROOT}/<target_doc>` to understand existing sections (never duplicate it under the project repo).
2. Derive the owning space from the doc path (e.g., `<space>/.../foo.md` → space `<space>`). If the space is unclear, run `oc folder ls --all`. Then run `oc context manifest <space> --limit 10` (or `oc context manifest . --limit 10`) and load each `abs_path` for inspiration.
3. Update the Markdown directly in the global file:
   - Ensure a `## Iteration Log` section exists (create if missing).
   - Append a new entry timestamped with local date/time in readable format (e.g., `2025-12-11 17:00` or `Dec 11, 2025 5:00 PM`) that summarizes insights, cites referenced docs, and lists next steps/risks.
   - **Citation rule (DO NOT SKIP)**: when citing any OpenContext doc in `Iteration Log`, you MUST use the stable link format `oc://doc/<stable_id>` as the primary reference (example: `[label](oc://doc/<stable_id>)`). Only add `abs_path` and/or `range` when you specifically need auditability or line-level evidence. Do NOT cite using only file paths if `stable_id` is available in the manifest output.
   - Refresh any other impacted sections (Overview, Requirements, Implementation notes, etc.).
4. Save the updated document and call `oc doc set-desc <target_doc> "<latest summary>"` so the manifest reflects the newest iteration.
5. Report the updated doc path plus which references were used.
