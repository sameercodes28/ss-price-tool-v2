# .claude/ Folder

This folder contains AI/LLM-specific configuration and context for working with this project.

## Files

### `instructions.md`
**Purpose:** Automatic instructions loaded by Claude Code at the start of every conversation.

**What it does:**
- Tells Claude to read `context.md` first
- Provides quick project reference
- Sets session protocol

**How it works:**
Claude Code automatically reads files in `.claude/` folder and uses them as context for conversations. This means you don't need to manually prompt Claude to read the context file - it happens automatically!

### `context.md`
**Purpose:** Project state, history, and memory for LLM sessions.

**What it contains:**
- Current project state
- Recent changes (session log)
- Ongoing tasks
- Known issues/gotchas
- Important design decisions
- Code reference points
- Test queries

**Maintenance:**
- Update at END of each session
- Add new entries to "Recent Changes"
- Update "Ongoing Tasks"
- Document new gotchas

## How This Works

```
New Claude Code Session Started
         ↓
Claude Code reads .claude/instructions.md automatically
         ↓
Instructions tell Claude to read .claude/context.md
         ↓
Claude has full project context
         ↓
You can start working immediately!
```

## Benefits

✅ **No manual prompting** - Context loads automatically
✅ **Session continuity** - Every new Claude session understands the project
✅ **Version controlled** - Git tracks all context changes
✅ **Prevents hallucinations** - Claude knows recent changes and decisions
✅ **Fast onboarding** - New LLM sessions get up to speed instantly

## Usage

### Starting a New Session
Just start chatting! Claude will automatically:
1. Read instructions.md
2. Read context.md
3. Understand full project state

No need to say "Read .claude/context.md first" anymore!

### Ending a Session

**Option 1: Use the slash command (Easiest)**
```
/update-context
```

Claude will:
- Read current context.md
- Ask what you worked on today
- Format it properly
- Show you a preview
- Save the update

**Option 2: Manual prompt**
```
"Please update .claude/context.md with today's changes"
```

**Option 3: Git will remind you**

When you commit code, git will check if context.md was updated. If not, you'll see:

```bash
⚠️  REMINDER: You're committing code changes but .claude/context.md hasn't been updated.

   Quick update: Type '/update-context' in Claude Code

   Continue with commit anyway? (y/N)
```

## Example Workflow

```bash
# Start new terminal session
$ cd ~/Desktop/SS-1

# Open Claude Code
$ claude

# Just start chatting - no manual context loading needed!
You: "Help me deploy the frontend to GitHub Pages"

# Claude automatically knows:
# - Backend is already deployed
# - Frontend URL is in index.html line 188
# - Previous session updated main.py
# - There's a checklist in context.md

# At end of session:
You: "Update context.md with what we did"

# Claude updates context.md with deployment details
```

## File Organization

```
.claude/
├── README.md                  ← This file (explains the setup)
├── instructions.md            ← Auto-loaded by Claude Code
├── context.md                 ← Session memory & project state
└── commands/                  ← Custom slash commands
    ├── README.md              ← Command documentation
    └── update-context.md      ← /update-context command
```

## Configuration

If you want to customize what Claude sees automatically, edit `instructions.md`.

If you want to track specific patterns or gotchas, add them to `context.md`.

Both files are version controlled and should be committed to git.
