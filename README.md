# CampusKit — Campus Resource Management System

**Know what is available, who has it, and what comes back.**

CampusKit is a command-line Campus Resource Management System for Learn2Earn. It tracks equipment inventory, issues resources to fellows, accepts returns, searches stock, and produces reports checked against outstanding loans.

Built with Python and its standard library only. Runs locally without frameworks, databases, external services, third-party packages, or hosting.

## Project status

**All 10 stages complete. Source code, actual run evidence, design explanation, and submission guide are ready.**

The required inventory, borrowing, returns, search/filter, and reports are implemented, along with JSON persistence, receipts, consistency checks, and fellow loan views. All **55 tests passed** in a clean directory containing only the application and test files. The required demonstration also passed, including an extra invalid-input test.

Start with [the submission guide](docs/submission.md) for A1/A2/A3. The project is prepared; the assessment form has not been submitted automatically.

Repository: [el-ahavah/campuskit](https://github.com/el-ahavah/campuskit)

## Project goals

- Meet every required function and reproduce the seven demonstration steps in order.
- Keep inventory and outstanding loans consistent after every successful operation.
- Reject invalid requests without changing inventory, loans, or transaction history.
- Keep the code readable enough to explain and maintain as a solo learning project.
- Make the terminal experience distinctive through clear tables, useful errors, and simple transaction receipts.

## Required features

| Area | Implemented behaviour | Requirement marks |
| --- | --- | --- |
| Inventory | Add and list resources with unique ID, name, category, total units, and available units; reject duplicate IDs. | 10 |
| Borrowing | Validate fellow ID, resource ID, and positive integer quantity; check stock; record every successful borrowing and reduce availability. | 15 |
| Returns | Accept only quantities the fellow currently owes for that resource; update the borrowing records and stock. | 10 |
| Search and filter | Search resource names without case sensitivity; filter by category. | 10 |
| Reports | Show overall total, available, and borrowed units; list resources with fewer than 3 available; identify all resources tied for most units currently borrowed. | 15 |
| Structure and robustness | Use meaningful functions, a repeating menu, input validation, and helpful errors. | 10 |

The supplied brief lists these requirements as 70 marks and separately lists A1/A2/A3 as 50/15/5 marks. This README preserves those figures without assuming how they combine into the final grade. Optional JSON persistence carries up to 5 bonus marks according to the brief.

## What makes CampusKit distinctive

These small enhancements support the assignment without changing its scope:

- **Fellow loan view:** see each fellow's outstanding resources and quantities.
- **Readable receipts:** confirm the fellow, resource, quantity, and remaining stock after a successful transaction.
- **Stock health labels:** show AVAILABLE, LOW STOCK, or OUT OF STOCK without relying on terminal colours.
- **Consistency check:** verify that available units plus outstanding borrowed units equal total units for every resource.
- **Repeatable demonstration:** run the required scenario on fresh starting data, separate from any saved working inventory.

Core requirements come first. Enhancements must not delay correctness or make the code difficult to explain.

## Starting data

```python
resources = [
    {"id": "R001", "name": "Laptop", "category": "Electronics", "total": 10, "available": 10},
    {"id": "R002", "name": "Keyboard", "category": "Accessories", "total": 5, "available": 5},
    {"id": "R003", "name": "Headset", "category": "Accessories", "total": 3, "available": 3}
]

fellows = {"F001": "Ada", "F002": "John", "F003": "Grace"}
borrow_records = []
```

When no save file exists, the application starts with these values. Otherwise it reloads the validated saved state. Use `--no-save` for a fresh temporary session. Demonstration mode will always use a fresh copy.

## Data design

**Inventory:** a list of resource dictionaries using the exact fields in the starting data. Newly added resources start with `available` equal to `total`. Resource IDs are unique after trimming whitespace and converting to uppercase.

**Fellows:** a dictionary mapping valid fellow IDs to names. Fellow registration is outside the required scope; borrowing and returns use the supplied fellows.

**Borrowing records:** a list containing one dictionary for each successful borrowing. Each record contains `loan_id`, `fellow_id`, `resource_id`, `quantity_borrowed`, and `quantity_returned`. The outstanding quantity is `quantity_borrowed - quantity_returned`. Fully returned records remain in the list so the original borrowing is not lost.

If a fellow borrows the same resource more than once, returns reduce the oldest outstanding borrowing first. Before updating anything, the program confirms that the full requested return is valid across that fellow's records for that resource.

**Report calculations:** sum resource totals and availability; calculate outstanding borrowed units from the records and verify that they agree with `total - available`. Most borrowed means the largest number of units still on loan, not the largest historical borrowing count. Include every tied leader. If no units are borrowed, report that explicitly.

## Validation rules

- Require non-empty resource IDs, names, and categories.
- Reject duplicate resource IDs, including IDs that differ only in case or surrounding spaces.
- Require positive whole numbers for new resource totals, borrowing, and returns. Reject text, decimals, zero, and negative quantities.
- Validate both fellow and resource IDs before processing a loan or return.
- Do not lend more units than are available.
- Do not accept more returned units than the fellow currently owes for that resource.
- Complete validation before changing any state; rejected actions add no borrowing record.
- Keep `0 <= available <= total` and `0 <= quantity_returned <= quantity_borrowed`.
- Treat name searches as case-insensitive substring matches; use case-insensitive exact category matching.
- List zero-stock resources in the fewer-than-3 report, alongside other low-stock resources.
- Explain empty search results, invalid menu choices, and an empty inventory clearly.

## Implemented functions

| Function | Responsibility |
| --- | --- |
| `create_initial_state()` | Return fresh starting inventory, fellows, and borrowing records. |
| `find_resource()` | Locate a resource by its normalized ID. |
| `add_resource()` | Validate and add a new resource without duplicate IDs. |
| `list_resources()` | Display inventory in a readable terminal table. |
| `borrow_resource()` | Validate a request, record a successful borrowing, and reduce stock. |
| `return_resource()` | Validate the fellow's outstanding quantity, update records, and restore stock. |
| `search_resources()` | Find names regardless of letter case. |
| `filter_by_category()` | Select resources in a matching category. |
| `generate_report()` | Calculate stock totals, low-stock items, and all most-borrowed leaders. |
| `check_consistency()` | Check stock/loan bounds, references, IDs, and inventory/loan agreement. |
| `get_fellow_loans()` | Group outstanding units by resource for one valid fellow. |
| `stock_status()` | Label resources AVAILABLE, LOW STOCK, or OUT OF STOCK. |
| `run_demo()` | Execute the required scenario on fresh data and print actual results. |
| `main()` | Run the menu until the user exits. |

Business functions receive state explicitly instead of depending on changing global variables. Input prompts and display formatting are kept separate from validation and calculations where practical.

## Running the current version

From the project folder, start the program:

```bash
python campuskit.py
```

Choose `1` for the session overview, `2` for registered fellows, `3` to list resources, `4` to add a resource, `5` to borrow a resource, `6` to return a resource, `7` to search names, `8` to filter by category, `9` for the stock report, `10` for a fellow’s outstanding loans, or `0` to exit. Blank or invalid menu choices show an explanation and prompt again. Ctrl+C or end-of-input closes the application cleanly. Normal launches reload `data/campuskit.json` beside the program and save each successful change. Use `--no-save` for fresh in-memory sessions.

Run all checks:

```bash
python -m unittest -v
```

Final verification: **55 tests passed**, covering the foundation plus valid additions, normalized IDs, duplicate rejection, blank/non-text fields, invalid totals, inventory display, empty inventory, interrupted additions, and the full add/list menu flow. Borrowing checks also cover the first two required borrowing steps, unknown IDs, invalid quantities, insufficient stock, exact-stock borrowing, repeated loans, newly added resources, interrupted entry, and CLI receipts. Return tests cover partial/full returns, oldest-loan allocation across repeated borrowings, loan history retention, other fellows/resources remaining unchanged, duplicate returns, excessive returns, invalid inputs, interrupted entry, and CLI receipts. Search/filter checks cover case and outer-space handling, partial names, exact categories, multiple matches, new resources, zero stock, empty inventory, no matches, invalid queries, and current availability after loans and returns. Report tests cover the full required scenario, ties, current versus historical borrowing, zero stock, the low-stock threshold, empty/no-loan reports, fellow-specific balances, and deliberate inconsistencies. Demo tests cover the non-interactive command, ordered steps, repeatability, isolation from existing state, help/invalid arguments, and detection of a rejection that wrongly mutates state. Rejection and read-only-operation tests compare state before and after the attempt.

Try adding resource `r004`, name `Projector`, category `Electronics`, and total `4` through option `4`. Its stored ID becomes `R004`, with total and available units both set to 4. Option `3` lists all five inventory fields. Adding `R004` again is rejected. These are instructions to try locally, not the required seven-step demonstration output.

To borrow, choose `5`, enter a fellow ID such as `F001`, a resource ID such as `R001`, and a positive whole-number quantity. IDs ignore case and outer spaces. Invalid quantity input prompts again; an unknown ID or insufficient stock rejects the request and returns to the menu. Successful receipts show the loan ID, fellow, resource, quantity, and remaining stock. Every successful request creates a separate record (`L001`, `L002`, and so on); rejected requests create none.

To return, choose `6`, enter the fellow ID, resource ID, and quantity to return. The program checks the total still owed by that fellow for that resource before changing anything. A return can span multiple borrowing records, settling the oldest first. The receipt shows units returned, units still owed, and stock now available. Returning too many units, returning an item the fellow never borrowed, or returning an already settled loan is rejected without changing state.

To search names, choose `7` and enter a name or part of one, such as `LAPtop` or `lap`. To filter by category, choose `8` and enter the full category, such as `ACCESSORIES`. Both ignore case and outer spaces. Blank input prompts again; no matches produce a helpful message. Matching rows include ID, name, category, total units, and current available units, including resources with zero stock.

Choose `9` for the stock report: total units, available units, units currently borrowed, per-resource stock labels, resources with fewer than 3 available (including zero), and all tied leaders by outstanding units. Labels are AVAILABLE (3 or more), LOW STOCK (1–2), and OUT OF STOCK (0). If nothing is borrowed, the report says so instead of naming zero-unit leaders.

Choose `10` and enter a fellow ID for their outstanding resource quantities. Repeated loans are combined; fully returned loans are omitted from this view but retained in history. Unknown IDs are rejected, and fellows with no outstanding loans receive a clear message.

Before either balance view, `check_consistency()` checks stock bounds, loan quantity bounds, duplicate resource/loan IDs, known fellow/resource references, and available units plus outstanding units equalling total units for every resource. If a check fails, the view reports the problem without altering data or showing a misleading balance. Loaded JSON also undergoes schema, ID, version, quantity, and reference validation before it becomes session state.

Run `python campuskit.py --demo` for the standalone verified demonstration. It starts with fresh data, requires no input, and does not alter an interactive session. Verification failures raise an error and cause a nonzero exit; they never print an overall PASS. The session overview still counts resource types, fellows, and retained borrowing records, including settled records; it is separate from the stock report.

## Files and commands

| File | Purpose |
| --- | --- |
| `README.md` | Project overview, rules, build stages, and usage. |
| `campuskit.py` | Application functions, menu, and demonstration mode in one submission-friendly file. |
| `test_campuskit.py` | Core operations, report, consistency, and fellow-loan tests using the standard-library `unittest` module. |
| `docs/demo-output.txt` | Actual output captured from `python3 campuskit.py --demo`. |
| `docs/test-output.txt` | Actual verbose output captured from `python3 -m unittest -v`; 55 tests passed. |
| `docs/persistence-output.txt` | Actual output from three processes proving loans and returns survive restarts. |
| `docs/design.md` | Final explanation of implemented functions, data representation, and limitations. |
| `docs/submission.md` | A1/A2/A3 preparation instructions and a concise design explanation. |
| `docs/final-verification.txt` | Clean-directory verification, Python version, and tested source hashes. |
| `.gitignore` | Exclude Python cache files and local saved data. |
| `data/campuskit.json` | Default local saved state, created on the first successful change; not committed. |

Available commands:

```bash
python campuskit.py
python campuskit.py --demo
python -m unittest -v
```

Use `python3` if that is your system's Python 3 command, or `py` on Windows where appropriate. No `pip install` step is needed.

## Build stages and GitHub checkpoints

The project was built one stage at a time, with verification and a GitHub commit for each stage.

| Stage | Deliverable | Completion check | Suggested commit |
| --- | --- | --- | --- |
| 1. Project definition — complete | README, working name, requirements, and roadmap. | Every required feature and submission item is mapped. | `docs: define CampusKit project and build roadmap` |
| 2. Application foundation — complete | Starting data, entry point, menu loop, input helpers, and `.gitignore`. | Menu repeats, invalid selections are handled, and exit works. | `feat: add CLI foundation and starting data` |
| 3. Resource inventory — complete | Add/list resources and validate resource fields. | Valid additions work; duplicate IDs and invalid totals leave inventory unchanged. | `feat: implement resource inventory management` |
| 4. Borrowing — complete | Fellow/resource validation, stock checks, records, and receipts. | Valid loans reduce stock; invalid IDs, quantities, and insufficient stock leave all state unchanged. | `feat: implement validated resource borrowing` |
| 5. Returns — complete | Outstanding loan calculation and partial/full returns. | Repeated borrowings and returns remain correct; excessive or invalid returns change nothing. | `feat: implement validated resource returns` |
| 6. Search and category filter — complete | Case-insensitive name search and category filtering. | `LAPtop` finds Laptop; category matching and no-match messages work. | `feat: add inventory search and category filters` |
| 7. Reports and loan visibility — complete | Required reports, all tied leaders, fellow loan view, stock labels, and consistency checks. | Totals agree with loans; ties, zero stock, and no outstanding loans are handled correctly. | `feat: add stock reports and fellow loan views` |
| 8. Demonstration and test evidence — complete | Fresh-state demo, full regression tests, and captured output. | Steps 1–7 pass in order; include an additional invalid-input test and actual output. | `test: verify requirements and capture demonstration evidence` |
| 9. Optional JSON persistence — complete | Save/reload inventory and borrowing records using `json`. | Restart preserves state; malformed or inconsistent files are rejected without silently overwriting them; demo remains isolated. | `feat: add optional JSON save and reload` |
| 10. Final review and submission preparation — complete | Update README, complete design explanation, rerun checks, and prepare A1/A2/A3. | A clean source copy runs locally, evidence matches final code, and submission files are prepared. | `docs: finalize usage and project submission` |

Tests were added alongside each feature. Stage 8 captured demonstration evidence, Stage 9 added the optional persistence bonus, and Stage 10 verified a clean copy and prepared the final submission documents.

## Required demonstration specification

**The table below contains expected acceptance criteria, not actual run output.** The real captured transcript is [docs/demo-output.txt](docs/demo-output.txt). Refresh evidence after later code changes.

Run the following steps in order from the starting data:

| Step | Action | Required result |
| --- | --- | --- |
| 1 | F001 borrows 2 units of R001 (Laptop). | Laptop available: 8. |
| 2 | F002 borrows 3 units of R002 (Keyboard). | Keyboard available: 2. |
| 3 | F001 returns 1 unit of R001. | Laptop available: 9; F001 still owes 1 laptop. |
| 4 | F003 requests 4 units of R003 (Headset). | Rejected; Headset available remains 3; all state unchanged. |
| 5 | F002 tries to return 4 units of R002. | Rejected; Keyboard available remains 2; F002 still owes 3 keyboards; all state unchanged. |
| 6 | Search for `LAPtop`. | Laptop found despite different capitalization. |
| 7 | Generate the report. | Overall total: 18; available: 14; borrowed: 4; Keyboard low stock at 2; Keyboard most borrowed at 3. |

After Step 7, run an additional invalid-input test: F001 attempts to borrow `two` laptops. The program must explain that the quantity must be a positive integer and leave all state unchanged.

Automated coverage includes zero, negative and decimal quantities; unknown IDs; duplicate resource IDs; borrowing exactly the available quantity; returns across multiple loans; fully returned loans; case-insensitive filtering; report ties; and empty/no-loan reports. Rejection tests compare the full state before and after the action.

## JSON saving and reloading

Normal startup uses `data/campuskit.json` beside `campuskit.py`, regardless of the current working directory. Successful additions, borrowing, and returns are saved immediately. Read-only actions and rejected requests do not rewrite the file. There is no need to save separately on exit.

```bash
python campuskit.py
python campuskit.py --data my-campus.json
python campuskit.py --no-save
python campuskit.py --demo
```

`--data` selects another save file; `--no-save` creates a temporary session without reading or writing saved data. These two options are mutually exclusive. Demo mode always uses isolated fresh state, even when `--data` points to an existing or broken save.

The JSON document contains `version: 1`, `resources`, `fellows`, and `borrow_records`. Loading checks required fields, supported version, uppercase trimmed IDs, positive totals, stock and loan bounds, valid references, unique IDs, sequential retained loan IDs, and agreement between inventory and outstanding loans. A missing file starts fresh; malformed, unreadable, or inconsistent files stop startup with an error and remain untouched. Repair or restore the file, or use `--no-save`; the program does not silently reset a damaged save.

Saving validates state, writes a temporary file in the destination directory, flushes it, and replaces the previous save atomically. If saving fails, the latest in-memory change is rolled back and the menu clearly reports that it was NOT saved, even if a transaction receipt was already printed. The previous save remains intact when replacement fails. Keep only one running instance per save file.

The default save file is ignored by Git. Custom `--data` files should be kept outside the repository or added to your own ignore rules. The demo and tests use isolated state and temporary paths, so they do not modify your working save.

## Actual demonstration and test evidence

Demonstration and test evidence were refreshed during Stage 10 from a clean source copy; the restart transcript was captured in Stage 9 using the same unchanged application source:

- [Demonstration output](docs/demo-output.txt): all seven required steps followed by the additional invalid-input test.
- [Verbose test output](docs/test-output.txt): 55 tests passed, including menu subprocess tests and persistence failure/restart cases.
- [Persistence output](docs/persistence-output.txt): actual output from separate processes sharing a temporary save file.

For **A2**, paste the actual demonstration transcript and include the test evidence as requested. The extra demo case calls `borrow_resource()` with the text quantity `two`, demonstrating rejection by the business function. Separate CLI tests exercise text/decimal/zero/negative input and confirm that the interactive prompts recover correctly.

To regenerate the files from the project directory (the `docs` directory is already included):

```bash
python campuskit.py --demo > docs/demo-output.txt 2>&1
python -m unittest -v > docs/test-output.txt 2>&1
```

Use `python3` instead if needed. Check both commands exit successfully and review the files before submitting. These files are captured runtime output, not hand-written expected results. Test execution time can vary. JSON persistence, final verification, and the design explanation are complete. See [final-verification.txt](docs/final-verification.txt) for the tested file hashes and execution environment.

## Submission preparation

- [x] **A1 — Source code:** complete application in [campuskit.py](campuskit.py).
- [x] **A2 — Evidence:** actual [demonstration output](docs/demo-output.txt) and [test output](docs/test-output.txt).
- [x] **A3 — Design:** functions, data representation, and limitations in [design.md](docs/design.md).
- [x] **Optional bonus:** implemented JSON persistence with [restart evidence](docs/persistence-output.txt).
- [x] **Final verification:** clean-copy execution and source hashes in [final-verification.txt](docs/final-verification.txt).
- [ ] **Fellow's final action:** review the files, paste them into the assessment fields, verify link access, and submit. See [submission.md](docs/submission.md).

## Design limitations

The application is for one local operator at a time. Fellow ID checks confirm that an ID exists; they do not authenticate the person using it. Resources are tracked by quantity, so individual laptop serial numbers, damage, due dates, and fines are outside scope. Temporary sessions started with `--no-save` lose changes on exit. JSON saving supports one operator/process at a time; simultaneous writers are not supported. It is not a database or a backup system.

## Learning workflow

This is a solo fellow project. Each stage should be understood well enough to explain the functions, trace a transaction, and justify the validation rules. Keep commits focused on real progress and follow the programme's rules for acknowledging assistance.
