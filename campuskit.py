"""CampusKit: a local, standard-library campus equipment lending desk."""

import argparse
import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path


def create_initial_state():
    """Create independent inventory, fellows, and loan records for a session."""
    resources = [
        {"id": "R001", "name": "Laptop", "category": "Electronics", "total": 10, "available": 10},
        {"id": "R002", "name": "Keyboard", "category": "Accessories", "total": 5, "available": 5},
        {"id": "R003", "name": "Headset", "category": "Accessories", "total": 3, "available": 3},
    ]
    fellows = {"F001": "Ada", "F002": "John", "F003": "Grace"}
    borrow_records = []
    return resources, fellows, borrow_records


def read_non_empty(prompt):
    """Prompt again until the user supplies non-blank text."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a value; this field cannot be blank.")


def read_positive_integer(prompt):
    """Read a positive whole number for resource and loan prompts."""
    while True:
        value = read_non_empty(prompt)
        try:
            quantity = int(value)
        except ValueError:
            print("Please enter a positive whole number, such as 1 or 2.")
            continue
        if quantity > 0:
            return quantity
        print("Please enter a positive whole number greater than zero.")


def validate_text(value, field):
    """Return trimmed text or reject a missing/non-text field."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def find_resource(resources, resource_id):
    """Find a resource by ID, ignoring outer spaces and letter case."""
    resource_id = validate_text(resource_id, "Resource ID").upper()
    for resource in resources:
        if resource["id"].strip().upper() == resource_id:
            return resource
    return None


def add_resource(resources, resource_id, name, category, total):
    """Validate everything before appending a resource; return the new record."""
    resource_id = validate_text(resource_id, "Resource ID").upper()
    name = validate_text(name, "Name")
    category = validate_text(category, "Category")
    if type(total) is not int or total <= 0:
        raise ValueError("Total units must be a positive whole number.")
    if find_resource(resources, resource_id) is not None:
        raise ValueError(f"Resource ID {resource_id} already exists. Use a different ID.")
    resource = {
        "id": resource_id,
        "name": name,
        "category": category,
        "total": total,
        "available": total,
    }
    resources.append(resource)
    return resource


