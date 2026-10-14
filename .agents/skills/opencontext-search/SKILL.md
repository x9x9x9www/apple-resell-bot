---
name: opencontext-search
description: Search OpenContext to find the right docs (safe, no index build by default)
---

# /opencontext-search

Safety: You may read from `.idea`, but do NOT write inside `.idea`.
OpenContext docs must live under the global contexts root; never create or edit docs in the project workspace.

Goal: Help the user find relevant existing docs quickly.
Safety: Do NOT trigger index builds by default (cost may be unpredictable).

1. Ask the user for a short query (or infer one from the conversation).
2. Try search in read-only mode:
   - Run: `oc search "<query>" --format json --limit 10`
   - If it succeeds, use results to pick candidate docs and then use **/opencontext-context** (manifest + reads) to load and cite them.
3. If search fails due to missing index:
   - Fall back to `oc context manifest <folder> --limit 20` and use doc `description` + filename triage.
   - Optionally suggest a controlled index build, but do NOT run it unless the user explicitly approves.
4. Cite sources using stable links `oc://doc/<stable_id>` when available.
