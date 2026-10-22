# Reflection

> The handout PDF refers to reflection questions but does not print them, so
> these are the four standard ones for this lab.

## 1. Which issues were the easiest and which the hardest to fix?

The Flake8 findings were the easiest: four one-character formatting changes
that took seconds. The Pylint naming and docstring messages were also easy but
tedious, because renaming nine functions touches every call site. The hardest
were the Bandit findings. Replacing `os.system` needed a real design choice
(an argument list with no shell, plus input validation), and replacing pickle
meant changing the file format and restoring integer ids that JSON turns into
strings.

## 2. Did the tools report false positives? How did you decide?

Yes. Bandit flagged `random.choice` (B311), but the call only picks a to-do
suggestion, so no security decision depends on it. After the `os.system` fix,
Bandit also flagged the safe `subprocess` call (B404, B603, B607) because it
cannot tell that the arguments are a fixed list. I decided by asking whether an
attacker controls the input and whether the output has a security
consequence. For those four I suppressed the warning with a specific
`# nosec` code and a comment explaining why, rather than a blanket ignore, so
a reviewer can check the reasoning.

## 3. How would you integrate static analysis into a real workflow?

Run Flake8 (and a formatter) in a pre-commit hook so style problems never
reach a commit, and run Pylint and Bandit in CI on every pull request with the
build failing on Bandit medium and high findings and on a Pylint score drop.
Pin tool versions and keep a small config file for agreed exceptions, so the
suppressions are reviewed once instead of argued about repeatedly.

## 4. What tangible improvements did you see in the code?

- Security: the command-injection hole and the code-execution-on-load hole are
  gone.
- Correctness: the shared mutable default is fixed, labels are now actually
  stored per task, and an empty task list no longer crashes the suggestion.
- Maintainability: every function is documented, names follow PEP 8, and the
  module can be imported without running the demo.
- Numbers: Pylint rose from 5.09 to 10.00, Bandit went from 4 findings
  (including 1 High) to none, and Flake8 went from 4 findings to none, while
  the program's printed output stayed the same.

The tools did not catch everything. The empty-list crash and the run-on-import
problem were found by reading the code, so static analysis supports a code
review rather than replacing one.
