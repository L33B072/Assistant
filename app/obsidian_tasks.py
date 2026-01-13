from dataclasses import dataclass
from typing import List
import os
import aiofiles

from .msgraph_client import MSGraphClient
from .config import settings

@dataclass
class ObsidianTask:
    description: str
    completed: bool
    line_number: int
    tags: list[str]

def parse_markdown_tasks(md: str) -> List[ObsidianTask]:
    tasks: List[ObsidianTask] = []
    for idx, line in enumerate(md.splitlines(), start=1):
        line = line.strip()
        if line.startswith("- [ ]") or line.startswith("- [x]"):
            completed = line.startswith("- [x]")
            body = line[5:].strip()
            tags = [word for word in body.split() if word.startswith("#")]
            tasks.append(
                ObsidianTask(
                    description=body,
                    completed=completed,
                    line_number=idx,
                    tags=tags,
                )
            )
    return tasks

async def get_tasks_from_note(relative_path: str) -> List[ObsidianTask]:
    """
    Get tasks from an Obsidian note.
    relative_path like 'WeeklyPlan.md' or 'Tasks/WeeklyPlan.md' relative to vault root
    """
    # Try local file first (faster and works offline)
    local_file_path = os.path.join(settings.obsidian_local_path, relative_path)
    
    if os.path.exists(local_file_path):
        # Read from local file system
        async with aiofiles.open(local_file_path, 'r', encoding='utf-8') as f:
            md = await f.read()
    else:
        # Fallback to OneDrive Graph API
        client = MSGraphClient()
        full_path = settings.obsidian_root_path.strip("/") + "/" + relative_path.strip("/")
        md = await client.get_obsidian_file_text(full_path)
    
    return parse_markdown_tasks(md)


async def get_priorities_from_obsidian(note_path: str = "WeeklyPlan.md") -> str:
    """
    Extract priorities/tasks from an Obsidian note and format as text.
    Returns a formatted string of tasks for LLM context.
    """
    try:
        tasks = await get_tasks_from_note(note_path)
        
        if not tasks:
            return "No tasks found in weekly plan."
        
        incomplete_tasks = [t for t in tasks if not t.completed]
        
        if not incomplete_tasks:
            return "All tasks completed! 🎉"
        
        # Format tasks with numbers
        lines = ["Weekly Priorities (from Obsidian):"]
        for idx, task in enumerate(incomplete_tasks, start=1):
            tags_str = " ".join(task.tags) if task.tags else ""
            lines.append(f"  {idx}. {task.description} {tags_str}".strip())
        
        return "\n".join(lines)
    except Exception as e:
        return f"Could not load priorities from Obsidian: {e}"


async def read_obsidian_note(relative_path: str) -> str:
    """
    Read any Obsidian markdown note and return its full content.
    """
    local_file_path = os.path.join(settings.obsidian_local_path, relative_path)
    
    if os.path.exists(local_file_path):
        async with aiofiles.open(local_file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    else:
        # Fallback to OneDrive Graph API
        client = MSGraphClient()
        full_path = settings.obsidian_root_path.strip("/") + "/" + relative_path.strip("/")
        return await client.get_obsidian_file_text(full_path)


async def write_obsidian_note(relative_path: str, content: str) -> bool:
    """
    Write content to an Obsidian markdown note.
    Returns True if successful, False otherwise.
    """
    try:
        local_file_path = os.path.join(settings.obsidian_local_path, relative_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        
        async with aiofiles.open(local_file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to {relative_path}: {e}")
        return False

async def create_obsidian_page(page_name: str, content: str = "") -> bool:
    """
    Create a new Obsidian page with the given name.
    Returns True if successful, False otherwise.
    """
    # Ensure the page name ends with .md
    if not page_name.endswith('.md'):
        page_name = f"{page_name}.md"
    
    # Default content if none provided
    if not content:
        # Get current date for page creation
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        content = f"# {page_name[:-3]}\n\nCreated: {today}\n\n"
    
    return await write_obsidian_note(page_name, content)

async def append_to_obsidian_page(page_name: str, content: str) -> bool:
    """
    Append content to an existing Obsidian page, or create it if it doesn't exist.
    Returns True if successful, False otherwise.
    """
    # Ensure the page name ends with .md
    if not page_name.endswith('.md'):
        page_name = f"{page_name}.md"
    
    try:
        # Try to read existing content first
        try:
            existing_content = await read_obsidian_note(page_name)
            # Append new content with spacing
            updated_content = f"{existing_content}\n\n---\n\n{content}"
        except:
            # File doesn't exist, create it with just the new content
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            updated_content = f"# {page_name[:-3]}\n\nCreated: {today}\n\n{content}"
        
        return await write_obsidian_note(page_name, updated_content)
    except Exception as e:
        print(f"Error appending to {page_name}: {e}")
        return False


async def add_task_to_note(task_description: str, note_path: str = "WeeklyPlan.md", section: str = "## This Week's Priorities") -> bool:
    """
    Add a new task to an Obsidian note under a specific section.
    Creates the file if it doesn't exist.
    """
    try:
        local_file_path = os.path.join(settings.obsidian_local_path, note_path)
        
        # Read existing content or create new
        if os.path.exists(local_file_path):
            async with aiofiles.open(local_file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
        else:
            # Create new file with header
            content = f"# Weekly Plan\n\n{section}\n"
        
        # Find the section to add the task to
        lines = content.split('\n')
        insert_index = None
        
        for i, line in enumerate(lines):
            if line.strip() == section:
                # Find the next line after the section header
                insert_index = i + 1
                break
        
        if insert_index is None:
            # Section not found, append to end
            if not content.endswith('\n\n'):
                content += '\n\n'
            content += f"{section}\n- [ ] {task_description}\n"
        else:
            # Insert after section header
            lines.insert(insert_index, f"- [ ] {task_description}")
            content = '\n'.join(lines)
        
        # Write back to file
        return await write_obsidian_note(note_path, content)
    except Exception as e:
        print(f"Error adding task: {e}")
        return False


async def complete_task_in_note(task_number: int, note_path: str = "WeeklyPlan.md") -> bool:
    """
    Mark a task as complete by its number (1-indexed).
    """
    try:
        content = await read_obsidian_note(note_path)
        lines = content.split('\n')
        
        # Find incomplete tasks
        task_count = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("- [ ]"):
                task_count += 1
                if task_count == task_number:
                    # Mark as complete
                    lines[i] = line.replace("- [ ]", "- [x]", 1)
                    updated_content = '\n'.join(lines)
                    return await write_obsidian_note(note_path, updated_content)
        
        return False  # Task number not found
    except Exception as e:
        print(f"Error completing task: {e}")
        return False


async def remove_task_from_note(task_number: int, note_path: str = "WeeklyPlan.md") -> bool:
    """
    Remove a task by its number (1-indexed).
    """
    try:
        content = await read_obsidian_note(note_path)
        lines = content.split('\n')
        
        # Find incomplete tasks
        task_count = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("- [ ]"):
                task_count += 1
                if task_count == task_number:
                    # Remove the line
                    lines.pop(i)
                    updated_content = '\n'.join(lines)
                    return await write_obsidian_note(note_path, updated_content)
        
        return False  # Task number not found
    except Exception as e:
        print(f"Error removing task: {e}")
        return False
