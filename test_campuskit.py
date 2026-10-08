"""CampusKit regression checks; run with python -m unittest -v."""

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


class BorrowingTests(unittest.TestCase):
    def setUp(self):
        self.resources, self.fellows, self.loans = campuskit.create_initial_state()

    def borrow(self, fellow_id, resource_id, quantity):
        return campuskit.borrow_resource(
            self.resources, self.fellows, self.loans, fellow_id, resource_id, quantity
        )

    def test_required_first_two_borrowings(self):
        first = self.borrow("F001", "R001", 2)
        second = self.borrow("F002", "R002", 3)
        self.assertEqual([r["available"] for r in self.resources], [8, 2, 3])
        self.assertEqual([r["total"] for r in self.resources], [10, 5, 3])
        self.assertEqual(self.loans, [
            {"loan_id": "L001", "fellow_id": "F001", "resource_id": "R001",
             "quantity_borrowed": 2, "quantity_returned": 0},
            {"loan_id": "L002", "fellow_id": "F002", "resource_id": "R002",
             "quantity_borrowed": 3, "quantity_returned": 0},
        ])
        self.assertEqual(first, self.loans[0])
        self.assertEqual(second, self.loans[1])

    def test_rejected_requests_preserve_all_state_and_next_loan_id(self):
        self.borrow("F001", "R001", 2)
        before = deepcopy((self.resources, self.fellows, self.loans))
        cases = [("F999", "R001", 1), ("F001", "R999", 1), ("F003", "R003", 4)]
        cases += [("F001", "R001", q) for q in (0, -1, 1.5, 2.0, "two", "2", None, True, False)]
        cases += [(bad, "R001", 1) for bad in ("", " ", None, 123)]
        cases += [("F001", bad, 1) for bad in ("", " ", None, 123)]
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    self.borrow(*args)
                self.assertEqual((self.resources, self.fellows, self.loans), before)
        self.assertEqual(self.borrow("F002", "R002", 1)["loan_id"], "L002")

    def test_exact_stock_then_zero_stock_rejection(self):
        self.borrow("F003", "R003", 3)
        self.assertEqual(self.resources[2]["available"], 0)
        before = deepcopy((self.resources, self.fellows, self.loans))
        with self.assertRaisesRegex(ValueError, "has 0 available"):
            self.borrow("F001", "R003", 1)
        self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_repeated_loans_keep_separate_records_and_normalize_ids(self):
        self.borrow(" f001 ", " r001 ", 2)
        self.borrow("F001", "R001", 3)
        self.borrow("F002", "R001", 1)
        self.assertEqual(self.resources[0]["available"], 4)
        self.assertEqual([r["loan_id"] for r in self.loans], ["L001", "L002", "L003"])
        self.assertEqual([r["fellow_id"] for r in self.loans], ["F001", "F001", "F002"])
        self.assertEqual(sum(r["quantity_borrowed"] for r in self.loans), 6)
        self.assertTrue(all(r["resource_id"] == "R001" for r in self.loans))

    def test_newly_added_resource_can_be_borrowed(self):
        campuskit.add_resource(self.resources, "R004", "Projector", "Electronics", 2)
        self.borrow("F002", "R004", 1)
        self.assertEqual(self.resources[-1]["available"], 1)
        self.assertEqual(self.loans[-1]["resource_id"], "R004")

    def test_interrupted_borrow_does_not_change_state(self):
        before = deepcopy((self.resources, self.fellows, self.loans))
        for error in (EOFError, KeyboardInterrupt):
            for prefix in ([], ["F001"], ["F001", "R001"]):
                with self.subTest(error=error, prefix=prefix):
                    with patch("builtins.input", side_effect=prefix + [error]), redirect_stdout(io.StringIO()):
                        with self.assertRaises(error):
                            campuskit.prompt_borrow_resource(self.resources, self.fellows, self.loans)
                    self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_cli_borrow_receipts_rejections_and_stock(self):
        result = subprocess.run(
            [sys.executable, str(Path(campuskit.__file__))],
            input="5\n f001 \n r001 \ntwo\n0\n-1\n1.5\n2\n5\nF002\nR002\n3\n5\nF003\nR003\n4\n5\nF999\nR001\n1\n5\nF001\nR999\n1\n3\n1\n0\n",
            text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.count("Borrowing confirmed"), 2)
        self.assertEqual(result.stdout.count("Borrowing rejected"), 3)
        self.assertEqual(result.stdout.count("positive whole number"), 4)
        for text in ("Fellow: F001 | Ada", "Resource: R001 | Laptop",
                     "Quantity borrowed: 2", "Available now: 8", "Available now: 2",
                     "Unknown fellow ID F999", "Unknown resource ID R999", "Borrowing records: 2"):
            self.assertIn(text, result.stdout)
        rows = [line.split() for line in result.stdout.splitlines()]
        for row in (["R001", "Laptop", "Electronics", "10", "8"],
                    ["R002", "Keyboard", "Accessories", "5", "2"],
                    ["R003", "Headset", "Accessories", "3", "3"]):
            self.assertIn(row, rows)
        self.assertTrue(result.stdout.rstrip().endswith("Goodbye from CampusKit."))


