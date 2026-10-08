"""Foundation and inventory checks; run with python -m unittest -v."""

import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import campuskit


class FoundationTests(unittest.TestCase):
    def test_starting_data_matches_brief(self):
        resources, fellows, loans = campuskit.create_initial_state()
        self.assertEqual(resources, [
            {"id": "R001", "name": "Laptop", "category": "Electronics", "total": 10, "available": 10},
            {"id": "R002", "name": "Keyboard", "category": "Accessories", "total": 5, "available": 5},
            {"id": "R003", "name": "Headset", "category": "Accessories", "total": 3, "available": 3},
        ])
        self.assertEqual(fellows, {"F001": "Ada", "F002": "John", "F003": "Grace"})
        self.assertEqual(loans, [])

    def test_sessions_do_not_share_mutable_data(self):
        resources, fellows, loans = campuskit.create_initial_state()
        resources[0]["available"] = 0
        fellows["F001"] = "Changed"
        loans.append({"resource_id": "R001"})
        fresh_resources, fresh_fellows, fresh_loans = campuskit.create_initial_state()
        self.assertEqual(fresh_resources[0]["available"], 10)
        self.assertEqual(fresh_fellows["F001"], "Ada")
        self.assertEqual(fresh_loans, [])

    def test_text_helper_retries_blank_and_trims_spaces(self):
        with patch("builtins.input", side_effect=["", "   ", " Laptop "]), redirect_stdout(io.StringIO()):
            self.assertEqual(campuskit.read_non_empty("Name: "), "Laptop")

    def test_quantity_helper_rejects_invalid_values_before_accepting(self):
        output = io.StringIO()
        with patch("builtins.input", side_effect=["", "two", "2.5", "0", "-2", " 3 "]), redirect_stdout(output):
            self.assertEqual(campuskit.read_positive_integer("Quantity: "), 3)
        self.assertIn("cannot be blank", output.getvalue())
        self.assertEqual(output.getvalue().count("positive whole number"), 4)

    def test_cli_recovers_from_invalid_input_and_repeats_menu(self):
        result = subprocess.run(
            [sys.executable, str(Path(campuskit.__file__))],
            input="\nwrong\n9\n1\n2\n0\n", text=True,
            capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("cannot be blank", result.stdout)
        self.assertEqual(result.stdout.count("Invalid option"), 2)
        self.assertEqual(result.stdout.count("CampusKit | Main menu"), 3)
        self.assertIn("Resource types: 3", result.stdout)
        self.assertIn("Borrowing records: 0", result.stdout)
        for fellow in ("F001  Ada", "F002  John", "F003  Grace"):
            self.assertIn(fellow, result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith("Goodbye from CampusKit."))

    def test_eof_and_keyboard_interrupt_exit_cleanly(self):
        for interruption in (EOFError, KeyboardInterrupt):
            with self.subTest(interruption=interruption):
                output = io.StringIO()
                with patch("builtins.input", side_effect=interruption), redirect_stdout(output):
                    campuskit.main()
                self.assertIn("Input ended. Closing CampusKit.", output.getvalue())
                self.assertIn("Goodbye from CampusKit.", output.getvalue())


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.resources, self.fellows, self.loans = campuskit.create_initial_state()

    def test_add_normalizes_fields_and_sets_available_to_total(self):
        before = deepcopy(self.resources)
        resource = campuskit.add_resource(self.resources, " r004 ", " Projector ", " Electronics ", 4)
        self.assertEqual(resource, {
            "id": "R004", "name": "Projector", "category": "Electronics", "total": 4, "available": 4,
        })
        self.assertEqual(self.resources, before + [resource])

    def test_duplicate_ids_leave_all_state_unchanged(self):
        before = deepcopy((self.resources, self.fellows, self.loans))
        for resource_id in ("R001", "r001", " R001 "):
            with self.subTest(resource_id=resource_id):
                with self.assertRaisesRegex(ValueError, "already exists"):
                    campuskit.add_resource(self.resources, resource_id, "Other", "Other", 2)
                self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_invalid_fields_leave_all_state_unchanged(self):
        before = deepcopy((self.resources, self.fellows, self.loans))
        valid = ["R004", "Projector", "Electronics", 2]
        cases = [(index, value) for index in range(3) for value in ("", "  ", None, 123)]
        cases += [(3, value) for value in (0, -1, 2.5, 2.0, "2", "two", True, False, None)]
        for index, value in cases:
            with self.subTest(field=index, value=value):
                args = valid.copy()
                args[index] = value
                with self.assertRaises(ValueError):
                    campuskit.add_resource(self.resources, *args)
                self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_find_resource_normalizes_id_and_handles_missing_id(self):
        self.assertEqual(campuskit.find_resource(self.resources, " r001 ")["name"], "Laptop")
        self.assertIsNone(campuskit.find_resource(self.resources, "R999"))

    def test_listing_contains_all_fields_and_preserves_inventory(self):
        self.resources[0]["available"] = 8
        before = deepcopy(self.resources)
        output = io.StringIO()
        with redirect_stdout(output):
            campuskit.list_resources(self.resources)
        lines = output.getvalue().splitlines()
        self.assertEqual(lines[2].split(), ["ID", "Name", "Category", "Total", "Available"])
        self.assertEqual(lines[4].split(), ["R001", "Laptop", "Electronics", "10", "8"])
        self.assertEqual(lines[5].split(), ["R002", "Keyboard", "Accessories", "5", "5"])
        self.assertEqual(lines[6].split(), ["R003", "Headset", "Accessories", "3", "3"])
        self.assertEqual(self.resources, before)

    def test_empty_inventory_can_be_listed_then_populated(self):
        resources = []
        output = io.StringIO()
        with redirect_stdout(output):
            campuskit.list_resources(resources)
        self.assertIn("No resources yet", output.getvalue())
        campuskit.add_resource(resources, "R004", "Projector", "Electronics", 1)
        self.assertEqual(resources[0]["available"], 1)

    def test_interrupted_add_does_not_partially_change_inventory(self):
        before = deepcopy(self.resources)
        for interruption in (EOFError, KeyboardInterrupt):
            with self.subTest(interruption=interruption):
                with patch("builtins.input", side_effect=["R004", "Projector", interruption]), redirect_stdout(io.StringIO()):
                    with self.assertRaises(interruption):
                        campuskit.prompt_add_resource(self.resources)
                self.assertEqual(self.resources, before)

    def test_cli_add_retry_duplicate_and_list_flow(self):
        result = subprocess.run(
            [sys.executable, str(Path(campuskit.__file__))],
            input="4\n r004 \n\nProjector\n \nElectronics\ntwo\n2.5\n0\n-1\n4\n4\nr004\n3\n1\n0\n",
            text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("Added R004 | Projector | 4 of 4 units available.", result.stdout)
        self.assertIn("already exists. Nothing was added.", result.stdout)
        self.assertIn("Resource types: 4", result.stdout)
        self.assertEqual(result.stdout.count("cannot be blank"), 2)
        self.assertEqual(result.stdout.count("positive whole number"), 4)
        self.assertIn(["R004", "Projector", "Electronics", "4", "4"],
                      [line.split() for line in result.stdout.splitlines()])
        self.assertTrue(result.stdout.rstrip().endswith("Goodbye from CampusKit."))


if __name__ == "__main__":
    unittest.main()
