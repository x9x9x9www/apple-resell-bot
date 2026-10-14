---
name: openwolf
description: OpenWolf persistent project memory, context restoration, and fast symbol/file navigation. Use when starting or resuming work, searching symbols/files via openwolf index, checking past bug fixes (.wolf/buglog.json), managing project status (.wolf/STATUS.md), recording learnings (.wolf/cerebrum.md), or completing a task handoff.
---

# OpenWolf Operating Protocol for Apple Resell Bot

OpenWolf maintains persistent project memory and token efficiency across coding sessions and compaction cycles.

## 1. Session Resume & State Check
When starting or resuming work on this project:
1. Check `.wolf/STATUS.md` first. It contains the active task objectives, recently completed milestones, blockers, and acceptance criteria.
2. Check `.wolf/cerebrum.md` for:
   - `## Do-Not-Repeat`: Past traps (e.g. running multiple bot instances without PID lock, sending banners without LinkPreview/Article support).
   - `## Key Learnings`: Telegram Article structure (`send_rich_message`), custom emojis, regional routing.
   - `## User Preferences`: Single living message, no slash commands, beautiful banners with `•••` separator.

## 2. Instant Symbol & File Navigation
Before running expensive full-file reads or deep recursive greps:
1. Use `openwolf find <query>` to search symbols, functions, classes, and file paths with exact line numbers and estimated token sizes.
2. For an individual file summary:
   ```bash
   openwolf find --file bot/bot.py
   ```
3. Codebase map:
   ```bash
   openwolf map
   ```
4. If files changed:
   ```bash
   openwolf scan
   ```

## 3. Bug Logging & Knowledge Recording
- **Before fixing a bug:** Search `.wolf/buglog.json` for the error message or affected file name.
- **After fixing an issue:** Record the fix in `.wolf/buglog.json` or `.wolf/cerebrum.md`.

## 4. Session Handoff & Completion
Before concluding a task:
1. Update `.wolf/STATUS.md`.
2. Log a short one-line entry to `.wolf/memory.md`.
