# CampusKit — Campus Resource Management System

**Know what is available, who has it, and what comes back.**

A local Python command-line equipment lending program for Learn2Earn. The simplified version has **12 functions**, uses the standard library only, and meets the required inventory, borrowing, returns, search/filter, and reporting features.

JSON persistence is omitted for now. Each launch starts fresh; changes last only for the current session. The optional JSON bonus is not included in this version. Earlier versions remain in Git history.

## Run

Download or clone this repository, then open a terminal in its folder:

```bash
python campuskit.py
python campuskit.py --demo
python test_campuskit.py
```

Use `python3` or Windows `py` if needed. No package installation is required. Run the test file directly; it uses plain assertions and prints the result of each group of checks.

## Menu

| Option | Action |
| --- | --- |
| 1 | List resources |
| 2 | Add a resource |
| 3 | Borrow |
| 4 | Return |
| 5 | Search by name |
| 6 | Filter by category |
| 7 | Generate report |
| 8 | List registered fellows |
| 0 | Exit |

Menu numbers have changed from the earlier version. Invalid input displays an error and returns to the menu. Ctrl+C or end-of-input closes the program. No files are read or written by the application.

## The 12 functions

| Function | Purpose |
| --- | --- |
| `create_initial_state()` | Return fresh resources, fellows, and an empty loan list. |
| `add_resource()` | Validate fields, reject duplicate IDs, and add inventory. |
| `list_resources()` | Print all five resource fields. |
| `borrow_resource()` | Validate IDs, quantity, and stock; record each successful loan. |
| `return_resource()` | Check quantities owed, update oldest matching loans, and restore stock. |
| `search_resources()` | Search names, ignoring case. |
| `filter_by_category()` | Match a category, ignoring case. |
| `generate_report()` | Calculate totals, low stock, and all tied leaders. |
| `show_report()` | Print the calculated report. |
| `read_input()` | Read non-empty text or a positive integer. |
| `main()` | Run the menu and handle input errors. |
| `run_demo()` | Run the required scenario plus one invalid-input case on fresh data. |

There are no classes, nested functions, or lambdas in the application. The test script defines no additional functions. Search and reporting use ordinary loops.

## Starting data and rules

Resources begin as Laptop R001 (10), Keyboard R002 (5), and Headset R003 (3). All units are initially available. Fellows are F001 Ada, F002 John, and F003 Grace; borrowing records start empty.

- Each resource has ID, name, category, total, and available units.
- IDs are trimmed and made uppercase; duplicate resource IDs are rejected.
- Names/categories cannot be blank. Totals, borrowing, and returns require positive integers.
- Unknown IDs, insufficient stock, and returns beyond a fellow's outstanding balance are rejected before state changes.
- Successful borrowings create separate records; returns update returned quantities without deleting history.
- Name search matches part of a name, ignoring case. Category filtering matches the whole category, ignoring case.
- Borrowed units are `total - available`. Low stock is strictly fewer than 3 available, including zero.
- Most borrowed means currently outstanding units. Every tied leader is shown; zero outstanding units produce a no-loans message.

## Demonstration and evidence

`python campuskit.py --demo` runs the required steps in order:

1. F001 borrows 2 laptops: 8 available.
2. F002 borrows 3 keyboards: 2 available.
3. F001 returns 1 laptop: 9 available.
4. F003 requests 4 headsets: rejected, all state unchanged.
5. F002 tries returning 4 keyboards: rejected, all state unchanged.
6. Search for `LAPtop`: Laptop found.
7. Report: 18 total, 14 available, 4 borrowed; Keyboard low at 2 and most borrowed at 3.

It then rejects the text quantity `two` without changing state. The list above is the specification; [demo-output.txt](docs/demo-output.txt) contains actual captured output.

[Tests](test_campuskit.py) cover the required scenario, invalid IDs/quantities, duplicates, partial/full returns, repeated loans, report ties, empty reports, search, menu recovery, restarts, and the function limit. [test-output.txt](docs/test-output.txt) contains actual results. [final-verification.txt](docs/final-verification.txt) identifies the tested source files.

Regenerate evidence with:

```bash
python campuskit.py --demo > docs/demo-output.txt 2>&1
python test_campuskit.py > docs/test-output.txt 2>&1
```

## Submission

- **A1:** full contents of [campuskit.py](campuskit.py).
- **A2:** [demo-output.txt](docs/demo-output.txt) and [test-output.txt](docs/test-output.txt).
- **A3:** the short explanation in [design.md](docs/design.md).
- [Submission guide](docs/submission.md).

The required features are complete. The assessment form has not been submitted automatically. JSON persistence is deferred, so do not submit old persistence evidence for this version.

## Limitations

All data is lost on exit. The program tracks quantities rather than individual equipment serial numbers. Fellow IDs identify registered fellows but do not authenticate the operator. Separate instances do not share state. Optional extras from the earlier version, such as a separate fellow-loan view and stock consistency checker, are omitted to keep the code easier to explain.
