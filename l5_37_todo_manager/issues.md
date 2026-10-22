# Issues found by static analysis

Line numbers refer to the **original** `todo_manager.py` (commit `7c281ce`).
Reports: `reports/*_before.txt` (original) and `reports/*_after.txt` (final).

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| OS command injection via `os.system` (Bandit B605, **High**) | Security | 57 | `remindByEmail` builds a shell command by concatenating `address`, so an address such as `a@b.c; rm -rf ~` runs arbitrary commands. | Validate the address with a regex, then call `subprocess.run` with an argument list (no shell) and feed `tasks.json` through `stdin`. `--` stops the address being read as an option. |
| Unsafe deserialisation with `pickle.load` (Bandit B301 **Medium**, B403 Low) | Security | 3, 47 | Loading a pickle file can execute arbitrary code, so a tampered `tasks.pkl` would take over the program. | Replaced pickle with JSON in `save_tasks`/`load_tasks`; JSON can only produce plain data. Integer task ids are restored on load because JSON keys are strings. |
| `random` used where Bandit expects crypto (Bandit B311, Low) | Security (false positive) | 70 | Flags `random.choice`. Here it only picks a to-do suggestion, so there is no security impact. | Reviewed and suppressed with `# nosec B311` plus a comment saying why. Also guarded the empty-list case (see next row). |
| `random.choice` on an empty list | Bug | 70 | If every task were complete, `pendingTasks()` returns `[]` and `random.choice` raises `IndexError`. The tools do not report this; found by reading the code. | Only suggest a task when there are pending tasks, otherwise print "Nothing left to do!". |
| Mutable default argument `labels=[]` (Pylint W0102) | Bug | 11-13 | One list is shared by every call, so each call appends to the same list. The labels were also never stored, so the parameter did nothing useful. | Default to `None`, copy into a fresh list per call, append the priority and store it in the task as `labels`. |
| Inconsistent return in `findTask` (Pylint R1710) | Bug / Style | 33-37 | The function returns an id on a match but falls off the end (implicit `None`) otherwise. | Added an explicit `return None` and documented it. |
| Demo runs on import | Design | 79 | `main()` is called at module level, so importing the file for reuse or tests runs the demo and writes files. Not reported by any tool. | Wrapped the call in `if __name__ == "__main__":`. |
| Missing docstrings (Pylint C0114, C0116) | Style | 1, 11, 19, 27, 33, 40, 45, 50, 55, 60 | Module and all 9 functions had no docstring. | Added a module docstring and a docstring to every function. |
| camelCase names (Pylint C0103) | Style | 11-60 | Functions, arguments and variables (`addTask`, `taskId`, `fileName`...) break PEP 8 snake_case. | Renamed to `add_task`, `complete_task`, `pending_tasks`, `find_task`, `save_tasks`, `load_tasks`, `export_json`, `remind_by_email`, `task_id`, `file_name`. |
| `open()` without an encoding (Pylint W1514) | Quality | 51 | `exportJson` used the platform default encoding, so output can differ between machines. | Added `encoding="utf-8"` to every `open` call. |
| Missing whitespace around `=` (Flake8 E225) | Style | 12 | `taskId=len(tasks) + 1` | Added spaces around the operator. |
| Too many blank lines (Flake8 E303) | Style | 40 | Three blank lines before `saveTasks`. | Reduced to two. |
| Inline comment spacing (Flake8 E261) | Style | 69 | Only one space before `# returns None silently`. | Used two spaces. |
| Missing space after comma (Flake8 E231) | Style | 74 | `"...from file:",len(restored)` | Added the space. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.09 / 10 (27 messages) | 10.00 / 10 |
| Bandit | 1 High, 1 Medium, 2 Low | No issues (4 reviewed `# nosec` suppressions: B404, B603, B607, B311) |
| Flake8 | 4 findings | 0 findings |