class ReturnTests(unittest.TestCase):
    def setUp(self):
        self.resources, self.fellows, self.loans = campuskit.create_initial_state()

    def borrow(self, fellow, resource, quantity):
        return campuskit.borrow_resource(self.resources, self.fellows, self.loans, fellow, resource, quantity)

    def give_back(self, fellow, resource, quantity):
        return campuskit.return_resource(self.resources, self.fellows, self.loans, fellow, resource, quantity)

    def assert_stock_matches_loans(self):
        for resource in self.resources:
            owed = sum(r["quantity_borrowed"] - r["quantity_returned"]
                       for r in self.loans if r["resource_id"] == resource["id"])
            self.assertEqual(resource["available"] + owed, resource["total"])
            self.assertGreaterEqual(resource["available"], 0)
            self.assertLessEqual(resource["available"], resource["total"])

    def test_required_steps_one_to_five_in_order(self):
        self.borrow("F001", "R001", 2)
        self.assertEqual(self.resources[0]["available"], 8)
        self.borrow("F002", "R002", 3)
        self.assertEqual(self.resources[1]["available"], 2)
        receipt = self.give_back(" f001 ", " r001 ", 1)
        self.assertEqual(receipt, {"fellow_id": "F001", "resource_id": "R001",
                                  "quantity_returned": 1, "outstanding": 1, "available": 9})
        before = deepcopy((self.resources, self.fellows, self.loans))
        with self.assertRaises(ValueError):
            self.borrow("F003", "R003", 4)
        self.assertEqual((self.resources, self.fellows, self.loans), before)
        with self.assertRaisesRegex(ValueError, "has 3 units.*cannot return 4"):
            self.give_back("F002", "R002", 4)
        self.assertEqual((self.resources, self.fellows, self.loans), before)
        self.assertEqual(self.loans[0]["quantity_returned"], 1)
        self.assertEqual(self.loans[1]["quantity_returned"], 0)
        self.assertEqual(sum(r["available"] for r in self.resources), 14)
        self.assert_stock_matches_loans()

    def test_full_return_retains_history_and_rejects_double_return(self):
        self.borrow("F001", "R001", 2)
        self.give_back("F001", "R001", 2)
        self.assertEqual(self.resources[0]["available"], 10)
        self.assertEqual(len(self.loans), 1)
        self.assertEqual(self.loans[0]["quantity_borrowed"], 2)
        self.assertEqual(self.loans[0]["quantity_returned"], 2)
        before = deepcopy((self.resources, self.fellows, self.loans))
        with self.assertRaisesRegex(ValueError, "has 0 units"):
            self.give_back("F001", "R001", 1)
        self.assertEqual((self.resources, self.fellows, self.loans), before)
        self.assertEqual(self.borrow("F001", "R001", 1)["loan_id"], "L002")
        self.give_back("F001", "R001", 1)
        self.assertEqual([r["quantity_returned"] for r in self.loans], [2, 1])
        self.assert_stock_matches_loans()

    def test_returns_span_oldest_loans_without_touching_other_loans(self):
        self.borrow("F001", "R001", 2)
        self.borrow("F002", "R001", 1)
        self.borrow("F001", "R002", 1)
        self.borrow("F001", "R001", 3)
        other_loans = deepcopy([self.loans[1], self.loans[2]])
        self.give_back("F001", "R001", 1)
        self.give_back("F001", "R001", 3)
        self.assertEqual([r["quantity_returned"] for r in self.loans], [2, 0, 0, 2])
        self.assertEqual([self.loans[1], self.loans[2]], other_loans)
        self.assertEqual(campuskit.outstanding_quantity(self.loans, " f001 ", " r001 "), 1)
        self.assertEqual(self.resources[0]["available"], 8)
        self.give_back("F001", "R001", 1)
        self.assertEqual(self.resources[0]["available"], 9)
        self.assert_stock_matches_loans()

    def test_excessive_return_across_multiple_loans_is_not_partially_applied(self):
        self.borrow("F001", "R001", 2)
        self.borrow("F001", "R001", 3)
        self.give_back("F001", "R001", 1)
        before = deepcopy((self.resources, self.fellows, self.loans))
        with self.assertRaisesRegex(ValueError, "has 4 units"):
            self.give_back("F001", "R001", 5)
        self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_invalid_returns_preserve_all_state(self):
        self.borrow("F001", "R001", 2)
        before = deepcopy((self.resources, self.fellows, self.loans))
        cases = [("F999", "R001", 1), ("F001", "R999", 1),
                 ("F002", "R001", 1), ("F001", "R002", 1)]
        cases += [("F001", "R001", q) for q in (0, -1, 1.5, 2.0, "2", "two", None, True, False)]
        cases += [(bad, "R001", 1) for bad in ("", " ", None, 123)]
        cases += [("F001", bad, 1) for bad in ("", " ", None, 123)]
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    self.give_back(*args)
                self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_return_without_any_borrowings_is_rejected(self):
        before = deepcopy((self.resources, self.fellows, self.loans))
        with self.assertRaisesRegex(ValueError, "has 0 units"):
            self.give_back("F001", "R001", 1)
        self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_interrupted_return_preserves_state(self):
        self.borrow("F001", "R001", 2)
        before = deepcopy((self.resources, self.fellows, self.loans))
        for error in (EOFError, KeyboardInterrupt):
            for prefix in ([], ["F001"], ["F001", "R001"]):
                with self.subTest(error=error, prefix=prefix):
                    with patch("builtins.input", side_effect=prefix + [error]), redirect_stdout(io.StringIO()):
                        with self.assertRaises(error):
                            campuskit.prompt_return_resource(self.resources, self.fellows, self.loans)
                    self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_cli_return_receipts_rejections_and_inventory(self):
        result = subprocess.run(
            [sys.executable, str(Path(campuskit.__file__))],
            input="5\nF001\nR001\n2\n5\nF002\nR002\n3\n6\n f001 \n r001 \n\ntwo\n0\n-1\n1.5\n1\n5\nF003\nR003\n4\n6\nF002\nR002\n4\n3\n1\n0\n",
            text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.count("Return confirmed"), 1)
        self.assertEqual(result.stdout.count("Return rejected"), 1)
        self.assertEqual(result.stdout.count("positive whole number"), 4)
        for text in ("Quantity returned: 1", "Still on loan for this fellow: 1",
                     "Available now: 9", "cannot return 4", "Borrowing records: 2"):
            self.assertIn(text, result.stdout)
        rows = [line.split() for line in result.stdout.splitlines()]
        for row in (["R001", "Laptop", "Electronics", "10", "9"],
                    ["R002", "Keyboard", "Accessories", "5", "2"],
                    ["R003", "Headset", "Accessories", "3", "3"]):
            self.assertIn(row, rows)
        self.assertTrue(result.stdout.rstrip().endswith("Goodbye from CampusKit."))


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.resources, self.fellows, self.loans = campuskit.create_initial_state()

    def test_name_search_ignores_case_and_supports_partial_matches(self):
        for query in ("LAPtop", " laptop ", "LAP", "top"):
            with self.subTest(query=query):
                self.assertEqual([r["id"] for r in campuskit.search_resources(self.resources, query)], ["R001"])
        self.assertEqual([r["id"] for r in campuskit.search_resources(self.resources, "a")],
                         ["R001", "R002", "R003"])
        self.assertEqual(campuskit.search_resources(self.resources, "Electronics"), [])

    def test_category_filter_is_case_insensitive_but_exact(self):
        for category in ("Accessories", "ACCESSORIES", " accessories "):
            with self.subTest(category=category):
                self.assertEqual([r["id"] for r in campuskit.filter_by_category(self.resources, category)],
                                 ["R002", "R003"])
        self.assertEqual(campuskit.filter_by_category(self.resources, "Access"), [])
        self.assertEqual(campuskit.filter_by_category(self.resources, "Laptop"), [])

    def test_empty_no_match_and_invalid_queries_preserve_state(self):
        before = deepcopy((self.resources, self.fellows, self.loans))
        for function in (campuskit.search_resources, campuskit.filter_by_category):
            self.assertEqual(function([], "Laptop"), [])
            self.assertEqual(function(self.resources, "Missing"), [])
            for query in ("", "  ", None, 123):
                with self.subTest(function=function.__name__, query=query):
                    with self.assertRaises(ValueError):
                        function(self.resources, query)
            self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_search_after_steps_one_to_five_shows_current_stock_without_changes(self):
        campuskit.borrow_resource(self.resources, self.fellows, self.loans, "F001", "R001", 2)
        campuskit.borrow_resource(self.resources, self.fellows, self.loans, "F002", "R002", 3)
        campuskit.return_resource(self.resources, self.fellows, self.loans, "F001", "R001", 1)
        with self.assertRaises(ValueError):
            campuskit.borrow_resource(self.resources, self.fellows, self.loans, "F003", "R003", 4)
        with self.assertRaises(ValueError):
            campuskit.return_resource(self.resources, self.fellows, self.loans, "F002", "R002", 4)
        before = deepcopy((self.resources, self.fellows, self.loans))
        matches = campuskit.search_resources(self.resources, "LAPtop")
        self.assertEqual(matches, [{"id": "R001", "name": "Laptop", "category": "Electronics",
                                    "total": 10, "available": 9}])
        self.assertEqual([r["available"] for r in campuskit.filter_by_category(self.resources, "Accessories")], [2, 3])
        self.assertEqual((self.resources, self.fellows, self.loans), before)

    def test_new_resources_and_zero_stock_remain_searchable(self):
        campuskit.add_resource(self.resources, "R004", "Laptop Stand", "accessories", 1)
        campuskit.borrow_resource(self.resources, self.fellows, self.loans, "F001", "R004", 1)
        self.assertEqual([r["id"] for r in campuskit.search_resources(self.resources, "laptop")], ["R001", "R004"])
        matches = campuskit.filter_by_category(self.resources, "ACCESSORIES")
        self.assertEqual([r["id"] for r in matches], ["R002", "R003", "R004"])
        self.assertEqual(matches[-1]["available"], 0)

    def test_cli_search_filter_blank_retry_and_no_matches(self):
        result = subprocess.run(
            [sys.executable, str(Path(campuskit.__file__))],
            input="7\n\n LAPtop \n8\n \n aCCESSories \n7\nMissing\n8\nAccess\n0\n",
            text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.count("cannot be blank"), 2)
        self.assertIn("Matches found: 1", result.stdout)
        self.assertIn("Matches found: 2", result.stdout)
        self.assertIn("No resources match name 'Missing'.", result.stdout)
        self.assertIn("No resources found in category 'Access'.", result.stdout)
        rows = [line.split() for line in result.stdout.splitlines()]
        for row in (["R001", "Laptop", "Electronics", "10", "10"],
                    ["R002", "Keyboard", "Accessories", "5", "5"],
                    ["R003", "Headset", "Accessories", "3", "3"]):
            self.assertEqual(rows.count(row), 1)
        self.assertTrue(result.stdout.rstrip().endswith("Goodbye from CampusKit."))


if __name__ == "__main__":
    unittest.main()
