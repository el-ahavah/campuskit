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

    # Records are retained, including fully returned loans in later stages.
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


def show_menu():
    """Display only the actions currently implemented."""
    print("\nCampusKit | Main menu")
    print("1. View session overview")
    print("2. View registered fellows")
    print("3. List resources")
    print("4. Add a resource")
    print("5. Borrow a resource")
    print("0. Exit")


def read_menu_choice():
    """Keep asking until the user chooses an available menu action."""
    while True:
        choice = read_non_empty("Choose an option (0-5): ")
        if choice in ("0", "1", "2", "3", "4", "5"):
            return choice
        print("Invalid option. Please choose 0, 1, 2, 3, 4, or 5.")


def show_overview(resources, fellows, borrow_records):
    """Show session counts; full stock reporting arrives in Stage 7."""
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
    print("Borrow resources using option 5. Returns arrive in Stage 5.")
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
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended. Closing CampusKit.")
    print("Goodbye from CampusKit.")


if __name__ == "__main__":
    main()
