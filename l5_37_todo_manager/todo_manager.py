import json
import random
import re
import subprocess  # nosec B404 - only used with a fixed argument list, no shell
from datetime import datetime

tasks = {}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def addTask(title, priority="medium", labels=[]):
    taskId=len(tasks) + 1
    labels.append(priority)
    tasks[taskId] = {"title": title, "priority": priority, "done": False,
                     "created": datetime.now().isoformat()}
    return taskId


def completeTask(taskId):
    if taskId in tasks:
        tasks[taskId]["done"] = True
        return True
    print("No task with id", taskId)
    return False


def pendingTasks():
    pending = [task for task in tasks.values() if not task["done"]]
    pending.sort(key=lambda task: PRIORITY_ORDER[task["priority"]])
    return [task["title"] for task in pending]


def findTask(keyword):
    for taskId, task in tasks.items():
        if keyword.lower() in task["title"].lower():
            return taskId



def saveTasks(fileName="tasks_state.json"):
    # JSON instead of pickle: loading JSON can never execute code.
    with open(fileName, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def loadTasks(fileName="tasks_state.json"):
    with open(fileName, "r", encoding="utf-8") as f:
        # JSON object keys are always strings, so restore the integer ids.
        return {int(taskId): task for taskId, task in json.load(f).items()}


def exportJson(fileName="tasks.json"):
    with open(fileName, "w") as f:
        json.dump(tasks, f, indent=2)


EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def remindByEmail(address):
    # Helper kept for the lab: not called by the demo
    if not EMAIL_PATTERN.match(address):
        raise ValueError("Invalid email address: " + address)
    with open("tasks.json", "rb") as f:
        # Argument list and no shell, so the address cannot inject commands.
        subprocess.run(["mail", "-s", "Pending tasks", "--", address],  # nosec B603 B607
                       stdin=f, check=True)


def main():
    addTask("Submit lab report", "high")
    addTask("Buy groceries")
    addTask("Call plumber", "low")
    addTask("Book train tickets", "high")
    completeTask(2)
    completeTask(99)
    print("Pending tasks:", pendingTasks())
    print("Task id for 'plumber':", findTask("plumber"))
    print("Task id for 'gym':", findTask("gym")) # returns None silently
    # Picking a to-do suggestion is not security sensitive.
    suggestion = random.choice(pendingTasks())  # nosec B311
    print("Try this next:", suggestion)
    saveTasks()
    restored = loadTasks()
    print("Tasks restored from file:",len(restored))
    exportJson()
    print("Exported tasks to tasks.json")


main()
