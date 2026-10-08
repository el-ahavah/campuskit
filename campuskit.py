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
    """Read a positive whole number for future resource and loan prompts."""
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


def show_menu():
    """Display only the actions currently implemented."""
    print("\nCampusKit | Main menu")
    print("1. View session overview")
    print("2. View registered fellows")
    print("0. Exit")


def read_menu_choice():
    """Keep asking until the user chooses an available menu action."""
    while True:
        choice = read_non_empty("Choose an option (0-2): ")
        if choice in ("0", "1", "2"):
            return choice
        print("Invalid option. Please choose 0, 1, or 2.")


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
    print("Stage 2: session overview and fellow directory are ready.")
    print("Inventory editing, borrowing, and returns arrive in later stages.")
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
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended. Closing CampusKit.")
    print("Goodbye from CampusKit.")


if __name__ == "__main__":
    main()
