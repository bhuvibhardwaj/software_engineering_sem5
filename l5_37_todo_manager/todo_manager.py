"""A small command-line to-do list and task manager.

Tasks have a priority and labels, can be completed, searched by keyword and
listed in priority order. They can be saved to JSON and exported.
"""
import json
import random
import re
# subprocess is only used with a fixed argument list and no shell.
import subprocess  # nosec B404
from datetime import datetime

tasks = {}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def add_task(title, priority="medium", labels=None):
    """Add a task and return its id.

    ``labels`` defaults to None rather than a list, because a mutable default
    would be shared (and grow) across every call. The priority is always
    added to the task's own labels.
    """
    task_id = len(tasks) + 1
    task_labels = list(labels) if labels is not None else []
    task_labels.append(priority)
    tasks[task_id] = {"title": title, "priority": priority, "done": False,
                      "labels": task_labels,
                      "created": datetime.now().isoformat()}
    return task_id


def complete_task(task_id):
    """Mark a task as done. Return False if the id does not exist."""
    if task_id in tasks:
        tasks[task_id]["done"] = True
        return True
    print("No task with id", task_id)
    return False


def pending_tasks():
    """Return the titles of unfinished tasks, highest priority first."""
    pending = [task for task in tasks.values() if not task["done"]]
    pending.sort(key=lambda task: PRIORITY_ORDER[task["priority"]])
    return [task["title"] for task in pending]


def find_task(keyword):
    """Return the id of the first task whose title contains keyword.

    The search ignores case. Returns None when nothing matches.
    """
    for task_id, task in tasks.items():
        if keyword.lower() in task["title"].lower():
            return task_id
    return None


def save_tasks(file_name="tasks_state.json"):
    """Save all tasks to a JSON file."""
    # JSON instead of pickle: loading JSON can never execute code.
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)


def load_tasks(file_name="tasks_state.json"):
    """Load tasks from a JSON file written by save_tasks."""
    with open(file_name, "r", encoding="utf-8") as file:
        # JSON object keys are always strings, so restore the integer ids.
        data = json.load(file)
    return {int(task_id): task for task_id, task in data.items()}


def export_json(file_name="tasks.json"):
    """Export all tasks to a human-readable JSON file."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)


def remind_by_email(address):
    """Email the exported tasks file to address using the system mail command.

    Helper kept for the lab: not called by the demo.
    """
    if not EMAIL_PATTERN.match(address):
        raise ValueError("Invalid email address: " + address)
    with open("tasks.json", "rb") as file:
        # Argument list and no shell, so the address cannot inject commands.
        subprocess.run(  # nosec B603 B607
            ["mail", "-s", "Pending tasks", "--", address],
            stdin=file, check=True)


def main():
    """Run a short demonstration of the task manager."""
    add_task("Submit lab report", "high")
    add_task("Buy groceries")
    add_task("Call plumber", "low")
    add_task("Book train tickets", "high")
    complete_task(2)
    complete_task(99)
    print("Pending tasks:", pending_tasks())
    print("Task id for 'plumber':", find_task("plumber"))
    print("Task id for 'gym':", find_task("gym"))  # returns None silently
    pending = pending_tasks()
    if pending:
        # Picking a to-do suggestion is not security sensitive.
        print("Try this next:", random.choice(pending))  # nosec B311
    else:
        print("Nothing left to do!")
    save_tasks()
    restored = load_tasks()
    print("Tasks restored from file:", len(restored))
    export_json()
    print("Exported tasks to tasks.json")


if __name__ == "__main__":
    main()
