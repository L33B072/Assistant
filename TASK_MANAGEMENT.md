# Task Management Commands

## ✅ New Commands Available!

### View Tasks
```
/priorities
```
Shows all incomplete tasks from WeeklyPlan.md with numbers.

**Example output:**
```
Weekly Priorities (from Obsidian):
  1. Review CNC specifications #work
  2. Complete client proposal #urgent
  3. Schedule team meeting #work
```

---

### Add a Task
```
/addtask <task description>
```
Adds a new task to WeeklyPlan.md under "This Week's Priorities"

**Examples:**
```
/addtask Review Q1 budget #work
/addtask Call supplier about materials #urgent
/addtask Update project documentation
```

The task will be added as uncompleted (`- [ ]`) in your Obsidian vault.

---

### Complete a Task
```
/completetask <number>
```
Marks a task as complete by its number from `/priorities` list.

**Examples:**
```
/completetask 1     # Completes the first task
/completetask 3     # Completes the third task
```

The task will be marked with `- [x]` in your Obsidian vault.

---

## Workflow Example

1. **See what needs to be done:**
   ```
   /priorities
   ```

2. **Start working on task #2:**
   ```
   /starttimer Working on client proposal
   ```

3. **When finished:**
   ```
   /stoptimer
   /completetask 2
   ```

4. **Add something new:**
   ```
   /addtask Follow up with client tomorrow #followup
   ```

---

## File Location

All tasks are stored in your configured Obsidian vault:
```
{your_vault_path}\WeeklyPlan.md
```

Configure the path in your `.env` file or `app/config.py`.

Changes made through Telegram are **immediately synced** to your Obsidian vault!

You can also edit the file directly in Obsidian, and use Telegram to view/manage tasks.

---

## Tips

- ✅ Use hashtags (#work, #urgent, #followup) to categorize tasks
- ✅ Tasks are numbered in the `/priorities` list for easy reference
- ✅ Completed tasks move to "- [x]" format in Obsidian
- ✅ You can mix Telegram commands and direct Obsidian editing
- ✅ If WeeklyPlan.md doesn't exist, `/addtask` will create it

---

## All Commands Summary

| Command | Description |
|---------|-------------|
| `/start` | Show all available commands |
| `/priorities` | View incomplete tasks (numbered) |
| `/addtask <text>` | Add a new task |
| `/completetask <#>` | Mark task as done |
| `/starttimer <desc>` | Start time tracking |
| `/stoptimer` | Stop time tracking |
| `/calendar` | Today's schedule (needs Azure) |
| `/focus` | AI focus coaching (needs OpenAI) |
| `/brainstorm <topic>` | AI brainstorming (needs OpenAI) |
