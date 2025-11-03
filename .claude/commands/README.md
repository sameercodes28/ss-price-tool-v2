# Claude Code Custom Commands

This folder contains custom slash commands for this project.

## Available Commands

### `/update-context`

**Purpose:** Automatically update `.claude/context.md` with today's session changes.

### `/audit`

**Purpose:** Run comprehensive codebase audit to prevent documentation drift and code bloat.

**Usage:**
```
/audit
```

**What it does:**
1. Checks version consistency across all documentation files
2. Finds TODO/FIXME/DEPRECATED comments
3. Lists backup and test files in root directory
4. Verifies CHANGELOG is up to date
5. Generates actionable report with findings

**When to use:**
- After completing any feature
- Before bumping version numbers
- Monthly maintenance check
- Before major deployments

---

### `/update-context`

**Usage:**
```
/update-context
```

**What it does:**
1. Reads current context.md
2. Prompts you to describe what changed today
3. Formats it properly
4. Adds new session entry with date
5. Updates "Current State" and "Ongoing Tasks" sections
6. Shows you a summary before saving

**When to use:**
- At the end of each working session
- After making significant changes
- Before committing code to git

**Example:**
```
You: /update-context

Claude: I'll help you update the context file. What did we work on today?

You: We deployed the frontend to GitHub Pages and fixed the mobile CSS

Claude: [Creates properly formatted entry and shows summary]
        Should I save this update? (y/n)

You: y

Claude: ✅ Context updated! Don't forget to commit it.
```

## Creating New Commands

To create a new command:

1. Create a new `.md` file in this folder
2. Name it with the command name (e.g., `my-command.md`)
3. Add a description in the frontmatter:
   ```markdown
   ---
   description: What this command does
   ---

   Command instructions here...
   ```
4. Claude Code will automatically detect it

You can then use it with: `/my-command`
