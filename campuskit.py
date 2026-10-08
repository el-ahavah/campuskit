"""CampusKit: a local, standard-library campus equipment lending desk."""

import argparse


def create_initial_state():
    """Return fresh inventory, fellows, and borrowing records."""
    resources = [
        {"id": "R001", "name": "Laptop", "category": "Electronics", "total": 10, "available": 10},
        {"id": "R002", "name": "Keyboard", "category": "Accessories", "total": 5, "available": 5},
        {"id": "R003", "name": "Headset", "category": "Accessories", "total": 3, "available": 3},
    ]
    fellows = {"F001": "Ada", "F002": "John", "F003": "Grace"}
    borrow_records = []
    return resources, fellows, borrow_records


def add_resource(resources, resource_id, name, category, total):
    """Check every field before adding a resource."""
    for value in (resource_id, name, category):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID, name, and category must be non-empty text.")
    resource_id = resource_id.strip().upper()
    if type(total) is not int or total <= 0:
        raise ValueError("Total must be a positive integer.")
    for resource in resources:
        if resource["id"] == resource_id:
            raise ValueError("That resource ID already exists.")
    resource = {"id": resource_id, "name": name.strip(), "category": category.strip(),
                "total": total, "available": total}
    resources.append(resource)
    return resource


def list_resources(resources):
    """Display the five inventory fields."""
    if not resources:
        print("No matching resources.")
        return
    print("ID | Name | Category | Total | Available")
    for resource in resources:
        print(f"{resource['id']} | {resource['name']} | {resource['category']} | "
              f"{resource['total']} | {resource['available']}")


def borrow_resource(resources, fellows, records, fellow_id, resource_id, quantity):
    """Validate first, then record a loan and reduce stock."""
    if not isinstance(fellow_id, str) or not isinstance(resource_id, str):
        raise ValueError("Fellow and resource IDs must be text.")
    fellow_id = fellow_id.strip().upper()
    resource_id = resource_id.strip().upper()
    if fellow_id not in fellows:
        raise ValueError("Unknown fellow ID.")
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")
    resource = None
    for item in resources:
        if item["id"] == resource_id:
            resource = item
            break
    if resource is None:
        raise ValueError("Unknown resource ID.")
    if quantity > resource["available"]:
        raise ValueError(f"Not enough stock: only {resource['available']} available.")
    records.append({"loan_id": f"L{len(records) + 1:03d}", "fellow_id": fellow_id,
                    "resource_id": resource_id, "quantity_borrowed": quantity,
                    "quantity_returned": 0})
    resource["available"] -= quantity
    return resource["available"]


def return_resource(resources, fellows, records, fellow_id, resource_id, quantity):
    """Check the full return, then update the oldest matching loans."""
    if not isinstance(fellow_id, str) or not isinstance(resource_id, str):
        raise ValueError("Fellow and resource IDs must be text.")
    fellow_id = fellow_id.strip().upper()
    resource_id = resource_id.strip().upper()
    if fellow_id not in fellows:
        raise ValueError("Unknown fellow ID.")
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")
    resource = None
    for item in resources:
        if item["id"] == resource_id:
            resource = item
            break
    if resource is None:
        raise ValueError("Unknown resource ID.")
    outstanding = 0
    for record in records:
        if record["fellow_id"] == fellow_id and record["resource_id"] == resource_id:
            outstanding += record["quantity_borrowed"] - record["quantity_returned"]
    if quantity > outstanding:
        raise ValueError(f"Cannot return {quantity}: this fellow owes only {outstanding}.")
    remaining = quantity
    for record in records:
        if record["fellow_id"] == fellow_id and record["resource_id"] == resource_id:
            owed = record["quantity_borrowed"] - record["quantity_returned"]
            returned = min(remaining, owed)
            record["quantity_returned"] += returned
            remaining -= returned
            if remaining == 0:
                break
    resource["available"] += quantity
    return resource["available"]


