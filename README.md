# CampusKit — Campus Resource Management System

**Know what is available, who has it, and what comes back.**

CampusKit is a planned command-line Campus Resource Management System for Learn2Earn. It will help track equipment inventory, issue resources to fellows, accept returns, search stock, and produce accurate reports.

Built with Python and its standard library only. Runs locally without frameworks, databases, external services, third-party packages, or hosting.

## Project status

**Stages 1–4 complete: project plan, CLI foundation, inventory, and borrowing.**

The application starts with the required data, runs a repeating menu, displays the session overview and fellows, and supports adding and listing resources. Additions validate all fields before changing inventory, reject duplicate IDs regardless of case or outer spaces, and set available units equal to total units. Borrowing validates fellow/resource IDs, positive integer quantities, and available stock before recording a loan and reducing availability. Each successful borrowing prints a receipt. All 21 foundation, inventory, and borrowing tests have passed, including actual CLI subprocess runs. The complete required seven-step demonstration has not been implemented or run yet; its first two borrowing steps and insufficient-stock case are covered by tests. Each completed and verified stage has its own GitHub commit.

Repository: [el-ahavah/campuskit](https://github.com/el-ahavah/campuskit)

## Project goals

- Meet every required function and reproduce the seven demonstration steps in order.
- Keep inventory and outstanding loans consistent after every successful operation.
- Reject invalid requests without changing inventory, loans, or transaction history.
- Keep the code readable enough to explain and maintain as a solo learning project.
- Make the terminal experience distinctive through clear tables, useful errors, and simple transaction receipts.

## Required features

| Area | Planned behaviour | Requirement marks |
| --- | --- | --- |
| Inventory | Add and list resources with unique ID, name, category, total units, and available units; reject duplicate IDs. | 10 |
| Borrowing | Validate fellow ID, resource ID, and positive integer quantity; check stock; record every successful borrowing and reduce availability. | 15 |
| Returns | Accept only quantities the fellow currently owes for that resource; update the borrowing records and stock. | 10 |
| Search and filter | Search resource names without case sensitivity; filter by category. | 10 |
| Reports | Show overall total, available, and borrowed units; list resources with fewer than 3 available; identify all resources tied for most units currently borrowed. | 15 |
| Structure and robustness | Use meaningful functions, a repeating menu, input validation, and helpful errors. | 10 |

The supplied brief lists these requirements as 70 marks and separately lists A1/A2/A3 as 50/15/5 marks. This README preserves those figures without assuming how they combine into the final grade. Optional JSON persistence carries up to 5 bonus marks according to the brief.

## What makes CampusKit distinctive

These small enhancements will support the assignment without changing its scope:

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

Every new session starts with these values until optional persistence is implemented. Demonstration mode will always use a fresh copy.

## Planned data design

**Inventory:** a list of resource dictionaries using the exact fields in the starting data. Newly added resources start with `available` equal to `total`. Resource IDs are unique after trimming whitespace and converting to uppercase.

**Fellows:** a dictionary mapping valid fellow IDs to names. Fellow registration is outside the required scope; borrowing and returns use the supplied fellows.

**Borrowing records:** a list containing one dictionary for each successful borrowing. Each record will contain `loan_id`, `fellow_id`, `resource_id`, `quantity_borrowed`, and `quantity_returned`. The outstanding quantity is `quantity_borrowed - quantity_returned`. Fully returned records remain in the list so the original borrowing is not lost.

If a fellow borrows the same resource more than once, returns will reduce the oldest outstanding borrowing first. Before updating anything, the program will confirm that the full requested return is valid across that fellow's records for that resource.

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

## Planned functions

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
| `check_consistency()` | Check that inventory and outstanding loans agree. |
| `run_demo()` | Execute the required scenario on fresh data and print actual results. |
| `main()` | Run the menu until the user exits. |

Business functions will receive state explicitly instead of depending on changing global variables. Input prompts and display formatting will be kept separate from validation and calculations where practical.

## Running the current version

From the project folder, start the program:

```bash
python campuskit.py
```

Choose `1` for the session overview, `2` for registered fellows, `3` to list resources, `4` to add a resource, `5` to borrow a resource, or `0` to exit. Blank or invalid menu choices show an explanation and prompt again. Ctrl+C or end-of-input closes the application cleanly. Each launch creates fresh data; saving is not implemented yet.

Run the foundation, inventory, and borrowing checks:

```bash
python -m unittest -v
```

Stage 4 verification: **21 tests passed**, covering the foundation plus valid additions, normalized IDs, duplicate rejection, blank/non-text fields, invalid totals, inventory display, empty inventory, interrupted additions, and the full add/list menu flow. Borrowing checks also cover the first two required borrowing steps, unknown IDs, invalid quantities, insufficient stock, exact-stock borrowing, repeated loans, newly added resources, interrupted entry, and CLI receipts. Rejection tests compare all inventory, fellow, and loan state before and after the attempt.

Try adding resource `r004`, name `Projector`, category `Electronics`, and total `4` through option `4`. Its stored ID becomes `R004`, with total and available units both set to 4. Option `3` lists all five inventory fields. Adding `R004` again is rejected. These are instructions to try locally, not the required seven-step demonstration output.

To borrow, choose `5`, enter a fellow ID such as `F001`, a resource ID such as `R001`, and a positive whole-number quantity. IDs ignore case and outer spaces. Invalid quantity input prompts again; an unknown ID or insufficient stock rejects the request and returns to the menu. Successful receipts show the loan ID, fellow, resource, quantity, and remaining stock. Every successful request creates a separate record (`L001`, `L002`, and so on); rejected requests create none.

Returns, searching, full reports, and `--demo` remain planned. The session overview only counts resource types, fellows, and borrowing records; it is not the final stock report.

## Files and planned commands

| File | Purpose |
| --- | --- |
| `README.md` | Project overview, rules, build stages, and usage. |
| `campuskit.py` | Application functions, menu, and demonstration mode in one submission-friendly file. |
| `test_campuskit.py` | Foundation, inventory, and borrowing tests using the standard-library `unittest` module. |
| `docs/demo-output.txt` | Actual captured demonstration output, created after execution. |
| `docs/test-output.txt` | Actual captured test output, created after execution. |
| `docs/design.md` | Final explanation of implemented functions, data representation, and limitations. |
| `.gitignore` | Exclude Python cache files and local saved data. |
| `data/campuskit.json` | Optional local saved state; not committed. |

Planned commands, available after their implementation stages:

```bash
python campuskit.py
python campuskit.py --demo
python -m unittest -v
```

Use `python3` if that is your system's Python 3 command, or `py` on Windows where appropriate. No `pip install` step is needed.

## Build stages and GitHub checkpoints

We will complete one stage at a time. For each stage: explain the change, implement it, verify its behaviour, review the result, update project status, then commit and push to GitHub before moving on.

| Stage | Deliverable | Completion check | Suggested commit |
| --- | --- | --- | --- |
| 1. Project definition — complete | README, working name, requirements, and roadmap. | Every required feature and submission item is mapped. | `docs: define CampusKit project and build roadmap` |
| 2. Application foundation — complete | Starting data, entry point, menu loop, input helpers, and `.gitignore`. | Menu repeats, invalid selections are handled, and exit works. | `feat: add CLI foundation and starting data` |
| 3. Resource inventory — complete | Add/list resources and validate resource fields. | Valid additions work; duplicate IDs and invalid totals leave inventory unchanged. | `feat: implement resource inventory management` |
| 4. Borrowing — complete | Fellow/resource validation, stock checks, records, and receipts. | Valid loans reduce stock; invalid IDs, quantities, and insufficient stock leave all state unchanged. | `feat: implement validated resource borrowing` |
| 5. Returns | Outstanding loan calculation and partial/full returns. | Repeated borrowings and returns remain correct; excessive or invalid returns change nothing. | `feat: implement validated resource returns` |
| 6. Search and category filter | Case-insensitive name search and category filtering. | `LAPtop` finds Laptop; category matching and no-match messages work. | `feat: add inventory search and category filters` |
| 7. Reports and loan visibility | Required reports, all tied leaders, fellow loan view, stock labels, and consistency checks. | Totals agree with loans; ties, zero stock, and no outstanding loans are handled correctly. | `feat: add stock reports and fellow loan views` |
| 8. Demonstration and test evidence | Fresh-state demo, full regression tests, and captured output. | Steps 1–7 pass in order; include an additional invalid-input test and actual output. | `test: verify requirements and capture demonstration evidence` |
| 9. Optional JSON persistence | Save/reload inventory and borrowing records using `json`. | Restart preserves state; malformed or inconsistent files are rejected without silently overwriting them; demo remains isolated. | `feat: add optional JSON save and reload` |
| 10. Final review and submission | Update README, complete design explanation, rerun checks, and prepare A1/A2/A3. | A fresh checkout runs locally, evidence matches final code, and all changes are pushed. | `docs: finalize usage and project submission` |

Tests for each feature will be introduced alongside that feature. Stage 8 brings them together and captures the required evidence. Stage 9 is optional; complete the required project first.

## Required demonstration specification

**The table below contains expected acceptance criteria, not actual run output.** Actual results will be captured during Stage 8 and refreshed after any later code changes.

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

Automated coverage will also include zero, negative and decimal quantities; unknown IDs; duplicate resource IDs; borrowing exactly the available quantity; returns across multiple loans; fully returned loans; case-insensitive filtering; report ties; and empty/no-loan reports. Rejection tests will compare the full state before and after the action.

## Submission checklist

- [ ] **A1 — Source code (50 marks):** provide the full final Python code as requested by the submission field, plus a viewable source link if appropriate. Check repository access for the grader.
- [ ] **A2 — Demonstration and test evidence (15 marks):** paste actual output from Steps 1–7 in order and one additional invalid-input test. Never present the acceptance table as executed evidence.
- [ ] **A3 — Design explanation (5 marks):** describe at least four implemented functions, the inventory and fellow-loan representations, and one genuine design limitation.
- [ ] **Optional bonus:** demonstrate JSON saving and reloading if Stage 9 is completed.
- [ ] Ensure final evidence was generated from the submitted code and commit.

## Design limitations

The planned application is for one local operator at a time. Fellow ID checks confirm that an ID exists; they do not authenticate the person using it. Resources are tracked by quantity, so individual laptop serial numbers, damage, due dates, and fines are outside scope. Before optional JSON persistence, closing the program loses session changes. Even with JSON, simultaneous users are not supported.

## Learning workflow

This is a solo fellow project. Each stage should be understood well enough to explain the functions, trace a transaction, and justify the validation rules. Keep commits focused on real progress and follow the programme's rules for acknowledging assistance.
