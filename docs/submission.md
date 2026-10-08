# CampusKit submission guide

The project and evidence are prepared. Nothing has been submitted to the assessment platform automatically.

## A1 — Source code (50 marks)

Open [campuskit.py](../campuskit.py) and paste its complete contents into the source-code field as requested. This one file contains the application and demonstration; `test_campuskit.py` is the separate test suite.

Viewable source link: https://github.com/el-ahavah/campuskit/blob/main/campuskit.py

If submitting a link to a particular version, open the final commit on GitHub and use its file link. Ensure the assessor can access the repository.

## A2 — Demonstration and test evidence (15 marks)

Paste the actual contents of [demo-output.txt](demo-output.txt). It includes Steps 1–7 in order and the additional invalid-input test in which F001 requests `two` laptops. The transcript prints actual results and verifies unchanged state after rejected requests.

Include [test-output.txt](test-output.txt) as test evidence. It records 48 passing tests. JSON persistence is deferred, so do not include old persistence evidence or claim the optional bonus.

These files contain real captured output. The README's acceptance table is a specification, not a substitute for the transcript. The text-quantity case in the demo tests the borrowing function directly; the test suite separately exercises invalid text through interactive prompts.

## A3 — Project design explanation (5 marks)

Use [design.md](design.md), which names and explains more than four implemented functions, describes the inventory and fellow-loan representations, and explains the single-operator limitation.

For a short text field, the following explanation covers the requested points:

CampusKit stores inventory as a list of dictionaries containing each resource's ID, name, category, total units, and available units. Fellows are stored in a dictionary mapping IDs to names. Loans are a list of dictionaries containing the loan ID, fellow ID, resource ID, quantity borrowed, and quantity returned. The difference between borrowed and returned quantities is the outstanding loan. `add_resource()` validates and adds unique resources. `borrow_resource()` checks IDs, quantity, and stock before recording a loan and reducing availability. `return_resource()` checks what the fellow owes, settles the oldest matching loans, and restores stock. `search_resources()` finds names without case sensitivity, while `generate_report()` calculates current stock totals, low-stock items, and all tied most-borrowed resources. One limitation is that all data is held in memory and lost when the program closes; each new launch starts with the original inventory and no loans.

## Run it yourself before submitting

Download the repository ZIP and extract it, or clone the repository. Open a terminal in the project directory. Python 3 is required; no package installation is needed.

```bash
python campuskit.py --demo
python -m unittest -v
python campuskit.py
```

On systems where needed, replace `python` with `python3` or Windows `py`. Review the actual output and practise explaining a borrowing and a return. Follow your programme's rules for acknowledging assistance.

Final checks for the fellow:

- [ ] Paste the complete source into A1, or provide the source link if accepted.
- [ ] Paste the demonstration transcript and test evidence into A2.
- [ ] Paste the design explanation into A3.
- [ ] Use only the current evidence; the optional JSON bonus is deferred.
- [ ] Confirm the assessor can view any submitted links, then submit the form.
