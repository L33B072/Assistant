from dataclasses import dataclass
from typing import List

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
    """relative_path like 'Tasks/WeeklyPlan.md' under your Obsidian root"""
    client = MSGraphClient()
    full_path = settings.obsidian_root_path.strip("/") + "/" + relative_path.strip("/")
    md = await client.get_obsidian_file_text(full_path)
    return parse_markdown_tasks(md)
