# CampusKit project design — A3

CampusKit separates the operations that change data from the functions that ask for input or print results. It uses Python's standard library and runs locally in a repeating command-line menu.

## Main functions

| Function | What it does |
| --- | --- |
| `create_initial_state()` | Creates fresh copies of the three starting resources, the fellow dictionary, and an empty borrowing-record list. |
| `add_resource()` | Validates the ID, name, category, and total; rejects duplicate IDs; adds a resource with all units initially available. |
| `borrow_resource()` | Checks the fellow, resource, positive integer quantity, and stock before appending a loan and reducing availability. |
| `return_resource()` | Checks how many units the fellow still owes, updates the oldest matching loans first, and restores available units. |
| `search_resources()` | Finds resource names containing a search term using case-insensitive matching. |
| `filter_by_category()` | Matches a whole category name, ignoring case and surrounding spaces. |
| `generate_report()` | Calculates total, available, and outstanding borrowed units, low-stock resources, and every tied most-borrowed leader. |
| `check_consistency()` | Detects stock/loan mismatches, invalid quantities, duplicate IDs, and unknown fellow or resource references. |
| `get_fellow_loans()` | Groups one fellow's outstanding units by resource and omits fully returned loans. |
| `run_demo()` | Runs the seven required steps and an invalid-input test on fresh state, checking the actual results. |
| `main()` | Runs the menu until exit, handles input interruptions, and holds the current session’s state. |

## Inventory and fellow loans

Inventory is a list of dictionaries. Each resource has `id`, `name`, `category`, `total`, and `available`. IDs are trimmed and converted to uppercase, so `r001` and ` R001 ` refer to the same resource. A dictionary maps fellow IDs to names, such as `F001` to `Ada`.

`borrow_records` is a list of dictionaries with one record per successful borrowing. Each stores `loan_id`, `fellow_id`, `resource_id`, `quantity_borrowed`, and `quantity_returned`. A record's outstanding quantity is the borrowed quantity minus the returned quantity. To find a fellow's balance for a resource, the program sums that quantity across their matching records.

For example, borrowing two laptops produces a record with `quantity_borrowed` equal to 2 and `quantity_returned` equal to 0. Returning one changes the returned quantity to 1 and increases Laptop availability from 8 to 9. The fellow still owes one laptop. Fully returned records stay in the list to preserve the original borrowing history and keep loan IDs sequential.

If a return spans multiple borrowings, the program first checks the entire outstanding balance. Only a valid return updates records, starting with the oldest matching loan. Other fellows' loans and other resources are untouched.

## Validation and reports

The business functions validate before changing data. Rejected requests do not alter inventory or loan records. Prompts handle blank input and retry invalid numeric input; direct business-function calls also reject invalid quantities, including booleans and decimal values.

For each resource, available units plus outstanding loan units must equal total units. Reports check this relationship before displaying balances. Low stock means fewer than three available units, including zero. Most borrowed means units still on loan, not cumulative historical borrowing. All tied leaders are included; if nothing is borrowed, the program says so.

## Session lifetime

All data is stored in Python lists and dictionaries in memory. Normal startup and `--demo` each create fresh starting state. No JSON file is loaded or saved. Persistence is an optional bonus deferred until the author has learned JSON.

## Design limitations

The main limitation is that inventory and loans are lost when the program closes. A new launch starts with the original data, so this version cannot track loans across sessions. Separate running instances do not share data.

Fellow IDs identify registered fellows; they do not authenticate the person using the program. Equipment is tracked in quantities, not by individual serial numbers. Returns update aggregate quantities in borrowing records rather than creating a separate dated return-event history.
