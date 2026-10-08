# A3 — Project design explanation

CampusKit has nine functions. `add_resource()` adds resources and rejects duplicate IDs. `borrow_resource()` checks IDs, quantity, and stock before recording a loan and reducing availability. `return_resource()` checks what the fellow owes, updates the oldest matching loans, and restores stock. `search_resources()` searches names or filters categories. `generate_report()` calculates totals, low stock, and every tied most-borrowed resource.

Inventory is a list of dictionaries containing each resource's ID, name, category, total units, and available units. Fellows are a dictionary mapping IDs to names. Borrowing records are a list of dictionaries containing a loan ID, fellow ID, resource ID, quantity borrowed, and quantity returned. Outstanding units equal borrowed minus returned quantities. All validation happens before changing a transaction's records or stock.

One limitation is that data exists only in memory. Closing the program loses the session's changes, and reopening it starts with the original inventory and no loans. JSON saving is omitted for now.