def list_resources(resources):
    """Print all required inventory fields without changing stock."""
    print("\nResource inventory")
    if not resources:
        print("No resources yet. Choose Add a resource to get started.")
        return
    headers = ["ID", "Name", "Category", "Total", "Available"]
    rows = [
        [str(resource[key]) for key in ("id", "name", "category", "total", "available")]
        for resource in resources
    ]
    widths = [max(len(row[i]) for row in [headers] + rows) for i in range(5)]
    print("  ".join(value.ljust(width) for value, width in zip(headers, widths)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(value.ljust(width) for value, width in zip(row, widths)))


def prompt_add_resource(resources):
    """Collect a resource's fields and display the result of adding it."""
    print("\nAdd a resource")
    resource_id = read_non_empty("Resource ID (for example R004): ")
    if find_resource(resources, resource_id) is not None:
        print(f"Resource ID {resource_id.upper()} already exists. Nothing was added.")
        return
    name = read_non_empty("Name: ")
    category = read_non_empty("Category: ")
    total = read_positive_integer("Total units: ")
    try:
        resource = add_resource(resources, resource_id, name, category, total)
    except ValueError as error:
        print(f"Cannot add resource: {error}")
        return
    print(f"Added {resource['id']} | {resource['name']} | "
          f"{resource['available']} of {resource['total']} units available.")


def borrow_resource(resources, fellows, borrow_records, fellow_id, resource_id, quantity):
    """Validate a loan completely before changing stock or recording it."""
    fellow_id = validate_text(fellow_id, "Fellow ID").upper()
    resource_id = validate_text(resource_id, "Resource ID").upper()
    if fellow_id not in fellows:
        raise ValueError(f"Unknown fellow ID {fellow_id}. Check the registered fellows.")
    resource = find_resource(resources, resource_id)
    if resource is None:
        raise ValueError(f"Unknown resource ID {resource_id}. Check the resource inventory.")
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")
    if quantity > resource["available"]:
        raise ValueError(
            f"Insufficient stock: {resource['name']} has {resource['available']} "
            f"available; requested {quantity}."
        )

    # Records are retained, including fully returned loans.
    record = {
        "loan_id": f"L{len(borrow_records) + 1:03d}",
        "fellow_id": fellow_id,
        "resource_id": resource_id,
        "quantity_borrowed": quantity,
        "quantity_returned": 0,
    }
    borrow_records.append(record)
    resource["available"] -= quantity
    return record


def prompt_borrow_resource(resources, fellows, borrow_records):
    """Collect a loan request and show a receipt or a helpful rejection."""
    print("\nBorrow a resource")
    fellow_id = read_non_empty("Fellow ID: ")
    resource_id = read_non_empty("Resource ID: ")
    quantity = read_positive_integer("Quantity: ")
    try:
        record = borrow_resource(
            resources, fellows, borrow_records, fellow_id, resource_id, quantity
        )
    except ValueError as error:
        print(f"Borrowing rejected: {error} No stock or loan records changed.")
        return
    resource = find_resource(resources, record["resource_id"])
    print(f"Borrowing confirmed | {record['loan_id']}")
    print(f"Fellow: {record['fellow_id']} | {fellows[record['fellow_id']]}")
    print(f"Resource: {resource['id']} | {resource['name']}")
    print(f"Quantity borrowed: {record['quantity_borrowed']}")
    print(f"Available now: {resource['available']}")


def outstanding_quantity(borrow_records, fellow_id, resource_id):
    """Count units this fellow still owes for this resource."""
    fellow_id = validate_text(fellow_id, "Fellow ID").upper()
    resource_id = validate_text(resource_id, "Resource ID").upper()
    return sum(
        record["quantity_borrowed"] - record["quantity_returned"]
        for record in borrow_records
        if record["fellow_id"] == fellow_id and record["resource_id"] == resource_id
    )


def return_resource(resources, fellows, borrow_records, fellow_id, resource_id, quantity):
    """Validate a complete return, then settle the oldest matching loans first."""
    fellow_id = validate_text(fellow_id, "Fellow ID").upper()
    resource_id = validate_text(resource_id, "Resource ID").upper()
    if fellow_id not in fellows:
        raise ValueError(f"Unknown fellow ID {fellow_id}. Check the registered fellows.")
    resource = find_resource(resources, resource_id)
    if resource is None:
        raise ValueError(f"Unknown resource ID {resource_id}. Check the resource inventory.")
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")
    outstanding = outstanding_quantity(borrow_records, fellow_id, resource_id)
    if quantity > outstanding:
        raise ValueError(
            f"{fellow_id} has {outstanding} units of {resource['name']} on loan; "
            f"cannot return {quantity}."
        )

    # All validation finishes before any record or stock is changed.
    remaining = quantity
    for record in borrow_records:
        if record["fellow_id"] != fellow_id or record["resource_id"] != resource_id:
            continue
        owed = record["quantity_borrowed"] - record["quantity_returned"]
        returned = min(remaining, owed)
        record["quantity_returned"] += returned
        remaining -= returned
        if remaining == 0:
            break
    resource["available"] += quantity
    return {
        "fellow_id": fellow_id,
        "resource_id": resource_id,
        "quantity_returned": quantity,
        "outstanding": outstanding - quantity,
        "available": resource["available"],
    }


def prompt_return_resource(resources, fellows, borrow_records):
    """Collect a return request and show its outcome."""
    print("\nReturn a resource")
    fellow_id = read_non_empty("Fellow ID: ")
    resource_id = read_non_empty("Resource ID: ")
    quantity = read_positive_integer("Quantity to return: ")
    try:
        receipt = return_resource(
            resources, fellows, borrow_records, fellow_id, resource_id, quantity
        )
    except ValueError as error:
        print(f"Return rejected: {error} No stock or loan records changed.")
        return
    resource = find_resource(resources, receipt["resource_id"])
    print("Return confirmed")
    print(f"Fellow: {receipt['fellow_id']} | {fellows[receipt['fellow_id']]}")
    print(f"Resource: {resource['id']} | {resource['name']}")
    print(f"Quantity returned: {receipt['quantity_returned']}")
    print(f"Still on loan for this fellow: {receipt['outstanding']}")
    print(f"Available now: {receipt['available']}")


def search_resources(resources, query):
    """Find names containing the query, ignoring case and outer spaces."""
    query = validate_text(query, "Search term").casefold()
    return [resource for resource in resources if query in resource["name"].casefold()]


def filter_by_category(resources, category):
    """Match a complete category name, ignoring case and outer spaces."""
    category = validate_text(category, "Category").casefold()
    return [resource for resource in resources
            if resource["category"].strip().casefold() == category]


def prompt_search_resources(resources):
    """Display matching resources or a specific no-match message."""
    print("\nSearch resources by name")
    query = read_non_empty("Name or part of name: ")
    matches = search_resources(resources, query)
    if matches:
        print(f"Matches found: {len(matches)}")
        list_resources(matches)
    else:
        print(f"No resources match name '{query}'.")


def prompt_filter_by_category(resources):
    """Display the resources in the requested category."""
    print("\nFilter resources by category")
    category = read_non_empty("Category (for example Accessories): ")
    matches = filter_by_category(resources, category)
    if matches:
        print(f"Matches found: {len(matches)}")
        list_resources(matches)
    else:
        print(f"No resources found in category '{category}'.")


def check_consistency(resources, fellows, borrow_records):
    """Return stock/loan consistency errors without repairing or changing state."""
    errors = []
    resource_ids = [r["id"] for r in resources]
    if len(set(resource_ids)) != len(resource_ids):
        errors.append("Duplicate resource IDs found.")
    loan_ids = [r["loan_id"] for r in borrow_records]
    if len(set(loan_ids)) != len(loan_ids):
        errors.append("Duplicate loan IDs found.")
    borrowed = {resource_id: 0 for resource_id in resource_ids}
    for record in borrow_records:
        label = record["loan_id"]
        if record["fellow_id"] not in fellows:
            errors.append(f"{label}: unknown fellow ID.")
        if record["resource_id"] not in borrowed:
            errors.append(f"{label}: unknown resource ID.")
        issued, returned = record["quantity_borrowed"], record["quantity_returned"]
        if (type(issued) is not int or type(returned) is not int
                or issued <= 0 or not 0 <= returned <= issued):
            errors.append(f"{label}: invalid borrowed or returned quantity.")
            continue
        if record["resource_id"] in borrowed:
            borrowed[record["resource_id"]] += issued - returned
    for resource in resources:
        total, available = resource["total"], resource["available"]
        if (type(total) is not int or type(available) is not int
                or total <= 0 or not 0 <= available <= total):
            errors.append(f"{resource['id']}: invalid stock quantities.")
        elif available + borrowed[resource["id"]] != total:
            errors.append(f"{resource['id']}: available stock plus outstanding loans does not equal total.")
    return errors


def stock_status(available):
    """Label stock using the assignment's fewer-than-three threshold."""
    if available == 0:
        return "OUT OF STOCK"
    if available < 3:
        return "LOW STOCK"
    return "AVAILABLE"


def generate_report(resources, fellows, borrow_records):
    """Calculate current stock figures, refusing inconsistent inventory/loans."""
    errors = check_consistency(resources, fellows, borrow_records)
    if errors:
        raise ValueError("Consistency check failed: " + " ".join(errors))
    rows = []
    for resource in resources:
        borrowed = sum(r["quantity_borrowed"] - r["quantity_returned"]
                       for r in borrow_records if r["resource_id"] == resource["id"])
        rows.append({**resource, "borrowed": borrowed, "status": stock_status(resource["available"])})
    highest = max((row["borrowed"] for row in rows), default=0)
    return {
        "total": sum(row["total"] for row in rows),
        "available": sum(row["available"] for row in rows),
        "borrowed": sum(row["borrowed"] for row in rows),
        "resources": rows,
        "low_stock": [row for row in rows if row["available"] < 3],
        "most_borrowed": [row for row in rows if highest > 0 and row["borrowed"] == highest],
    }


def show_report(resources, fellows, borrow_records):
    """Display totals, stock labels, low stock, and every tied leader."""
    try:
        report = generate_report(resources, fellows, borrow_records)
    except ValueError as error:
        print(f"Cannot generate report. {error}")
        return
    print("\nCampusKit stock report")
    print(f"Total units: {report['total']}")
    print(f"Available units: {report['available']}")
    print(f"Units currently borrowed: {report['borrowed']}")
    print("Stock by resource:")
    if not report["resources"]:
        print("No resources in inventory.")
    for row in report["resources"]:
        print(f"{row['id']} | {row['name']} | Total: {row['total']} | "
              f"Available: {row['available']} | Borrowed: {row['borrowed']} | {row['status']}")
    print("Low stock (fewer than 3 available):")
    if not report["low_stock"]:
        print("None.")
    for row in report["low_stock"]:
        print(f"{row['id']} | {row['name']} | Available: {row['available']}")
    print("Most units currently borrowed (all tied leaders):")
    if not report["most_borrowed"]:
        print("No units currently borrowed.")
    for row in report["most_borrowed"]:
        print(f"{row['id']} | {row['name']} | Borrowed: {row['borrowed']}")
    print("Consistency check: PASS")


def get_fellow_loans(resources, fellows, borrow_records, fellow_id):
    """Group a fellow's outstanding loans by resource, omitting settled loans."""
    fellow_id = validate_text(fellow_id, "Fellow ID").upper()
    if fellow_id not in fellows:
        raise ValueError(f"Unknown fellow ID {fellow_id}.")
    errors = check_consistency(resources, fellows, borrow_records)
    if errors:
        raise ValueError("Consistency check failed: " + " ".join(errors))
    rows = []
    for resource in resources:
        quantity = outstanding_quantity(borrow_records, fellow_id, resource["id"])
        if quantity:
            rows.append({"resource_id": resource["id"], "name": resource["name"], "outstanding": quantity})
    return rows


def prompt_fellow_loans(resources, fellows, borrow_records):
    """Ask for a fellow and display only their outstanding resource quantities."""
    fellow_id = read_non_empty("Fellow ID: ").upper()
    try:
        rows = get_fellow_loans(resources, fellows, borrow_records, fellow_id)
    except ValueError as error:
        print(f"Cannot show fellow loans. {error}")
        return
    print(f"\nOutstanding loans: {fellow_id} | {fellows[fellow_id]}")
    if not rows:
        print("No outstanding loans.")
    for row in rows:
        print(f"{row['resource_id']} | {row['name']} | Outstanding: {row['outstanding']}")
    print(f"Total units on loan: {sum(row['outstanding'] for row in rows)}")


def show_menu():
    """Display only the actions currently implemented."""
    print("\nCampusKit | Main menu")
    print("1. View session overview")
    print("2. View registered fellows")
    print("3. List resources")
    print("4. Add a resource")
    print("5. Borrow a resource")
    print("6. Return a resource")
    print("7. Search resources by name")
    print("8. Filter resources by category")
    print("9. View stock report")
    print("10. View a fellow's outstanding loans")
    print("0. Exit")


def read_menu_choice():
    """Keep asking until the user chooses an available menu action."""
    while True:
        choice = read_non_empty("Choose an option (0-10): ")
        if choice in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"):
            return choice
        print("Invalid option. Please choose a number from 0 to 10.")


def show_overview(resources, fellows, borrow_records):
    """Show session counts; option 9 provides the full stock report."""
    print("\nSession overview")
    print(f"Resource types: {len(resources)}")
    print(f"Registered fellows: {len(fellows)}")
    print(f"Borrowing records: {len(borrow_records)}")


def show_fellows(fellows):
    """Display the fellow IDs that will be used when issuing equipment."""
    print("\nRegistered fellows")
    for fellow_id, name in fellows.items():
        print(f"{fellow_id}  {name}")


def validate_saved_state(payload):
    """Validate a complete JSON document before allowing it into a session."""
    if not isinstance(payload, dict) or type(payload.get("version")) is not int or payload["version"] != 1:
        raise ValueError("Saved data must be an object with version 1.")
    resources = payload.get("resources")
    fellows = payload.get("fellows")
    records = payload.get("borrow_records")
    if not isinstance(resources, list) or not isinstance(fellows, dict) or not isinstance(records, list):
        raise ValueError("Saved resources/borrow_records must be lists and fellows must be an object.")
    for fellow_id, name in fellows.items():
        if validate_text(fellow_id, "Fellow ID").upper() != fellow_id:
            raise ValueError("Saved fellow IDs must be trimmed and uppercase.")
        validate_text(name, "Fellow name")
    for resource in resources:
        if not isinstance(resource, dict) or not {"id", "name", "category", "total", "available"} <= resource.keys():
            raise ValueError("Saved resource is missing required fields.")
        if validate_text(resource["id"], "Resource ID").upper() != resource["id"]:
            raise ValueError("Saved resource IDs must be trimmed and uppercase.")
        validate_text(resource["name"], "Resource name")
        validate_text(resource["category"], "Category")
    for index, record in enumerate(records, start=1):
        fields = {"loan_id", "fellow_id", "resource_id", "quantity_borrowed", "quantity_returned"}
        if not isinstance(record, dict) or not fields <= record.keys():
            raise ValueError("Saved loan is missing required fields.")
        if record["loan_id"] != f"L{index:03d}":
            raise ValueError("Saved loan IDs must be sequential and in original borrowing order.")
        validate_text(record["fellow_id"], "Fellow ID")
        validate_text(record["resource_id"], "Resource ID")
    errors = check_consistency(resources, fellows, records)
    if errors:
        raise ValueError("Invalid saved state: " + " ".join(errors))
    return resources, fellows, records


def load_state(path):
    """Load validated JSON; only a genuinely missing file starts fresh."""
    try:
        with Path(path).open(encoding="utf-8") as stream:
            payload = json.load(stream)
    except FileNotFoundError:
        return create_initial_state()
    return validate_saved_state(payload)


def save_state(path, resources, fellows, borrow_records):
    """Validate and atomically replace the save file using a sibling temporary file."""
    payload = {"version": 1, "resources": resources, "fellows": fellows, "borrow_records": borrow_records}
    validate_saved_state(payload)
    path = Path(path)
    # Never silently replace a corrupt existing save.
    if path.exists():
        load_state(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".campuskit-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(data_path=None):
    """Start a session and keep the menu running until exit or interruption."""
    try:
        resources, fellows, borrow_records = load_state(data_path) if data_path is not None else create_initial_state()
    except (OSError, ValueError) as error:
        print(f"Cannot load saved data: {error}")
        print("The file was not changed. Repair it or use --no-save for a fresh temporary session.")
        return 1
    print("Welcome to CampusKit")
    print("Know what is available, who has it, and what comes back.")

    try:
        while True:
            show_menu()
            choice = read_menu_choice()
            if choice == "0":
                break
            before = deepcopy((resources, fellows, borrow_records)) if data_path is not None else None
            if choice == "1":
                show_overview(resources, fellows, borrow_records)
            elif choice == "2":
                show_fellows(fellows)
            elif choice == "3":
                list_resources(resources)
            elif choice == "4":
                prompt_add_resource(resources)
            elif choice == "5":
                prompt_borrow_resource(resources, fellows, borrow_records)
            elif choice == "6":
                prompt_return_resource(resources, fellows, borrow_records)
            elif choice == "7":
                prompt_search_resources(resources)
            elif choice == "8":
                prompt_filter_by_category(resources)
            elif choice == "9":
                show_report(resources, fellows, borrow_records)
            elif choice == "10":
                prompt_fellow_loans(resources, fellows, borrow_records)
            if data_path is not None and (resources, fellows, borrow_records) != before:
                try:
                    save_state(data_path, resources, fellows, borrow_records)
                except (OSError, ValueError) as error:
                    resources, fellows, borrow_records = before
                    print(f"Save failed: {error}")
                    print("The preceding change was rolled back; it was NOT saved. Please retry.")
                else:
                    print("Changes saved.")
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended. Closing CampusKit.")
    print("Goodbye from CampusKit.")
    return 0


def run_demo():
    """Run and verify the required scenario using isolated, fresh state."""
    resources, fellows, records = create_initial_state()

    def verify(condition, message):
        if not condition:
            raise RuntimeError(f"Demonstration failed: {message}")

    def reject_without_changes(action):
        before = deepcopy((resources, fellows, records))
        try:
            action()
        except ValueError as error:
            print(f"Rejected: {error}")
        else:
            raise RuntimeError("Demonstration failed: invalid request was accepted.")
        verify((resources, fellows, records) == before, "rejection changed state")
        print("Inventory, fellows, and loan records unchanged: PASS")

    print("CampusKit required demonstration")
    print("Fresh starting data: 18 total units, 18 available, no loans.")
    print("\n1. F001 borrows 2 laptops")
    borrow_resource(resources, fellows, records, "F001", "R001", 2)
    available = find_resource(resources, "R001")["available"]
    print(f"Laptop available: {available}")
    verify(available == 8, "step 1 stock")

    print("\n2. F002 borrows 3 keyboards")
    borrow_resource(resources, fellows, records, "F002", "R002", 3)
    available = find_resource(resources, "R002")["available"]
    print(f"Keyboard available: {available}")
    verify(available == 2, "step 2 stock")

    print("\n3. F001 returns 1 laptop")
    receipt = return_resource(resources, fellows, records, "F001", "R001", 1)
    print(f"Laptop available: {receipt['available']}")
    print(f"F001 laptops still on loan: {receipt['outstanding']}")
    verify(receipt["available"] == 9 and receipt["outstanding"] == 1, "step 3 return")

    print("\n4. F003 requests 4 headsets")
    reject_without_changes(lambda: borrow_resource(resources, fellows, records, "F003", "R003", 4))
    print(f"Headset available: {find_resource(resources, 'R003')['available']}")

    print("\n5. F002 tries to return 4 keyboards")
    reject_without_changes(lambda: return_resource(resources, fellows, records, "F002", "R002", 4))
    print(f"Keyboard available: {find_resource(resources, 'R002')['available']}")
    print(f"F002 keyboards still on loan: {outstanding_quantity(records, 'F002', 'R002')}")

    print("\n6. Search for LAPtop")
    matches = search_resources(resources, "LAPtop")
    list_resources(matches)
    verify([r["id"] for r in matches] == ["R001"], "case-insensitive search")

    print("\n7. Generate the report")
    report = generate_report(resources, fellows, records)
    show_report(resources, fellows, records)
    verify((report["total"], report["available"], report["borrowed"]) == (18, 14, 4), "report totals")
    verify([(r["id"], r["available"]) for r in report["low_stock"]] == [("R002", 2)], "low stock")
    verify([(r["id"], r["borrowed"]) for r in report["most_borrowed"]] == [("R002", 3)], "most borrowed")

    print("\nAdditional invalid-input test: F001 requests 'two' laptops")
    print("Testing the borrowing function with a text quantity.")
    reject_without_changes(lambda: borrow_resource(resources, fellows, records, "F001", "R001", "two"))
    print(f"Laptop available: {find_resource(resources, 'R001')['available']}")
    print(f"Borrowing records: {len(records)}")
    print("\nAll seven required steps and the additional invalid-input test: PASS")


def cli():
    """Select the interactive application or the reproducible demonstration."""
    parser = argparse.ArgumentParser(description="CampusKit resource management")
    parser.add_argument("--demo", action="store_true", help="run the required demonstration on fresh data")
    storage = parser.add_mutually_exclusive_group()
    storage.add_argument("--data", type=Path, default=Path(__file__).resolve().parent / "data" / "campuskit.json",
                         help="JSON save file (default: data/campuskit.json beside the program)")
    storage.add_argument("--no-save", action="store_true", help="start fresh without reading or writing saved data")
    args = parser.parse_args()
    if args.demo:
        run_demo()
        return 0
    else:
        return main(None if args.no_save else args.data)


if __name__ == "__main__":
    raise SystemExit(cli())
