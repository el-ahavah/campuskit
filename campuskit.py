"""CampusKit: a local campus equipment manager, built one stage at a time."""


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


def main():
    """Start a session and keep the menu running until exit or interruption."""
    resources, fellows, borrow_records = create_initial_state()
    print("Welcome to CampusKit")
    print("Know what is available, who has it, and what comes back.")
    print("Inventory: add and list resources from the menu.")
    print("Borrow resources using option 5; return them using option 6.")
    print("Session data is in memory only; nothing is saved on exit.")

    try:
        while True:
            show_menu()
            choice = read_menu_choice()
            if choice == "0":
                break
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
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended. Closing CampusKit.")
    print("Goodbye from CampusKit.")


if __name__ == "__main__":
    main()