def search_resources(resources, query, category=False):
    """Search part of a name, or match a complete category."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Enter a non-empty search term.")
    query = query.strip().lower()
    matches = []
    for resource in resources:
        if category:
            matched = resource["category"].lower() == query
        else:
            matched = query in resource["name"].lower()
        if matched:
            matches.append(resource)
    return matches


def generate_report(resources):
    """Calculate and print totals, low stock, and every tied leader."""
    total = 0
    available = 0
    low_stock = []
    leaders = []
    highest = 0
    for resource in resources:
        total += resource["total"]
        available += resource["available"]
        borrowed = resource["total"] - resource["available"]
        if resource["available"] < 3:
            low_stock.append(resource)
        if borrowed > highest:
            highest = borrowed
            leaders = [resource]
        elif borrowed == highest and borrowed > 0:
            leaders.append(resource)
    print(f"Total units: {total}")
    print(f"Available units: {available}")
    print(f"Units currently borrowed: {total - available}")
    print("Low stock (fewer than 3 available):")
    if not low_stock:
        print("None.")
    for resource in low_stock:
        print(f"{resource['name']} ({resource['id']}): {resource['available']} available")
    print("Most units currently borrowed (all tied leaders):")
    if not leaders:
        print("No units currently borrowed.")
    for resource in leaders:
        print(f"{resource['name']} ({resource['id']}): {highest} borrowed")
    return {"total": total, "available": available, "borrowed": total - available,
            "low_stock": low_stock, "most_borrowed": leaders}


def main():
    """Run the menu, showing errors without ending the session."""
    resources, fellows, records = create_initial_state()
    print("Welcome to CampusKit")
    print("Know what is available, who has it, and what comes back.")
    try:
        while True:
            print("\n1. List resources\n2. Add resource\n3. Borrow\n4. Return")
            print("5. Search name\n6. Filter category\n7. Report\n8. List fellows\n0. Exit")
            choice = input("Choose 0-8: ").strip()
            if choice == "0":
                break
            try:
                if choice == "1":
                    list_resources(resources)
                elif choice == "2":
                    resource_id = input("Resource ID: ")
                    name = input("Name: ")
                    category = input("Category: ")
                    total = int(input("Total units (positive integer): "))
                    add_resource(resources, resource_id, name, category, total)
                    print("Resource added.")
                elif choice in ("3", "4"):
                    fellow_id = input("Fellow ID: ")
                    resource_id = input("Resource ID: ")
                    quantity = int(input("Quantity (positive integer): "))
                    if choice == "3":
                        available = borrow_resource(resources, fellows, records, fellow_id, resource_id, quantity)
                        print(f"Borrowing recorded. Available now: {available}")
                    else:
                        available = return_resource(resources, fellows, records, fellow_id, resource_id, quantity)
                        print(f"Return recorded. Available now: {available}")
                elif choice in ("5", "6"):
                    query = input("Search term: ")
                    list_resources(search_resources(resources, query, choice == "6"))
                elif choice == "7":
                    generate_report(resources)
                elif choice == "8":
                    for fellow_id, name in fellows.items():
                        print(f"{fellow_id}: {name}")
                else:
                    print("Invalid option. Choose 0-8.")
            except ValueError as error:
                print(f"Invalid input: {error}")
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended.")
    print("Goodbye from CampusKit. Session changes are not saved.")
    return 0


def run_demo():
    """Run the required steps on fresh data and check their actual results."""
    from copy import deepcopy

    resources, fellows, records = create_initial_state()
    print("CampusKit required demonstration")
    steps = [
        ("1. F001 borrows 2 laptops", "borrow", "F001", "R001", 2, 8),
        ("2. F002 borrows 3 keyboards", "borrow", "F002", "R002", 3, 2),
        ("3. F001 returns 1 laptop", "return", "F001", "R001", 1, 9),
        ("4. F003 requests 4 headsets", "borrow", "F003", "R003", 4, None),
        ("5. F002 tries to return 4 keyboards", "return", "F002", "R002", 4, None),
    ]
    for title, action, fellow_id, resource_id, quantity, expected in steps:
        print("\n" + title)
        before = deepcopy((resources, fellows, records))
        try:
            if action == "borrow":
                available = borrow_resource(resources, fellows, records, fellow_id, resource_id, quantity)
            else:
                available = return_resource(resources, fellows, records, fellow_id, resource_id, quantity)
        except ValueError as error:
            if expected is not None or (resources, fellows, records) != before:
                raise RuntimeError("Demonstration failed.") from error
            print(f"Rejected: {error}")
            print("All state unchanged: PASS")
        else:
            if expected is None or available != expected:
                raise RuntimeError("Demonstration produced an incorrect result.")
        for resource in resources:
            if resource["id"] == resource_id:
                print(f"{resource['name']} available: {resource['available']}")
    print("\n6. Search for LAPtop")
    matches = search_resources(resources, "LAPtop")
    list_resources(matches)
    if len(matches) != 1 or matches[0]["id"] != "R001":
        raise RuntimeError("Search demonstration failed.")
    print("\n7. Generate the report")
    report = generate_report(resources)
    if (report["total"], report["available"], report["borrowed"]) != (18, 14, 4):
        raise RuntimeError("Report totals are incorrect.")
    if report["low_stock"] != [resources[1]] or report["most_borrowed"] != [resources[1]]:
        raise RuntimeError("Report leaders or low stock are incorrect.")
    print("\nAdditional invalid-input test: F001 requests 'two' laptops")
    before = deepcopy((resources, fellows, records))
    try:
        borrow_resource(resources, fellows, records, "F001", "R001", "two")
    except ValueError as error:
        print(f"Rejected: {error}")
    else:
        raise RuntimeError("Invalid quantity was accepted.")
    if (resources, fellows, records) != before:
        raise RuntimeError("Rejected request changed state.")
    print("All state unchanged: PASS")
    print("All seven steps and the additional invalid-input test: PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CampusKit resource management")
    parser.add_argument("--demo", action="store_true", help="run the required demonstration")
    args = parser.parse_args()
    if args.demo:
        run_demo()
    else:
        raise SystemExit(main())
